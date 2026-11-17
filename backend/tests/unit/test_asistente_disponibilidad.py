"""Funciones puras del asistente para responder disponibilidad de áreas comunes."""

import datetime as dt

import pytest

from services.asistente_service import (
    describir_disponibilidad,
    extraer_fecha,
    extraer_hora,
    limpiar_respuesta,
)

LIMA = dt.timezone(dt.timedelta(hours=-5))
HOY = dt.date(2026, 11, 17)
AHORA = dt.datetime(2026, 11, 17, 10, 0, tzinfo=LIMA)

PARRILLA = {"nombre": "Zona de parrillas", "aforo": 15, "uso_exclusivo": True, "hora_apertura": "11:00",
            "hora_cierre": "22:00", "anticipacion_min_horas": 24, "duracion_max_horas": 4}
GIMNASIO = {"nombre": "Gimnasio", "aforo": 8, "uso_exclusivo": False, "hora_apertura": "06:00",
            "hora_cierre": "22:00", "anticipacion_min_horas": 1, "duracion_max_horas": 2}


class TestExtraerFecha:
    @pytest.mark.parametrize("texto, esperado", [
        ("¿hay horario disponible en la zona de parrillas a las 2pm del 20 de noviembre?", dt.date(2026, 11, 20)),
        ("¿está libre el salón el 20 de enero?", dt.date(2027, 1, 20)),   # ya pasó este año: el siguiente
        ("el 5 de diciembre de 2027", dt.date(2027, 12, 5)),
        ("¿y mañana?", dt.date(2026, 11, 18)),
        ("pasado mañana en la tarde", dt.date(2026, 11, 19)),
        ("¿hoy está libre el gimnasio?", HOY),
        ("el 20/11", dt.date(2026, 11, 20)),
        ("el 3/1/27", dt.date(2027, 1, 3)),
        ("el 2026-12-01", dt.date(2026, 12, 1)),
        ("a las 10 de la mañana del 25 de noviembre", dt.date(2026, 11, 25)),
    ])
    def test_reconoce_formatos(self, texto, esperado):
        assert extraer_fecha(texto, HOY) == esperado

    @pytest.mark.parametrize("texto", ["¿cuánto cuesta la parrilla?", "el 31 de febrero", "el 40/13"])
    def test_sin_fecha_valida(self, texto):
        assert extraer_fecha(texto, HOY) is None


class TestExtraerHora:
    @pytest.mark.parametrize("texto, esperado", [
        ("a las 2pm", dt.time(14, 0)),
        ("a las 2 p.m.", dt.time(14, 0)),
        ("8:30 am", dt.time(8, 30)),
        ("12 pm", dt.time(12, 0)),
        ("3 de la tarde", dt.time(15, 0)),
        ("10 de la mañana", dt.time(10, 0)),
        ("8 de la noche", dt.time(20, 0)),
        ("desde las 14:30", dt.time(14, 30)),
        ("a las 2", dt.time(14, 0)),     # 1 a 5 sin am/pm: tarde
        ("a las 9", dt.time(9, 0)),
        ("a las 18", dt.time(18, 0)),
    ])
    def test_reconoce_formatos(self, texto, esperado):
        assert extraer_hora(texto) == esperado

    @pytest.mark.parametrize("texto", ["puedo reservar 3 horas", "para 15 personas", "a las 13pm", "el 20/11"])
    def test_no_confunde_duraciones_ni_cantidades(self, texto):
        assert extraer_hora(texto) is None


class TestDescribirDisponibilidad:
    FECHA = dt.date(2026, 11, 20)
    OCUPADO = [{"hora_inicio": "13:00", "hora_fin": "16:00", "personas": 10}]

    def test_hora_dentro_de_una_reserva_exclusiva_esta_ocupada(self):
        txt = describir_disponibilidad(PARRILLA, self.FECHA, dt.time(14), self.OCUPADO, AHORA)
        assert "13:00 a 16:00" in txt
        assert "A las 14:00 está OCUPADA" in txt
        assert "viernes 20 de noviembre de 2026" in txt

    def test_hora_libre_indica_hasta_cuando(self):
        txt = describir_disponibilidad(PARRILLA, self.FECHA, dt.time(11), self.OCUPADO, AHORA)
        assert "A las 11:00 está LIBRE" in txt
        assert "hasta las 13:00" in txt

    def test_sin_reservas_todo_libre(self):
        txt = describir_disponibilidad(PARRILLA, self.FECHA, None, [], AHORA)
        assert "no tiene reservas" in txt
        assert "11:00 a 22:00" in txt

    def test_fuera_del_horario(self):
        txt = describir_disponibilidad(PARRILLA, self.FECHA, dt.time(23), [], AHORA)
        assert "cerrada" in txt

    def test_area_compartida_informa_cupos(self):
        ocupado = [{"hora_inicio": "18:00", "hora_fin": "20:00", "personas": 5}]
        txt = describir_disponibilidad(GIMNASIO, self.FECHA, dt.time(19), ocupado, AHORA)
        assert "5 de 8 lugares reservados, quedan 3" in txt

    def test_avisa_si_no_cumple_la_anticipacion(self):
        mañana = dt.date(2026, 11, 18)
        txt = describir_disponibilidad(PARRILLA, mañana, dt.time(9 + 3), [], AHORA)   # 26 h: cumple
        assert "anticipación" not in txt
        txt = describir_disponibilidad(PARRILLA, HOY, dt.time(14), [], AHORA)         # 4 h: no cumple 24 h
        assert "anticipación mínima de 24 h" in txt

    def test_fecha_pasada(self):
        txt = describir_disponibilidad(PARRILLA, dt.date(2026, 11, 1), None, [], AHORA)
        assert "ya pasó" in txt

    def test_no_revela_quien_reservo(self):
        ocupado = [{"hora_inicio": "13:00", "hora_fin": "16:00", "personas": 10, "propietario_id": 7}]
        txt = describir_disponibilidad(PARRILLA, self.FECHA, None, ocupado, AHORA)
        assert "7" not in txt.replace("2026", "")


class TestLimpiarRespuesta:
    def test_quita_caracteres_invisibles_de_las_citas(self):
        assert limpiar_respuesta("Abre a las 06:00 [​F1][F3⁠].") == "Abre a las 06:00 [F1][F3]."

    def test_normaliza_espacios_estrechos(self):
        assert limpiar_respuesta("el 20 de noviembre a las 2 p.m.") == "el 20 de noviembre a las 2 p.m."
