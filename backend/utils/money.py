from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

MONEY_STEP = Decimal("0.01")


def to_decimal(value):
    if isinstance(value, Decimal):
        return value
    if value in (None, ""):
        return Decimal("0")
    resultado = Decimal(str(value))
    if not resultado.is_finite():
        raise InvalidOperation("Monto no finito")
    return resultado


def round_money(value):
    return to_decimal(value).quantize(MONEY_STEP, rounding=ROUND_HALF_UP)


def money_float(value):
    return float(round_money(value))
