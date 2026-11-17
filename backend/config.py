import os


def jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise RuntimeError("JWT_SECRET no está configurado")
    if len(secret) < 32:
        import warnings
        warnings.warn("JWT_SECRET tiene menos de 32 caracteres: use uno largo y aleatorio en producción")
    return secret


def jwt_issuer() -> str:
    return os.getenv("JWT_ISSUER", "condominiox")


def jwt_exp_seconds() -> int:
    try:
        return int(os.getenv("JWT_EXPIRES_SECONDS", "3600"))
    except ValueError:
        return 3600
