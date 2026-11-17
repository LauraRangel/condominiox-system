from flask import Blueprint, jsonify, request

from middleware import get_payload, require_roles, auth_response, json_body
from services import pago_service

bp = Blueprint("pagos", __name__)


@bp.post("/api/pagos")
def pagar_en_linea():
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Propietario")
    if role_err:
        return auth_response(role_err)

    key = (request.headers.get("Idempotency-Key") or "").strip()[:80] or None
    body = json_body()
    data, error = pago_service.procesar_pago(payload.get("propietario_id"), body, key)
    if error == "not_found":
        return jsonify({"error": "Recibo no encontrado"}), 404
    if error == "forbidden":
        return jsonify({"error": "No autorizado"}), 403
    if error == "rechazado":
        return jsonify({"error": data["transaccion"]["mensaje"], **data}), 402
    if error:
        return jsonify({"error": error}), 400
    return jsonify(data), 200 if data.get("repetido") else 201


@bp.get("/api/pagos/mios")
def mis_pagos():
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Propietario")
    if role_err:
        return auth_response(role_err)
    return jsonify(pago_service.mis_transacciones(payload.get("propietario_id")))


@bp.get("/api/pagos")
def listar_pagos():
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Administrador")
    if role_err:
        return auth_response(role_err)
    estado = (request.args.get("estado") or "").strip().lower()
    return jsonify(pago_service.listar_transacciones_admin(estado))
