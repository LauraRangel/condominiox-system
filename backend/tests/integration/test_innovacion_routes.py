"""Pruebas de integración de los componentes innovadores (APF3):
pasarela de pagos emulada, reserva de áreas comunes y asistente con IA."""

import datetime as dt

import pytest

from db import execute, fetch_one

LIMA = dt.timezone(dt.timedelta(hours=-5))
TOKEN_OK = "tkn_test_visa_1111_abcdef123456"
TOKEN_RECHAZO = "tkn_test_visa_0002_abcdef123456"


def _h(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def recibo_mes(client, admin_token, propietario_token):
    """Genera un recibo del mes actual de S/ 150.00 (100 admin + 50 agua)."""
    hoy = dt.datetime.now(LIMA).date()
    client.put("/api/configuracion", json={"monto_administracion": 100}, headers=_h(admin_token))
    client.post("/api/gastos", json={"proveedor": "Sedapal", "concepto": "Agua", "monto": 50,
                                     "tipo": "agua", "fecha_registro": hoy.isoformat()},
                headers=_h(admin_token))
    resp = client.post("/api/recibos/generar", json={"fecha_emision": hoy.isoformat()}, headers=_h(admin_token))
    assert resp.status_code == 200, resp.get_json()
    return resp.get_json()["items"][0]


@pytest.fixture(autouse=True)
def _sin_llm(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)


class TestPasarela:
    def test_pago_con_tarjeta_concilia_recibo(self, client, propietario_token, recibo_mes):
        resp = client.post("/api/pagos", headers=_h(propietario_token), json={
            "recibo_id": recibo_mes["id"], "monto": 150, "proveedor": "culqi",
            "datos": {"token_id": TOKEN_OK}})
        assert resp.status_code == 201, resp.get_json()
        data = resp.get_json()
        assert data["transaccion"]["estado"] == "aprobado"
        assert data["transaccion"]["codigo_operacion"].startswith("chr_test_")
        assert data["recibo"]["pagado"] is True

    def test_pago_rechazado_no_toca_el_recibo(self, client, propietario_token, recibo_mes):
        resp = client.post("/api/pagos", headers=_h(propietario_token), json={
            "recibo_id": recibo_mes["id"], "monto": 150, "proveedor": "culqi",
            "datos": {"token_id": TOKEN_RECHAZO}})
        assert resp.status_code == 402
        row = fetch_one("SELECT monto_pagado FROM recibos WHERE id = %s", [recibo_mes["id"]])
        assert float(row["monto_pagado"]) == 0

    def test_pago_parcial_con_yape(self, client, propietario_token, recibo_mes):
        resp = client.post("/api/pagos", headers=_h(propietario_token), json={
            "recibo_id": recibo_mes["id"], "monto": 40, "proveedor": "yape",
            "datos": {"celular": "912345678", "otp": "123456"}})
        assert resp.status_code == 201
        assert resp.get_json()["recibo"]["saldo"] == 110.0

    def test_idempotencia_no_cobra_dos_veces(self, client, propietario_token, recibo_mes):
        body = {"recibo_id": recibo_mes["id"], "monto": 40, "proveedor": "yape",
                "datos": {"celular": "912345678", "otp": "123456"}}
        h = {**_h(propietario_token), "Idempotency-Key": "abc-123"}
        r1 = client.post("/api/pagos", headers=h, json=body)
        r2 = client.post("/api/pagos", headers=h, json=body)
        assert r1.status_code == 201 and r2.status_code == 200
        assert r2.get_json()["repetido"] is True
        row = fetch_one("SELECT monto_pagado FROM recibos WHERE id = %s", [recibo_mes["id"]])
        assert float(row["monto_pagado"]) == 40

    def test_monto_mayor_al_saldo(self, client, propietario_token, recibo_mes):
        resp = client.post("/api/pagos", headers=_h(propietario_token), json={
            "recibo_id": recibo_mes["id"], "monto": 999, "proveedor": "yape",
            "datos": {"celular": "912345678", "otp": "123456"}})
        assert resp.status_code == 400

    def test_admin_ve_transacciones(self, client, admin_token, propietario_token, recibo_mes):
        client.post("/api/pagos", headers=_h(propietario_token), json={
            "recibo_id": recibo_mes["id"], "monto": 150, "proveedor": "mercadopago",
            "datos": {"email": "juan@test.com"}})
        data = client.get("/api/pagos", headers=_h(admin_token)).get_json()
        assert data["resumen"]["aprobadas"] == 1
        assert data["resumen"]["monto_conciliado"] == 150.0

    def test_propietario_ya_no_marca_pagado_sin_pasarela(self, client, propietario_token, recibo_mes):
        resp = client.post(f"/api/recibos/{recibo_mes['id']}/pagar", json={"monto": 150},
                           headers=_h(propietario_token))
        assert resp.status_code == 403


def _manana_a_las(hora):
    fecha = dt.datetime.now(LIMA).date() + dt.timedelta(days=3)
    return fecha.isoformat()


def _area(nombre):
    return fetch_one("SELECT id, tarifa, garantia FROM areas_comunes WHERE nombre = %s", [nombre])


@pytest.fixture
def parrilla_sin_garantia():
    execute("UPDATE areas_comunes SET garantia = 0 WHERE nombre = 'Zona de parrillas'")
    return _area("Zona de parrillas")


class TestReservas:
    def test_lista_areas_sembradas(self, client, propietario_token):
        items = client.get("/api/areas-comunes", headers=_h(propietario_token)).get_json()["items"]
        assert {a["nombre"] for a in items} == {"Salón de usos múltiples", "Zona de parrillas",
                                                "Gimnasio", "Cowork", "Pet shower"}

    def test_reserva_valida_y_cargo_al_recibo(self, client, propietario_token, recibo_mes, parrilla_sin_garantia):
        area = parrilla_sin_garantia
        fecha = dt.datetime.now(LIMA).date() + dt.timedelta(days=3)
        if fecha.strftime("%Y-%m") != recibo_mes["fecha_emision"][:7]:
            pytest.skip("La fecha de prueba cae en otro mes que el recibo generado")
        resp = client.post("/api/reservas", headers=_h(propietario_token), json={
            "area_id": area["id"], "fecha": fecha.isoformat(), "hora_inicio": "13:00",
            "hora_fin": "16:00", "asistentes": 8})
        assert resp.status_code == 201, resp.get_json()
        row = fetch_one("SELECT monto_reservas FROM recibos WHERE id = %s", [recibo_mes["id"]])
        assert float(row["monto_reservas"]) == float(area["tarifa"])

    def test_reserva_sin_recibo_se_suma_al_generar(self, client, admin_token, propietario_token, parrilla_sin_garantia):
        area = parrilla_sin_garantia
        fecha = dt.datetime.now(LIMA).date() + dt.timedelta(days=3)
        resp = client.post("/api/reservas", headers=_h(propietario_token), json={
            "area_id": area["id"], "fecha": fecha.isoformat(), "hora_inicio": "13:00",
            "hora_fin": "16:00", "asistentes": 8})
        assert resp.status_code == 201, resp.get_json()
        client.put("/api/configuracion", json={"monto_administracion": 100}, headers=_h(admin_token))
        gen = client.post("/api/recibos/generar", json={"fecha_emision": fecha.isoformat()},
                          headers=_h(admin_token)).get_json()
        assert float(gen["items"][0]["monto_reservas"]) == float(area["tarifa"])
        assert gen["items"][0]["total"] == 100 + float(area["tarifa"])

    def test_cruce_de_horario_rechazado(self, client, propietario_token):
        area = _area("Zona de parrillas")
        fecha = (dt.datetime.now(LIMA).date() + dt.timedelta(days=3)).isoformat()
        body = {"area_id": area["id"], "fecha": fecha, "hora_inicio": "13:00", "hora_fin": "16:00", "asistentes": 5}
        assert client.post("/api/reservas", headers=_h(propietario_token), json=body).status_code == 201
        body.update(hora_inicio="15:00", hora_fin="17:00")
        resp = client.post("/api/reservas", headers=_h(propietario_token), json=body)
        assert resp.status_code == 409
        assert "ya está reservado" in resp.get_json()["reglas_incumplidas"][0]

    def test_supera_aforo_rechazado(self, client, propietario_token):
        area = _area("Zona de parrillas")
        fecha = (dt.datetime.now(LIMA).date() + dt.timedelta(days=3)).isoformat()
        resp = client.post("/api/reservas", headers=_h(propietario_token), json={
            "area_id": area["id"], "fecha": fecha, "hora_inicio": "13:00", "hora_fin": "16:00", "asistentes": 50})
        assert resp.status_code == 409

    def test_moroso_no_puede_reservar(self, client, propietario_token, recibo_mes):
        execute("UPDATE recibos SET fecha_emision = CURRENT_DATE - 45 WHERE id = %s", [recibo_mes["id"]])
        area = _area("Cowork")
        fecha = (dt.datetime.now(LIMA).date() + dt.timedelta(days=3)).isoformat()
        resp = client.post("/api/reservas", headers=_h(propietario_token), json={
            "area_id": area["id"], "fecha": fecha, "hora_inicio": "10:00", "hora_fin": "11:00", "asistentes": 3})
        assert resp.status_code == 409
        assert any("deuda" in e for e in resp.get_json()["reglas_incumplidas"])

    def test_cancelar_descuenta_cargo(self, client, propietario_token, recibo_mes, parrilla_sin_garantia):
        area = parrilla_sin_garantia
        fecha = dt.datetime.now(LIMA).date() + dt.timedelta(days=3)
        if fecha.strftime("%Y-%m") != recibo_mes["fecha_emision"][:7]:
            pytest.skip("La fecha de prueba cae en otro mes que el recibo generado")
        res = client.post("/api/reservas", headers=_h(propietario_token), json={
            "area_id": area["id"], "fecha": fecha.isoformat(), "hora_inicio": "13:00",
            "hora_fin": "16:00", "asistentes": 8}).get_json()
        resp = client.delete(f"/api/reservas/{res['id']}", headers=_h(propietario_token))
        assert resp.status_code == 200
        row = fetch_one("SELECT monto_reservas FROM recibos WHERE id = %s", [recibo_mes["id"]])
        assert float(row["monto_reservas"]) == 0


class TestAsistente:
    def test_responde_en_modo_respaldo_con_fuente_del_reglamento(self, client, propietario_token):
        resp = client.post("/api/asistente/consulta", headers=_h(propietario_token),
                           json={"pregunta": "¿Puedo llevar a mi perro a la zona de parrillas?"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["modo"] == "respaldo"
        assert any("Mascotas" in f["etiqueta"] for f in data["fuentes"])

    def test_responde_saldo_del_propietario(self, client, propietario_token, recibo_mes):
        data = client.post("/api/asistente/consulta", headers=_h(propietario_token),
                           json={"pregunta": "¿Cuánto debo?"}).get_json()
        assert "150.00" in data["respuesta"]
        assert any(f["tipo"] == "recibo" for f in data["fuentes"])

    def test_admin_no_usa_el_asistente_de_propietario(self, client, admin_token):
        resp = client.post("/api/asistente/consulta", headers=_h(admin_token), json={"pregunta": "hola"})
        assert resp.status_code == 403

    def test_responde_disponibilidad_de_un_area(self, client, propietario_token):
        area = _area("Zona de parrillas")
        fecha = dt.datetime.now(LIMA).date() + dt.timedelta(days=3)
        resp = client.post("/api/reservas", headers=_h(propietario_token), json={
            "area_id": area["id"], "fecha": fecha.isoformat(), "hora_inicio": "13:00",
            "hora_fin": "16:00", "asistentes": 5})
        assert resp.status_code == 201, resp.get_json()
        meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
                 "septiembre", "octubre", "noviembre", "diciembre"]
        cuando = f"el {fecha.day} de {meses[fecha.month - 1]}"

        data = client.post("/api/asistente/consulta", headers=_h(propietario_token),
                           json={"pregunta": f"¿Hay horario disponible en la zona de parrillas a las 2pm {cuando}?"}).get_json()
        assert "A las 14:00 está OCUPADA" in data["respuesta"]
        assert any(f["tipo"] == "disponibilidad" for f in data["fuentes"])

        data = client.post("/api/asistente/consulta", headers=_h(propietario_token),
                           json={"pregunta": f"¿Está libre la zona de parrillas a las 11 de la mañana {cuando}?"}).get_json()
        assert "A las 11:00 está LIBRE" in data["respuesta"]
        assert "hasta las 13:00" in data["respuesta"]

    def test_queda_registro_de_auditoria(self, client, propietario_token):
        client.post("/api/asistente/consulta", headers=_h(propietario_token), json={"pregunta": "horario de silencio"})
        row = fetch_one("SELECT COUNT(*) AS n FROM consultas_asistente")
        assert row["n"] == 1


class TestAsistenteConLLM:
    def test_usa_el_llm_y_devuelve_solo_fuentes_citadas(self, client, propietario_token, monkeypatch):
        capturado = {}

        def falso_completar(system, user):
            capturado["user"] = user
            return "Sí, con correa y fuera del salón [F1].", "groq/llama-3.3-70b-versatile"

        monkeypatch.setattr("services.asistente_service.completar", falso_completar)
        data = client.post("/api/asistente/consulta", headers=_h(propietario_token),
                           json={"pregunta": "¿Puedo llevar a mi perro?"}).get_json()
        assert data["modo"] == "ia"
        assert [f["id"] for f in data["fuentes"]] == ["F1"]
        assert "Mascotas" in capturado["user"]
        # minimización de datos: el DNI y el correo nunca se envían al LLM
        assert "12345678" not in capturado["user"]
        assert "jperez@example.com" not in capturado["user"]


    def test_citas_con_caracteres_invisibles_se_reconocen(self, client, propietario_token, monkeypatch):
        monkeypatch.setattr("services.asistente_service.completar",
                            lambda s, u: ("Abre a las 06:00\u202fa.m. [\u200bF1].", "groq/openai/gpt-oss-120b"))
        data = client.post("/api/asistente/consulta", headers=_h(propietario_token),
                           json={"pregunta": "¿A qué hora abre el gimnasio?"}).get_json()
        assert data["respuesta"] == "Abre a las 06:00 a.m. [F1]."
        assert [f["id"] for f in data["fuentes"]] == ["F1"]


def _area_body(area_id, client, token, **cambios):
    items = client.get("/api/areas-comunes?todas=1", headers=_h(token)).get_json()["items"]
    area = next(a for a in items if a["id"] == area_id)
    body = {k: area[k] for k in ("nombre", "descripcion", "aforo", "tarifa", "hora_apertura", "hora_cierre",
                                 "anticipacion_min_horas", "duracion_max_horas", "activo")}
    body.update(cambios)
    return body


class TestConfiguracionAreas:
    def test_admin_cambia_tarifa_y_la_nueva_reserva_la_usa(self, client, admin_token, propietario_token):
        area = _area("Zona de parrillas")
        resp = client.put(f"/api/areas-comunes/{area['id']}", headers=_h(admin_token),
                          json=_area_body(area["id"], client, admin_token, tarifa=65.5, garantia=0,
                                          duracion_max_horas=3))
        assert resp.status_code == 200, resp.get_json()
        assert resp.get_json()["tarifa"] == 65.5
        fecha = (dt.datetime.now(LIMA).date() + dt.timedelta(days=3)).isoformat()
        res = client.post("/api/reservas", headers=_h(propietario_token), json={
            "area_id": area["id"], "fecha": fecha, "hora_inicio": "13:00", "hora_fin": "16:00", "asistentes": 5})
        assert res.status_code == 201
        assert res.get_json()["cargo"] == 65.5
        # la nueva duración máxima (3 h) también se aplica
        res2 = client.post("/api/reservas", headers=_h(propietario_token), json={
            "area_id": area["id"], "fecha": fecha, "hora_inicio": "17:00", "hora_fin": "21:00", "asistentes": 5})
        assert res2.status_code == 409

    def test_propietario_no_puede_editar(self, client, admin_token, propietario_token):
        area = _area("Zona de parrillas")
        resp = client.put(f"/api/areas-comunes/{area['id']}", headers=_h(propietario_token),
                          json=_area_body(area["id"], client, admin_token, tarifa=1))
        assert resp.status_code == 403

    def test_datos_invalidos(self, client, admin_token):
        area = _area("Zona de parrillas")
        resp = client.put(f"/api/areas-comunes/{area['id']}", headers=_h(admin_token),
                          json=_area_body(area["id"], client, admin_token, hora_cierre="08:00"))
        assert resp.status_code == 400

    def test_area_desactivada_no_se_lista_ni_se_reserva(self, client, admin_token, propietario_token):
        area = _area("Cowork")
        client.put(f"/api/areas-comunes/{area['id']}", headers=_h(admin_token),
                   json=_area_body(area["id"], client, admin_token, activo=False))
        nombres = [a["nombre"] for a in client.get("/api/areas-comunes", headers=_h(propietario_token)).get_json()["items"]]
        assert "Cowork" not in nombres
        fecha = (dt.datetime.now(LIMA).date() + dt.timedelta(days=3)).isoformat()
        resp = client.post("/api/reservas", headers=_h(propietario_token), json={
            "area_id": area["id"], "fecha": fecha, "hora_inicio": "10:00", "hora_fin": "11:00", "asistentes": 2})
        assert resp.status_code == 409

    def test_asistente_informa_la_tarifa_vigente(self, client, admin_token, propietario_token):
        area = _area("Zona de parrillas")
        client.put(f"/api/areas-comunes/{area['id']}", headers=_h(admin_token),
                   json=_area_body(area["id"], client, admin_token, tarifa=72))
        data = client.post("/api/asistente/consulta", headers=_h(propietario_token),
                           json={"pregunta": "¿Cuánto cuesta la parrilla?"}).get_json()
        assert "S/ 72.00" in data["respuesta"]
        assert any(f["tipo"] == "areas" for f in data["fuentes"])



def _reservar(client, token, nombre, inicio="13:00", fin="16:00", asistentes=5, dias=3):
    area = _area(nombre)
    fecha = (dt.datetime.now(LIMA).date() + dt.timedelta(days=dias)).isoformat()
    return client.post("/api/reservas", headers=_h(token), json={
        "area_id": area["id"], "fecha": fecha, "hora_inicio": inicio, "hora_fin": fin, "asistentes": asistentes})


def _pagar_garantia(client, token, reserva_id, token_tarjeta=TOKEN_OK):
    return client.post("/api/pagos", headers=_h(token), json={
        "concepto": "garantia", "reserva_id": reserva_id, "proveedor": "culqi",
        "datos": {"token_id": token_tarjeta}})


class TestGarantia:
    def test_reserva_con_garantia_queda_pendiente_y_bloquea_el_horario(self, client, propietario_token):
        resp = _reservar(client, propietario_token, "Zona de parrillas")
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["estado"] == "pendiente_garantia" and data["garantia_estado"] == "pendiente"
        assert data["garantia"] == 100.0
        assert "pagar_garantia_antes_de" in data
        assert _reservar(client, propietario_token, "Zona de parrillas", "14:00", "15:00").status_code == 409

    def test_pagar_garantia_confirma_y_pasa_tarifa_al_recibo(self, client, propietario_token, recibo_mes):
        res = _reservar(client, propietario_token, "Zona de parrillas").get_json()
        mismo_mes = res["fecha"][:7] == recibo_mes["fecha_emision"][:7]
        resp = _pagar_garantia(client, propietario_token, res["id"])
        assert resp.status_code == 201, resp.get_json()
        assert resp.get_json()["transaccion"]["concepto"] == "garantia"
        assert resp.get_json()["transaccion"]["monto"] == 100.0
        row = fetch_one("SELECT estado, garantia_estado, recibo_id FROM reservas WHERE id = %s", [res["id"]])
        assert row["estado"] == "confirmada" and row["garantia_estado"] == "pagada"
        if mismo_mes:
            rec = fetch_one("SELECT monto_reservas FROM recibos WHERE id = %s", [recibo_mes["id"]])
            assert float(rec["monto_reservas"]) == 50.0

    def test_garantia_rechazada_deja_la_reserva_pendiente(self, client, propietario_token):
        res = _reservar(client, propietario_token, "Zona de parrillas").get_json()
        assert _pagar_garantia(client, propietario_token, res["id"], TOKEN_RECHAZO).status_code == 402
        row = fetch_one("SELECT estado, garantia_estado FROM reservas WHERE id = %s", [res["id"]])
        assert row["estado"] == "pendiente_garantia" and row["garantia_estado"] == "pendiente"

    def test_garantia_no_pagada_a_tiempo_expira_y_libera_horario(self, client, propietario_token):
        res = _reservar(client, propietario_token, "Zona de parrillas").get_json()
        execute("UPDATE reservas SET creado_en = NOW() - INTERVAL '31 minutes' WHERE id = %s", [res["id"]])
        assert _pagar_garantia(client, propietario_token, res["id"]).status_code == 400
        estado = client.get("/api/reservas/mias", headers=_h(propietario_token)).get_json()["items"][0]["estado"]
        assert estado == "expirada"
        assert _reservar(client, propietario_token, "Zona de parrillas").status_code == 201

    def test_admin_devuelve_parcial_con_motivo(self, client, admin_token, propietario_token):
        res = _reservar(client, propietario_token, "Zona de parrillas").get_json()
        pago = _pagar_garantia(client, propietario_token, res["id"]).get_json()["transaccion"]
        url = f"/api/reservas/{res['id']}/garantia/resolucion"
        assert client.post(url, headers=_h(admin_token), json={"retener": 30}).status_code == 400  # sin motivo
        assert client.post(url, headers=_h(propietario_token), json={}).status_code == 403
        resp = client.post(url, headers=_h(admin_token), json={"retener": 30, "motivo": "Limpieza adicional"})
        assert resp.status_code == 200, resp.get_json()
        data = resp.get_json()
        assert data["garantia_estado"] == "devuelta_parcial"
        assert data["devuelto"] == 70.0
        assert data["transaccion"]["concepto"] == "devolucion"
        origen = fetch_one("SELECT transaccion_origen_id FROM transacciones_pago WHERE id = %s",
                           [data["transaccion"]["id"]])
        assert origen["transaccion_origen_id"] == pago["id"]
        # no se puede resolver dos veces
        assert client.post(url, headers=_h(admin_token), json={}).status_code == 400

    def test_admin_retiene_todo(self, client, admin_token, propietario_token):
        res = _reservar(client, propietario_token, "Zona de parrillas").get_json()
        _pagar_garantia(client, propietario_token, res["id"])
        data = client.post(f"/api/reservas/{res['id']}/garantia/resolucion", headers=_h(admin_token),
                           json={"retener": 100, "motivo": "Parrilla dañada"}).get_json()
        assert data["garantia_estado"] == "retenida" and data["transaccion"] is None

    def test_cancelar_devuelve_garantia_automaticamente(self, client, propietario_token):
        res = _reservar(client, propietario_token, "Zona de parrillas").get_json()
        _pagar_garantia(client, propietario_token, res["id"])
        resp = client.delete(f"/api/reservas/{res['id']}", headers=_h(propietario_token))
        assert resp.status_code == 200
        assert resp.get_json()["garantia_devuelta"] == 100.0
        row = fetch_one("SELECT garantia_estado FROM reservas WHERE id = %s", [res["id"]])
        assert row["garantia_estado"] == "devuelta"


class TestUsoCompartido:
    def test_gimnasio_acepta_reservas_cruzadas_hasta_el_aforo(self, client, propietario_token):
        assert _reservar(client, propietario_token, "Gimnasio", "07:00", "08:00", asistentes=5).status_code == 201
        assert _reservar(client, propietario_token, "Gimnasio", "07:30", "08:30", asistentes=3).status_code == 201
        resp = _reservar(client, propietario_token, "Gimnasio", "07:00", "08:00", asistentes=1)
        assert resp.status_code == 409
        assert "cupo" in resp.get_json()["reglas_incumplidas"][0]

    def test_pet_shower_es_exclusivo(self, client, propietario_token):
        assert _reservar(client, propietario_token, "Pet shower", "10:00", "11:00", asistentes=1).status_code == 201
        assert _reservar(client, propietario_token, "Pet shower", "10:30", "11:00", asistentes=1).status_code == 409


INVITADOS = [
    {"nombres": "Lucía", "apellidos": "Ramos Díaz", "tipo_documento": "DNI", "numero_documento": "70112233"},
    {"nombres": "Mark", "apellidos": "Taylor", "tipo_documento": "CE", "numero_documento": "001234567"},
]


class TestInvitados:
    def _reservar_con_invitados(self, client, token, invitados, asistentes=5):
        area = _area("Cowork")
        fecha = (dt.datetime.now(LIMA).date() + dt.timedelta(days=3)).isoformat()
        return client.post("/api/reservas", headers=_h(token), json={
            "area_id": area["id"], "fecha": fecha, "hora_inicio": "10:00", "hora_fin": "11:00",
            "asistentes": asistentes, "invitados": invitados})

    def test_guarda_invitados_y_el_admin_los_ve(self, client, admin_token, propietario_token):
        resp = self._reservar_con_invitados(client, propietario_token, INVITADOS)
        assert resp.status_code == 201, resp.get_json()
        res = resp.get_json()
        assert res["invitados"] == 2
        data = client.get(f"/api/reservas/{res['id']}/invitados", headers=_h(admin_token)).get_json()
        assert {i["numero_documento"] for i in data["items"]} == {"70112233", "001234567"}
        assert data["titular"] == "Juan Perez"

    def test_documento_invalido_rechaza_la_reserva(self, client, propietario_token):
        malo = [dict(INVITADOS[0], numero_documento="123")]
        resp = self._reservar_con_invitados(client, propietario_token, malo)
        assert resp.status_code == 409
        assert "8 dígitos" in resp.get_json()["reglas_incumplidas"][0]
        assert fetch_one("SELECT COUNT(*) AS n FROM reservas")["n"] == 0

    def test_mas_invitados_que_personas(self, client, propietario_token):
        resp = self._reservar_con_invitados(client, propietario_token, INVITADOS, asistentes=2)
        assert resp.status_code == 409

    def test_otro_propietario_no_ve_los_invitados(self, client, admin_token, propietario_token):
        res = self._reservar_con_invitados(client, propietario_token, INVITADOS).get_json()
        client.post("/api/propietarios", headers=_h(admin_token), json={
            "usuario": "otra", "nombre": "Otra", "apellido": "Vecina", "dni": "87654321",
            "nro_departamento": "101", "torre": "B"})
        tok = client.post("/api/login", json={"usuario": "otra", "contrasena": "87654321",
                                              "tipo": "Propietario"}).get_json()["token"]
        assert client.get(f"/api/reservas/{res['id']}/invitados", headers=_h(tok)).status_code == 403


class TestAsistentePrivacidad:
    def test_no_responde_por_otro_vecino(self, client, admin_token, propietario_token, monkeypatch):
        llamado = []
        monkeypatch.setattr("services.asistente_service.completar", lambda s, u: llamado.append(u) or ("x", "groq/x"))
        client.post("/api/propietarios", headers=_h(admin_token), json={
            "usuario": "crojas", "nombre": "Carlos", "apellido": "Rojas Vega", "dni": "41236587",
            "nro_departamento": "502", "torre": "A"})
        for pregunta in ["¿Cuánto debe Carlos Rojas?", "¿El depto 502 está al día?"]:
            data = client.post("/api/asistente/consulta", headers=_h(propietario_token),
                               json={"pregunta": pregunta}).get_json()
            assert data["modo"] == "privacidad"
            assert "29733" in data["respuesta"]
        assert llamado == []   # nunca se llamó al LLM

    def test_su_propio_depto_si_responde(self, client, propietario_token):
        data = client.post("/api/asistente/consulta", headers=_h(propietario_token),
                           json={"pregunta": "¿Cuánto debe el depto 301?"}).get_json()
        assert data["modo"] != "privacidad"


import io as _io  # noqa: E402

from utils.pdf_simple import generar_pdf  # noqa: E402

ACTA = generar_pdf("Acta de Junta Octubre 2026", [[
    "Acuerdo 1: La Junta aprobó pintar la fachada del edificio en diciembre con un presupuesto de S/ 12,500.",
    "Acuerdo 2: Se cambiará la bomba de agua de la cisterna en enero.",
]])


def _subir(client, token, contenido=ACTA, nombre="acta.pdf", publico="true", titulo="Acta de Junta Octubre 2026"):
    return client.post("/api/documentos", headers=_h(token), content_type="multipart/form-data", data={
        "archivo": (_io.BytesIO(contenido), nombre), "titulo": titulo, "categoria": "acta",
        "descripcion": "Sesión ordinaria", "publico": publico})


class TestDocumentos:
    def test_admin_sube_pdf_y_propietario_lo_ve_y_descarga(self, client, admin_token, propietario_token):
        resp = _subir(client, admin_token)
        assert resp.status_code == 201, resp.get_json()
        doc = resp.get_json()
        assert doc["paginas"] == 1 and doc["tiene_texto"] is True
        items = client.get("/api/documentos", headers=_h(propietario_token)).get_json()["items"]
        assert [d["id"] for d in items] == [doc["id"]]
        archivo = client.get(f"/api/documentos/{doc['id']}/archivo", headers=_h(propietario_token))
        assert archivo.status_code == 200 and archivo.data.startswith(b"%PDF-")
        assert archivo.mimetype == "application/pdf"

    def test_rechaza_no_pdf_aunque_tenga_extension(self, client, admin_token):
        resp = _subir(client, admin_token, contenido=b"MZ\x90\x00 ejecutable", nombre="virus.pdf")
        assert resp.status_code == 400
        assert _subir(client, admin_token, nombre="acta.docx").status_code == 400

    def test_rechaza_mas_de_5mb(self, client, admin_token):
        grande = ACTA + b"0" * (5 * 1024 * 1024)
        assert _subir(client, admin_token, contenido=grande).status_code in (400, 413)

    def test_privado_no_lo_ve_el_propietario(self, client, admin_token, propietario_token):
        doc = _subir(client, admin_token, publico="false").get_json()
        assert client.get("/api/documentos", headers=_h(propietario_token)).get_json()["items"] == []
        assert client.get(f"/api/documentos/{doc['id']}/archivo", headers=_h(propietario_token)).status_code == 404
        assert client.get(f"/api/documentos/{doc['id']}/archivo", headers=_h(admin_token)).status_code == 200

    def test_propietario_no_sube_ni_elimina(self, client, admin_token, propietario_token):
        assert _subir(client, propietario_token).status_code == 403
        doc = _subir(client, admin_token).get_json()
        assert client.delete(f"/api/documentos/{doc['id']}", headers=_h(propietario_token)).status_code == 403

    def test_asistente_cita_el_acta_y_olvida_al_ocultarla(self, client, admin_token, propietario_token):
        doc = _subir(client, admin_token).get_json()
        data = client.post("/api/asistente/consulta", headers=_h(propietario_token),
                           json={"pregunta": "¿Qué se acordó sobre la fachada?"}).get_json()
        assert any(f["tipo"] == "documento" and "Acta de Junta" in f["etiqueta"] for f in data["fuentes"])
        assert "12,500" in data["respuesta"]
        client.put(f"/api/documentos/{doc['id']}", headers=_h(admin_token), json={
            "titulo": doc["titulo"], "categoria": "acta", "publico": False})
        data = client.post("/api/asistente/consulta", headers=_h(propietario_token),
                           json={"pregunta": "¿Qué se acordó sobre la fachada?"}).get_json()
        assert not any(f["tipo"] == "documento" for f in data["fuentes"])

    def test_reglamento_se_puede_leer(self, client, propietario_token):
        data = client.get("/api/reglamento", headers=_h(propietario_token)).get_json()
        assert len(data["articulos"]) >= 20
