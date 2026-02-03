import os
import datetime as dt
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
import jwt

from db import fetch_one
from security import verify_password

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})


def _jwt_secret():
    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise RuntimeError("JWT_SECRET no está configurado")
    return secret


def _jwt_issuer():
    return os.getenv("JWT_ISSUER", "condominiox")


def _jwt_exp_seconds():
    try:
        return int(os.getenv("JWT_EXPIRES_SECONDS", "3600"))
    except ValueError:
        return 3600


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/api/login")
def login():
    body = request.get_json(silent=True) or {}
    usuario = (body.get("usuario") or "").strip()
    contrasena = body.get("contrasena") or ""
    tipo = (body.get("tipo") or "").strip()

    if not usuario or not contrasena or not tipo:
        return jsonify({"error": "Datos incompletos"}), 400

    user = fetch_one(
        """
        SELECT id, usuario, password_hash, tipo, activo
        FROM usuarios
        WHERE usuario = %s
        """,
        [usuario],
    )

    if not user or not user["activo"]:
        return jsonify({"error": "Usuario o contraseña inválidos"}), 401

    if user["tipo"] != tipo:
        return jsonify({"error": f"Este usuario es {user['tipo']}, no {tipo}"}), 403

    if not verify_password(user["password_hash"], contrasena):
        return jsonify({"error": "Usuario o contraseña inválidos"}), 401

    now = dt.datetime.utcnow()
    payload = {
        "sub": str(user["id"]),
        "usuario": user["usuario"],
        "tipo": user["tipo"],
        "iss": _jwt_issuer(),
        "iat": int(now.timestamp()),
        "exp": int((now + dt.timedelta(seconds=_jwt_exp_seconds())).timestamp()),
    }
    token = jwt.encode(payload, _jwt_secret(), algorithm="HS256")

    return jsonify(
        {
            "token": token,
            "user": {
                "id": user["id"],
                "usuario": user["usuario"],
                "tipo": user["tipo"],
            },
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
