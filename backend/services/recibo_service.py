import datetime as dt
from decimal import Decimal, InvalidOperation

from dao import recibo_dao, gasto_dao
from db import get_db
from services.configuracion_service import get_monto_administracion
from structures import (
    MatrizRecibos,
    ArbolRecibosBST,
    ArbolRecibosAVL,
    ColaPrioridadMorosos,
)
from utils.money import round_money, money_float, to_decimal
from utils.logger import get_logger

log = get_logger(__name__)


def _recibo_total(recibo) -> float:
    t = (to_decimal(recibo["monto_administracion"])
         + to_decimal(recibo["monto_agua"])
         + to_decimal(recibo["monto_luz"])
         + to_decimal(recibo["monto_mantenimiento"]))
    return money_float(t)


def _recibo_saldo(recibo) -> float:
    total = (to_decimal(recibo["monto_administracion"])
             + to_decimal(recibo["monto_agua"])
             + to_decimal(recibo["monto_luz"])
             + to_decimal(recibo["monto_mantenimiento"]))
    saldo = total - to_decimal(recibo.get("monto_pagado") or 0)
    if saldo < 0:
        saldo = Decimal("0")
    return money_float(saldo)


def _enriquecer_recibo(row: dict) -> dict:
    recibo = {
        "id": row["id"],
        "propietario_id": row["propietario_id"],
        "monto_administracion": row["monto_administracion"],
        "monto_agua": row["monto_agua"],
        "monto_luz": row["monto_luz"],
        "monto_mantenimiento": row["monto_mantenimiento"],
        "monto_pagado": row.get("monto_pagado", 0),
        "fecha_emision": row["fecha_emision"].isoformat() if hasattr(row["fecha_emision"], "isoformat") else row["fecha_emision"],
        "fecha_pago": row["fecha_pago"].isoformat() if row.get("fecha_pago") else None,
        "pagado": row["pagado"],
    }
    if row.get("nombre") is not None:
        recibo["propietario"] = {"nombre": row["nombre"], "apellido": row["apellido"]}
        recibo["nro_departamento"] = row["nro_departamento"]
        recibo["torre"] = row["torre"]
    recibo["total"] = _recibo_total(recibo)
    recibo["saldo"] = _recibo_saldo(recibo)
    return recibo


def aplicar_pago_fifo(monto, fecha_emision: str) -> tuple[float, float]:
    mes = str(fecha_emision)[:7]
    remaining = round_money(monto)
    applied = Decimal("0.00")
    if remaining <= 0:
        return float(applied), float(remaining)

    with get_db() as conn:
        with conn.cursor() as cur:
            gastos = gasto_dao.get_gastos_pendientes_del_mes(mes, conn, cur)
            for gasto in gastos:
                if remaining <= 0:
                    break
                saldo_gasto = round_money(
                    to_decimal(gasto["monto"]) - to_decimal(gasto.get("monto_pagado") or 0)
                )
                if saldo_gasto <= 0:
                    continue
                aplicar = min(remaining, saldo_gasto)
                gasto_dao.insert_pago_gasto_tx(cur, gasto["id"], aplicar)
                remaining = round_money(remaining - aplicar)
                applied = round_money(applied + aplicar)
        conn.commit()

    return float(applied), float(remaining)


def generar_recibos(fecha_emision: str, mes: str) -> dict:
    from dao import propietario_dao as pdao
    propietarios = pdao.get_all_propietarios()
    if not propietarios:
        return None, "No hay propietarios registrados"

    divisor = Decimal(len(propietarios))
    monto_admin = round_money(get_monto_administracion())

    def _sum_tipo(tipo):
        row = gasto_dao.get_total_tipo_mes(tipo, mes)
        v = row["total"] if row else 0
        return Decimal(str(v)) if not isinstance(v, Decimal) else v

    monto_agua = round_money(_sum_tipo("agua") / divisor)
    monto_luz = round_money(_sum_tipo("luz") / divisor)
    monto_mant = round_money(_sum_tipo("mantenimiento") / divisor)

    generados = 0
    recibos = []
    for prop in propietarios:
        if recibo_dao.recibo_existe_en_mes(prop["id"], mes):
            continue
        row = recibo_dao.create_recibo(
            prop["id"], monto_admin, monto_agua, monto_luz, monto_mant, fecha_emision
        )
        recibo = _enriquecer_recibo(row)
        recibo["propietario"] = {"nombre": prop["nombre"], "apellido": prop["apellido"]}
        recibo["nro_departamento"] = prop["nro_departamento"]
        recibo["torre"] = prop["torre"]
        recibos.append(recibo)
        generados += 1

    log.info("Recibos generados", extra={"mes": mes, "cantidad": generados})
    return {"generados": generados, "items": recibos}, None


def recalcular_recibos(mes: str) -> dict:
    from dao import propietario_dao as pdao
    propietarios = pdao.get_all_propietarios()
    if not propietarios:
        return None, "No hay propietarios registrados"

    divisor = Decimal(len(propietarios))
    monto_admin = round_money(get_monto_administracion())

    def _sum_tipo(tipo):
        row = gasto_dao.get_total_tipo_mes(tipo, mes)
        v = row["total"] if row else 0
        return Decimal(str(v)) if not isinstance(v, Decimal) else v

    monto_agua = round_money(_sum_tipo("agua") / divisor)
    monto_luz = round_money(_sum_tipo("luz") / divisor)
    monto_mant = round_money(_sum_tipo("mantenimiento") / divisor)

    rows = recibo_dao.recalcular_recibos_mes(mes, monto_admin, monto_agua, monto_luz, monto_mant)
    items = [_enriquecer_recibo(r) for r in rows]
    return {"actualizados": len(items), "items": items}, None


def listar_recibos_admin(estado: str = "", mes_filter: str = "") -> dict:
    rows = recibo_dao.get_recibos_admin(estado, mes_filter)
    matriz = MatrizRecibos()
    items = []
    resumen = {}
    for row in rows:
        recibo = _enriquecer_recibo(row)
        mes = recibo["fecha_emision"][:7]
        matriz.set_recibo(mes, recibo["propietario_id"], recibo)
        items.append(recibo)
        bucket = resumen.setdefault(mes, {"mes": mes, "emitido": 0.0, "pagado": 0.0, "pendiente": 0.0, "cantidad": 0})
        bucket["emitido"] += recibo["total"]
        bucket["pagado"] += float(recibo.get("monto_pagado") or 0)
        bucket["pendiente"] += recibo["saldo"]
        bucket["cantidad"] += 1
    resumen_list = sorted(resumen.values(), key=lambda x: x["mes"], reverse=True)
    return {"items": items, "resumen_mensual": resumen_list}


def listar_recibos_propietario(propietario_id, estado: str = "") -> dict:
    rows = recibo_dao.get_recibos_propietario(propietario_id, estado)
    matriz = MatrizRecibos()
    items = []
    for row in rows:
        recibo = _enriquecer_recibo(row)
        mes = recibo["fecha_emision"][:7]
        matriz.set_recibo(mes, propietario_id, recibo)
        items.append(recibo)
    return {"items": items}


def pagar_recibo(recibo_id, monto_raw, propietario_payload_id=None):
    try:
        monto = round_money(monto_raw)
    except (TypeError, ValueError, InvalidOperation):
        return None, "Monto inválido"
    if monto <= 0:
        return None, "El monto debe ser mayor a cero"

    current = recibo_dao.get_recibo_por_id(recibo_id)
    if not current:
        return None, "not_found"

    if propietario_payload_id is not None:
        if str(current["propietario_id"]) != str(propietario_payload_id):
            return None, "forbidden"

    total = (to_decimal(current["monto_administracion"])
             + to_decimal(current["monto_agua"])
             + to_decimal(current["monto_luz"])
             + to_decimal(current["monto_mantenimiento"]))
    saldo = round_money(total - to_decimal(current.get("monto_pagado") or 0))
    if monto > saldo:
        return None, f"El monto excede el saldo pendiente ({money_float(saldo):.2f})"

    row = recibo_dao.pagar_recibo(recibo_id, monto)
    if not row:
        return None, "not_found"

    recibo = _enriquecer_recibo(row)
    aplicado, no_aplicado = 0.0, round(float(monto), 2)
    try:
        aplicado, no_aplicado = aplicar_pago_fifo(monto, recibo["fecha_emision"])
    except Exception:
        pass

    recibo["aplicado_gastos"] = aplicado
    recibo["saldo_no_aplicado_gastos"] = no_aplicado
    return recibo, None


def eliminar_recibo(recibo_id):
    return recibo_dao.delete_recibo(recibo_id)


def _recibos_para_estructuras(mes_filter: str = "", estado: str = "") -> list:
    rows = recibo_dao.get_recibos_para_estructuras(mes_filter, estado)
    return [_enriquecer_recibo(r) for r in rows]


def buscar_recibos_bst(mes: str, estado: str, recorrido: str, min_val, max_val) -> dict:
    items = _recibos_para_estructuras(mes, estado)
    tree = ArbolRecibosBST()
    for item in items:
        tree.insertar((float(item["saldo"]), item["id"]), item)
    result = _tree_filtered(tree, recorrido, min_val, max_val)
    return {"estructura": "bst", "total": len(result), "items": result}


def buscar_recibos_avl(mes: str, estado: str, recorrido: str, min_val, max_val) -> dict:
    items = _recibos_para_estructuras(mes, estado)
    tree = ArbolRecibosAVL()
    for item in items:
        tree.insertar((float(item["saldo"]), item["id"]), item)
    result = _tree_filtered(tree, recorrido, min_val, max_val)
    return {"estructura": "avl", "total": len(result), "items": result}


def _tree_filtered(tree, recorrido, min_val, max_val):
    if min_val is None and max_val is None:
        return tree.recorrer(recorrido)
    mn = -1e18 if min_val is None else float(min_val)
    mx = 1e18 if max_val is None else float(max_val)
    return tree.rango((mn, -1), (mx, 10**12))


def get_morosos_prioridad(mes: str, limit: int) -> dict:
    pendientes = _recibos_para_estructuras(mes, "pendientes")
    hoy = dt.date.today()
    cola = ColaPrioridadMorosos()
    for r in pendientes:
        fecha = dt.date.fromisoformat(r["fecha_emision"][:10])
        dias = max((hoy - fecha).days, 0)
        cola.enqueue({
            "recibo_id": r["id"],
            "propietario_id": r["propietario_id"],
            "propietario": r["propietario"],
            "nro_departamento": r["nro_departamento"],
            "torre": r["torre"],
            "saldo": float(r["saldo"]),
            "dias_pendiente": dias,
            "fecha_emision": r["fecha_emision"],
        })
    items = cola.to_sorted_list(limit=limit)
    return {"total": len(items), "items": items}


def get_estado_cuenta(propietario_id, desde: str = "", hasta: str = "") -> dict:
    rows = recibo_dao.get_recibos_estado_cuenta(propietario_id, desde, hasta)
    items = [_enriquecer_recibo(r) for r in rows]
    return {"propietario_id": propietario_id, "items": items, "total": len(items)}
