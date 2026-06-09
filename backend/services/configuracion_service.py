from dao import configuracion_dao
from utils.money import money_float


def get_monto_administracion() -> float:
    row = configuracion_dao.get_ultima_configuracion()
    if row and row.get("monto_administracion") is not None:
        return money_float(row["monto_administracion"])
    return 50.0


def update_monto_administracion(monto):
    row = configuracion_dao.create_configuracion(monto)
    return {"monto_administracion": float(row["monto_administracion"])}
