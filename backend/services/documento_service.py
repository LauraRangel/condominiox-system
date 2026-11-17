"""Documentos del condominio: solo PDF, guardados en PostgreSQL (BYTEA).

Al subir un PDF se valida, se extrae su texto por página con pypdf y se parte en
fragmentos que el asistente con IA usa como fuente (RAG), igual que el reglamento.
"""

import io
import json
import os
import re

from dao import documento_dao
from utils.logger import get_logger

log = get_logger(__name__)

MAX_BYTES = 5 * 1024 * 1024
CATEGORIAS = {"reglamento": "Reglamento", "acta": "Acta de junta", "manual": "Manual de uso",
              "presupuesto": "Presupuesto", "otro": "Otro"}
TAM_FRAGMENTO = 800


class PdfProtegido(ValueError):
    """El PDF está cifrado: se informa al usuario con un mensaje propio."""


_RUTA_REGLAMENTO = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "reglamento.json")


def extraer_texto_pdf(contenido: bytes) -> tuple[int, list]:
    """Devuelve (número de páginas, [(página, fragmento), ...]). Lanza ValueError si el PDF no es válido."""
    from pypdf import PdfReader
    from pypdf.errors import PdfReadError

    try:
        lector = PdfReader(io.BytesIO(contenido))
        if lector.is_encrypted:
            raise PdfProtegido("El PDF está protegido con contraseña")
        paginas = len(lector.pages)
        fragmentos = []
        for n, pagina in enumerate(lector.pages, start=1):
            texto = re.sub(r"[ \t]+", " ", pagina.extract_text() or "").strip()
            fragmentos.extend((n, f) for f in partir_texto(texto))
    except (PdfReadError, KeyError, TypeError, AttributeError) as e:
        raise ValueError("El archivo no es un PDF válido") from e
    return paginas, fragmentos


def partir_texto(texto: str, tamano: int = TAM_FRAGMENTO) -> list:
    """Parte el texto en fragmentos de ~tamano caracteres sin cortar oraciones."""
    oraciones = re.split(r"(?<=[.!?:;])\s+|\n+", texto)
    fragmentos, actual = [], ""
    for oracion in (o.strip() for o in oraciones):
        if not oracion:
            continue
        if actual and len(actual) + len(oracion) + 1 > tamano:
            fragmentos.append(actual)
            actual = oracion
        else:
            actual = f"{actual} {oracion}".strip()
    if actual:
        fragmentos.append(actual)
    return [f for f in fragmentos if len(f) >= 20]


def _meta_json(d) -> dict:
    return {
        "id": d["id"],
        "titulo": d["titulo"],
        "categoria": d["categoria"],
        "categoria_label": CATEGORIAS.get(d["categoria"], d["categoria"]),
        "descripcion": d.get("descripcion"),
        "nombre_archivo": d["nombre_archivo"],
        "tamano_kb": round(d["tamano_bytes"] / 1024, 1),
        "paginas": d["paginas"],
        "publico": d["publico"],
        "tiene_texto": d["tiene_texto"],
        "subido_por": d.get("subido_por"),
        "fecha": d["creado_en"].isoformat(timespec="seconds"),
    }


def _validar_meta(titulo, categoria, descripcion):
    titulo = " ".join(str(titulo or "").split())
    if not 3 <= len(titulo) <= 150:
        return None, "El título debe tener entre 3 y 150 caracteres"
    if categoria not in CATEGORIAS:
        return None, "Categoría inválida"
    return (titulo, categoria, (str(descripcion or "").strip()[:300] or None)), None


def subir(archivo, titulo, categoria, descripcion, publico, usuario):
    if archivo is None or not archivo.filename:
        return None, "Seleccione un archivo PDF"
    nombre = os.path.basename(archivo.filename)[:200]
    if not nombre.lower().endswith(".pdf"):
        return None, "Solo se aceptan archivos PDF"
    contenido = archivo.read(MAX_BYTES + 1)
    if len(contenido) > MAX_BYTES:
        return None, "El archivo supera el máximo de 5 MB"
    if not contenido.startswith(b"%PDF-"):
        return None, "El archivo no es un PDF válido"   # se revisa el contenido, no solo la extensión
    meta, err = _validar_meta(titulo, categoria, descripcion)
    if err:
        return None, err
    try:
        paginas, fragmentos = extraer_texto_pdf(contenido)
    except PdfProtegido:
        return None, "El PDF está protegido con contraseña"
    except ValueError:
        # Cualquier otro error del lector (incluidos los internos de pypdf) se registra
        # en el log y al cliente solo le llega un mensaje genérico
        log.warning("PDF rechazado al extraer texto", exc_info=True)
        return None, "El archivo no es un PDF válido"

    doc = documento_dao.crear_documento(*meta, nombre, contenido, paginas, bool(publico),
                                        bool(fragmentos), usuario, fragmentos)
    log.info("Documento subido", extra={"documento_id": doc["id"], "paginas": paginas,
                                        "fragmentos": len(fragmentos)})
    data = _meta_json(doc)
    if not fragmentos:
        data["aviso"] = ("El PDF no tiene texto seleccionable (parece escaneado): se puede ver y descargar, "
                         "pero el asistente no podrá leerlo")
    return data, None


def listar(es_admin: bool):
    return {"items": [_meta_json(d) for d in documento_dao.listar(solo_publicos=not es_admin)],
            "categorias": CATEGORIAS}


def archivo(documento_id, es_admin: bool):
    row = documento_dao.get_archivo(documento_id)
    if not row or (not es_admin and not row["publico"]):
        return None
    return row


def actualizar(documento_id, body: dict):
    if not documento_dao.get_meta(documento_id):
        return None, "not_found"
    meta, err = _validar_meta(body.get("titulo"), body.get("categoria"), body.get("descripcion"))
    if err:
        return None, err
    publico = body.get("publico", True)
    publico = publico if isinstance(publico, bool) else str(publico).lower() in ("1", "true", "si", "sí")
    return _meta_json(documento_dao.actualizar(documento_id, *meta, publico)), None


def eliminar(documento_id):
    return documento_dao.eliminar(documento_id)


def reglamento():
    with open(_RUTA_REGLAMENTO, encoding="utf-8") as f:
        data = json.load(f)
    return {"titulo": data.get("titulo"), "nota": data.get("nota"),
            "articulos": [{"numero": a["numero"], "titulo": a["titulo"], "contenido": a["contenido"]}
                          for a in data["articulos"]]}
