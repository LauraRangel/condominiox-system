import os
import psycopg
from psycopg.rows import dict_row


def get_db():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL no está configurado")
    return psycopg.connect(database_url, row_factory=dict_row)


def fetch_one(query, params=None):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or [])
            return cur.fetchone()


def fetch_all(query, params=None):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or [])
            return cur.fetchall()


def execute_returning(query, params=None):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or [])
            row = cur.fetchone()
        conn.commit()
    return row


def execute(query, params=None):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or [])
        conn.commit()
