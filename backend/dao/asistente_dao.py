import json

from db import fetch_all, fetch_one, execute_returning


def get_contexto_propietario(propietario_id):
    return fetch_one(
        "SELECT nombre, nro_departamento, torre FROM propietarios WHERE id = %s",
        [propietario_id],
    )


def get_recibos_pendientes(propietario_id):
    return fetch_all(
        """
        SELECT id, fecha_emision, monto_administracion, monto_agua, monto_luz,
               monto_mantenimiento, monto_reservas, monto_pagado
        FROM recibos
        WHERE propietario_id = %s AND pagado = FALSE
        ORDER BY fecha_emision
        """,
        [propietario_id],
    )


def get_ultimos_pagos(propietario_id, limite=3):
    return fetch_all(
        """
        SELECT proveedor, monto, estado, codigo_operacion, creado_en
        FROM transacciones_pago
        WHERE propietario_id = %s
        ORDER BY creado_en DESC LIMIT %s
        """,
        [propietario_id, limite],
    )


def get_gastos_mes_por_tipo(mes):
    return fetch_all(
        """
        SELECT tipo, SUM(monto) AS total, COUNT(*) AS cantidad
        FROM gastos
        WHERE TO_CHAR(fecha_registro, 'YYYY-MM') = %s
        GROUP BY tipo ORDER BY tipo
        """,
        [mes],
    )


def get_areas_activas():
    return fetch_all(
        """
        SELECT id, nombre, aforo, tarifa, garantia, uso_exclusivo, hora_apertura, hora_cierre,
               anticipacion_min_horas, duracion_max_horas
        FROM areas_comunes WHERE activo = TRUE ORDER BY id
        """
    )


def get_otros_propietarios(propietario_id):
    """Solo para detectar si la pregunta menciona a otro vecino; estos datos nunca van al LLM."""
    return fetch_all(
        "SELECT nombre, apellido, nro_departamento FROM propietarios WHERE id <> %s",
        [propietario_id],
    )


def contar_propietarios():
    row = fetch_one("SELECT COUNT(*) AS n FROM propietarios")
    return int(row["n"]) if row else 0


def registrar_consulta(propietario_id, pregunta, respuesta, fuentes, modo, proveedor, latencia_ms):
    return execute_returning(
        """
        INSERT INTO consultas_asistente (propietario_id, pregunta, respuesta, fuentes,
                                         modo, proveedor, latencia_ms)
        VALUES (%s, %s, %s, %s::jsonb, %s, %s, %s)
        RETURNING id
        """,
        [propietario_id, pregunta, respuesta, json.dumps(fuentes), modo, proveedor, latencia_ms],
    )

