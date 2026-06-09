from db import fetch_all, fetch_one, execute_returning


def get_recibos_admin(estado: str = "", mes_filter: str = ""):
    filtros = []
    params = []
    if estado == "pendientes":
        filtros.append("r.pagado = FALSE")
    elif estado == "pagados":
        filtros.append("r.pagado = TRUE")
    if mes_filter:
        filtros.append("TO_CHAR(r.fecha_emision, 'YYYY-MM') = %s")
        params.append(mes_filter)
    where = f"WHERE {' AND '.join(filtros)}" if filtros else ""
    return fetch_all(
        f"""
        SELECT r.id, r.propietario_id, r.monto_administracion, r.monto_agua,
               r.monto_luz, r.monto_mantenimiento, r.monto_pagado,
               r.fecha_emision, r.fecha_pago, r.pagado,
               p.nombre, p.apellido, p.nro_departamento, p.torre
        FROM recibos r
        JOIN propietarios p ON p.id = r.propietario_id
        {where}
        ORDER BY r.fecha_emision DESC, r.id DESC
        """,
        params,
    )


def get_recibos_propietario(propietario_id, estado: str = ""):
    filtros = ["r.propietario_id = %s"]
    params = [propietario_id]
    if estado == "pendientes":
        filtros.append("r.pagado = FALSE")
    elif estado == "pagados":
        filtros.append("r.pagado = TRUE")
    return fetch_all(
        f"""
        SELECT r.id, r.propietario_id, r.monto_administracion, r.monto_agua,
               r.monto_luz, r.monto_mantenimiento, r.monto_pagado,
               r.fecha_emision, r.fecha_pago, r.pagado
        FROM recibos r
        WHERE {' AND '.join(filtros)}
        ORDER BY r.fecha_emision DESC, r.id DESC
        """,
        params,
    )


def get_recibos_para_estructuras(mes_filter: str = "", estado: str = ""):
    filtros = []
    params = []
    if estado == "pendientes":
        filtros.append("r.pagado = FALSE")
    elif estado == "pagados":
        filtros.append("r.pagado = TRUE")
    if mes_filter:
        filtros.append("TO_CHAR(r.fecha_emision, 'YYYY-MM') = %s")
        params.append(mes_filter)
    where = f"WHERE {' AND '.join(filtros)}" if filtros else ""
    return fetch_all(
        f"""
        SELECT r.id, r.propietario_id, r.monto_administracion, r.monto_agua,
               r.monto_luz, r.monto_mantenimiento, r.monto_pagado,
               r.fecha_emision, r.fecha_pago, r.pagado,
               p.nombre, p.apellido, p.nro_departamento, p.torre
        FROM recibos r
        JOIN propietarios p ON p.id = r.propietario_id
        {where}
        ORDER BY r.fecha_emision DESC, r.id DESC
        """,
        params,
    )


def get_recibo_por_id(recibo_id):
    return fetch_one(
        """
        SELECT id, propietario_id, monto_administracion, monto_agua,
               monto_luz, monto_mantenimiento, monto_pagado,
               fecha_emision, fecha_pago, pagado
        FROM recibos WHERE id = %s
        """,
        [recibo_id],
    )


def recibo_existe_en_mes(propietario_id, mes: str):
    return fetch_one(
        """
        SELECT id FROM recibos
        WHERE propietario_id = %s AND TO_CHAR(fecha_emision, 'YYYY-MM') = %s
        """,
        [propietario_id, mes],
    )


def create_recibo(propietario_id, monto_administracion, monto_agua,
                  monto_luz, monto_mantenimiento, fecha_emision):
    return execute_returning(
        """
        INSERT INTO recibos (
            propietario_id, monto_administracion, monto_agua,
            monto_luz, monto_mantenimiento, monto_pagado, fecha_emision, fecha_pago, pagado
        )
        VALUES (%s, %s, %s, %s, %s, 0, %s, NULL, FALSE)
        RETURNING id, propietario_id, monto_administracion, monto_agua,
                  monto_luz, monto_mantenimiento, monto_pagado, fecha_emision, fecha_pago, pagado
        """,
        [propietario_id, monto_administracion, monto_agua,
         monto_luz, monto_mantenimiento, fecha_emision],
    )


def recalcular_recibos_mes(mes: str, monto_admin, monto_agua, monto_luz, monto_mant):
    return fetch_all(
        """
        UPDATE recibos
        SET monto_administracion = %s,
            monto_agua = %s,
            monto_luz = %s,
            monto_mantenimiento = %s,
            pagado = CASE
                WHEN monto_pagado >= (%s + %s + %s + %s) THEN TRUE
                ELSE FALSE
            END,
            fecha_pago = CASE
                WHEN monto_pagado >= (%s + %s + %s + %s)
                    THEN COALESCE(fecha_pago, CURRENT_DATE)
                ELSE NULL
            END
        WHERE TO_CHAR(fecha_emision, 'YYYY-MM') = %s
        RETURNING id, propietario_id, monto_administracion, monto_agua, monto_luz,
                  monto_mantenimiento, monto_pagado, fecha_emision, fecha_pago, pagado
        """,
        [monto_admin, monto_agua, monto_luz, monto_mant,
         monto_admin, monto_agua, monto_luz, monto_mant,
         monto_admin, monto_agua, monto_luz, monto_mant,
         mes],
    )


def pagar_recibo(recibo_id, monto):
    return execute_returning(
        """
        UPDATE recibos
        SET monto_pagado = ROUND(monto_pagado + %s, 2),
            pagado = CASE
                WHEN ROUND(monto_pagado + %s, 2) >=
                     ROUND((monto_administracion + monto_agua + monto_luz + monto_mantenimiento), 2)
                    THEN TRUE
                ELSE FALSE
            END,
            fecha_pago = CASE
                WHEN ROUND(monto_pagado + %s, 2) >=
                     ROUND((monto_administracion + monto_agua + monto_luz + monto_mantenimiento), 2)
                    THEN CURRENT_DATE
                ELSE NULL
            END
        WHERE id = %s
        RETURNING id, monto_pagado, pagado, fecha_emision, fecha_pago,
                  monto_administracion, monto_agua, monto_luz, monto_mantenimiento
        """,
        [monto, monto, monto, recibo_id],
    )


def delete_recibo(recibo_id):
    return execute_returning(
        "DELETE FROM recibos WHERE id = %s RETURNING id",
        [recibo_id],
    )


def get_recibos_estado_cuenta(propietario_id, desde: str = "", hasta: str = ""):
    filtros = ["r.propietario_id = %s"]
    params = [propietario_id]
    if desde:
        filtros.append("TO_CHAR(r.fecha_emision, 'YYYY-MM') >= %s")
        params.append(desde)
    if hasta:
        filtros.append("TO_CHAR(r.fecha_emision, 'YYYY-MM') <= %s")
        params.append(hasta)
    return fetch_all(
        f"""
        SELECT r.id, r.propietario_id, r.monto_administracion, r.monto_agua, r.monto_luz,
               r.monto_mantenimiento, r.monto_pagado, r.fecha_emision, r.fecha_pago, r.pagado,
               p.nombre, p.apellido, p.nro_departamento, p.torre
        FROM recibos r
        JOIN propietarios p ON p.id = r.propietario_id
        WHERE {' AND '.join(filtros)}
        ORDER BY r.fecha_emision DESC
        """,
        params,
    )
