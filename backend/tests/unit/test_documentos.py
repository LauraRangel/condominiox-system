import pytest

from services.documento_service import extraer_texto_pdf, partir_texto
from utils.pdf_simple import generar_pdf


def test_extrae_texto_por_pagina():
    pdf = generar_pdf("Acta", [["Se aprobó pintar la fachada en diciembre."], ["Limpieza de cisterna en enero."]])
    paginas, frags = extraer_texto_pdf(pdf)
    assert paginas == 2
    assert any(p == 1 and "fachada" in t for p, t in frags)
    assert any(p == 2 and "cisterna" in t for p, t in frags)


def test_pdf_invalido():
    with pytest.raises(ValueError):
        extraer_texto_pdf(b"%PDF-1.4 esto no es un pdf")


def test_partir_texto_respeta_tamano_y_oraciones():
    texto = " ".join(f"Oración número {i} del acta de junta." for i in range(100))
    frags = partir_texto(texto, 200)
    assert len(frags) > 5
    assert all(len(f) <= 200 for f in frags)
    assert all(f.endswith(".") for f in frags)
