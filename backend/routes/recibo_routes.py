import datetime as dt

from flask import Blueprint, jsonify, request

from middleware import get_payload, require_roles, auth_response
from services import recibo_service

bp = Blueprint("recibos", __name__)


@bp.post("/api/recibos/generar")
def generar_recibos():
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Administrador")
    if role_err:
        return auth_response(role_err)

    body = request.get_json(silent=True) or {}
    fecha_emision = body.get("fecha_emision") or dt.date.today().isoformat()
    mes = body.get("mes") or str(fecha_emision)[:7]

    result, err = recibo_service.generar_recibos(fecha_emision, mes)
    if err:
        return jsonify({"error": err}), 400
    return jsonify(result)


@bp.post("/api/recibos/recalcular")
def recalcular_recibos():
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Administrador")
    if role_err:
        return auth_response(role_err)

    body = request.get_json(silent=True) or {}
    mes = body.get("mes")
    if not mes:
        return jsonify({"error": "Mes requerido (YYYY-MM)"}), 400

    result, err = recibo_service.recalcular_recibos(mes)
    if err:
        return jsonify({"error": err}), 400
    return jsonify(result)


@bp.get("/api/recibos")
def listar_recibos_admin():
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Administrador")
    if role_err:
        return auth_response(role_err)

    estado = (request.args.get("estado") or "").strip().lower()
    mes_filter = (request.args.get("mes") or "").strip()
    return jsonify(recibo_service.listar_recibos_admin(estado, mes_filter))


@bp.get("/api/recibos/propietario/<int:propietario_id>")
def listar_recibos_propietario(propietario_id):
    payload, err = get_payload()
    if err:
        return auth_response(err)

    if payload.get("tipo") == "Propietario":
        if str(propietario_id) != str(payload.get("propietario_id")):
            return jsonify({"error": "No autorizado"}), 403

    estado = (request.args.get("estado") or "").strip().lower()
    return jsonify(recibo_service.listar_recibos_propietario(propietario_id, estado))


@bp.post("/api/recibos/<int:recibo_id>/pagar")
def pagar_recibo(recibo_id):
    payload, err = get_payload()
    if err:
        return auth_response(err)

    propietario_payload_id = None
    if payload.get("tipo") == "Propietario":
        propietario_payload_id = payload.get("propietario_id")

    body = request.get_json(silent=True) or {}
    monto = body.get("monto")
    if monto is None:
        return jsonify({"error": "Monto requerido"}), 400

    result, err = recibo_service.pagar_recibo(recibo_id, monto, propietario_payload_id)
    if err == "not_found":
        return jsonify({"error": "Recibo no encontrado"}), 404
    if err == "forbidden":
        return jsonify({"error": "No autorizado"}), 403
    if err:
        return jsonify({"error": err}), 400
    return jsonify(result)


@bp.get("/api/recibos/<int:recibo_id>")
def detalle_recibo(recibo_id):
    payload, err = get_payload()
    if err:
        return auth_response(err)

    row = recibo_service.get_detalle_recibo(recibo_id)
    if not row:
        return jsonify({"error": "Recibo no encontrado"}), 404

    if payload.get("tipo") == "Propietario":
        if str(row.get("propietario_id")) != str(payload.get("propietario_id")):
            return jsonify({"error": "No autorizado"}), 403

    return jsonify(row)


@bp.delete("/api/recibos/<int:recibo_id>")
def eliminar_recibo(recibo_id):
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Administrador")
    if role_err:
        return auth_response(role_err)

    row = recibo_service.eliminar_recibo(recibo_id)
    if not row:
        return jsonify({"error": "Recibo no encontrado"}), 404
    return jsonify({"deleted": recibo_id})


@bp.get("/api/recibos/estructura/bst")
def buscar_recibos_bst():
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Administrador")
    if role_err:
        return auth_response(role_err)

    mes = (request.args.get("mes") or "").strip()
    estado = (request.args.get("estado") or "").strip().lower()
    recorrido = (request.args.get("recorrido") or "inorden").strip().lower()
    if recorrido not in ("inorden", "preorden", "postorden"):
        recorrido = "inorden"
    min_val, max_val, parse_err = _parse_saldo_range()
    if parse_err:
        return jsonify({"error": parse_err}), 400

    return jsonify(recibo_service.buscar_recibos_bst(mes, estado, recorrido, min_val, max_val))


@bp.get("/api/recibos/estructura/avl")
def buscar_recibos_avl():
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Administrador")
    if role_err:
        return auth_response(role_err)

    mes = (request.args.get("mes") or "").strip()
    estado = (request.args.get("estado") or "").strip().lower()
    recorrido = (request.args.get("recorrido") or "inorden").strip().lower()
    if recorrido not in ("inorden", "preorden", "postorden"):
        recorrido = "inorden"
    min_val, max_val, parse_err = _parse_saldo_range()
    if parse_err:
        return jsonify({"error": parse_err}), 400

    return jsonify(recibo_service.buscar_recibos_avl(mes, estado, recorrido, min_val, max_val))


@bp.get("/api/recibos/morosos/prioridad")
def morosos_prioridad():
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Administrador")
    if role_err:
        return auth_response(role_err)

    mes = (request.args.get("mes") or "").strip()
    limit_raw = request.args.get("limit", "5")
    try:
        limit = max(1, min(int(limit_raw), 100))
    except ValueError:
        limit = 5

    return jsonify(recibo_service.get_morosos_prioridad(mes, limit))


@bp.get("/api/propietarios/<int:propietario_id>/estado-cuenta")
def estado_cuenta(propietario_id):
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Administrador")
    if role_err:
        return auth_response(role_err)

    desde = (request.args.get("desde") or "").strip()
    hasta = (request.args.get("hasta") or "").strip()
    return jsonify(recibo_service.get_estado_cuenta(propietario_id, desde, hasta))


def _parse_saldo_range():
    saldo_min = request.args.get("saldo_min")
    saldo_max = request.args.get("saldo_max")
    try:
        min_val = float(saldo_min) if saldo_min not in (None, "") else None
        max_val = float(saldo_max) if saldo_max not in (None, "") else None
    except ValueError:
        return None, None, "Parámetros de saldo inválidos"
    return min_val, max_val, None
