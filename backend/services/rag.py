"""Recuperación de información (RAG) implementada desde cero, sin librerías externas.

Indexa los artículos del reglamento con TF-IDF y responde las consultas por
similitud coseno. El LLM solo recibe los artículos recuperados aquí.
"""

import json
import math
import os
import re
import unicodedata
from collections import Counter

_STOPWORDS = set("""
a al algo algun alguna algunas alguno algunos ante antes como con contra cual cuales
cuando de del desde donde dos e el ella ellas ellos en entre era es esa esas ese eso esos
esta estan estas este esto estos fue fueron ha han hasta hay la las le les lo los mas me mi
mis mucho muy no nos nosotros o os otra otro para pero poco por porque puede pueden que
quien se sea ser si sin sobre son su sus tambien te tengo tiene tienen todo todos tu tus un
una uno unos y ya yo hacer hago puedo quiero saber dime decir favor hola gracias
""".split())


# Sinónimos coloquiales -> términos del reglamento (se aplican solo a la consulta)
_SINONIMOS = {
    "cuesta": "costo tarifa", "cuestan": "costo tarifa", "precio": "costo tarifa", "cobran": "costo tarifa",
    "perro": "mascota", "perros": "mascota", "gato": "mascota", "gatos": "mascota",
    "bulla": "ruido", "musica": "ruido", "fiesta": "ruido salon",
    "vence": "pago fecha plazo", "plazo": "fecha pago", "deudor": "morosidad", "debo": "morosidad",
    "atraso": "morosidad", "atrasado": "morosidad", "multa": "sancion",
    "carro": "vehiculo estacionamiento", "auto": "vehiculo estacionamiento", "cochera": "estacionamiento",
    "basura": "residuo", "parrillada": "parrilla", "bbq": "parrilla", "yape": "pago medio",
    "tarjeta": "pago medio", "privacidad": "dato personal",
    "deposito": "garantia", "devuelven": "devolucion garantia", "devolver": "devolucion garantia",
    "gym": "gimnasio", "banar": "pet shower mascota", "bano": "pet shower",
}


def expandir(texto: str) -> str:
    extra = [_SINONIMOS[t] for t in re.findall(r"[a-z0-9]+", normalizar(texto)) if t in _SINONIMOS]
    return f"{texto} {' '.join(extra)}" if extra else texto


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFD", (texto or "").lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def _stem(token: str) -> str:
    """Stemmer mínimo para español: quita plurales y algunos sufijos frecuentes."""
    for suf in ("aciones", "acion", "amientos", "amiento", "mente", "idades", "idad", "es", "s"):
        if token.endswith(suf) and len(token) - len(suf) >= 4:
            return token[: -len(suf)]
    return token


def tokenizar(texto: str) -> list:
    tokens = re.findall(r"[a-z0-9]+", normalizar(texto))
    return [_stem(t) for t in tokens if t not in _STOPWORDS and len(t) > 1]


class IndiceTfIdf:
    def __init__(self, documentos: list):
        """documentos: lista de dicts con al menos 'texto'."""
        self.documentos = documentos
        tokens_docs = [tokenizar(d["texto"]) for d in documentos]
        n = len(documentos)
        df = Counter()
        for toks in tokens_docs:
            df.update(set(toks))
        self.idf = {t: math.log((1 + n) / (1 + c)) + 1 for t, c in df.items()}
        self.vectores = [self._vectorizar(toks) for toks in tokens_docs]

    def _vectorizar(self, tokens):
        tf = Counter(tokens)
        vec = {t: (1 + math.log(c)) * self.idf.get(t, 0.0) for t, c in tf.items()}
        norma = math.sqrt(sum(v * v for v in vec.values())) or 1.0
        return {t: v / norma for t, v in vec.items()}

    def buscar(self, consulta: str, k: int = 3, umbral: float = 0.08) -> list:
        q = self._vectorizar(tokenizar(expandir(consulta)))
        if not q:
            return []
        puntajes = []
        for i, vec in enumerate(self.vectores):
            s = sum(peso * vec.get(t, 0.0) for t, peso in q.items())
            if s >= umbral:
                puntajes.append((s, i))
        puntajes.sort(reverse=True)
        return [dict(self.documentos[i], puntaje=round(s, 3)) for s, i in puntajes[:k]]


_RUTA_REGLAMENTO = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "reglamento.json")
_indice = None
_reglamento_titulo = ""


def indice_reglamento() -> IndiceTfIdf:
    global _indice, _reglamento_titulo
    if _indice is None:
        with open(_RUTA_REGLAMENTO, encoding="utf-8") as f:
            data = json.load(f)
        _reglamento_titulo = data.get("titulo", "Reglamento interno")
        docs = [
            {
                "numero": a["numero"],
                "titulo": a["titulo"],
                "contenido": a["contenido"],
                # el título pesa doble para que "mascotas" encuentre el artículo de mascotas
                "texto": f"{a['titulo']} {a['titulo']} {a['contenido']}",
            }
            for a in data["articulos"]
        ]
        _indice = IndiceTfIdf(docs)
    return _indice


def buscar_articulos(consulta: str, k: int = 3) -> list:
    return indice_reglamento().buscar(consulta, k=k)


# ---------- Documentos PDF subidos por la administración ----------
_indice_docs = None
_firma_docs = None


def indice_documentos():
    """Índice de los fragmentos de PDFs públicos. Se reconstruye solo si cambió algún documento."""
    global _indice_docs, _firma_docs
    from dao import documento_dao
    firma = documento_dao.firma_publicos()
    if _indice_docs is None or firma != _firma_docs:
        filas = documento_dao.fragmentos_publicos()
        docs = [{"documento_id": f["documento_id"], "titulo": f["titulo"], "pagina": f["pagina"],
                 "contenido": f["texto"], "texto": f"{f['titulo']} {f['texto']}"} for f in filas]
        _indice_docs = IndiceTfIdf(docs) if docs else None
        _firma_docs = firma
    return _indice_docs


def buscar_documentos(consulta: str, k: int = 2) -> list:
    idx = indice_documentos()
    return idx.buscar(consulta, k=k, umbral=0.12) if idx else []
