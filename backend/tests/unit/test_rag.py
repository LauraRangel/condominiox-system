from services.rag import IndiceTfIdf, buscar_articulos, tokenizar, normalizar


class TestTokenizacion:
    def test_normaliza_tildes_y_mayusculas(self):
        assert normalizar("Salón ÁREA común") == "salon area comun"

    def test_quita_stopwords_y_plurales(self):
        assert tokenizar("las parrillas del edificio") == ["parrilla", "edificio"]


class TestIndice:
    def test_documento_mas_parecido_primero(self):
        idx = IndiceTfIdf([
            {"id": 1, "texto": "mascotas con correa en areas comunes"},
            {"id": 2, "texto": "pago del recibo mensual"},
        ])
        res = idx.buscar("puedo pagar mi recibo")
        assert res[0]["id"] == 2

    def test_consulta_sin_relacion_devuelve_vacio(self):
        idx = IndiceTfIdf([{"id": 1, "texto": "mascotas con correa"}])
        assert idx.buscar("zzz qqq") == []


class TestReglamento:
    def test_sinonimo_perro_encuentra_mascotas(self):
        assert buscar_articulos("puedo llevar mi perro")[0]["titulo"] == "Mascotas"

    def test_costo_reserva_encuentra_tarifas(self):
        assert buscar_articulos("cuanto cuesta reservar un area")[0]["titulo"] == "Tarifas de reserva"

    def test_ruido_encuentra_horario_de_silencio(self):
        assert buscar_articulos("hasta que hora puedo hacer bulla")[0]["numero"] == 14
