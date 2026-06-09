from db import fetch_all, fetch_one, execute_returning, execute


def get_all_anuncios():
    return fetch_all(
        """
        SELECT id, titulo, contenido, tipo, fecha_publicacion, activo
        FROM anuncios
        WHERE activo = TRUE
        ORDER BY fecha_publicacion DESC, id DESC
        """
    )


def get_anuncios_con_lectura(propietario_id):
    return fetch_all(
        """
        SELECT a.id, a.titulo, a.contenido, a.tipo, a.fecha_publicacion,
               CASE WHEN la.id IS NOT NULL THEN TRUE ELSE FALSE END AS leido
        FROM anuncios a
        LEFT JOIN lecturas_anuncios la
            ON la.anuncio_id = a.id AND la.propietario_id = %s
        WHERE a.activo = TRUE
        ORDER BY a.fecha_publicacion DESC, a.id DESC
        """,
        [propietario_id],
    )


def create_anuncio(titulo: str, contenido: str, tipo: str):
    return execute_returning(
        """
        INSERT INTO anuncios (titulo, contenido, tipo)
        VALUES (%s, %s, %s)
        RETURNING id, titulo, contenido, tipo, fecha_publicacion, activo
        """,
        [titulo, contenido, tipo],
    )


def delete_anuncio(anuncio_id):
    return execute_returning(
        "UPDATE anuncios SET activo = FALSE WHERE id = %s AND activo = TRUE RETURNING id",
        [anuncio_id],
    )


def marcar_leido(anuncio_id, propietario_id):
    execute(
        """
        INSERT INTO lecturas_anuncios (anuncio_id, propietario_id)
        VALUES (%s, %s)
        ON CONFLICT (anuncio_id, propietario_id) DO NOTHING
        """,
        [anuncio_id, propietario_id],
    )
