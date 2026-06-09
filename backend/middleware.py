import jwt as pyjwt
from flask import request, jsonify

import config


def get_payload():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None, ("Token requerido", 401)
    token = auth.split(" ", 1)[1].strip()
    try:
        payload = pyjwt.decode(
            token,
            config.jwt_secret(),
            algorithms=["HS256"],
            issuer=config.jwt_issuer(),
        )
        return payload, None
    except pyjwt.ExpiredSignatureError:
        return None, ("Token expirado", 401)
    except pyjwt.InvalidTokenError:
        return None, ("Token inválido", 401)


def require_roles(payload, *roles):
    if not roles:
        return None
    if payload.get("tipo") not in roles:
        return ("No autorizado", 403)
    return None


def auth_response(err):
    return jsonify({"error": err[0]}), err[1]
