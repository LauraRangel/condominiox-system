"""Pruebas de seguridad: fuerza bruta, validación de entradas, CORS, cabeceras y errores."""


def _h(token):
    return {"Authorization": f"Bearer {token}"}


class TestFuerzaBruta:
    def test_login_se_bloquea_tras_5_fallos(self, client, propietario_creado):
        for _ in range(5):
            r = client.post("/api/login", json={"usuario": "jperez", "contrasena": "mala", "tipo": "Propietario"})
            assert r.status_code == 401
        r = client.post("/api/login", json={"usuario": "jperez", "contrasena": "12345678", "tipo": "Propietario"})
        assert r.status_code == 429
        assert "Retry-After" in r.headers

    def test_recuperar_no_revela_si_el_usuario_existe(self, client, propietario_creado):
        a = client.post("/api/recuperar-contrasena", json={"usuario": "noexiste", "dni": "12345678",
                                                           "nueva_contrasena": "Nueva2026"})
        b = client.post("/api/recuperar-contrasena", json={"usuario": "jperez", "dni": "00000000",
                                                           "nueva_contrasena": "Nueva2026"})
        assert a.status_code == b.status_code == 403
        assert a.get_json() == b.get_json()


class TestContrasenas:
    def test_login_con_dni_pide_cambiar_contrasena(self, client, propietario_creado):
        r = client.post("/api/login", json={"usuario": "jperez", "contrasena": "12345678", "tipo": "Propietario"})
        assert r.get_json()["user"]["debe_cambiar_contrasena"] is True

    def test_contrasena_debil_rechazada(self, client, propietario_token):
        for debil in ["corta1", "solotexto", "12345678"]:
            r = client.put("/api/mi-contrasena", headers=_h(propietario_token),
                           json={"actual_contrasena": "12345678", "nueva_contrasena": debil})
            assert r.status_code == 400


class TestEntradas:
    def test_telefono_con_html_rechazado(self, client, propietario_token):
        r = client.put("/api/mi-perfil", headers=_h(propietario_token),
                       json={"correo": "a@b.pe", "telefono": "<svg onload=x()>"})
        assert r.status_code == 400

    def test_nombre_con_html_rechazado(self, client, admin_token):
        r = client.post("/api/propietarios", headers=_h(admin_token), json={
            "usuario": "malo", "nombre": "<script>", "apellido": "X", "dni": "87654321",
            "nro_departamento": "101", "torre": "B"})
        assert r.status_code == 400


class TestCabecerasYCors:
    def test_cabeceras_de_seguridad(self, client):
        r = client.get("/api/health")
        assert r.headers["X-Content-Type-Options"] == "nosniff"
        assert r.headers["X-Frame-Options"] == "DENY"
        assert "default-src 'none'" in r.headers["Content-Security-Policy"]

    def test_cors_rechaza_origen_desconocido(self, client):
        r = client.options("/api/login", headers={"Origin": "https://sitio-malicioso.com",
                                                  "Access-Control-Request-Method": "POST"})
        assert "Access-Control-Allow-Origin" not in r.headers

    def test_cors_permite_el_frontend(self, client):
        r = client.options("/api/login", headers={"Origin": "https://laurarangel.github.io",
                                                  "Access-Control-Request-Method": "POST"})
        assert r.headers.get("Access-Control-Allow-Origin") == "https://laurarangel.github.io"

    def test_error_interno_no_expone_detalles(self, client, admin_token, monkeypatch):
        def falla(*a, **k):
            raise RuntimeError("password=secreto en la base de datos")
        monkeypatch.setattr("services.propietario_service.listar_propietarios", falla)
        r = client.get("/api/propietarios", headers=_h(admin_token))
        assert r.status_code == 500
        assert "secreto" not in r.get_data(as_text=True)
