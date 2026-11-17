"""Genera PDFs simples de texto (sin dependencias) para datos de demostración y pruebas."""

import textwrap


def _escapar(linea: str) -> bytes:
    data = linea.encode("cp1252", errors="replace")
    return data.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)")


def generar_pdf(titulo: str, paginas: list[list[str]]) -> bytes:
    """paginas: lista de páginas; cada página es una lista de párrafos."""
    objetos = []

    def agregar(cuerpo: bytes) -> int:
        objetos.append(cuerpo)
        return len(objetos)

    agregar(b"")  # 1: catálogo (se completa al final)
    agregar(b"")  # 2: árbol de páginas
    fuente = agregar(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    fuente_b = agregar(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>")

    ids_paginas = []
    for n, parrafos in enumerate(paginas):
        lineas = [b"BT", b"/F2 15 Tf", b"60 790 Td", b"(" + _escapar(titulo) + b") Tj",
                  b"/F1 11 Tf", b"0 -14 Td", b"(" + _escapar(f"Pagina {n + 1}") + b") Tj", b"16 TL"]
        for parrafo in parrafos:
            lineas.append(b"T*")
            for linea in textwrap.wrap(parrafo, 88) or [""]:
                lineas.append(b"(" + _escapar(linea) + b") '")
        lineas.append(b"ET")
        stream = b"\n".join(lineas)
        contenido = agregar(b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream")
        ids_paginas.append(agregar(
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents %d 0 R "
            b"/Resources << /Font << /F1 %d 0 R /F2 %d 0 R >> >> >>" % (contenido, fuente, fuente_b)))

    objetos[0] = b"<< /Type /Catalog /Pages 2 0 R >>"
    kids = b" ".join(b"%d 0 R" % i for i in ids_paginas)
    objetos[1] = b"<< /Type /Pages /Kids [" + kids + b"] /Count %d >>" % len(ids_paginas)

    salida = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = []
    for i, cuerpo in enumerate(objetos, start=1):
        offsets.append(len(salida))
        salida += b"%d 0 obj\n" % i + cuerpo + b"\nendobj\n"
    xref = len(salida)
    salida += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objetos) + 1)
    for off in offsets:
        salida += b"%010d 00000 n \n" % off
    salida += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objetos) + 1, xref)
    return bytes(salida)
