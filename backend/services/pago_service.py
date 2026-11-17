"""Pagos en línea: recibos y garantías de reserva, más devoluciones de garantía.

Cada operación es ATÓMICA: el cobro aprobado, la actualización del recibo o la reserva,
la distribución FIFO a los gastos y el registro de la transacción se confirman en un
único commit, con el recibo o la reserva bloqueados (SELECT ... FOR UPDATE).
"""

from decimal import InvalidOperation

import psycopg

from dao import pago_dao, recibo_dao, reserva_dao
from db import get_db
from services import recibo_service
from services.pasarelas import obtener_pasarela, MODO
from utils.money import round_money, money_float, to_decimal
from utils.logger import get_logger

log = get_logger(__name__)

_ETIQUETA_CONCEPTO = {"recibo": "Recibo", "garantia": "Garantía", "devolucion": "Devolución de garantía"}


def _tx_json(t: dict) -> dict:
    data = {
        "id": t["id"],
        "concepto": t.get("concepto", "recibo"),
        "recibo_id": t.get("recibo_id"),
        "reserva_id": t.get("reserva_id"),
        "proveedor": t["proveedor"],
        "monto": money_float(t["monto"]),
        "moneda": t.get("moneda", "PEN"),
        "estado": t["estado"],
        "codigo_operacion": t["codigo_operacion"],
        "medio_detalle": t.get("medio_detalle"),
        "mensaje": t.get("mensaje"),
        "modo": t.get("modo"),
        "fecha": t["creado_en"].isoformat(timespec="seconds") if hasattr(t.get("creado_en"), "isoformat") else t.get("creado_en"),
    }
    if t.get("fecha_emision") is not None:
        data["mes_recibo"] = str(t["fecha_emision"])[:7]
    if t.get("area"):
        data["area"] = t["area"]
    if t.get("nombre") is not None:
        data["propietario"] = f"{t['nombre']} {t['apellido']}"
        data["nro_departamento"] = t.get("nro_departamento")
        data["torre"] = t.get("torre")
    return data


def _previa_por_clave(idempotency_key, propietario_id):
    previa = pago_dao.get_por_idempotency_key(idempotency_key)
    if not previa:
        return None, None
    if str(previa["propietario_id"]) != str(propietario_id):
        return None, "forbidden"
    return {"transaccion": _tx_json(previa), "repetido": True}, None


def procesar_pago(propietario_id, body: dict, idempotency_key: str | None):
    if idempotency_key:
        previa, err = _previa_por_clave(idempotency_key, propietario_id)
        if err or previa:
            return previa, err

    concepto = (body.get("concepto") or "recibo").lower()
    if concepto not in ("recibo", "garantia"):
        return None, "Concepto de pago inválido"
    pasarela = obtener_pasarela(body.get("proveedor"))
    if not pasarela:
        return None, "Medio de pago no soportado (yape, culqi o mercadopago)"
    datos = body.get("datos") if isinstance(body.get("datos"), dict) else {}
    error_datos = pasarela.validar(datos)
    if error_datos:
        return None, error_datos

    try:
        if concepto == "recibo":
            return _pagar_recibo(propietario_id, body, pasarela, datos, idempotency_key)
        return _pagar_garantia(propietario_id, body, pasarela, datos, idempotency_key)
    except psycopg.errors.UniqueViolation:
        # Dos peticiones simultáneas con la misma Idempotency-Key: gana la primera
        if idempotency_key:
            previa, err = _previa_por_clave(idempotency_key, propietario_id)
            if previa or err:
                return previa, err
        raise


def _registrar(cur, resultado, estado, **kw):
    return pago_dao.registrar_transaccion_tx(
        cur, estado=estado, codigo_operacion=resultado["codigo_operacion"],
        medio_detalle=resultado["medio_detalle"], mensaje=resultado["mensaje"],
        respuesta_pasarela=resultado["respuesta"], modo=MODO, **kw,
    )


def _pagar_recibo(propietario_id, body, pasarela, datos, idempotency_key):
    try:
        recibo_id = int(body.get("recibo_id"))
        monto = round_money(body.get("monto"))
    except (TypeError, ValueError, InvalidOperation):
        return None, "Recibo o monto inválido"
    if monto <= 0:
        return None, "El monto debe ser mayor a cero"

    with get_db() as conn:
        with conn.cursor() as cur:
            recibo = recibo_dao.get_recibo_para_actualizar(cur, recibo_id)
            if not recibo:
                return None, "not_found"
            if str(recibo["propietario_id"]) != str(propietario_id):
                return None, "forbidden"
            saldo = recibo_service.saldo_decimal(recibo)
            if monto > saldo:
                return None, f"El monto excede el saldo pendiente (S/ {money_float(saldo):.2f})"

            mes = str(recibo["fecha_emision"])[:7]
            resultado = pasarela.cobrar(monto, datos, f"CondominioX recibo {recibo_id} ({mes})")
            recibo_actualizado = None
            if resultado["aprobado"]:
                row = recibo_dao.pagar_recibo_tx(cur, recibo_id, monto)
                recibo_service.aplicar_pago_fifo_tx(conn, cur, monto, row["fecha_emision"])
                recibo_actualizado = recibo_service.enriquecer_recibo(row)
            tx = _registrar(cur, resultado, "aprobado" if resultado["aprobado"] else "rechazado",
                            propietario_id=propietario_id, concepto="recibo", proveedor=pasarela.proveedor,
                            monto=monto, recibo_id=recibo_id, idempotency_key=idempotency_key)
        conn.commit()

    _log(tx)
    data = {"transaccion": _tx_json(tx), "recibo": recibo_actualizado}
    return data, (None if resultado["aprobado"] else "rechazado")


def _pagar_garantia(propietario_id, body, pasarela, datos, idempotency_key):
    try:
        reserva_id = int(body.get("reserva_id"))
    except (TypeError, ValueError):
        return None, "Reserva inválida"

    reserva_dao.expirar_pendientes()
    with get_db() as conn:
        with conn.cursor() as cur:
            reserva = reserva_dao.get_reserva_para_actualizar(cur, reserva_id)
            if not reserva:
                return None, "not_found"
            if str(reserva["propietario_id"]) != str(propietario_id):
                return None, "forbidden"
            if reserva["estado"] == "expirada":
                return None, "Venció el plazo para pagar la garantía; vuelva a reservar"
            if reserva["estado"] != "pendiente_garantia" or reserva["garantia_estado"] != "pendiente":
                return None, "Esta reserva no tiene una garantía pendiente de pago"

            monto = round_money(reserva["garantia"])  # la garantía se paga completa, nunca parcial
            resultado = pasarela.cobrar(monto, datos, f"CondominioX garantía reserva {reserva_id}")
            mensaje_cargo = None
            if resultado["aprobado"]:
                recibo = recibo_dao.get_recibo_del_mes_tx(cur, propietario_id, reserva["fecha"].strftime("%Y-%m"))
                recibo_id = recibo["id"] if recibo else None
                reserva_dao.confirmar_reserva_tx(cur, reserva_id, recibo_id)
                if recibo_id and reserva["cargo"] > 0:
                    recibo_dao.ajustar_monto_reservas_tx(cur, recibo_id, reserva["cargo"])
                if reserva["cargo"] > 0:
                    mensaje_cargo = (f"La tarifa de S/ {money_float(reserva['cargo']):.2f} "
                                     + ("se agregó a su recibo del mes" if recibo_id else "se incluirá en su próximo recibo"))
            tx = _registrar(cur, resultado, "aprobado" if resultado["aprobado"] else "rechazado",
                            propietario_id=propietario_id, concepto="garantia", proveedor=pasarela.proveedor,
                            monto=monto, reserva_id=reserva_id, idempotency_key=idempotency_key)
        conn.commit()

    _log(tx)
    data = {"transaccion": _tx_json(tx), "reserva_id": reserva_id, "mensaje_cargo": mensaje_cargo}
    return data, (None if resultado["aprobado"] else "rechazado")


def devolver_garantia_tx(cur, reserva, retener=0, motivo=None):
    """Devuelve la garantía pagada de una reserva (total o parcial) por el mismo medio del cobro.
    Debe llamarse con la reserva bloqueada. Devuelve (estado_final, transaccion_devolucion|None)."""
    garantia = round_money(reserva["garantia"])
    retener = round_money(retener or 0)
    a_devolver = round_money(garantia - retener)
    tx = None
    if a_devolver > 0:
        cargo = pago_dao.get_pago_garantia_tx(cur, reserva["id"])
        pasarela = obtener_pasarela(cargo["proveedor"])
        resultado = pasarela.reembolsar(cargo["codigo_operacion"], a_devolver,
                                        motivo or "Devolución de garantía")
        resultado["medio_detalle"] = cargo["medio_detalle"]
        tx = _registrar(cur, resultado, "aprobado", propietario_id=reserva["propietario_id"],
                        concepto="devolucion", proveedor=cargo["proveedor"], monto=a_devolver,
                        reserva_id=reserva["id"], transaccion_origen_id=cargo["id"])
    if retener == 0:
        estado = "devuelta"
    elif a_devolver == 0:
        estado = "retenida"
    else:
        estado = "devuelta_parcial"
    reserva_dao.resolver_garantia_tx(cur, reserva["id"], estado, retener, motivo)
    return estado, tx


def resolver_garantia(reserva_id, body: dict):
    """Acción del administrador después del uso del área: devolver todo, parte o retener."""
    try:
        retener = round_money(body.get("retener") or 0)
    except (TypeError, ValueError, InvalidOperation):
        return None, "Monto a retener inválido"
    motivo = (str(body.get("motivo") or "").strip())[:300] or None

    with get_db() as conn:
        with conn.cursor() as cur:
            reserva = reserva_dao.get_reserva_para_actualizar(cur, reserva_id)
            if not reserva:
                return None, "not_found"
            if reserva["garantia_estado"] != "pagada":
                return None, "La garantía de esta reserva no está en custodia"
            if retener < 0 or retener > to_decimal(reserva["garantia"]):
                return None, f"Puede retener entre S/ 0.00 y S/ {money_float(reserva['garantia']):.2f}"
            if retener > 0 and not motivo:
                return None, "Indique el motivo de la retención (por ejemplo, daños o limpieza)"
            estado, tx = devolver_garantia_tx(cur, reserva, retener, motivo)
        conn.commit()

    if tx:
        _log(tx)
    return {
        "reserva_id": reserva_id,
        "garantia_estado": estado,
        "devuelto": money_float(to_decimal(reserva["garantia"]) - retener),
        "retenido": money_float(retener),
        "transaccion": _tx_json(tx) if tx else None,
    }, None


def _log(tx):
    log.info("Operación de pasarela", extra={
        "event": "pago_en_linea", "concepto": tx["concepto"], "recibo_id": tx.get("recibo_id"),
        "reserva_id": tx.get("reserva_id"), "proveedor": tx["proveedor"], "estado": tx["estado"],
        "codigo_operacion": tx["codigo_operacion"],
    })


def mis_transacciones(propietario_id):
    return {"items": [_tx_json(t) for t in pago_dao.get_transacciones_propietario(propietario_id)]}


def listar_transacciones_admin(estado=""):
    items = [_tx_json(t) for t in pago_dao.get_transacciones_admin(estado)]
    aprobadas = [t for t in items if t["estado"] == "aprobado" and t["concepto"] == "recibo"]
    custodia = reserva_dao.total_garantias_en_custodia()
    return {
        "items": items,
        "resumen": {
            "aprobadas": len([t for t in items if t["estado"] == "aprobado" and t["concepto"] != "devolucion"]),
            "rechazadas": len([t for t in items if t["estado"] == "rechazado"]),
            "monto_conciliado": round(sum(t["monto"] for t in aprobadas), 2),
            "garantias_en_custodia": money_float(custodia["total"]) if custodia else 0.0,
            "garantias_en_custodia_cantidad": int(custodia["n"]) if custodia else 0,
        },
    }
