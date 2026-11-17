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
    reserva_routes,
    pago_routes,
    asistente_routes,
    documento_routes,
)
from migrations import run_migrations
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
app.register_blueprint(reserva_routes.bp)
app.register_blueprint(pago_routes.bp)
app.register_blueprint(asistente_routes.bp)
app.register_blueprint(documento_routes.bp)
app.config["MAX_CONTENT_LENGTH"] = 6 * 1024 * 1024  # PDFs de hasta 5 MB + datos del formulario

import os  # noqa: E402

# Solo el frontend propio puede llamar a la API desde el navegador
_ORIGENES = [o.strip() for o in os.getenv(
    "CORS_ORIGINS",
    "https://laurarangel.github.io,http://localhost:8080,http://127.0.0.1:8080,http://localhost:5500,http://127.0.0.1:5500",
).split(",") if o.strip()]
CORS(app, resources={r"/api/*": {"origins": _ORIGENES, "methods": ["GET","POST","PUT","DELETE","OPTIONS","PATCH"], "allow_headers": ["Content-Type","Authorization","Idempotency-Key"]}})


@app.before_request
def _iniciar_request():
    g.request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
    g.inicio_request = time.perf_counter()


@app.after_request
def _registrar_acceso(response):
    duracion_ms = round((time.perf_counter() - g.get("inicio_request", time.perf_counter())) * 1000, 2)
    response.headers["X-Request-Id"] = g.get("request_id", "-")
    # Cabeceras de seguridad: la API solo devuelve JSON y PDFs, nunca páginas
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if request.path.startswith("/api/") and "Cache-Control" not in response.headers:
        response.headers["Cache-Control"] = "no-store"
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


@app.errorhandler(413)
def _archivo_grande(_e):
    return {"error": "El archivo supera el tamaño máximo permitido"}, 413


@app.errorhandler(404)
def _no_encontrado(_e):
    return {"error": "Recurso no encontrado"}, 404


@app.errorhandler(Exception)
def _error_interno(e):
    from werkzeug.exceptions import HTTPException
    if isinstance(e, HTTPException):
        return {"error": e.description}, e.code
    if isinstance(e, (TypeError, AttributeError, ValueError)) and request.get_data(cache=True):
        # Casi siempre es un JSON con tipos inesperados (lista donde va texto, etc.)
        _access_log.warning("Datos con formato inválido", extra={"request_id": g.get("request_id", "-"), "path": request.path, "detalle": repr(e)[:200]})
        return {"error": "Datos con formato inválido"}, 400
    # Se registra el detalle en el log, pero al cliente no se le muestra ningún dato interno
    _access_log.exception("Error no controlado", extra={"request_id": g.get("request_id", "-"), "path": request.path})
    return {"error": "Ocurrió un error inesperado", "request_id": g.get("request_id", "-")}, 500


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
run_migrations()

if __name__ == "__main__":
    # Solo para desarrollo local; en Render arranca Gunicorn
    app.run(debug=os.getenv("FLASK_DEBUG") == "1")
