from dao import anuncio_dao
from utils.logger import get_logger

log = get_logger(__name__)

TIPOS_VALIDOS = ("mantenimiento", "pago", "informativo")


def _serializar(row: dict) -> dict:
    row["fecha_publicacion"] = row["fecha_publicacion"].isoformat() if row.get("fecha_publicacion") else None
    row["fecha_caducidad"] = row["fecha_caducidad"].isoformat() if row.get("fecha_caducidad") else None
    return row


def listar_anuncios() -> dict:
    rows = anuncio_dao.get_all_anuncios()
    return {"items": [_serializar(row) for row in rows]}


def listar_comunicados(propietario_id) -> dict:
    rows = anuncio_dao.get_anuncios_con_lectura(propietario_id)
    return {"items": [_serializar(row) for row in rows]}


def crear_anuncio(titulo: str, contenido: str, tipo: str, fecha_caducidad=None):
    if not titulo or not contenido or not tipo:
        return None, "Datos incompletos"
    if tipo not in TIPOS_VALIDOS:
        return None, f"Tipo inválido. Use: {', '.join(TIPOS_VALIDOS)}"
    row = anuncio_dao.create_anuncio(titulo.strip(), contenido.strip(), tipo, fecha_caducidad or None)
    if row:
        _serializar(row)
    log.info("Anuncio creado", extra={"tipo": tipo})
    return row, None


def eliminar_anuncio(anuncio_id):
    return anuncio_dao.delete_anuncio(anuncio_id)


def marcar_leido(anuncio_id, propietario_id):
    anuncio_dao.marcar_leido(anuncio_id, propietario_id)
    return True
