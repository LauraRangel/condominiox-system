from decimal import Decimal

from utils.money import money_float, round_money, to_decimal


class TestToDecimal:
    def test_none_devuelve_cero(self):
        assert to_decimal(None) == Decimal("0")

    def test_string_vacio_devuelve_cero(self):
        assert to_decimal("") == Decimal("0")

    def test_string_numerico(self):
        assert to_decimal("10.5") == Decimal("10.5")

    def test_float(self):
        assert to_decimal(10.5) == Decimal("10.5")

    def test_int(self):
        assert to_decimal(10) == Decimal("10")

    def test_decimal_pass_through(self):
        valor = Decimal("3.14")
        assert to_decimal(valor) is valor


class TestRoundMoney:
    def test_redondea_hacia_arriba_en_empate(self):
        assert round_money(Decimal("2.005")) == Decimal("2.01")

    def test_redondea_normal_hacia_abajo(self):
        assert round_money(Decimal("2.674")) == Decimal("2.67")

    def test_redondea_normal_hacia_arriba(self):
        assert round_money(Decimal("2.676")) == Decimal("2.68")

    def test_valor_ya_redondeado_no_cambia(self):
        assert round_money(Decimal("5.00")) == Decimal("5.00")

    def test_acepta_string(self):
        assert round_money("2.005") == Decimal("2.01")

    def test_acepta_none(self):
        assert round_money(None) == Decimal("0.00")

    def test_negativo(self):
        # ROUND_HALF_UP redondea los empates alejándose de cero (por magnitud absoluta)
        assert round_money(Decimal("-2.005")) == Decimal("-2.01")


class TestMoneyFloat:
    def test_devuelve_float(self):
        resultado = money_float(Decimal("2.005"))
        assert isinstance(resultado, float)

    def test_redondea_igual_que_round_money(self):
        assert money_float(Decimal("2.005")) == 2.01

    def test_none_devuelve_cero_float(self):
        assert money_float(None) == 0.0
