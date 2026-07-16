import jwt as pyjwt
from flask import request, jsonify, g

import config
from utils.logger import get_logger

_sec_log = get_logger("security")


def _ip():
    return request.headers.get("X-Forwarded-For", request.remote_addr or "unknown").split(",")[0].strip()


def _request_id():
    return g.get("request_id", "-")


def get_payload():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        _sec_log.warning("Acceso sin token", extra={
            "event": "missing_token",
            "request_id": _request_id(),
            "ip": _ip(),
            "path": request.path,
            "method": request.method,
        })
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
        _sec_log.warning("Token expirado", extra={
            "event": "expired_token",
            "request_id": _request_id(),
            "ip": _ip(),
            "path": request.path,
        })
        return None, ("Token expirado", 401)
    except pyjwt.InvalidTokenError:
        _sec_log.warning("Token inválido", extra={
            "event": "invalid_token",
            "request_id": _request_id(),
            "ip": _ip(),
            "path": request.path,
        })
        return None, ("Token inválido", 401)


def require_roles(payload, *roles):
    if not roles:
        return None
    if payload.get("tipo") not in roles:
        _sec_log.warning("Acceso denegado por rol", extra={
            "event": "forbidden_role",
            "request_id": _request_id(),
            "ip": _ip(),
            "path": request.path,
            "method": request.method,
            "user": payload.get("usuario"),
            "rol_actual": payload.get("tipo"),
            "rol_requerido": list(roles),
        })
        return ("No autorizado", 403)
    return None


def auth_response(err):
    return jsonify({"error": err[0]}), err[1]
