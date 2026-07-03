import os

import pytest
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env.test"))

import app as flask_app_module  # noqa: E402  (import tras cargar env vars de test)
from db import execute  # noqa: E402

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
