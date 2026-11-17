import datetime as dt

from services.reserva_service import validar_reglas

AREA = {
    "nombre": "Zona de parrillas", "activo": True, "aforo": 15,
    "hora_apertura": dt.time(11, 0), "hora_cierre": dt.time(22, 0),
    "anticipacion_min_horas": 24, "duracion_max_horas": 4,
}
AHORA = dt.datetime(2026, 11, 16, 10, 0)
MANANA = dt.date(2026, 11, 18)


def _validar(**kw):
    args = dict(area=AREA, fecha=MANANA, hora_inicio=dt.time(13, 0), hora_fin=dt.time(16, 0),
                asistentes=10, ahora=AHORA, recibos_vencidos=0)
    args.update(kw)
    return validar_reglas(**args)


def test_reserva_valida():
    assert _validar() == []


def test_fuera_de_horario():
    assert any("horario" in e for e in _validar(hora_inicio=dt.time(9, 0)))


def test_supera_aforo():
    assert any("aforo" in e for e in _validar(asistentes=20))


def test_supera_duracion():
    assert any("durar" in e for e in _validar(hora_inicio=dt.time(12, 0), hora_fin=dt.time(18, 0)))


def test_sin_anticipacion_minima():
    assert any("anticipación" in e for e in _validar(fecha=dt.date(2026, 11, 16), hora_inicio=dt.time(20, 0),
                                                     hora_fin=dt.time(21, 0)))


def test_fecha_pasada():
    assert any("pasada" in e for e in _validar(fecha=dt.date(2026, 11, 1)))


def test_con_deuda_vencida():
    assert any("deuda" in e for e in _validar(recibos_vencidos=2))


def test_area_inactiva():
    assert _validar(area=dict(AREA, activo=False)) == ["El área no está disponible"]


# ---------- Configuración de áreas por la administración ----------
from services.reserva_service import validar_area  # noqa: E402

AREA_OK = {"nombre": "Zona de parrillas", "descripcion": "Terraza", "aforo": 15, "tarifa": "65.50",
           "hora_apertura": "11:00", "hora_cierre": "22:00", "anticipacion_min_horas": 24,
           "duracion_max_horas": 4, "activo": True}


def test_area_valida_normaliza_datos():
    datos, errores = validar_area(AREA_OK)
    assert errores == []
    assert str(datos["tarifa"]) == "65.50"
    assert datos["hora_cierre"] == dt.time(22, 0)


def test_area_tarifa_negativa():
    assert validar_area(dict(AREA_OK, tarifa=-5))[1]


def test_area_cierre_antes_de_apertura():
    _, errores = validar_area(dict(AREA_OK, hora_apertura="22:00", hora_cierre="11:00"))
    assert any("cierre" in e for e in errores)


def test_area_duracion_mayor_al_horario():
    _, errores = validar_area(dict(AREA_OK, hora_apertura="20:00", hora_cierre="22:00", duracion_max_horas=4))
    assert any("duración máxima" in e for e in errores)


def test_area_aforo_cero():
    assert validar_area(dict(AREA_OK, aforo=0))[1]


def test_area_garantia_negativa_y_uso_compartido():
    assert validar_area(dict(AREA_OK, garantia=-1))[1]
    datos, _ = validar_area(dict(AREA_OK, garantia="150", uso_exclusivo=False))
    assert str(datos["garantia"]) == "150.00" and datos["uso_exclusivo"] is False


# ---------- Invitados ----------
from services.reserva_service import validar_invitados  # noqa: E402


def test_invitados_validos_se_normalizan():
    lista, errores = validar_invitados([
        {"nombres": "  Ana  María ", "apellidos": "Pérez", "tipo_documento": "dni", "numero_documento": "12345678"},
        {"nombres": "John", "apellidos": "Smith", "tipo_documento": "CE", "numero_documento": "ab1234567"},
    ], asistentes=3)
    assert errores == []
    assert lista[0]["nombres"] == "Ana María" and lista[0]["tipo_documento"] == "DNI"
    assert lista[1]["numero_documento"] == "AB1234567"


def test_invitados_no_superan_asistentes_menos_titular():
    _, errores = validar_invitados([{"nombres": "Ana", "apellidos": "Pérez", "numero_documento": "12345678"}] * 2, 2)
    assert errores and "hasta 1" in errores[0]


def test_dni_invalido_y_repetido():
    inv = {"nombres": "Ana", "apellidos": "Pérez", "tipo_documento": "DNI", "numero_documento": "1234"}
    assert "8 dígitos" in validar_invitados([inv], 5)[1][0]
    ok = dict(inv, numero_documento="12345678")
    assert "repetido" in validar_invitados([ok, ok], 5)[1][0]


def test_sin_invitados_es_valido():
    assert validar_invitados(None, 1) == ([], [])
