from flask import Blueprint, jsonify, request

from middleware import get_payload, require_roles, auth_response
from services import configuracion_service

bp = Blueprint("configuracion", __name__)


@bp.get("/api/configuracion")
def obtener_configuracion():
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Administrador")
    if role_err:
        return auth_response(role_err)
    return jsonify({"monto_administracion": configuracion_service.get_monto_administracion()})


@bp.put("/api/configuracion")
def actualizar_configuracion():
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Administrador")
    if role_err:
        return auth_response(role_err)

    body = request.get_json(silent=True) or {}
    monto = body.get("monto_administracion")
    if monto is None:
        return jsonify({"error": "Monto de administración requerido"}), 400

    result = configuracion_service.update_monto_administracion(monto)
    return jsonify(result)
