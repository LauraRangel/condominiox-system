from decimal import Decimal, ROUND_HALF_UP

MONEY_STEP = Decimal("0.01")


def to_decimal(value):
    if isinstance(value, Decimal):
        return value
    if value in (None, ""):
        return Decimal("0")
    return Decimal(str(value))


def round_money(value):
    return to_decimal(value).quantize(MONEY_STEP, rounding=ROUND_HALF_UP)


def money_float(value):
    return float(round_money(value))
