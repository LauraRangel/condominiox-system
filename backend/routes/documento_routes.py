import io

from flask import Blueprint, jsonify, request, send_file

from middleware import get_payload, require_roles, auth_response, json_body
from services import documento_service

bp = Blueprint("documentos", __name__)


def _es_admin(payload):
    return payload.get("tipo") == "Administrador"


@bp.get("/api/documentos")
def listar():
    payload, err = get_payload()
    if err:
        return auth_response(err)
    return jsonify(documento_service.listar(_es_admin(payload)))


@bp.post("/api/documentos")
def subir():
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Administrador")
    if role_err:
        return auth_response(role_err)
    f = request.form
    data, error = documento_service.subir(
        request.files.get("archivo"), f.get("titulo"), f.get("categoria"), f.get("descripcion"),
        f.get("publico", "true").lower() in ("1", "true", "si", "sí", "on"), payload.get("usuario"),
    )
    if error:
        return jsonify({"error": error}), 400
    return jsonify(data), 201


@bp.get("/api/documentos/<int:documento_id>/archivo")
def descargar(documento_id):
    payload, err = get_payload()
    if err:
        return auth_response(err)
    row = documento_service.archivo(documento_id, _es_admin(payload))
    if not row:
        return jsonify({"error": "Documento no encontrado"}), 404
    resp = send_file(io.BytesIO(bytes(row["contenido"])), mimetype="application/pdf",
                     download_name=row["nombre_archivo"],
                     as_attachment=request.args.get("descargar") == "1")
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Cache-Control"] = "private, no-store"
    return resp


@bp.put("/api/documentos/<int:documento_id>")
def actualizar(documento_id):
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Administrador")
    if role_err:
        return auth_response(role_err)
    data, error = documento_service.actualizar(documento_id, json_body())
    if error == "not_found":
        return jsonify({"error": "Documento no encontrado"}), 404
    if error:
        return jsonify({"error": error}), 400
    return jsonify(data)


@bp.delete("/api/documentos/<int:documento_id>")
def eliminar(documento_id):
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Administrador")
    if role_err:
        return auth_response(role_err)
    if not documento_service.eliminar(documento_id):
        return jsonify({"error": "Documento no encontrado"}), 404
    return jsonify({"deleted": documento_id})


@bp.get("/api/reglamento")
def reglamento():
    payload, err = get_payload()
    if err:
        return auth_response(err)
    return jsonify(documento_service.reglamento())
