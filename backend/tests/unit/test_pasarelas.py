from decimal import Decimal

from services.pasarelas import obtener_pasarela


def test_proveedor_desconocido():
    assert obtener_pasarela("paypal") is None


class TestCulqi:
    p = obtener_pasarela("culqi")

    def test_rechaza_token_mal_formado(self):
        assert self.p.validar({"token_id": "4111111111111111"}) is not None

    def test_tarjeta_aprobada_respuesta_tipo_charge(self):
        r = self.p.cobrar(Decimal("120.50"), {"token_id": "tkn_test_visa_1111_abcdef123456"}, "ref")
        assert r["aprobado"] is True
        assert r["respuesta"]["object"] == "charge"
        assert r["respuesta"]["amount"] == 12050
        assert r["respuesta"]["outcome"]["type"] == "venta_exitosa"
        assert r["medio_detalle"] == "Visa ****1111"

    def test_tarjeta_de_prueba_rechazada(self):
        r = self.p.cobrar(Decimal("10"), {"token_id": "tkn_test_visa_0002_abcdef123456"}, "ref")
        assert r["aprobado"] is False
        assert r["respuesta"]["outcome"]["type"] == "tarjeta_rechazada"


class TestYape:
    p = obtener_pasarela("yape")

    def test_valida_celular_y_otp(self):
        assert self.p.validar({"celular": "812345678", "otp": "123456"}) is not None
        assert self.p.validar({"celular": "912345678", "otp": "12"}) is not None
        assert self.p.validar({"celular": "912345678", "otp": "123456"}) is None

    def test_otp_000000_rechazado_y_celular_enmascarado(self):
        r = self.p.cobrar(Decimal("5"), {"celular": "912345678", "otp": "000000"}, "ref")
        assert r["aprobado"] is False
        assert "912345678" not in str(r["respuesta"])


class TestMercadoPago:
    p = obtener_pasarela("mercadopago")

    def test_aprobado_y_correo_enmascarado(self):
        r = self.p.cobrar(Decimal("50"), {"email": "laura@test.com"}, "ref")
        assert r["aprobado"] is True
        assert r["respuesta"]["status"] == "approved"
        assert "laura@test.com" not in str(r["respuesta"])

    def test_correo_de_rechazo(self):
        r = self.p.cobrar(Decimal("50"), {"email": "rechazo@test.com"}, "ref")
        assert r["respuesta"]["status"] == "rejected"
