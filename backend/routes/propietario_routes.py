from flask import Blueprint, jsonify, request

from middleware import get_payload, require_roles, auth_response
from services import propietario_service

bp = Blueprint("propietarios", __name__)


@bp.get("/api/propietarios")
def listar_propietarios():
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Administrador")
    if role_err:
        return auth_response(role_err)
    return jsonify(propietario_service.listar_propietarios())


@bp.get("/api/propietarios/busqueda")
def buscar_propietarios():
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Administrador")
    if role_err:
        return auth_response(role_err)

    q = request.args.get("q") or ""
    torre = request.args.get("torre") or ""
    piso = request.args.get("piso") or ""
    return jsonify(propietario_service.buscar_propietarios(q, torre, piso))


@bp.post("/api/propietarios")
def crear_propietario():
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Administrador")
    if role_err:
        return auth_response(role_err)

    body = request.get_json(silent=True) or {}
    row, err = propietario_service.crear_propietario(body)
    if err:
        code = 409 if "Ya existe" in err else 400
        return jsonify({"error": err}), code
    return jsonify(row), 201


@bp.put("/api/propietarios/<int:propietario_id>")
def actualizar_propietario(propietario_id):
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Administrador")
    if role_err:
        return auth_response(role_err)

    body = request.get_json(silent=True) or {}
    row, err = propietario_service.actualizar_propietario(propietario_id, body)
    if err == "not_found":
        return jsonify({"error": "Propietario no encontrado"}), 404
    if err:
        code = 409 if "Ya existe" in err else 400
        return jsonify({"error": err}), code
    return jsonify(row)


@bp.delete("/api/propietarios/<int:propietario_id>")
def eliminar_propietario(propietario_id):
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Administrador")
    if role_err:
        return auth_response(role_err)

    row = propietario_service.eliminar_propietario(propietario_id)
    if not row:
        return jsonify({"error": "Propietario no encontrado"}), 404
    return jsonify({"deleted": propietario_id})
