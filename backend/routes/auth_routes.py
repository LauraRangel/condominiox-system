from flask import Blueprint, jsonify, request

from middleware import get_payload, auth_response
from services import auth_service

bp = Blueprint("auth", __name__)


@bp.post("/api/login")
def login():
    body = request.get_json(silent=True) or {}
    usuario = (body.get("usuario") or "").strip()
    contrasena = body.get("contrasena") or ""
    tipo = (body.get("tipo") or "").strip()

    if not usuario or not contrasena or not tipo:
        return jsonify({"error": "Datos incompletos"}), 400

    user, err = auth_service.autenticar(usuario, contrasena, tipo)
    if err:
        code = 403 if "tipo" in err else 401
        return jsonify({"error": err}), code

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
    return jsonify({"token": token, "user": user_data})


@bp.post("/api/recuperar-contrasena")
def recuperar_contrasena():
    body = request.get_json(silent=True) or {}
    usuario = (body.get("usuario") or "").strip()
    dni = (body.get("dni") or "").strip()
    nueva = body.get("nueva_contrasena") or ""

    if not usuario or not dni or not nueva:
        return jsonify({"error": "Datos incompletos"}), 400
    if len(nueva) < 6:
        return jsonify({"error": "La nueva contraseña debe tener al menos 6 caracteres"}), 400

    ok, err = auth_service.recuperar_contrasena(usuario, dni, nueva)
    if err:
        code = 404 if "no encontrado" in err.lower() else 403
        return jsonify({"error": err}), code
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

    body = request.get_json(silent=True) or {}
    correo = (body.get("correo") or "").strip() or None
    telefono = (body.get("telefono") or "").strip() or None
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

    body = request.get_json(silent=True) or {}
    actual = body.get("actual_contrasena") or ""
    nueva = body.get("nueva_contrasena") or ""
    if not actual or not nueva:
        return jsonify({"error": "Datos incompletos"}), 400
    if len(nueva) < 6:
        return jsonify({"error": "La nueva contraseña debe tener al menos 6 caracteres"}), 400

    ok, err = auth_service.cambiar_contrasena(payload.get("sub"), actual, nueva)
    if err:
        code = 404 if "no encontrado" in err.lower() else 403
        return jsonify({"error": err}), code
    return jsonify({"ok": True})
