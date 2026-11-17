"""Carga datos de demostración para la sustentación (idempotente).

Uso:  cd backend && DATABASE_URL=... python seed_demo.py

- Crea el usuario administrador `admin` (contraseña: Admin2026!) si no existe ningún administrador.
- Registra 8 propietarios de prueba (contraseña inicial = DNI) si su DNI no existe.
- Registra gastos de agua, luz y mantenimiento de los dos últimos meses si el mes no tiene gastos.
- Genera los recibos de ambos meses y deja pagados los del mes anterior, salvo el de
  Carlos Rojas, que queda moroso (para mostrar que el sistema bloquea su reserva).
"""

import datetime as dt

from dotenv import load_dotenv

load_dotenv()

import app  # noqa: E402,F401  (importar app ejecuta las migraciones)
from db import fetch_one, execute  # noqa: E402
from security import hash_password  # noqa: E402
from services import recibo_service  # noqa: E402
from utils.pdf_simple import generar_pdf  # noqa: E402
from dao import documento_dao  # noqa: E402
from services.documento_service import extraer_texto_pdf  # noqa: E402

DOCUMENTOS = [
    ("Acta de Junta de Propietarios - Octubre 2026", "acta", "Sesión ordinaria del 25 de octubre de 2026", [
        ["Asistieron 21 de 28 propietarios, con quórum suficiente. Presidió la sesión la presidenta de la Junta.",
         "Acuerdo 1: Se aprobó pintar la fachada del edificio en diciembre de 2026 con un presupuesto de S/ 12,500, "
         "financiado con el fondo de reserva. La empresa se elegirá entre tres cotizaciones.",
         "Acuerdo 2: Se cambiará la bomba de agua de la cisterna en enero de 2027. Mientras tanto, el corte de agua "
         "por mantenimiento será el primer sábado de cada mes de 8:00 a 12:00 horas."],
        ["Acuerdo 3: A partir de noviembre, las áreas comunes se reservan únicamente por la plataforma CondominioX "
         "y los pagos de cuotas pueden hacerse con Yape, tarjeta o Mercado Pago.",
         "Acuerdo 4: Se instalarán dos cámaras adicionales en el estacionamiento antes de fin de año.",
         "Sin más puntos que tratar, se levantó la sesión a las 21:30 horas."],
    ]),
    ("Manual de uso del gimnasio", "manual", "Normas y horarios del gimnasio", [
        ["El gimnasio atiende de 6:00 a 22:00 horas. Es obligatorio usar toalla y limpiar las máquinas después de usarlas.",
         "Los menores de 16 años solo pueden ingresar acompañados de un adulto responsable.",
         "Las pesas deben regresarse a su rack. Si una máquina está malograda, repórtelo a la administración por la plataforma."],
    ]),
]

LIMA = dt.timezone(dt.timedelta(hours=-5))

PROPIETARIOS = [
    ("maria.quispe", "María", "Quispe Huamán", "45678912", "maria.quispe@correo.pe", "987654321", "301", "A"),
    ("carlos.rojas", "Carlos", "Rojas Vega", "41236587", "carlos.rojas@correo.pe", "976543210", "502", "A"),
    ("ana.torres", "Ana", "Torres Salazar", "47851236", "ana.torres@correo.pe", "965432109", "203", "A"),
    ("luis.mendoza", "Luis", "Mendoza Paredes", "43215678", "luis.mendoza@correo.pe", "954321098", "704", "B"),
    ("rosa.flores", "Rosa", "Flores Cárdenas", "46547891", "rosa.flores@correo.pe", "943210987", "101", "B"),
    ("jorge.castillo", "Jorge", "Castillo Ramos", "42589631", "jorge.castillo@correo.pe", "932109876", "602", "B"),
    ("lucia.vargas", "Lucía", "Vargas Ñique", "48963217", "lucia.vargas@correo.pe", "921098765", "405", "A"),
    ("pedro.salas", "Pedro", "Salas Gutiérrez", "44781256", "pedro.salas@correo.pe", "910987654", "803", "B"),
]

GASTOS_MES = [
    ("Sedapal", "Consumo de agua de áreas comunes y cisterna", 480.00, "agua"),
    ("Luz del Sur", "Energía de ascensores, bombas y pasillos", 320.00, "luz"),
    ("Ascensores Andinos SAC", "Mantenimiento preventivo de ascensores", 380.00, "mantenimiento"),
    ("Limpieza Total EIRL", "Servicio de limpieza de áreas comunes", 180.00, "mantenimiento"),
]


def _admin():
    if fetch_one("SELECT id FROM usuarios WHERE tipo = 'Administrador' LIMIT 1"):
        return
    execute(
        "INSERT INTO usuarios (usuario, password_hash, tipo) VALUES (%s, %s, 'Administrador')",
        ["admin", hash_password("Admin2026!")],
    )
    print("Administrador creado: admin / Admin2026!")


def _propietarios():
    for usuario, nombre, apellido, dni, correo, tel, depto, torre in PROPIETARIOS:
        if fetch_one("SELECT id FROM propietarios WHERE dni = %s", [dni]):
            continue
        execute(
            "INSERT INTO usuarios (usuario, password_hash, tipo) VALUES (%s, %s, 'Propietario')",
            [usuario, hash_password(dni)],
        )
        u = fetch_one("SELECT id FROM usuarios WHERE usuario = %s", [usuario])
        execute(
            """INSERT INTO propietarios (usuario_id, nombre, apellido, dni, correo, telefono, nro_departamento, torre)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            [u["id"], nombre, apellido, dni, correo, tel, depto, torre],
        )
        print(f"Propietario: {usuario} / {dni}")


def _gastos(fecha: dt.date):
    mes = fecha.strftime("%Y-%m")
    if fetch_one("SELECT id FROM gastos WHERE TO_CHAR(fecha_registro, 'YYYY-MM') = %s LIMIT 1", [mes]):
        return
    for proveedor, concepto, monto, tipo in GASTOS_MES:
        execute(
            "INSERT INTO gastos (proveedor, concepto, monto, tipo, fecha_registro) VALUES (%s, %s, %s, %s, %s)",
            [proveedor, concepto, monto, tipo, fecha],
        )


def _documentos():
    for titulo, categoria, descripcion, paginas in DOCUMENTOS:
        if fetch_one("SELECT id FROM documentos WHERE titulo = %s", [titulo]):
            continue
        pdf = generar_pdf(titulo, paginas)
        n, fragmentos = extraer_texto_pdf(pdf)
        nombre = titulo.lower().replace(" - ", "-").replace(" ", "-") + ".pdf"
        documento_dao.crear_documento(titulo, categoria, descripcion, nombre, pdf, n, True,
                                      bool(fragmentos), "admin", fragmentos)
        print(f"Documento: {titulo}")


def main():
    _admin()
    _documentos()
    if not fetch_one("SELECT id FROM configuracion LIMIT 1"):
        execute("INSERT INTO configuracion (monto_administracion) VALUES (120.00)")
    _propietarios()

    hoy = dt.datetime.now(LIMA).date()
    actual = hoy.replace(day=1)
    anterior = (actual - dt.timedelta(days=1)).replace(day=1)

    for primer_dia in (anterior, actual):
        _gastos(primer_dia + dt.timedelta(days=2))
        recibo_service.generar_recibos(primer_dia.isoformat(), primer_dia.strftime("%Y-%m"))

    moroso = fetch_one("SELECT id FROM propietarios WHERE dni = '41236587'")
    pendientes = recibo_service.listar_recibos_admin("pendientes", anterior.strftime("%Y-%m"))["items"]
    for r in pendientes:
        if moroso and r["propietario_id"] == moroso["id"]:
            continue
        recibo_service.pagar_recibo(r["id"], r["saldo"])
    print(f"Recibos de {anterior:%Y-%m} pagados (salvo Carlos Rojas) y de {actual:%Y-%m} pendientes.")


if __name__ == "__main__":
    main()
