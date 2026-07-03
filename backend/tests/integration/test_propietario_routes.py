from security import verify_password
from db import fetch_one


class TestCrearPropietario:
    def test_crea_propietario_y_password_inicial_es_el_dni(self, client, propietario_creado):
        assert propietario_creado["dni"] == "12345678"
        row = fetch_one(
            "SELECT password_hash FROM usuarios WHERE usuario = %s",
            [propietario_creado["usuario"]],
        )
        assert verify_password(row["password_hash"], "12345678") is True

    def test_sin_token(self, client):
        resp = client.post("/api/propietarios", json={})
        assert resp.status_code == 401

    def test_con_token_de_propietario_403(self, client, propietario_token):
        resp = client.post(
            "/api/propietarios",
            json={"usuario": "otro", "nombre": "X", "apellido": "Y",
                  "dni": "87654321", "nro_departamento": "101", "torre": "B"},
            headers={"Authorization": f"Bearer {propietario_token}"},
        )
        assert resp.status_code == 403

    def test_dni_invalido(self, client, admin_token):
        resp = client.post(
            "/api/propietarios",
            json={"usuario": "malo", "nombre": "X", "apellido": "Y",
                  "dni": "123", "nro_departamento": "101", "torre": "B"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 400


class TestListarPropietarios:
    def test_lista_incluye_el_creado(self, client, admin_token, propietario_creado):
        resp = client.get(
            "/api/propietarios",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        ids = [p["id"] for p in resp.get_json()["items"]]
        assert propietario_creado["id"] in ids


class TestActualizarPropietario:
    def test_actualiza_campos(self, client, admin_token, propietario_creado):
        body = {
            "usuario": propietario_creado["usuario"],
            "nombre": "Juan Carlos",
            "apellido": propietario_creado["apellido"],
            "dni": propietario_creado["dni"],
            "nro_departamento": propietario_creado["nro_departamento"],
            "torre": propietario_creado["torre"],
        }
        resp = client.put(
            f"/api/propietarios/{propietario_creado['id']}",
            json=body,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        assert resp.get_json()["nombre"] == "Juan Carlos"

    def test_id_inexistente_404(self, client, admin_token):
        body = {
            "usuario": "x", "nombre": "x", "apellido": "x",
            "dni": "11111111", "nro_departamento": "1", "torre": "A",
        }
        resp = client.put(
            "/api/propietarios/999999",
            json=body,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 404


class TestEliminarPropietario:
    def test_elimina_y_desaparece_de_la_lista(self, client, admin_token, propietario_creado):
        resp = client.delete(
            f"/api/propietarios/{propietario_creado['id']}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200

        listado = client.get(
            "/api/propietarios",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        ids = [p["id"] for p in listado.get_json()["items"]]
        assert propietario_creado["id"] not in ids

    def test_id_inexistente_404(self, client, admin_token):
        resp = client.delete(
            "/api/propietarios/999999",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 404
