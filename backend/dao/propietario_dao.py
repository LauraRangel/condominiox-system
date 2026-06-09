from db import fetch_all, fetch_one, execute, execute_returning, get_db


def get_all_propietarios():
    return fetch_all(
        """
        SELECT p.id, p.usuario_id, u.usuario, p.nombre, p.apellido, p.dni, p.correo,
               p.telefono, p.nro_departamento, p.torre
        FROM propietarios p
        LEFT JOIN usuarios u ON u.id = p.usuario_id
        ORDER BY p.id
        """
    )


def get_propietario_por_id(propietario_id):
    return fetch_one(
        """
        SELECT p.id, p.usuario_id, u.usuario, p.nombre, p.apellido, p.dni, p.correo,
               p.telefono, p.nro_departamento, p.torre
        FROM propietarios p
        LEFT JOIN usuarios u ON u.id = p.usuario_id
        WHERE p.id = %s
        """,
        [propietario_id],
    )


def get_propietario_por_dni(dni: str):
    return fetch_one("SELECT id FROM propietarios WHERE dni = %s", [dni])


def usuario_existe(usuario: str):
    return fetch_one("SELECT id FROM usuarios WHERE usuario = %s", [usuario])


def dni_existe_excluyendo(dni: str, propietario_id):
    return fetch_one(
        "SELECT id FROM propietarios WHERE dni = %s AND id != %s",
        [dni, propietario_id],
    )


def usuario_existe_excluyendo(usuario: str, propietario_id):
    return fetch_one(
        """
        SELECT u.id FROM usuarios u
        JOIN propietarios p ON p.usuario_id = u.id
        WHERE u.usuario = %s AND p.id != %s
        """,
        [usuario, propietario_id],
    )


def create_propietario(usuario, nombre, apellido, dni, correo, telefono,
                       nro_departamento, torre, password_hash):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO usuarios (usuario, password_hash, tipo)
                VALUES (%s, %s, 'Propietario')
                RETURNING id
                """,
                [usuario, password_hash],
            )
            usuario_id = cur.fetchone()["id"]
            cur.execute(
                """
                INSERT INTO propietarios
                    (usuario_id, nombre, apellido, dni, correo, telefono, nro_departamento, torre)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, nombre, apellido, dni, correo, telefono, nro_departamento, torre
                """,
                [usuario_id, nombre, apellido, dni, correo, telefono, nro_departamento, torre],
            )
            row = cur.fetchone()
        conn.commit()
    row["usuario_id"] = usuario_id
    row["usuario"] = usuario
    return row


def update_propietario(propietario_id, usuario, nombre, apellido, dni,
                       correo, telefono, nro_departamento, torre):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT usuario_id FROM propietarios WHERE id = %s
                """,
                [propietario_id],
            )
            prop = cur.fetchone()
            if not prop:
                return None
            cur.execute(
                "UPDATE usuarios SET usuario = %s WHERE id = %s",
                [usuario, prop["usuario_id"]],
            )
            cur.execute(
                """
                UPDATE propietarios
                SET nombre = %s, apellido = %s, dni = %s,
                    correo = %s, telefono = %s,
                    nro_departamento = %s, torre = %s
                WHERE id = %s
                RETURNING id, nombre, apellido, dni, correo, telefono, nro_departamento, torre
                """,
                [nombre, apellido, dni, correo, telefono, nro_departamento, torre, propietario_id],
            )
            row = cur.fetchone()
        conn.commit()
    return row


def delete_propietario(propietario_id):
    return execute_returning(
        "DELETE FROM propietarios WHERE id = %s RETURNING id",
        [propietario_id],
    )


def update_perfil_propietario(propietario_id, correo, telefono):
    return execute_returning(
        """
        UPDATE propietarios SET correo = %s, telefono = %s
        WHERE id = %s RETURNING id, correo, telefono
        """,
        [correo, telefono, propietario_id],
    )
