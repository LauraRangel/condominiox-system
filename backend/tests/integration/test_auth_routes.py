from tests.integration.conftest import token_expirado, token_firma_invalida


class TestLogin:
    def test_login_exitoso(self, client, admin_token):
        assert admin_token  # el fixture ya valida 200 + token presente

    def test_login_tipo_incorrecto(self, client, admin_token, propietario_creado):
        resp = client.post(
            "/api/login",
            json={
                "usuario": propietario_creado["usuario"],
                "contrasena": propietario_creado["dni"],
                "tipo": "Administrador",
            },
        )
        assert resp.status_code == 401
        assert resp.get_json()["error"] == "Usuario o contraseña inválidos"

    def test_login_password_incorrecta(self, client, propietario_creado):
        resp = client.post(
            "/api/login",
            json={
                "usuario": propietario_creado["usuario"],
                "contrasena": "clave-equivocada",
                "tipo": "Propietario",
            },
        )
        assert resp.status_code == 401
        assert resp.get_json()["error"] == "Usuario o contraseña inválidos"

    def test_login_usuario_inexistente(self, client):
        resp = client.post(
            "/api/login",
            json={"usuario": "no-existe", "contrasena": "x", "tipo": "Administrador"},
        )
        assert resp.status_code == 401
        assert resp.get_json()["error"] == "Usuario o contraseña inválidos"

    def test_login_datos_incompletos(self, client):
        resp = client.post("/api/login", json={"usuario": "a"})
        assert resp.status_code == 400


class TestMiddlewareToken:
    def test_sin_token(self, client):
        resp = client.get("/api/mi-perfil")
        assert resp.status_code == 401
        assert resp.get_json()["error"] == "Token requerido"

    def test_token_firma_invalida(self, client):
        resp = client.get(
            "/api/mi-perfil",
            headers={"Authorization": f"Bearer {token_firma_invalida()}"},
        )
        assert resp.status_code == 401
        assert resp.get_json()["error"] == "Token inválido"

    def test_token_expirado(self, client):
        resp = client.get(
            "/api/mi-perfil",
            headers={"Authorization": f"Bearer {token_expirado()}"},
        )
        assert resp.status_code == 401
        assert resp.get_json()["error"] == "Token expirado"

    def test_token_malformado_sin_bearer(self, client):
        resp = client.get("/api/mi-perfil", headers={"Authorization": "abc123"})
        assert resp.status_code == 401
        assert resp.get_json()["error"] == "Token requerido"


class TestMiddlewareRoles:
    def test_rol_incorrecto_devuelve_403(self, client, propietario_token):
        resp = client.get(
            "/api/propietarios",
            headers={"Authorization": f"Bearer {propietario_token}"},
        )
        assert resp.status_code == 403
        assert resp.get_json()["error"] == "No autorizado"

    def test_rol_correcto_permite_acceso(self, client, admin_token):
        resp = client.get(
            "/api/propietarios",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
