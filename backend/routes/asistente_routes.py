from flask import Blueprint, jsonify

from middleware import get_payload, require_roles, auth_response, json_body
from services import asistente_service

bp = Blueprint("asistente", __name__)


@bp.post("/api/asistente/consulta")
def consultar():
    payload, err = get_payload()
    if err:
        return auth_response(err)
    role_err = require_roles(payload, "Propietario")
    if role_err:
        return auth_response(role_err)

    body = json_body()
    # El propietario_id sale del token, nunca del body: el asistente solo ve los datos de quien pregunta
    data, error = asistente_service.consultar(payload.get("propietario_id"), body.get("pregunta"))
    if error == "rate_limit":
        return jsonify({"error": "Demasiadas consultas seguidas. Espere un minuto."}), 429
    if error:
        return jsonify({"error": error}), 400
    return jsonify(data)

