import time

from flask import Blueprint, jsonify

from db import fetch_one
from utils.logger import get_logger

bp = Blueprint("health", __name__)
_log = get_logger("health")


@bp.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@bp.get("/api/health/db")
def health_db():
    inicio = time.perf_counter()
    try:
        fetch_one("SELECT 1")
        duracion_ms = round((time.perf_counter() - inicio) * 1000, 2)
        return jsonify({"status": "ok", "db": "up", "latency_ms": duracion_ms})
    except Exception as exc:
        duracion_ms = round((time.perf_counter() - inicio) * 1000, 2)
        _log.error("Health check de base de datos falló", extra={
            "event": "health_db_down",
            "error": str(exc),
            "latency_ms": duracion_ms,
        })
        return jsonify({"status": "error", "db": "down"}), 503
