from flask import Blueprint, jsonify, request

from middleware import get_payload, auth_response, json_body
from services import auth_service
from utils.validacion import LimitadorIntentos, validar_contrasena, validar_telefono
from utils.logger import get_logger

_sec_log = get_logger("security")
# 5 fallos en 15 minutos por IP+usuario bloquean el login; 5 por hora bloquean la recuperación
limitador_login = LimitadorIntentos(maximo=5, ventana_seg=15 * 60)
limitador_recuperar = LimitadorIntentos(maximo=5, ventana_seg=60 * 60)


def _ip():
    return request.headers.get("X-Forwarded-For", request.remote_addr or "?").split(",")[0].strip()


def _bloqueo(limitador, clave):
    espera = limitador.bloqueado(clave)
    if espera:
        _sec_log.warning("Demasiados intentos", extra={"event": "rate_limited", "ip": clave[0],
                                                       "usuario": clave[1], "path": request.path})
        resp = jsonify({"error": f"Demasiados intentos. Intente de nuevo en {max(espera // 60, 1)} minuto(s)."})
        resp.headers["Retry-After"] = str(espera)
        return resp, 429
    return None

bp = Blueprint("auth", __name__)


@bp.post("/api/login")
def login():
    body = json_body()
    usuario = (body.get("usuario") or "").strip()
    contrasena = body.get("contrasena") or ""
    tipo = (body.get("tipo") or "").strip()

    if not usuario or not contrasena or not tipo:
        return jsonify({"error": "Datos incompletos"}), 400

    clave = (_ip(), usuario.lower())
    bloqueo = _bloqueo(limitador_login, clave)
    if bloqueo:
        return bloqueo

    user, err = auth_service.autenticar(usuario, contrasena, tipo)
    if err:
        limitador_login.registrar_fallo(clave)
        code = 403 if "tipo" in err else 401
        return jsonify({"error": err}), code
    limitador_login.reiniciar(clave)

    token = auth_service.generar_token(user)
    user_data = {"id": user["id"], "usuario": user["usuario"], "tipo": user["tipo"]}
    if user.get("propietario_id"):
        user_data["propietario_id"] = user["propietario_id"]
        user_data["perfil"] = {
            "nombre": user["nombre"],
            "apellido": user["apellido"],
            "dni": user["dni"],
            "correo": user["correo"],
            "telefono": user["telefono"],
            "nro_departamento": user["nro_departamento"],
            "torre": user["torre"],
        }
    # La contraseña inicial del propietario es su DNI: se le pide cambiarla
    debe_cambiar = bool(user.get("dni")) and contrasena == user.get("dni")
    user_data["debe_cambiar_contrasena"] = debe_cambiar
    return jsonify({"token": token, "user": user_data})


@bp.post("/api/recuperar-contrasena")
def recuperar_contrasena():
    body = json_body()
    usuario = (body.get("usuario") or "").strip()
    dni = (body.get("dni") or "").strip()
    nueva = body.get("nueva_contrasena") or ""

    if not usuario or not dni or not nueva:
        return jsonify({"error": "Datos incompletos"}), 400
    error_clave = validar_contrasena(nueva)
    if error_clave:
        return jsonify({"error": error_clave}), 400
    if nueva == dni:
        return jsonify({"error": "La nueva contraseña no puede ser su DNI"}), 400

    clave = (_ip(), usuario.lower())
    bloqueo = _bloqueo(limitador_recuperar, clave)
    if bloqueo:
        return bloqueo

    ok, err = auth_service.recuperar_contrasena(usuario, dni, nueva)
    if err:
        limitador_recuperar.registrar_fallo(clave)
        _sec_log.warning("Recuperación fallida", extra={"event": "recovery_failed", "usuario": usuario, "ip": clave[0]})
        # mismo mensaje exista o no el usuario, para no revelar cuentas
        return jsonify({"error": "Los datos no coinciden con ninguna cuenta"}), 403
    limitador_recuperar.reiniciar(clave)
    return jsonify({"ok": True})


@bp.get("/api/mi-perfil")
def mi_perfil():
    payload, err = get_payload()
    if err:
        return auth_response(err)

    user = auth_service.get_perfil(payload.get("sub"))
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({
        "id": user["id"],
        "usuario": user["usuario"],
        "tipo": user["tipo"],
        "propietario_id": user.get("propietario_id"),
        "perfil": {
            "nombre": user.get("nombre"),
            "apellido": user.get("apellido"),
            "dni": user.get("dni"),
            "correo": user.get("correo"),
            "telefono": user.get("telefono"),
            "nro_departamento": user.get("nro_departamento"),
            "torre": user.get("torre"),
        },
    })


@bp.put("/api/mi-perfil")
def actualizar_mi_perfil():
    payload, err = get_payload()
    if err:
        return auth_response(err)
    if payload.get("tipo") != "Propietario":
        return jsonify({"error": "No autorizado"}), 403

    body = json_body()
    correo = (body.get("correo") or "").strip() or None
    telefono = (body.get("telefono") or "").strip() or None
    error_tel = validar_telefono(telefono)
    if error_tel:
        return jsonify({"error": error_tel}), 400
    if correo:
        import validators
        if len(correo) > 120 or not validators.email(correo):
            return jsonify({"error": "Correo inválido"}), 400
    propietario_id = payload.get("propietario_id")
    if not propietario_id:
        return jsonify({"error": "Propietario no encontrado"}), 404

    row = auth_service.actualizar_perfil(propietario_id, correo, telefono)
    if not row:
        return jsonify({"error": "Propietario no encontrado"}), 404
    return jsonify(row)


@bp.put("/api/mi-contrasena")
def cambiar_mi_contrasena():
    payload, err = get_payload()
    if err:
        return auth_response(err)

    body = json_body()
    actual = body.get("actual_contrasena") or ""
    nueva = body.get("nueva_contrasena") or ""
    if not actual or not nueva:
        return jsonify({"error": "Datos incompletos"}), 400
    error_clave = validar_contrasena(nueva)
    if error_clave:
        return jsonify({"error": error_clave}), 400
    if nueva == actual:
        return jsonify({"error": "La nueva contraseña debe ser distinta de la actual"}), 400

    ok, err = auth_service.cambiar_contrasena(payload.get("sub"), actual, nueva)
    if err:
        code = 404 if "no encontrado" in err.lower() else 403
        return jsonify({"error": err}), code
    return jsonify({"ok": True})
