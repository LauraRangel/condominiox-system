from db import fetch_all, fetch_one, execute, execute_returning, get_db

MINUTOS_PARA_PAGAR_GARANTIA = 30

_COLUMNAS_AREA = """
    id, nombre, descripcion, aforo, tarifa, garantia, uso_exclusivo, hora_apertura, hora_cierre,
    anticipacion_min_horas, duracion_max_horas, activo
"""


def get_areas(solo_activas=True):
    where = "WHERE activo = TRUE" if solo_activas else ""
    return fetch_all(f"SELECT {_COLUMNAS_AREA} FROM areas_comunes {where} ORDER BY id")


def get_area(area_id):
    return fetch_one(f"SELECT {_COLUMNAS_AREA} FROM areas_comunes WHERE id = %s", [area_id])


def update_area(area_id, nombre, descripcion, aforo, tarifa, garantia, uso_exclusivo,
                hora_apertura, hora_cierre, anticipacion_min_horas, duracion_max_horas, activo):
    return execute_returning(
        f"""
        UPDATE areas_comunes
        SET nombre = %s, descripcion = %s, aforo = %s, tarifa = %s, garantia = %s,
            uso_exclusivo = %s, hora_apertura = %s, hora_cierre = %s,
            anticipacion_min_horas = %s, duracion_max_horas = %s, activo = %s
        WHERE id = %s
        RETURNING {_COLUMNAS_AREA}
        """,
        [nombre, descripcion, aforo, tarifa, garantia, uso_exclusivo, hora_apertura, hora_cierre,
         anticipacion_min_horas, duracion_max_horas, activo, area_id],
    )


def nombre_area_existe(nombre, excluir_id):
    return fetch_one(
        "SELECT id FROM areas_comunes WHERE LOWER(nombre) = LOWER(%s) AND id <> %s",
        [nombre, excluir_id],
    )


def contar_reservas_futuras(area_id):
    row = fetch_one(
        """
        SELECT COUNT(*) AS n FROM reservas
        WHERE area_id = %s AND estado = 'confirmada' AND fecha >= CURRENT_DATE
        """,
        [area_id],
    )
    return int(row["n"]) if row else 0


def expirar_pendientes():
    """Libera los horarios de reservas cuya garantía no se pagó a tiempo."""
    execute(
        """
        UPDATE reservas SET estado = 'expirada', garantia_estado = 'no_pagada'
        WHERE estado = 'pendiente_garantia'
          AND creado_en < NOW() - make_interval(mins => %s)
        """,
        [MINUTOS_PARA_PAGAR_GARANTIA],
    )


def get_reservas_activas_dia(area_id, fecha):
    return fetch_all(
        """
        SELECT id, propietario_id, hora_inicio, hora_fin, asistentes, estado
        FROM reservas
        WHERE area_id = %s AND fecha = %s AND estado IN ('confirmada', 'pendiente_garantia')
        ORDER BY hora_inicio
        """,
        [area_id, fecha],
    )


def crear_reserva_tx(cur, area, propietario_id, fecha, hora_inicio, hora_fin,
                     asistentes, cargo, garantia, recibo_id):
    """Inserta la reserva si hay espacio. Devuelve (fila, None) o (None, motivo)."""
    # Bloquea el área para que dos reservas simultáneas no tomen el mismo espacio
    cur.execute("SELECT id FROM areas_comunes WHERE id = %s FOR UPDATE", [area["id"]])
    cur.execute(
        """
        SELECT COUNT(*) AS n, COALESCE(SUM(asistentes), 0) AS personas
        FROM reservas
        WHERE area_id = %s AND fecha = %s AND estado IN ('confirmada', 'pendiente_garantia')
          AND hora_inicio < %s AND hora_fin > %s
        """,
        [area["id"], fecha, hora_fin, hora_inicio],
    )
    cruce = cur.fetchone()
    if area["uso_exclusivo"] and cruce["n"] > 0:
        return None, "El horario elegido ya está reservado"
    if not area["uso_exclusivo"] and cruce["personas"] + asistentes > area["aforo"]:
        libres = max(area["aforo"] - int(cruce["personas"]), 0)
        return None, f"En ese horario solo quedan {libres} cupo(s) de {area['aforo']}"

    con_garantia = garantia > 0
    cur.execute(
        """
        INSERT INTO reservas (area_id, propietario_id, fecha, hora_inicio, hora_fin, asistentes,
                              cargo, recibo_id, estado, garantia, garantia_estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        [area["id"], propietario_id, fecha, hora_inicio, hora_fin, asistentes, cargo,
         recibo_id if not con_garantia else None,
         "pendiente_garantia" if con_garantia else "confirmada",
         garantia, "pendiente" if con_garantia else "no_aplica"],
    )
    return cur.fetchone(), None


def insertar_invitados_tx(cur, reserva_id, invitados):
    for inv in invitados:
        cur.execute(
            """
            INSERT INTO reserva_invitados (reserva_id, nombres, apellidos, tipo_documento, numero_documento)
            VALUES (%s, %s, %s, %s, %s)
            """,
            [reserva_id, inv["nombres"], inv["apellidos"], inv["tipo_documento"], inv["numero_documento"]],
        )


def get_invitados(reserva_id):
    return fetch_all(
        """
        SELECT nombres, apellidos, tipo_documento, numero_documento
        FROM reserva_invitados WHERE reserva_id = %s ORDER BY apellidos, nombres
        """,
        [reserva_id],
    )


_SELECT_RESERVA = """
    SELECT (SELECT COUNT(*) FROM reserva_invitados i WHERE i.reserva_id = r.id) AS invitados,
           r.id, r.area_id, a.nombre AS area, r.propietario_id, r.fecha,
           r.hora_inicio, r.hora_fin, r.asistentes, r.cargo, r.estado,
           r.recibo_id, r.creado_en, r.garantia, r.garantia_estado, r.garantia_retenida,
           r.garantia_motivo, r.garantia_resuelta_en,
           p.nombre, p.apellido, p.nro_departamento, p.torre
    FROM reservas r
    JOIN areas_comunes a ON a.id = r.area_id
    JOIN propietarios p ON p.id = r.propietario_id
"""


def get_reserva(reserva_id):
    return fetch_one(_SELECT_RESERVA + " WHERE r.id = %s", [reserva_id])


def get_reserva_para_actualizar(cur, reserva_id):
    cur.execute(
        """
        SELECT id, area_id, propietario_id, fecha, hora_inicio, hora_fin, cargo, estado,
               recibo_id, garantia, garantia_estado, creado_en
        FROM reservas WHERE id = %s FOR UPDATE
        """,
        [reserva_id],
    )
    return cur.fetchone()


def confirmar_reserva_tx(cur, reserva_id, recibo_id):
    cur.execute(
        """
        UPDATE reservas SET estado = 'confirmada', garantia_estado = 'pagada', recibo_id = %s
        WHERE id = %s
        """,
        [recibo_id, reserva_id],
    )


def resolver_garantia_tx(cur, reserva_id, estado, retenida, motivo):
    cur.execute(
        """
        UPDATE reservas
        SET garantia_estado = %s, garantia_retenida = %s, garantia_motivo = %s,
            garantia_resuelta_en = NOW()
        WHERE id = %s
        """,
        [estado, retenida, motivo, reserva_id],
    )


def get_reservas_propietario(propietario_id):
    return fetch_all(
        _SELECT_RESERVA + " WHERE r.propietario_id = %s ORDER BY r.fecha DESC, r.hora_inicio DESC",
        [propietario_id],
    )


def get_reservas_admin(desde=None):
    params = []
    where = ""
    if desde:
        where = " WHERE r.fecha >= %s"
        params.append(desde)
    return fetch_all(_SELECT_RESERVA + where + " ORDER BY r.fecha DESC, r.hora_inicio", params)


def cancelar_reserva_tx(cur, reserva_id):
    cur.execute(
        """
        UPDATE reservas
        SET estado = 'cancelada',
            garantia_estado = CASE WHEN garantia_estado = 'pendiente' THEN 'no_pagada'
                                   ELSE garantia_estado END
        WHERE id = %s AND estado IN ('confirmada', 'pendiente_garantia')
        RETURNING id, recibo_id, cargo, estado
        """,
        [reserva_id],
    )
    return cur.fetchone()


def total_reservas_sin_recibo(propietario_id, mes):
    row = fetch_one(
        """
        SELECT COALESCE(SUM(cargo), 0) AS total
        FROM reservas
        WHERE propietario_id = %s AND estado = 'confirmada' AND recibo_id IS NULL
          AND TO_CHAR(fecha, 'YYYY-MM') = %s
        """,
        [propietario_id, mes],
    )
    return row["total"] if row else 0


def vincular_reservas_a_recibo(propietario_id, mes, recibo_id):
    return execute_returning(
        """
        UPDATE reservas SET recibo_id = %s
        WHERE propietario_id = %s AND estado = 'confirmada' AND recibo_id IS NULL
          AND TO_CHAR(fecha, 'YYYY-MM') = %s
        RETURNING id
        """,
        [recibo_id, propietario_id, mes],
    )


def proximas_reservas_propietario(propietario_id, limite=5):
    return fetch_all(
        _SELECT_RESERVA
        + " WHERE r.propietario_id = %s AND r.estado IN ('confirmada', 'pendiente_garantia')"
        + " AND r.fecha >= CURRENT_DATE ORDER BY r.fecha, r.hora_inicio LIMIT %s",
        [propietario_id, limite],
    )


def total_garantias_en_custodia():
    row = fetch_one(
        "SELECT COALESCE(SUM(garantia), 0) AS total, COUNT(*) AS n FROM reservas WHERE garantia_estado = 'pagada'"
    )
    return row


def transaccion():
    """Devuelve una conexión para operaciones que deben ser atómicas."""
    return get_db()
