import os
import psycopg2
from psycopg2.extras import RealDictCursor


def get_db():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL no está configurado")
    return psycopg2.connect(database_url, cursor_factory=RealDictCursor)


def fetch_one(query, params=None):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or [])
            return cur.fetchone()


def execute(query, params=None):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or [])
        conn.commit()
