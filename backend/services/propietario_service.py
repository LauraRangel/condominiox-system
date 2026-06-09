from dao import propietario_dao
from security import hash_password
from structures import ListaPropietarios, ArbolPropietariosBST
from utils.logger import get_logger

log = get_logger(__name__)


def _calcular_piso(nro_departamento) -> str:
    digits = "".join(ch for ch in str(nro_departamento or "") if ch.isdigit())
    if not digits:
        return ""
    if len(digits) <= 2:
        return str(int(digits))
    return str(int(digits[:-2]))


def listar_propietarios() -> dict:
    rows = propietario_dao.get_all_propietarios()
    lista = ListaPropietarios()
    for row in rows:
        lista.insertar(row)
    return {"items": lista.to_list(), "total": lista.length}


def buscar_propietarios(q: str = "", torre: str = "", piso: str = "") -> dict:
    q = q.strip().lower()
    torre = torre.strip().upper()
    rows = propietario_dao.get_all_propietarios()

    arbol = ArbolPropietariosBST()
    for row in rows:
        try:
            key = int(str(row.get("dni") or "0"))
        except ValueError:
            key = 0
        arbol.insertar(key, row)

    if q.isdigit() and len(q) == 8:
        encontrado = arbol.buscar(int(q))
        base = [encontrado] if encontrado else []
    else:
        base = arbol.inorden()

    items = []
    for row in base:
        texto = " ".join([
            str(row.get("usuario") or ""),
            str(row.get("nombre") or ""),
            str(row.get("apellido") or ""),
            str(row.get("dni") or ""),
            str(row.get("nro_departamento") or ""),
        ]).lower()
        if q and q not in texto:
            continue
        if torre and str(row.get("torre") or "").upper() != torre:
            continue
        if piso and _calcular_piso(row.get("nro_departamento")) != piso:
            continue
        items.append(row)

    return {"items": items, "total": len(items)}


def crear_propietario(body: dict):
    required = ["usuario", "nombre", "apellido", "dni", "nro_departamento", "torre"]
    if not all(body.get(k) for k in required):
        return None, "Datos incompletos"

    dni = str(body.get("dni", "")).strip()
    if not dni.isdigit() or len(dni) != 8:
        return None, "El DNI debe tener 8 dígitos"

    if propietario_dao.usuario_existe(body["usuario"].strip()):
        return None, "Ya existe un usuario con ese nombre"
    if propietario_dao.get_propietario_por_dni(dni):
        return None, "Ya existe un propietario con ese DNI"

    password_hash = hash_password(dni)
    row = propietario_dao.create_propietario(
        usuario=body["usuario"].strip(),
        nombre=body["nombre"].strip(),
        apellido=body["apellido"].strip(),
        dni=dni,
        correo=body.get("correo") or None,
        telefono=body.get("telefono") or None,
        nro_departamento=body["nro_departamento"].strip(),
        torre=body["torre"].strip(),
        password_hash=password_hash,
    )
    log.info("Propietario creado", extra={"id": row["id"]})
    return row, None


def actualizar_propietario(propietario_id, body: dict):
    required = ["usuario", "nombre", "apellido", "dni", "nro_departamento", "torre"]
    if not all(str(body.get(k) or "").strip() for k in required):
        return None, "Datos incompletos"

    dni = str(body.get("dni") or "").strip()
    if not dni.isdigit() or len(dni) != 8:
        return None, "El DNI debe tener 8 dígitos"

    existente = propietario_dao.get_propietario_por_id(propietario_id)
    if not existente:
        return None, "not_found"

    if propietario_dao.usuario_existe_excluyendo(body["usuario"].strip(), propietario_id):
        return None, "Ya existe otro usuario con ese nombre"
    if propietario_dao.dni_existe_excluyendo(dni, propietario_id):
        return None, "Ya existe otro propietario con ese DNI"

    row = propietario_dao.update_propietario(
        propietario_id=propietario_id,
        usuario=body["usuario"].strip(),
        nombre=body["nombre"].strip(),
        apellido=body["apellido"].strip(),
        dni=dni,
        correo=body.get("correo") or None,
        telefono=body.get("telefono") or None,
        nro_departamento=body["nro_departamento"].strip(),
        torre=body["torre"].strip(),
    )
    if row:
        row["usuario"] = body["usuario"].strip()
    return row, None


def eliminar_propietario(propietario_id):
    return propietario_dao.delete_propietario(propietario_id)
