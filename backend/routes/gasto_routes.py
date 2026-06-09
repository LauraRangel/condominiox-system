from flask import Blueprint, jsonify, request

from middleware import get_payload, require_roles, auth_response
from services import gasto_service

bp = Blueprint("gastos", __name__)


@bp.get("/api/gastos")
def listar_gastos():
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Administrador")
    if role_err:
        return auth_response(role_err)
    return jsonify(gasto_service.listar_gastos())


@bp.post("/api/gastos")
def crear_gasto():
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Administrador")
    if role_err:
        return auth_response(role_err)

    body = request.get_json(silent=True) or {}
    row, err = gasto_service.crear_gasto(
        body.get("proveedor"), body.get("concepto"),
        body.get("monto"), body.get("tipo"), body.get("fecha_registro"),
    )
    if err:
        return jsonify({"error": err}), 400
    return jsonify(row), 201


@bp.delete("/api/gastos/<int:gasto_id>")
def eliminar_gasto(gasto_id):
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Administrador")
    if role_err:
        return auth_response(role_err)

    row = gasto_service.eliminar_gasto(gasto_id)
    if not row:
        return jsonify({"error": "Gasto no encontrado"}), 404
    return jsonify({"deleted": gasto_id})


@bp.post("/api/gastos/<int:gasto_id>/pagar")
def pagar_gasto(gasto_id):
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Administrador")
    if role_err:
        return auth_response(role_err)

    body = request.get_json(silent=True) or {}
    row, err = gasto_service.pagar_gasto(gasto_id, body.get("monto"))
    if err == "not_found":
        return jsonify({"error": "Gasto no encontrado"}), 404
    if err:
        return jsonify({"error": err}), 400
    return jsonify(row), 201
