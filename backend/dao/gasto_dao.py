from db import fetch_all, fetch_one, execute_returning, get_db


def get_all_gastos():
    return fetch_all(
        """
        SELECT g.id, g.proveedor, g.concepto, g.monto, g.tipo, g.fecha_registro,
               COALESCE(SUM(pg.monto), 0) AS monto_pagado
        FROM gastos g
        LEFT JOIN pagos_gastos pg ON pg.gasto_id = g.id
        GROUP BY g.id, g.proveedor, g.concepto, g.monto, g.tipo, g.fecha_registro
        ORDER BY g.fecha_registro DESC, g.id DESC
        """
    )


def get_gasto_con_saldo(gasto_id):
    return fetch_one(
        """
        SELECT g.id, g.monto, COALESCE(SUM(pg.monto), 0) AS monto_pagado
        FROM gastos g
        LEFT JOIN pagos_gastos pg ON pg.gasto_id = g.id
        WHERE g.id = %s
        GROUP BY g.id, g.monto
        """,
        [gasto_id],
    )


def create_gasto(proveedor, concepto, monto, tipo, fecha_registro):
    return execute_returning(
        """
        INSERT INTO gastos (proveedor, concepto, monto, tipo, fecha_registro)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, proveedor, concepto, monto, tipo, fecha_registro
        """,
        [proveedor, concepto, monto, tipo, fecha_registro],
    )


def delete_gasto(gasto_id):
    return execute_returning(
        "DELETE FROM gastos WHERE id = %s RETURNING id",
        [gasto_id],
    )


def create_pago_gasto(gasto_id, monto):
    return execute_returning(
        """
        INSERT INTO pagos_gastos (gasto_id, monto, fecha_pago)
        VALUES (%s, %s, CURRENT_DATE)
        RETURNING id, gasto_id, monto, fecha_pago
        """,
        [gasto_id, monto],
    )


def get_total_tipo_mes(tipo: str, mes: str):
    return fetch_one(
        """
        SELECT COALESCE(SUM(monto), 0) AS total
        FROM gastos
        WHERE tipo = %s AND TO_CHAR(fecha_registro, 'YYYY-MM') = %s
        """,
        [tipo, mes],
    )


def get_gastos_pendientes_del_mes(mes: str, conn, cur):
    cur.execute(
        """
        SELECT g.id, g.monto, g.fecha_registro, COALESCE(SUM(pg.monto), 0) AS monto_pagado
        FROM gastos g
        LEFT JOIN pagos_gastos pg ON pg.gasto_id = g.id
        WHERE TO_CHAR(g.fecha_registro, 'YYYY-MM') = %s
        GROUP BY g.id, g.monto, g.fecha_registro
        HAVING (g.monto - COALESCE(SUM(pg.monto), 0)) > 0
        ORDER BY g.fecha_registro ASC, g.id ASC
        """,
        [mes],
    )
    return cur.fetchall()


def insert_pago_gasto_tx(cur, gasto_id, monto):
    cur.execute(
        """
        INSERT INTO pagos_gastos (gasto_id, monto, fecha_pago)
        VALUES (%s, %s, CURRENT_DATE)
        """,
        [gasto_id, monto],
    )
