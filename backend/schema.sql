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
