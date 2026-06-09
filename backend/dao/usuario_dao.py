from db import fetch_one, execute


def get_usuario_para_auth(usuario: str):
    return fetch_one(
        """
        SELECT u.id, u.usuario, u.password_hash, u.tipo, u.activo,
               p.id AS propietario_id, p.nombre, p.apellido, p.dni,
               p.correo, p.telefono, p.nro_departamento, p.torre
        FROM usuarios u
        LEFT JOIN propietarios p ON p.usuario_id = u.id
        WHERE u.usuario = %s
        """,
        [usuario],
    )


def get_usuario_por_id(usuario_id):
    return fetch_one(
        """
        SELECT u.id, u.usuario, u.tipo,
               p.id AS propietario_id, p.nombre, p.apellido, p.dni,
               p.correo, p.telefono, p.nro_departamento, p.torre
        FROM usuarios u
        LEFT JOIN propietarios p ON p.usuario_id = u.id
        WHERE u.id = %s
        """,
        [usuario_id],
    )


def get_usuario_con_dni(usuario: str):
    return fetch_one(
        """
        SELECT u.id, p.dni
        FROM usuarios u
        LEFT JOIN propietarios p ON p.usuario_id = u.id
        WHERE u.usuario = %s
        """,
        [usuario],
    )


def update_password(usuario_id, password_hash: str):
    execute(
        "UPDATE usuarios SET password_hash = %s WHERE id = %s",
        [password_hash, usuario_id],
    )
