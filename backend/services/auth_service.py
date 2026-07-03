import datetime as dt

import jwt

import config
from dao import usuario_dao
from security import verify_password, hash_password
from utils.logger import get_logger

log = get_logger(__name__)
_sec_log = get_logger("security")

_MSG_INVALIDO = "Usuario o contraseña inválidos"


def autenticar(usuario: str, contrasena: str, tipo: str):
    user = usuario_dao.get_usuario_para_auth(usuario)
    if not user or not user["activo"]:
        _sec_log.warning("Login fallido — usuario no existe o inactivo", extra={
            "event": "login_failed",
            "usuario": usuario,
            "tipo_solicitado": tipo,
        })
        return None, _MSG_INVALIDO
    if user["tipo"] != tipo:
        _sec_log.warning("Login fallido — rol incorrecto", extra={
            "event": "login_wrong_role",
            "usuario": usuario,
            "tipo_real": user["tipo"],
            "tipo_solicitado": tipo,
        })
        return None, _MSG_INVALIDO
    if not verify_password(user["password_hash"], contrasena):
        _sec_log.warning("Login fallido — contraseña incorrecta", extra={
            "event": "login_bad_password",
            "usuario": usuario,
            "tipo": tipo,
        })
        return None, _MSG_INVALIDO
    log.info("Login exitoso", extra={"usuario": usuario, "tipo": tipo})
    return user, None


def generar_token(user: dict) -> str:
    now = dt.datetime.now(dt.timezone.utc)
    payload = {
        "sub": str(user["id"]),
        "usuario": user["usuario"],
        "tipo": user["tipo"],
        "iss": config.jwt_issuer(),
        "iat": int(now.timestamp()),
        "exp": int((now + dt.timedelta(seconds=config.jwt_exp_seconds())).timestamp()),
    }
    if user.get("propietario_id"):
        payload["propietario_id"] = user["propietario_id"]
    return jwt.encode(payload, config.jwt_secret(), algorithm="HS256")


def decodificar_token(token: str):
    return jwt.decode(
        token,
        config.jwt_secret(),
        algorithms=["HS256"],
        issuer=config.jwt_issuer(),
    )


def get_perfil(usuario_id) -> dict | None:
    return usuario_dao.get_usuario_por_id(usuario_id)


def actualizar_perfil(propietario_id, correo, telefono):
    from dao import propietario_dao
    return propietario_dao.update_perfil_propietario(propietario_id, correo, telefono)


def recuperar_contrasena(usuario: str, dni: str, nueva: str):
    user = usuario_dao.get_usuario_con_dni(usuario)
    if not user:
        return None, "Usuario no encontrado"
    if (user.get("dni") or "") != dni:
        return None, "Verificación inválida"
    usuario_dao.update_password(user["id"], hash_password(nueva))
    return True, None


def cambiar_contrasena(usuario_id, actual: str, nueva: str):
    user = usuario_dao.get_usuario_por_id(usuario_id)
    # get_usuario_por_id no trae password_hash; necesitamos fetch directo
    from db import fetch_one
    row = fetch_one("SELECT id, password_hash FROM usuarios WHERE id = %s", [usuario_id])
    if not row:
        return None, "Usuario no encontrado"
    if not verify_password(row["password_hash"], actual):
        return None, "Contraseña actual incorrecta"
    usuario_dao.update_password(usuario_id, hash_password(nueva))
    return True, None
