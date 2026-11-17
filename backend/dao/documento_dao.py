from db import fetch_all, fetch_one, execute_returning, get_db

_META = """
    id, titulo, categoria, descripcion, nombre_archivo, tamano_bytes, paginas,
    publico, tiene_texto, subido_por, creado_en, actualizado_en
"""


def crear_documento(titulo, categoria, descripcion, nombre_archivo, contenido, paginas,
                    publico, tiene_texto, subido_por, fragmentos):
    """Inserta el documento y sus fragmentos de texto en una sola transacción."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO documentos (titulo, categoria, descripcion, nombre_archivo, tamano_bytes,
                                        paginas, contenido, publico, tiene_texto, subido_por)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING {_META}
                """,
                [titulo, categoria, descripcion, nombre_archivo, len(contenido), paginas,
                 contenido, publico, tiene_texto, subido_por],
            )
            doc = cur.fetchone()
            for pagina, texto in fragmentos:
                cur.execute(
                    "INSERT INTO documento_fragmentos (documento_id, pagina, texto) VALUES (%s, %s, %s)",
                    [doc["id"], pagina, texto],
                )
        conn.commit()
    return doc


def listar(solo_publicos):
    where = "WHERE publico = TRUE" if solo_publicos else ""
    return fetch_all(f"SELECT {_META} FROM documentos {where} ORDER BY creado_en DESC, id DESC")


def get_meta(documento_id):
    return fetch_one(f"SELECT {_META} FROM documentos WHERE id = %s", [documento_id])


def get_archivo(documento_id):
    return fetch_one(
        "SELECT id, nombre_archivo, contenido, publico FROM documentos WHERE id = %s", [documento_id]
    )


def actualizar(documento_id, titulo, categoria, descripcion, publico):
    return execute_returning(
        f"""
        UPDATE documentos SET titulo = %s, categoria = %s, descripcion = %s, publico = %s,
                              actualizado_en = NOW()
        WHERE id = %s RETURNING {_META}
        """,
        [titulo, categoria, descripcion, publico, documento_id],
    )


def eliminar(documento_id):
    return execute_returning("DELETE FROM documentos WHERE id = %s RETURNING id", [documento_id])


def firma_publicos():
    """Cambia cuando se sube, edita o elimina un documento público (para reindexar el asistente)."""
    row = fetch_one(
        "SELECT COUNT(*) AS n, COALESCE(MAX(id), 0) AS max_id, MAX(actualizado_en) AS ult "
        "FROM documentos WHERE publico = TRUE"
    )
    return (row["n"], row["max_id"], str(row["ult"])) if row else (0, 0, "")


def fragmentos_publicos():
    return fetch_all(
        """
        SELECT f.documento_id, d.titulo, f.pagina, f.texto
        FROM documento_fragmentos f JOIN documentos d ON d.id = f.documento_id
        WHERE d.publico = TRUE
        ORDER BY f.documento_id, f.pagina, f.id
        """
    )
