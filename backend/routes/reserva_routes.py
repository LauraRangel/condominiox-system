from flask import Blueprint, jsonify, request

from middleware import get_payload, require_roles, auth_response, json_body
from services import reserva_service, pago_service

bp = Blueprint("reservas", __name__)


@bp.get("/api/areas-comunes")
def listar_areas():
    payload, err = get_payload()
    if err:
        return auth_response(err)
    # El administrador ve también las áreas desactivadas para poder reactivarlas
    incluir_inactivas = payload.get("tipo") == "Administrador" and request.args.get("todas") == "1"
    return jsonify(reserva_service.listar_areas(incluir_inactivas))


@bp.put("/api/areas-comunes/<int:area_id>")
def actualizar_area(area_id):
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Administrador")
    if role_err:
        return auth_response(role_err)

    body = json_body()
    data, error = reserva_service.actualizar_area(area_id, body)
    if error == "not_found":
        return jsonify({"error": "Área no encontrada"}), 404
    if error == "invalido":
        return jsonify({"error": data["errores"][0], **data}), 400
    return jsonify(data)


@bp.get("/api/areas-comunes/<int:area_id>/disponibilidad")
def disponibilidad(area_id):
    payload, err = get_payload()
    if err:
        return auth_response(err)
    data, error = reserva_service.disponibilidad(area_id, request.args.get("fecha"))
    if error == "not_found":
        return jsonify({"error": "Área no encontrada"}), 404
    if error:
        return jsonify({"error": error}), 400
    return jsonify(data)


@bp.post("/api/reservas")
def crear_reserva():
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Propietario")
    if role_err:
        return auth_response(role_err)

    body = json_body()
    data, error = reserva_service.crear_reserva(payload.get("propietario_id"), body)
    if error == "reglas":
        return jsonify({"error": "La reserva no cumple las reglas del área", **data}), 409
    if error:
        return jsonify({"error": error}), 400
    return jsonify(data), 201


@bp.get("/api/reservas/mias")
def mis_reservas():
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Propietario")
    if role_err:
        return auth_response(role_err)
    return jsonify(reserva_service.mis_reservas(payload.get("propietario_id")))


@bp.get("/api/reservas")
def listar_reservas_admin():
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Administrador")
    if role_err:
        return auth_response(role_err)
    return jsonify(reserva_service.listar_reservas_admin(request.args.get("desde")))


@bp.delete("/api/reservas/<int:reserva_id>")
def cancelar_reserva(reserva_id):
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Propietario", "Administrador")
    if role_err:
        return auth_response(role_err)

    propietario_id = payload.get("propietario_id") if payload.get("tipo") == "Propietario" else None
    data, error = reserva_service.cancelar_reserva(reserva_id, propietario_id)
    if error == "not_found":
        return jsonify({"error": "Reserva no encontrada"}), 404
    if error == "forbidden":
        return jsonify({"error": "No autorizado"}), 403
    if error:
        return jsonify({"error": error}), 400
    return jsonify(data)


@bp.post("/api/reservas/<int:reserva_id>/garantia/resolucion")
def resolver_garantia(reserva_id):
    """El administrador devuelve la garantía completa, una parte o la retiene (con motivo)."""
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Administrador")
    if role_err:
        return auth_response(role_err)

    body = json_body()
    data, error = pago_service.resolver_garantia(reserva_id, body)
    if error == "not_found":
        return jsonify({"error": "Reserva no encontrada"}), 404
    if error:
        return jsonify({"error": error}), 400
    return jsonify(data)


@bp.get("/api/reservas/<int:reserva_id>/invitados")
def invitados(reserva_id):
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Propietario", "Administrador")
    if role_err:
        return auth_response(role_err)
    propietario_id = payload.get("propietario_id") if payload.get("tipo") == "Propietario" else None
    data, error = reserva_service.invitados_de_reserva(reserva_id, propietario_id)
    if error == "not_found":
        return jsonify({"error": "Reserva no encontrada"}), 404
    if error == "forbidden":
        return jsonify({"error": "No autorizado"}), 403
    return jsonify(data)
