# CondominioX System (Integrador)

Sistema web para gestión de condominio con autenticación por roles, administración de propietarios, control de gastos comunes y gestión de recibos con pagos parciales.

---

## 1. Alcance Funcional

### Rol Administrador
- Gestionar propietarios (crear, editar, eliminar).
- Configurar monto de administración.
- Registrar gastos (`mantenimiento`, `luz`, `agua`).
- Generar y recalcular recibos por mes.
- Visualizar pendientes/pagados y resumen mensual.
- Ver ranking automático de morosos.

### Rol Propietario
- Consultar datos personales.
- Editar correo y teléfono.
- Ver recibos pendientes y pagados.
- Realizar pagos parciales o totales.
- Cambiar contraseña.

---

## 2. Arquitectura Técnica (alto nivel)

- **Frontend:** HTML + CSS + JavaScript (sitio estático).
- **Backend:** Flask (API REST en Python).
- **BD:** PostgreSQL.
- **Auth:** JWT (token Bearer).

### Flujo general
1. Login desde frontend en `/api/login`.
2. Backend emite JWT con datos de usuario/rol.
3. Frontend consume endpoints protegidos con `Authorization: Bearer <token>`.
4. Backend valida rol, ejecuta reglas de negocio y persiste en PostgreSQL.

---

## 3. Modelo de Datos Actual (AS-IS)

Tablas activas del proyecto:
- `usuarios`
- `propietarios`
- `gastos`
- `pagos_gastos`
- `configuracion`
- `recibos`

Este modelo está operativo y corresponde al backend desplegado.

---

## 4. Reglas de Negocio Implementadas

### 4.1 Recibos
- Un recibo se marca como pagado solo cuando `monto_pagado >= total_recibo`.
- Soporte de pagos parciales con saldo pendiente.
- Recalculo mensual según gastos del periodo + configuración de administración.

### 4.2 Gastos
- Cada gasto mantiene saldo con base en sus pagos asociados (`pagos_gastos`).
- Pago manual de gastos desde panel admin.

### 4.3 Aplicación FIFO
- Al pagar recibos, el backend distribuye automáticamente ese monto a gastos pendientes del mismo mes (FIFO por fecha e id).

### 4.4 Precisión monetaria
- Cálculo y validación monetaria con redondeo a 2 decimales para evitar errores por punto flotante.

---

## 5. Estructuras de Datos Integradas

| Estructura | Uso en el sistema |
|---|---|
| `ArbolPropietariosBST` | Búsqueda estructurada de propietarios |
| `ArbolRecibosBST` | Consultas por deuda/rango en recibos |
| `ArbolRecibosAVL` | Búsqueda por saldo con balanceo |
| `ColaPrioridadMorosos` | Top de morosos por prioridad |
| `MatrizRecibos` | Organización y agregación por mes/propietario |
| `ListaPropietarios` | Recorrido secuencial encapsulado |

---

## 6. Endpoints Representativos

- **Auth:** `/api/login`, `/api/recuperar-contrasena`, `/api/mi-contrasena`
- **Perfil:** `/api/mi-perfil`
- **Propietarios:** `/api/propietarios`, `/api/propietarios/busqueda`
- **Gastos:** `/api/gastos`, `/api/gastos/<id>/pagar`
- **Recibos:** `/api/recibos`, `/api/recibos/generar`, `/api/recibos/recalcular`, `/api/recibos/<id>/pagar`
- **Estructuras:** `/api/recibos/estructura/bst`, `/api/recibos/estructura/avl`, `/api/recibos/morosos/prioridad`

---

## 7. Frontend y UX relevantes

- Menú responsivo (incluye hamburguesa en móvil).
- Modal de confirmación para acciones críticas.
- Filtros de búsqueda para propietarios, gastos y recibos.
- Estado visual de pendientes/pagados.
- Control de visibilidad de contraseña con iconos.

---

## 8. Despliegue Recomendado

| Componente | Plataforma |
|---|---|
| Frontend | GitHub Pages |
| Backend API | Render Web Service |
| Base de datos | PostgreSQL (Render) |

---

## 9. Estado del Integrador

- Proyecto funcional de extremo a extremo.
- Enfoque actual: estabilidad funcional + documentación académica.
- Línea de evolución: modelo de datos normalizado ampliado (TO-BE) sin romper compatibilidad del AS-IS.

---

## 10. Referencias internas

- `backend/schema.sql`
- `backend/app.py`
- `backend/structures.py`
- `js/admin.js`
- `DOCUMENTACION_TECNICA.md`

---

**Versión integrador:** 4.0  
**Fecha:** Mayo 2026
