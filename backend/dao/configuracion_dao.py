from db import fetch_one, execute_returning


def get_ultima_configuracion():
    return fetch_one(
        "SELECT monto_administracion FROM configuracion ORDER BY id DESC LIMIT 1"
    )


def create_configuracion(monto):
    return execute_returning(
        "INSERT INTO configuracion (monto_administracion) VALUES (%s) RETURNING monto_administracion",
        [monto],
    )
