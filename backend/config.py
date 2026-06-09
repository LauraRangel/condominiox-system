import os


def jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise RuntimeError("JWT_SECRET no está configurado")
    return secret


def jwt_issuer() -> str:
    return os.getenv("JWT_ISSUER", "condominiox")


def jwt_exp_seconds() -> int:
    try:
        return int(os.getenv("JWT_EXPIRES_SECONDS", "3600"))
    except ValueError:
        return 3600
