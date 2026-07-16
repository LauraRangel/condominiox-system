import datetime as dt
import os

import jwt
import pytest
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env.test"))

import app as flask_app_module  # noqa: E402  (import tras cargar env vars de test)
import config  # noqa: E402
from db import execute  # noqa: E402
from security import hash_password  # noqa: E402

TABLAS_A_LIMPIAR = [
    "lecturas_anuncios",
    "anuncios",
    "recibos",
    "pagos_gastos",
    "gastos",
    "propietarios",
    "usuarios",
]


@pytest.fixture
def client():
    flask_app_module.app.config["TESTING"] = True
    return flask_app_module.app.test_client()


@pytest.fixture(autouse=True)
def limpiar_tablas():
    yield
    for tabla in TABLAS_A_LIMPIAR:
        execute(f"TRUNCATE TABLE {tabla} RESTART IDENTITY CASCADE")


def _crear_usuario_admin(usuario="admin_test", password="clave-admin-123"):
    execute(
        "INSERT INTO usuarios (usuario, password_hash, tipo) VALUES (%s, %s, 'Administrador')",
        [usuario, hash_password(password)],
    )
    return usuario, password


@pytest.fixture
def admin_token(client):
    usuario, password = _crear_usuario_admin()
    resp = client.post(
        "/api/login",
        json={"usuario": usuario, "contrasena": password, "tipo": "Administrador"},
    )
    assert resp.status_code == 200, resp.get_json()
    return resp.get_json()["token"]


@pytest.fixture
def propietario_creado(client, admin_token):
    body = {
        "usuario": "jperez",
        "nombre": "Juan",
        "apellido": "Perez",
        "dni": "12345678",
        "correo": "jperez@example.com",
        "telefono": "999888777",
        "nro_departamento": "301",
        "torre": "A",
    }
    resp = client.post(
        "/api/propietarios",
        json=body,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 201, resp.get_json()
    return resp.get_json()


@pytest.fixture
def propietario_token(client, propietario_creado):
    resp = client.post(
        "/api/login",
        json={
            "usuario": propietario_creado["usuario"],
            "contrasena": propietario_creado["dni"],
            "tipo": "Propietario",
        },
    )
    assert resp.status_code == 200, resp.get_json()
    return resp.get_json()["token"]


def token_expirado(usuario_id=999999, tipo="Administrador"):
    now = dt.datetime.now(dt.timezone.utc)
    payload = {
        "sub": str(usuario_id),
        "usuario": "expirado",
        "tipo": tipo,
        "iss": config.jwt_issuer(),
        "iat": int((now - dt.timedelta(hours=2)).timestamp()),
        "exp": int((now - dt.timedelta(hours=1)).timestamp()),
    }
    return jwt.encode(payload, config.jwt_secret(), algorithm="HS256")


def token_firma_invalida(usuario_id=999999, tipo="Administrador"):
    now = dt.datetime.now(dt.timezone.utc)
    payload = {
        "sub": str(usuario_id),
        "usuario": "impostor",
        "tipo": tipo,
        "iss": config.jwt_issuer(),
        "iat": int(now.timestamp()),
        "exp": int((now + dt.timedelta(hours=1)).timestamp()),
    }
    return jwt.encode(payload, "secret-incorrecto", algorithm="HS256")
