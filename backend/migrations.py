"""Migraciones de los componentes innovadores (APF3).

Se ejecutan al iniciar la app (ver app.py). Todas son idempotentes:
CREATE TABLE IF NOT EXISTS / ADD COLUMN IF NOT EXISTS / INSERT condicionado.
"""

from db import execute

DDL = [
    # Cargo de reservas dentro del recibo mensual
    """
    ALTER TABLE recibos
    ADD COLUMN IF NOT EXISTS monto_reservas NUMERIC(10,2) NOT NULL DEFAULT 0
    """,
    # Reserva de áreas comunes
    """
    CREATE TABLE IF NOT EXISTS areas_comunes (
        id SERIAL PRIMARY KEY,
        nombre VARCHAR(80) NOT NULL UNIQUE,
        descripcion TEXT,
        aforo INTEGER NOT NULL CHECK (aforo > 0),
        tarifa NUMERIC(10,2) NOT NULL DEFAULT 0 CHECK (tarifa >= 0),
        garantia NUMERIC(10,2) NOT NULL DEFAULT 0 CHECK (garantia >= 0),
        uso_exclusivo BOOLEAN NOT NULL DEFAULT TRUE,
        hora_apertura TIME NOT NULL,
        hora_cierre TIME NOT NULL,
        anticipacion_min_horas INTEGER NOT NULL DEFAULT 24,
        duracion_max_horas INTEGER NOT NULL DEFAULT 4,
        activo BOOLEAN NOT NULL DEFAULT TRUE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS reservas (
        id SERIAL PRIMARY KEY,
        area_id INTEGER NOT NULL REFERENCES areas_comunes(id) ON DELETE CASCADE,
        propietario_id INTEGER NOT NULL REFERENCES propietarios(id) ON DELETE CASCADE,
        fecha DATE NOT NULL,
        hora_inicio TIME NOT NULL,
        hora_fin TIME NOT NULL,
        asistentes INTEGER NOT NULL CHECK (asistentes > 0),
        cargo NUMERIC(10,2) NOT NULL DEFAULT 0,
        estado VARCHAR(20) NOT NULL DEFAULT 'confirmada'
            CHECK (estado IN ('pendiente_garantia', 'confirmada', 'cancelada', 'expirada')),
        garantia NUMERIC(10,2) NOT NULL DEFAULT 0,
        garantia_estado VARCHAR(20) NOT NULL DEFAULT 'no_aplica'
            CHECK (garantia_estado IN ('no_aplica', 'pendiente', 'pagada', 'devuelta',
                                       'devuelta_parcial', 'retenida', 'no_pagada')),
        garantia_retenida NUMERIC(10,2) NOT NULL DEFAULT 0,
        garantia_motivo VARCHAR(300),
        garantia_resuelta_en TIMESTAMPTZ,
        recibo_id INTEGER REFERENCES recibos(id) ON DELETE SET NULL,
        creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        CHECK (hora_fin > hora_inicio)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_reservas_area_fecha ON reservas(area_id, fecha)",
    # Lista de invitados de cada reserva (control de acceso en portería)
    """
    CREATE TABLE IF NOT EXISTS reserva_invitados (
        id SERIAL PRIMARY KEY,
        reserva_id INTEGER NOT NULL REFERENCES reservas(id) ON DELETE CASCADE,
        nombres VARCHAR(60) NOT NULL,
        apellidos VARCHAR(60) NOT NULL,
        tipo_documento VARCHAR(3) NOT NULL CHECK (tipo_documento IN ('DNI', 'CE')),
        numero_documento VARCHAR(12) NOT NULL,
        UNIQUE (reserva_id, tipo_documento, numero_documento)
    )
    """,
    # Pasarela de pagos emulada
    """
    CREATE TABLE IF NOT EXISTS transacciones_pago (
        id SERIAL PRIMARY KEY,
        recibo_id INTEGER REFERENCES recibos(id) ON DELETE SET NULL,
        reserva_id INTEGER REFERENCES reservas(id) ON DELETE SET NULL,
        propietario_id INTEGER REFERENCES propietarios(id) ON DELETE SET NULL,
        concepto VARCHAR(20) NOT NULL DEFAULT 'recibo'
            CHECK (concepto IN ('recibo', 'garantia', 'devolucion')),
        transaccion_origen_id INTEGER REFERENCES transacciones_pago(id),
        proveedor VARCHAR(20) NOT NULL CHECK (proveedor IN ('yape', 'culqi', 'mercadopago')),
        monto NUMERIC(10,2) NOT NULL CHECK (monto > 0),
        moneda VARCHAR(3) NOT NULL DEFAULT 'PEN',
        estado VARCHAR(20) NOT NULL CHECK (estado IN ('aprobado', 'rechazado')),
        codigo_operacion VARCHAR(40) NOT NULL UNIQUE,
        idempotency_key VARCHAR(80) UNIQUE,
        medio_detalle VARCHAR(60),
        mensaje VARCHAR(200),
        respuesta_pasarela JSONB,
        modo VARCHAR(12) NOT NULL DEFAULT 'sandbox',
        creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """,
    # Documentos del condominio (solo PDF, guardados en PostgreSQL)
    """
    CREATE TABLE IF NOT EXISTS documentos (
        id SERIAL PRIMARY KEY,
        titulo VARCHAR(150) NOT NULL,
        categoria VARCHAR(20) NOT NULL
            CHECK (categoria IN ('reglamento', 'acta', 'manual', 'presupuesto', 'otro')),
        descripcion VARCHAR(300),
        nombre_archivo VARCHAR(200) NOT NULL,
        tamano_bytes INTEGER NOT NULL,
        paginas INTEGER NOT NULL,
        contenido BYTEA NOT NULL,
        publico BOOLEAN NOT NULL DEFAULT TRUE,
        tiene_texto BOOLEAN NOT NULL DEFAULT TRUE,
        subido_por VARCHAR(50),
        creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS documento_fragmentos (
        id SERIAL PRIMARY KEY,
        documento_id INTEGER NOT NULL REFERENCES documentos(id) ON DELETE CASCADE,
        pagina INTEGER NOT NULL,
        texto TEXT NOT NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_fragmentos_documento ON documento_fragmentos(documento_id)",
    # Auditoría del asistente con IA
    """
    CREATE TABLE IF NOT EXISTS consultas_asistente (
        id SERIAL PRIMARY KEY,
        propietario_id INTEGER REFERENCES propietarios(id) ON DELETE CASCADE,
        pregunta TEXT NOT NULL,
        respuesta TEXT NOT NULL,
        fuentes JSONB,
        modo VARCHAR(12) NOT NULL,
        proveedor VARCHAR(30),
        latencia_ms INTEGER,
        creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """,
]

# nombre, descripción, aforo, tarifa, garantía, uso exclusivo, apertura, cierre, anticipación (h), duración máx. (h)
AREAS_INICIALES = [
    ("Salón de usos múltiples", "Salón techado con mesas, sillas y cocina pequeña.", 40, 80.00, 200.00, True, "09:00", "23:00", 48, 5),
    ("Zona de parrillas", "Terraza con dos parrillas y lavadero.", 15, 50.00, 100.00, True, "11:00", "22:00", 24, 4),
    ("Gimnasio", "Máquinas de cardio y pesas. Uso compartido por turnos.", 8, 0.00, 0.00, False, "06:00", "22:00", 1, 2),
    ("Cowork", "Sala de trabajo con escritorios, wifi y enchufes. Uso compartido.", 12, 0.00, 0.00, False, "07:00", "22:00", 1, 4),
    ("Pet shower", "Zona de baño para mascotas con ducha, secadora y mesa de aseo.", 2, 15.00, 30.00, True, "08:00", "20:00", 2, 1),
]


def run_migrations():
    for sql in DDL:
        execute(sql)
    sembrar_areas()


def sembrar_areas():
    for nombre, desc, aforo, tarifa, garantia, exclusivo, apertura, cierre, antic, dur in AREAS_INICIALES:
        execute(
            """
            INSERT INTO areas_comunes (nombre, descripcion, aforo, tarifa, garantia, uso_exclusivo,
                                       hora_apertura, hora_cierre, anticipacion_min_horas, duracion_max_horas)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (nombre) DO NOTHING
            """,
            [nombre, desc, aforo, tarifa, garantia, exclusivo, apertura, cierre, antic, dur],
        )
