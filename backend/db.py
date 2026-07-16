import os
import time

import psycopg
from psycopg.rows import dict_row

from utils.logger import get_logger

_db_log = get_logger("db")
_SLOW_QUERY_MS = int(os.getenv("SLOW_QUERY_MS", "200"))


def get_db():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL no está configurado")
    return psycopg.connect(database_url, row_factory=dict_row)


def _log_si_lenta(query, inicio):
    duracion_ms = round((time.perf_counter() - inicio) * 1000, 2)
    if duracion_ms >= _SLOW_QUERY_MS:
        _db_log.warning("Query lenta detectada", extra={
            "event": "slow_query",
            "duration_ms": duracion_ms,
            "query": " ".join(query.split())[:200],
        })


def fetch_one(query, params=None):
    inicio = time.perf_counter()
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or [])
            row = cur.fetchone()
    _log_si_lenta(query, inicio)
    return row


def fetch_all(query, params=None):
    inicio = time.perf_counter()
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or [])
            rows = cur.fetchall()
    _log_si_lenta(query, inicio)
    return rows


def execute_returning(query, params=None):
    inicio = time.perf_counter()
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or [])
            row = cur.fetchone()
        conn.commit()
    _log_si_lenta(query, inicio)
    return row


def execute(query, params=None):
    inicio = time.perf_counter()
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or [])
        conn.commit()
    _log_si_lenta(query, inicio)
