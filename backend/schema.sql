CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('Administrador', 'Propietario')),
    activo BOOLEAN DEFAULT TRUE,
    creado_en TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS propietarios (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER UNIQUE REFERENCES usuarios(id) ON DELETE SET NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    dni VARCHAR(8) UNIQUE NOT NULL,
    correo VARCHAR(120),
    telefono VARCHAR(20),
    nro_departamento VARCHAR(10) NOT NULL,
    torre VARCHAR(5) NOT NULL
);

CREATE TABLE IF NOT EXISTS gastos (
    id SERIAL PRIMARY KEY,
    proveedor VARCHAR(120) NOT NULL,
    concepto TEXT NOT NULL,
    monto NUMERIC(10,2) NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('mantenimiento', 'luz', 'agua')),
    fecha_registro DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS pagos_gastos (
    id SERIAL PRIMARY KEY,
    gasto_id INTEGER NOT NULL REFERENCES gastos(id) ON DELETE CASCADE,
    monto NUMERIC(10,2) NOT NULL CHECK (monto > 0),
    fecha_pago DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS configuracion (
    id SERIAL PRIMARY KEY,
    monto_administracion NUMERIC(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS recibos (
    id SERIAL PRIMARY KEY,
    propietario_id INTEGER NOT NULL REFERENCES propietarios(id) ON DELETE CASCADE,
    monto_administracion NUMERIC(10,2) NOT NULL,
    monto_agua NUMERIC(10,2) NOT NULL,
    monto_luz NUMERIC(10,2) NOT NULL,
    monto_mantenimiento NUMERIC(10,2) NOT NULL,
    monto_pagado NUMERIC(10,2) NOT NULL DEFAULT 0,
    fecha_emision DATE NOT NULL,
    fecha_pago DATE,
    pagado BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS anuncios (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    contenido TEXT NOT NULL,
    tipo VARCHAR(30) NOT NULL CHECK (tipo IN ('mantenimiento','pago','informativo')),
    fecha_publicacion DATE NOT NULL DEFAULT CURRENT_DATE,
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS lecturas_anuncios (
    id SERIAL PRIMARY KEY,
    anuncio_id INTEGER NOT NULL REFERENCES anuncios(id) ON DELETE CASCADE,
    propietario_id INTEGER NOT NULL REFERENCES propietarios(id) ON DELETE CASCADE,
    fecha_lectura TIMESTAMP DEFAULT NOW(),
    UNIQUE(anuncio_id, propietario_id)
);


-- ===== Componentes innovadores APF3 (también se aplican solos en migrations.py) =====
ALTER TABLE recibos
ADD COLUMN IF NOT EXISTS monto_reservas NUMERIC(10,2) NOT NULL DEFAULT 0;

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
);

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
);

CREATE INDEX IF NOT EXISTS idx_reservas_area_fecha ON reservas(area_id, fecha);

CREATE TABLE IF NOT EXISTS reserva_invitados (
    id SERIAL PRIMARY KEY,
    reserva_id INTEGER NOT NULL REFERENCES reservas(id) ON DELETE CASCADE,
    nombres VARCHAR(60) NOT NULL,
    apellidos VARCHAR(60) NOT NULL,
    tipo_documento VARCHAR(3) NOT NULL CHECK (tipo_documento IN ('DNI', 'CE')),
    numero_documento VARCHAR(12) NOT NULL,
    UNIQUE (reserva_id, tipo_documento, numero_documento)
);

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
);

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
);

CREATE TABLE IF NOT EXISTS documento_fragmentos (
    id SERIAL PRIMARY KEY,
    documento_id INTEGER NOT NULL REFERENCES documentos(id) ON DELETE CASCADE,
    pagina INTEGER NOT NULL,
    texto TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_fragmentos_documento ON documento_fragmentos(documento_id);

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
);

