"""Reserva de áreas comunes (componente innovador 1).

Reglas que valida el sistema antes de confirmar una reserva:
  1. El área existe y está activa.
  2. La fecha y el horario están dentro del horario de atención del área.
  3. La duración no supera el máximo del área.
  4. Se respeta la anticipación mínima (en hora de Lima).
  5. Los asistentes no superan el aforo.
  6. El propietario no tiene recibos vencidos (más de DIAS_DEUDA_VENCIDA días sin pagar).
  7. No se cruza con otra reserva confirmada del mismo área (se verifica dentro de la transacción).
Si todo se cumple, el cargo del área se suma al recibo del mes de la reserva.
"""

import datetime as dt
import os
import re

from dao import reserva_dao, recibo_dao
from utils.money import round_money, money_float
from utils.logger import get_logger

log = get_logger(__name__)

LIMA_TZ = dt.timezone(dt.timedelta(hours=-5), "America/Lima")  # Perú no usa horario de verano


def dias_deuda_vencida() -> int:
    try:
        return int(os.getenv("DIAS_DEUDA_VENCIDA", "30"))
    except ValueError:
        return 30


def ahora_lima() -> dt.datetime:
    return dt.datetime.now(LIMA_TZ).replace(tzinfo=None)


def _parse_fecha(valor):
    try:
        return dt.date.fromisoformat(str(valor))
    except (TypeError, ValueError):
        return None


def _parse_hora(valor):
    try:
        return dt.time.fromisoformat(str(valor)[:5])
    except (TypeError, ValueError):
        return None


def _fmt_hora(t) -> str:
    return t.strftime("%H:%M") if hasattr(t, "strftime") else str(t)[:5]


def validar_reglas(area: dict, fecha: dt.date, hora_inicio: dt.time, hora_fin: dt.time,
                   asistentes: int, ahora: dt.datetime, recibos_vencidos: int = 0) -> list:
    """Función pura: devuelve la lista de reglas incumplidas (vacía si todo está bien)."""
    errores = []
    if not area or not area.get("activo", True):
        return ["El área no está disponible"]
    if hora_fin <= hora_inicio:
        errores.append("La hora de fin debe ser posterior a la hora de inicio")
    if hora_inicio < area["hora_apertura"] or hora_fin > area["hora_cierre"]:
        errores.append(
            f"El horario de {area['nombre']} es de {_fmt_hora(area['hora_apertura'])} "
            f"a {_fmt_hora(area['hora_cierre'])}"
        )
    inicio = dt.datetime.combine(fecha, hora_inicio)
    fin = dt.datetime.combine(fecha, hora_fin)
    duracion_h = (fin - inicio).total_seconds() / 3600
    if duracion_h > area["duracion_max_horas"]:
        errores.append(f"La reserva no puede durar más de {area['duracion_max_horas']} horas")
    if inicio < ahora:
        errores.append("No se puede reservar en una fecha u hora pasada")
    elif (inicio - ahora).total_seconds() / 3600 < area["anticipacion_min_horas"]:
        errores.append(
            f"{area['nombre']} se reserva con al menos {area['anticipacion_min_horas']} horas de anticipación"
        )
    if asistentes > area["aforo"]:
        errores.append(f"El aforo máximo de {area['nombre']} es de {area['aforo']} personas")
    if recibos_vencidos > 0:
        errores.append(
            f"Tiene {recibos_vencidos} recibo(s) con más de {dias_deuda_vencida()} días sin pagar; "
            "regularice su deuda para reservar"
        )
    return errores


_NOMBRE_RE = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' .-]{2,60}$")


def validar_invitados(invitados, asistentes: int) -> tuple[list, list]:
    """Función pura: normaliza la lista de invitados y devuelve (invitados, errores).
    El titular cuenta como un asistente, así que los invitados son como máximo asistentes - 1."""
    if invitados in (None, ""):
        return [], []
    if not isinstance(invitados, list):
        return [], ["La lista de invitados no es válida"]
    if len(invitados) > max(asistentes - 1, 0):
        return [], [f"Indicó {asistentes} persona(s) en total; puede registrar hasta {max(asistentes - 1, 0)} invitado(s) además de usted"]
    limpios, errores, vistos = [], [], set()
    for i, inv in enumerate(invitados, start=1):
        inv = inv if isinstance(inv, dict) else {}
        nombres = " ".join(str(inv.get("nombres") or "").split())
        apellidos = " ".join(str(inv.get("apellidos") or "").split())
        tipo = str(inv.get("tipo_documento") or "DNI").strip().upper()
        numero = str(inv.get("numero_documento") or "").strip().upper()
        if not _NOMBRE_RE.match(nombres) or not _NOMBRE_RE.match(apellidos):
            errores.append(f"Invitado {i}: nombres y apellidos deben tener solo letras (2 a 60 caracteres)")
            continue
        if tipo == "DNI" and not re.fullmatch(r"\d{8}", numero):
            errores.append(f"Invitado {i}: el DNI debe tener 8 dígitos")
            continue
        if tipo == "CE" and not re.fullmatch(r"[A-Z0-9]{9,12}", numero):
            errores.append(f"Invitado {i}: el carné de extranjería debe tener de 9 a 12 caracteres")
            continue
        if tipo not in ("DNI", "CE"):
            errores.append(f"Invitado {i}: el tipo de documento debe ser DNI o CE")
            continue
        if (tipo, numero) in vistos:
            errores.append(f"Invitado {i}: el documento {tipo} {numero} está repetido")
            continue
        vistos.add((tipo, numero))
        limpios.append({"nombres": nombres, "apellidos": apellidos,
                        "tipo_documento": tipo, "numero_documento": numero})
    return (limpios if not errores else []), errores


def _area_json(a):
    return {
        "activo": a.get("activo", True),
        "id": a["id"],
        "nombre": a["nombre"],
        "descripcion": a.get("descripcion"),
        "aforo": a["aforo"],
        "tarifa": money_float(a["tarifa"]),
        "garantia": money_float(a.get("garantia") or 0),
        "uso_exclusivo": a.get("uso_exclusivo", True),
        "hora_apertura": _fmt_hora(a["hora_apertura"]),
        "hora_cierre": _fmt_hora(a["hora_cierre"]),
        "anticipacion_min_horas": a["anticipacion_min_horas"],
        "duracion_max_horas": a["duracion_max_horas"],
    }


def _reserva_json(r, incluir_propietario=False):
    data = {
        "id": r["id"],
        "area_id": r["area_id"],
        "area": r.get("area"),
        "fecha": r["fecha"].isoformat() if hasattr(r["fecha"], "isoformat") else r["fecha"],
        "hora_inicio": _fmt_hora(r["hora_inicio"]),
        "hora_fin": _fmt_hora(r["hora_fin"]),
        "asistentes": r["asistentes"],
        "cargo": money_float(r["cargo"]),
        "estado": r["estado"],
        "recibo_id": r.get("recibo_id"),
        "propietario_id": r["propietario_id"],
        "garantia": money_float(r.get("garantia") or 0),
        "garantia_estado": r.get("garantia_estado", "no_aplica"),
        "garantia_retenida": money_float(r.get("garantia_retenida") or 0),
        "garantia_motivo": r.get("garantia_motivo"),
        "invitados": int(r.get("invitados") or 0),
    }
    if r.get("estado") == "pendiente_garantia" and r.get("creado_en"):
        limite = r["creado_en"] + dt.timedelta(minutes=reserva_dao.MINUTOS_PARA_PAGAR_GARANTIA)
        data["pagar_garantia_antes_de"] = limite.isoformat(timespec="seconds")
    if incluir_propietario and r.get("nombre") is not None:
        data["propietario"] = f"{r['nombre']} {r['apellido']}"
        data["nro_departamento"] = r.get("nro_departamento")
        data["torre"] = r.get("torre")
    return data


def listar_areas(incluir_inactivas=False):
    return {"items": [_area_json(a) for a in reserva_dao.get_areas(solo_activas=not incluir_inactivas)]}


def validar_area(body: dict) -> tuple[dict | None, list]:
    """Función pura: normaliza y valida la configuración de un área. Devuelve (datos, errores)."""
    errores = []
    nombre = str(body.get("nombre") or "").strip()
    descripcion = str(body.get("descripcion") or "").strip()[:300]
    if not 3 <= len(nombre) <= 80:
        errores.append("El nombre debe tener entre 3 y 80 caracteres")

    def entero(campo, etiqueta, minimo, maximo):
        try:
            v = int(body.get(campo))
        except (TypeError, ValueError):
            errores.append(f"{etiqueta} debe ser un número entero")
            return None
        if not minimo <= v <= maximo:
            errores.append(f"{etiqueta} debe estar entre {minimo} y {maximo}")
        return v

    aforo = entero("aforo", "El aforo", 1, 500)
    anticipacion = entero("anticipacion_min_horas", "La anticipación mínima (horas)", 0, 720)
    duracion = entero("duracion_max_horas", "La duración máxima (horas)", 1, 24)

    def monto(campo, etiqueta):
        try:
            v = round_money(body.get(campo) if body.get(campo) not in (None, "") else 0)
        except Exception:
            errores.append(f"{etiqueta} debe ser un monto válido")
            return None
        if v < 0 or v > 10000:
            errores.append(f"{etiqueta} debe estar entre S/ 0.00 y S/ 10,000.00")
        return v

    tarifa = monto("tarifa", "La tarifa")
    garantia = monto("garantia", "La garantía")

    apertura = _parse_hora(body.get("hora_apertura"))
    cierre = _parse_hora(body.get("hora_cierre"))
    if not apertura or not cierre:
        errores.append("Horario de apertura o cierre inválido (HH:MM)")
    elif cierre <= apertura:
        errores.append("La hora de cierre debe ser posterior a la de apertura")
    elif duracion is not None:
        horas_abierto = (dt.datetime.combine(dt.date.today(), cierre)
                         - dt.datetime.combine(dt.date.today(), apertura)).total_seconds() / 3600
        if duracion > horas_abierto:
            errores.append("La duración máxima no puede superar las horas que el área está abierta")

    def booleano(campo, defecto):
        v = body.get(campo, defecto)
        return v if isinstance(v, bool) else str(v).lower() in ("1", "true", "si", "sí")

    activo = booleano("activo", True)
    uso_exclusivo = booleano("uso_exclusivo", True)

    if errores:
        return None, errores
    return {
        "nombre": nombre, "descripcion": descripcion, "aforo": aforo, "tarifa": tarifa,
        "garantia": garantia, "uso_exclusivo": uso_exclusivo,
        "hora_apertura": apertura, "hora_cierre": cierre,
        "anticipacion_min_horas": anticipacion, "duracion_max_horas": duracion, "activo": activo,
    }, []


def actualizar_area(area_id, body: dict):
    """Cambia la configuración de un área. Solo afecta reservas nuevas: las confirmadas
    conservan el cargo con el que se registraron."""
    if not reserva_dao.get_area(area_id):
        return None, "not_found"
    datos, errores = validar_area(body)
    if errores:
        return {"errores": errores}, "invalido"
    if reserva_dao.nombre_area_existe(datos["nombre"], area_id):
        return {"errores": ["Ya existe otra área con ese nombre"]}, "invalido"
    row = reserva_dao.update_area(area_id, **datos)
    log.info("Área común actualizada", extra={"area_id": area_id, "tarifa": float(datos["tarifa"]),
                                               "activo": datos["activo"]})
    data = _area_json(row)
    data["reservas_futuras"] = reserva_dao.contar_reservas_futuras(area_id)
    return data, None


def disponibilidad(area_id, fecha_raw):
    area = reserva_dao.get_area(area_id)
    if not area:
        return None, "not_found"
    fecha = _parse_fecha(fecha_raw)
    if not fecha:
        return None, "Fecha inválida (YYYY-MM-DD)"
    reserva_dao.expirar_pendientes()
    ocupados = [
        {"hora_inicio": _fmt_hora(r["hora_inicio"]), "hora_fin": _fmt_hora(r["hora_fin"]),
         "personas": r["asistentes"]}
        for r in reserva_dao.get_reservas_activas_dia(area_id, fecha)
    ]
    return {"area": _area_json(area), "fecha": fecha.isoformat(), "ocupados": ocupados}, None


def crear_reserva(propietario_id, body: dict):
    try:
        area_id = int(body.get("area_id"))
        asistentes = int(body.get("asistentes") or 1)
    except (TypeError, ValueError):
        return None, "Datos de reserva inválidos"
    fecha = _parse_fecha(body.get("fecha"))
    hora_inicio = _parse_hora(body.get("hora_inicio"))
    hora_fin = _parse_hora(body.get("hora_fin"))
    if not fecha or not hora_inicio or not hora_fin:
        return None, "Fecha u horario inválidos"
    if asistentes < 1:
        return None, "Debe indicar al menos 1 asistente"

    area = reserva_dao.get_area(area_id)
    vencidos = recibo_dao.get_vencidos_propietario(propietario_id, dias_deuda_vencida())
    errores = validar_reglas(
        area, fecha, hora_inicio, hora_fin, asistentes, ahora_lima(),
        int(vencidos["cantidad"]) if vencidos else 0,
    )
    if errores:
        return {"reglas_incumplidas": errores}, "reglas"

    invitados, errores_inv = validar_invitados(body.get("invitados"), asistentes)
    if errores_inv:
        return {"reglas_incumplidas": errores_inv}, "reglas"

    cargo = round_money(area["tarifa"])
    garantia = round_money(area.get("garantia") or 0)
    mes = fecha.strftime("%Y-%m")
    reserva_dao.expirar_pendientes()

    with reserva_dao.transaccion() as conn:
        with conn.cursor() as cur:
            recibo = recibo_dao.get_recibo_del_mes_tx(cur, propietario_id, mes) if garantia == 0 else None
            row, motivo = reserva_dao.crear_reserva_tx(
                cur, area, propietario_id, fecha, hora_inicio, hora_fin, asistentes,
                cargo, garantia, recibo["id"] if recibo else None,
            )
            if not row:
                conn.rollback()
                return {"reglas_incumplidas": [motivo]}, "reglas"
            reserva_dao.insertar_invitados_tx(cur, row["id"], invitados)
            # Sin garantía la reserva queda confirmada y la tarifa pasa al recibo de inmediato;
            # con garantía, eso ocurre cuando se paga la garantía (pago_service)
            if garantia == 0 and recibo and cargo > 0:
                recibo_dao.ajustar_monto_reservas_tx(cur, recibo["id"], cargo)
        conn.commit()

    log.info("Reserva creada", extra={"reserva_id": row["id"], "area_id": area_id,
                                      "cargo": float(cargo), "garantia": float(garantia)})
    data = _reserva_json(reserva_dao.get_reserva(row["id"]))
    if garantia > 0:
        data["mensaje"] = (f"Pague la garantía de S/ {money_float(garantia):.2f} en los próximos "
                           f"{reserva_dao.MINUTOS_PARA_PAGAR_GARANTIA} minutos para confirmar la reserva")
    elif cargo > 0:
        data["mensaje"] = (
            f"Reserva confirmada. Se agregó S/ {money_float(cargo):.2f} a su recibo de {mes}"
            if recibo else
            f"Reserva confirmada. El cargo de S/ {money_float(cargo):.2f} se incluirá en su recibo de {mes}"
        )
    else:
        data["mensaje"] = "Reserva confirmada"
    return data, None


def mis_reservas(propietario_id):
    reserva_dao.expirar_pendientes()
    return {"items": [_reserva_json(r) for r in reserva_dao.get_reservas_propietario(propietario_id)]}


def listar_reservas_admin(desde=None):
    reserva_dao.expirar_pendientes()
    fecha = _parse_fecha(desde) if desde else None
    return {"items": [_reserva_json(r, True) for r in reserva_dao.get_reservas_admin(fecha)]}


def cancelar_reserva(reserva_id, propietario_id=None):
    """Cancela una reserva. Si la garantía estaba pagada se devuelve completa por la pasarela;
    si la tarifa ya estaba en el recibo, se descuenta."""
    reserva = reserva_dao.get_reserva(reserva_id)
    if not reserva:
        return None, "not_found"
    if propietario_id is not None and str(reserva["propietario_id"]) != str(propietario_id):
        return None, "forbidden"
    if reserva["estado"] not in ("confirmada", "pendiente_garantia"):
        return None, "La reserva ya no está activa"

    inicio = dt.datetime.combine(reserva["fecha"], reserva["hora_inicio"])
    if propietario_id is not None and inicio <= ahora_lima():
        return None, "No se puede cancelar una reserva que ya empezó o pasó"

    recibo = recibo_dao.get_recibo_por_id(reserva["recibo_id"]) if reserva.get("recibo_id") else None
    if propietario_id is not None and recibo and recibo["pagado"] and reserva["cargo"] > 0:
        return None, "El recibo con este cargo ya está pagado; solicite la devolución a la administración"

    from services.pago_service import devolver_garantia_tx  # import local: evita ciclo de imports

    devolucion = None
    with reserva_dao.transaccion() as conn:
        with conn.cursor() as cur:
            bloqueada = reserva_dao.get_reserva_para_actualizar(cur, reserva_id)
            row = reserva_dao.cancelar_reserva_tx(cur, reserva_id)
            if not row:
                conn.rollback()
                return None, "La reserva ya no está activa"
            if row["recibo_id"] and row["cargo"] > 0:
                recibo_dao.ajustar_monto_reservas_tx(cur, row["recibo_id"], -row["cargo"])
            if bloqueada["garantia_estado"] == "pagada":
                _, devolucion = devolver_garantia_tx(cur, bloqueada, 0, "Reserva cancelada")
        conn.commit()

    data = {"id": reserva_id, "estado": "cancelada"}
    if devolucion:
        data["garantia_devuelta"] = money_float(devolucion["monto"])
        data["codigo_devolucion"] = devolucion["codigo_operacion"]
    return data, None




def invitados_de_reserva(reserva_id, propietario_id=None):
    reserva = reserva_dao.get_reserva(reserva_id)
    if not reserva:
        return None, "not_found"
    if propietario_id is not None and str(reserva["propietario_id"]) != str(propietario_id):
        return None, "forbidden"
    return {
        "reserva_id": reserva_id,
        "area": reserva["area"],
        "fecha": reserva["fecha"].isoformat(),
        "hora_inicio": _fmt_hora(reserva["hora_inicio"]),
        "hora_fin": _fmt_hora(reserva["hora_fin"]),
        "titular": f"{reserva['nombre']} {reserva['apellido']}",
        "items": [dict(i) for i in reserva_dao.get_invitados(reserva_id)],
    }, None
