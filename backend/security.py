import base64
import hashlib
import hmac
import secrets


def hash_password(password, iterations=260000):
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    salt_b64 = base64.b64encode(salt).decode("utf-8")
    dk_b64 = base64.b64encode(dk).decode("utf-8")
    return f"pbkdf2_sha256${iterations}${salt_b64}${dk_b64}"


def verify_password(stored_hash, password):
    try:
        method, iter_str, salt_b64, dk_b64 = stored_hash.split("$", 3)
        if method != "pbkdf2_sha256":
            return False
        iterations = int(iter_str)
        salt = base64.b64decode(salt_b64.encode("utf-8"))
        expected = base64.b64decode(dk_b64.encode("utf-8"))
    except Exception:
        return False

    candidate = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, iterations
    )
    return hmac.compare_digest(candidate, expected)
