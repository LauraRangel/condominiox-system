from dao import anuncio_dao
from utils.logger import get_logger

log = get_logger(__name__)

TIPOS_VALIDOS = ("mantenimiento", "pago", "informativo")


def listar_anuncios() -> dict:
    rows = anuncio_dao.get_all_anuncios()
    items = []
    for row in rows:
        row["fecha_publicacion"] = row["fecha_publicacion"].isoformat() if row.get("fecha_publicacion") else None
        items.append(row)
    return {"items": items}


def listar_comunicados(propietario_id) -> dict:
    rows = anuncio_dao.get_anuncios_con_lectura(propietario_id)
    items = []
    for row in rows:
        row["fecha_publicacion"] = row["fecha_publicacion"].isoformat() if row.get("fecha_publicacion") else None
        items.append(row)
    return {"items": items}


def crear_anuncio(titulo: str, contenido: str, tipo: str):
    if not titulo or not contenido or not tipo:
        return None, "Datos incompletos"
    if tipo not in TIPOS_VALIDOS:
        return None, f"Tipo inválido. Use: {', '.join(TIPOS_VALIDOS)}"
    row = anuncio_dao.create_anuncio(titulo.strip(), contenido.strip(), tipo)
    if row and row.get("fecha_publicacion"):
        row["fecha_publicacion"] = row["fecha_publicacion"].isoformat()
    log.info("Anuncio creado", extra={"tipo": tipo})
    return row, None


def eliminar_anuncio(anuncio_id):
    return anuncio_dao.delete_anuncio(anuncio_id)


def marcar_leido(anuncio_id, propietario_id):
    anuncio_dao.marcar_leido(anuncio_id, propietario_id)
    return True
