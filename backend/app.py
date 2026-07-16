import time
import uuid

from dotenv import load_dotenv
from flask import Flask, g, request
from flask_cors import CORS

load_dotenv()

from db import execute
from routes import (
    health_routes,
    auth_routes,
    configuracion_routes,
    propietario_routes,
    gasto_routes,
    recibo_routes,
    anuncio_routes,
    reporte_routes,
)
from utils.logger import get_logger

app = Flask(__name__)
_access_log = get_logger("access")

# Registrar blueprints (Controllers en MVC)
app.register_blueprint(health_routes.bp)
app.register_blueprint(auth_routes.bp)
app.register_blueprint(configuracion_routes.bp)
app.register_blueprint(propietario_routes.bp)
app.register_blueprint(gasto_routes.bp)
app.register_blueprint(recibo_routes.bp)
app.register_blueprint(anuncio_routes.bp)
app.register_blueprint(reporte_routes.bp)

CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET","POST","PUT","DELETE","OPTIONS","PATCH"], "allow_headers": ["Content-Type","Authorization"]}})


@app.before_request
def _iniciar_request():
    g.request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
    g.inicio_request = time.perf_counter()


@app.after_request
def _registrar_acceso(response):
    duracion_ms = round((time.perf_counter() - g.get("inicio_request", time.perf_counter())) * 1000, 2)
    response.headers["X-Request-Id"] = g.get("request_id", "-")
    nivel = "warning" if response.status_code >= 400 else "info"
    getattr(_access_log, nivel)("HTTP request", extra={
        "event": "http_request",
        "request_id": g.get("request_id", "-"),
        "method": request.method,
        "path": request.path,
        "status": response.status_code,
        "duration_ms": duracion_ms,
    })
    return response


def _ensure_extra_tables():
    execute(
        """
        CREATE TABLE IF NOT EXISTS pagos_gastos (
            id SERIAL PRIMARY KEY,
            gasto_id INTEGER NOT NULL REFERENCES gastos(id) ON DELETE CASCADE,
            monto NUMERIC(10,2) NOT NULL CHECK (monto > 0),
            fecha_pago DATE NOT NULL DEFAULT CURRENT_DATE
        )
        """
    )
    execute(
        """
        CREATE TABLE IF NOT EXISTS anuncios (
            id SERIAL PRIMARY KEY,
            titulo VARCHAR(200) NOT NULL,
            contenido TEXT NOT NULL,
            tipo VARCHAR(30) NOT NULL CHECK (tipo IN ('mantenimiento','pago','informativo')),
            fecha_publicacion DATE NOT NULL DEFAULT CURRENT_DATE,
            fecha_caducidad DATE,
            activo BOOLEAN DEFAULT TRUE
        )
        """
    )
    execute(
        """
        CREATE TABLE IF NOT EXISTS lecturas_anuncios (
            id SERIAL PRIMARY KEY,
            anuncio_id INTEGER NOT NULL REFERENCES anuncios(id) ON DELETE CASCADE,
            propietario_id INTEGER NOT NULL REFERENCES propietarios(id) ON DELETE CASCADE,
            fecha_lectura TIMESTAMP DEFAULT NOW(),
            UNIQUE(anuncio_id, propietario_id)
        )
        """
    )


def _migrate_anuncios():
    execute(
        """
        ALTER TABLE anuncios
        ADD COLUMN IF NOT EXISTS fecha_caducidad DATE
        """
    )


_ensure_extra_tables()
_migrate_anuncios()

if __name__ == "__main__":
    app.run(debug=True)
