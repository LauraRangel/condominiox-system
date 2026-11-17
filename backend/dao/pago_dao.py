import json

from db import fetch_all, fetch_one

_COLUMNAS = """
    t.id, t.recibo_id, t.reserva_id, t.propietario_id, t.concepto, t.transaccion_origen_id,
    t.proveedor, t.monto, t.moneda, t.estado, t.codigo_operacion, t.medio_detalle, t.mensaje,
    t.modo, t.creado_en
"""


def get_por_idempotency_key(key):
    return fetch_one(
        f"SELECT {_COLUMNAS} FROM transacciones_pago t WHERE t.idempotency_key = %s",
        [key],
    )


def registrar_transaccion_tx(cur, *, propietario_id, concepto, proveedor, monto, estado,
                             codigo_operacion, medio_detalle, mensaje, respuesta_pasarela, modo,
                             recibo_id=None, reserva_id=None, idempotency_key=None,
                             transaccion_origen_id=None):
    cur.execute(
        f"""
        INSERT INTO transacciones_pago (
            recibo_id, reserva_id, propietario_id, concepto, transaccion_origen_id, proveedor,
            monto, estado, codigo_operacion, idempotency_key, medio_detalle, mensaje,
            respuesta_pasarela, modo
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s)
        RETURNING {_COLUMNAS.replace('t.', '')}
        """,
        [recibo_id, reserva_id, propietario_id, concepto, transaccion_origen_id, proveedor,
         monto, estado, codigo_operacion, idempotency_key, medio_detalle, mensaje,
         json.dumps(respuesta_pasarela), modo],
    )
    return cur.fetchone()


def get_pago_garantia_tx(cur, reserva_id):
    """Cobro aprobado de la garantía de una reserva (para devolverla por el mismo medio)."""
    cur.execute(
        f"""
        SELECT {_COLUMNAS} FROM transacciones_pago t
        WHERE t.reserva_id = %s AND t.concepto = 'garantia' AND t.estado = 'aprobado'
        ORDER BY t.id DESC LIMIT 1
        """,
        [reserva_id],
    )
    return cur.fetchone()


def get_transacciones_propietario(propietario_id):
    return fetch_all(
        f"""
        SELECT {_COLUMNAS}, r.fecha_emision, a.nombre AS area
        FROM transacciones_pago t
        LEFT JOIN recibos r ON r.id = t.recibo_id
        LEFT JOIN reservas rs ON rs.id = t.reserva_id
        LEFT JOIN areas_comunes a ON a.id = rs.area_id
        WHERE t.propietario_id = %s
        ORDER BY t.creado_en DESC, t.id DESC
        """,
        [propietario_id],
    )


def get_transacciones_admin(estado=""):
    params = []
    where = ""
    if estado in ("aprobado", "rechazado"):
        where = "WHERE t.estado = %s"
        params.append(estado)
    return fetch_all(
        f"""
        SELECT {_COLUMNAS}, r.fecha_emision, a.nombre AS area,
               p.nombre, p.apellido, p.nro_departamento, p.torre
        FROM transacciones_pago t
        LEFT JOIN recibos r ON r.id = t.recibo_id
        LEFT JOIN reservas rs ON rs.id = t.reserva_id
        LEFT JOIN areas_comunes a ON a.id = rs.area_id
        LEFT JOIN propietarios p ON p.id = t.propietario_id
        {where}
        ORDER BY t.creado_en DESC, t.id DESC
        """,
        params,
    )
