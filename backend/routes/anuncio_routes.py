from flask import Blueprint, jsonify, request

from middleware import get_payload, require_roles, auth_response
from services import anuncio_service

bp = Blueprint("anuncios", __name__)


@bp.get("/api/anuncios")
def listar_anuncios():
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Administrador")
    if role_err:
        return auth_response(role_err)
    return jsonify(anuncio_service.listar_anuncios())


@bp.post("/api/anuncios")
def crear_anuncio():
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Administrador")
    if role_err:
        return auth_response(role_err)

    body = request.get_json(silent=True) or {}
    row, err = anuncio_service.crear_anuncio(
        body.get("titulo"), body.get("contenido"), body.get("tipo")
    )
    if err:
        return jsonify({"error": err}), 400
    return jsonify(row), 201


@bp.delete("/api/anuncios/<int:anuncio_id>")
def eliminar_anuncio(anuncio_id):
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Administrador")
    if role_err:
        return auth_response(role_err)

    row = anuncio_service.eliminar_anuncio(anuncio_id)
    if not row:
        return jsonify({"error": "Anuncio no encontrado"}), 404
    return jsonify({"deleted": anuncio_id})


@bp.get("/api/comunicados")
def listar_comunicados():
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Propietario")
    if role_err:
        return auth_response(role_err)

    propietario_id = payload.get("propietario_id")
    if not propietario_id:
        return jsonify({"error": "Propietario no encontrado"}), 404
    return jsonify(anuncio_service.listar_comunicados(propietario_id))


@bp.post("/api/comunicados/<int:anuncio_id>/leer")
def marcar_leido(anuncio_id):
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Propietario")
    if role_err:
        return auth_response(role_err)

    propietario_id = payload.get("propietario_id")
    if not propietario_id:
        return jsonify({"error": "Propietario no encontrado"}), 404
    anuncio_service.marcar_leido(anuncio_id, propietario_id)
    return jsonify({"ok": True})
