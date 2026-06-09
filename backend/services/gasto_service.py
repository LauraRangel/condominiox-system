from decimal import InvalidOperation

from dao import gasto_dao
from utils.money import round_money, money_float
from utils.logger import get_logger

log = get_logger(__name__)


def listar_gastos() -> dict:
    rows = gasto_dao.get_all_gastos()
    items = []
    for row in rows:
        total = float(row["monto"] or 0)
        pagado = float(row.get("monto_pagado") or 0)
        saldo = max(total - pagado, 0)
        if row.get("fecha_registro"):
            row["fecha_registro"] = row["fecha_registro"].isoformat()
        row["saldo"] = saldo
        row["pagado_gasto"] = saldo <= 0
        items.append(row)
    return {"items": items}


def crear_gasto(proveedor, concepto, monto, tipo, fecha_registro):
    if not all([proveedor, concepto, monto, tipo]):
        return None, "Datos incompletos"
    if tipo not in ("mantenimiento", "luz", "agua"):
        return None, "Tipo de gasto inválido"
    if not fecha_registro:
        return None, "Fecha requerida"
    try:
        monto_dec = round_money(monto)
        if monto_dec <= 0:
            return None, "El monto debe ser mayor a cero"
    except (TypeError, ValueError, InvalidOperation):
        return None, "Monto inválido"

    row = gasto_dao.create_gasto(proveedor, concepto, monto_dec, tipo, fecha_registro)
    if row and row.get("fecha_registro"):
        row["fecha_registro"] = row["fecha_registro"].isoformat()
    log.info("Gasto creado", extra={"tipo": tipo, "monto": float(monto_dec)})
    return row, None


def eliminar_gasto(gasto_id):
    return gasto_dao.delete_gasto(gasto_id)


def pagar_gasto(gasto_id, monto):
    if monto is None:
        return None, "Monto requerido"
    try:
        monto_dec = round_money(monto)
        if monto_dec <= 0:
            return None, "El monto debe ser mayor a cero"
    except (TypeError, ValueError, InvalidOperation):
        return None, "Monto inválido"

    gasto = gasto_dao.get_gasto_con_saldo(gasto_id)
    if not gasto:
        return None, "not_found"

    saldo = round_money(
        round_money(gasto["monto"]) - round_money(gasto.get("monto_pagado") or 0)
    )
    if monto_dec > saldo:
        return None, f"El monto excede el saldo ({money_float(saldo):.2f})"

    row = gasto_dao.create_pago_gasto(gasto_id, monto_dec)
    if row and row.get("fecha_pago"):
        row["fecha_pago"] = row["fecha_pago"].isoformat()
    return row, None
