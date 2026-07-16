# CondominioX — Guía de Uso

Sistema web para gestión de condominio residencial con roles `Administrador` y `Propietario`, autenticación JWT, pagos parciales, comunicados, reportes en Excel y descarga de comprobantes digitales.

## Acceso

1. Abrir `index.html`.
2. Seleccionar tipo de usuario (Administrador o Propietario).
3. Ingresar nombre de usuario y contraseña.

> La contraseña inicial de cada propietario es su **DNI**.

---

## Casos de Uso implementados

| CU | Descripción | Rol |
|---|---|---|
| CU01 | Login con roles | Admin / Propietario |
| CU02 | CRUD propietarios | Admin |
| CU03 | Configurar monto administración | Admin |
| CU04 | Registro y pago de gastos | Admin |
| CU05 | Generar recibos por fecha | Admin |
| CU06 | Recalcular recibos del mes | Admin |
| CU07 | Pago parcial/total de recibo | Admin / Propietario |
| CU08 | Recuperar contraseña | Admin / Propietario |
| CU09 | Cambiar contraseña | Admin / Propietario |
| CU10 | Editar contacto (correo/teléfono) | Admin / Propietario |
| CU11 | Estado de cuenta individual | Admin |
| CU12 | Historial de pagos con filtro mes | Admin / Propietario |
| CU13 | Comunicados con fecha caducidad | Admin / Propietario |
| CU14 | Estado financiero resumido | Admin |
| CU15 | Exportar morosidad a Excel | Admin |
| CU16 | Descargar comprobante de recibo (PDF) | Admin / Propietario |

---

## Funciones del Administrador

### Dashboard
- Indicadores generales: total de propietarios, recibos pendientes/pagados, gastos del mes.
- Resumen financiero mensual: total emitido, total cobrado, saldo pendiente, porcentaje de cobranza y desglose por concepto (administración, agua, luz, mantenimiento).
- Configurar el **monto de administración** mensual.

### Propietarios
- Crear propietario con usuario y datos personales (nombre, apellido, DNI, depto., torre, correo, teléfono).
- Editar todos los datos del propietario.
- Eliminar propietario.
- Ver **estado de cuenta individual** desde la tabla (modal con recibos filtrados por rango de fechas).
- Filtros de búsqueda por nombre/apellido/DNI/departamento, torre y piso.

### Gastos
- Registrar gastos de **mantenimiento**, **luz** y **agua** desde un modal con pestañas.
- Filtrar por mes, categoría y estado (pendiente / pagado).
- Pagar gastos manualmente.
- Eliminar gastos.

### Recibos
- **Generar recibos** para todos los propietarios en una fecha específica (masivo).
- **Recalcular mes**: actualiza montos de un mes ya generado.
- Ver recibos **pendientes** o **pagados**, filtrados por mes.
- **Descargar comprobante** de cualquier recibo en formato PDF (botón 🧾).
- **Morosos**: lista automática de propietarios con mayor saldo pendiente y días sin pagar.
- **Exportar Excel**: descarga el reporte de morosos en formato `.xlsx`.
- Búsqueda avanzada por rango de saldo (desplegable).
- Resumen mensual al pie de la sección.

### Anuncios
- Crear anuncios con título, contenido, tipo (informativo / pago / mantenimiento) y fecha de caducidad.
- Eliminar anuncios.
- Los anuncios caducados dejan de aparecer en el panel del propietario.

### Mi Perfil
- Cambiar contraseña con validación de la actual.

---

## Funciones del Propietario

### Mi Información
- Ver nombre, DNI, departamento, torre, correo y teléfono.
- Editar correo y teléfono directamente desde la vista.
- Indicadores rápidos: recibos pendientes y monto total por pagar.

### Recibos Pendientes
- Ver todos los recibos sin pagar con desglose (administración, agua, luz, mantenimiento, saldo).
- **Pagar recibo**: modal con monto ingresable y botón "Pagar total" para pago completo.
- **Descargar comprobante** del recibo en formato PDF (botón 🧾).

### Historial de Pagos
- Ver recibos pagados con detalle de montos y fecha de pago.
- **Descargar comprobante** de cualquier recibo pagado (botón 🧾).
- Filtrar por mes.

### Comunicados
- Ver anuncios publicados por el administrador (solo los activos y no caducados).
- Filtrar por tipo y estado (leído / sin leer).
- Badge en el menú indica cuántos comunicados no han sido leídos.
- Marcar comunicados como leídos.

### Mi Perfil
- Cambiar contraseña.
- Recuperar contraseña desde `recuperar.html` (usuario + DNI + nueva contraseña).

---

## Comprobante de Recibo (CU16)

Al pulsar el botón 🧾 en cualquier tabla de recibos se abre un comprobante digital con:
- Datos del propietario (nombre, DNI, departamento, torre).
- Desglose por concepto (administración, agua, luz, mantenimiento).
- Total, monto pagado y saldo pendiente.
- Estado del recibo (PAGADO / PENDIENTE) y fechas.

El botón **Imprimir / Guardar PDF** abre el diálogo de impresión del navegador, que permite guardar el comprobante directamente como PDF.

---

## Reglas de negocio

- Un recibo se marca como **pagado** cuando `monto_pagado >= total_recibo`.
- Los pagos parciales actualizan el saldo en tiempo real.
- Al pagar un recibo, el monto se distribuye automáticamente a los gastos pendientes del mismo mes en orden cronológico (**FIFO**).
- Los comunicados caducan automáticamente según su `fecha_caducidad`.

---

## Seguridad

- JWT stateless — el token expira en 24 h y se elimina al cerrar sesión.
- Guardias de rol en el frontend: un propietario que intente acceder a `admin.html` es redirigido al login.
- Todos los intentos de acceso no autorizado se registran en el backend con logs estructurados JSON (IP, ruta, usuario, rol).
- Los mensajes de error de login son genéricos — no revelan si el usuario existe o cuál es su rol.

---

## Estructuras de datos

| Estructura | Tipo | Dónde se usa |
|---|---|---|
| Lista enlazada | `ListaPropietarios` | Recorrido secuencial de propietarios |
| BST | `ArbolPropietariosBST` | Búsqueda de propietarios por DNI |
| BST | `ArbolRecibosBST` | Búsqueda de recibos por rango de saldo |
| AVL | `ArbolRecibosAVL` | Búsqueda balanceada garantizada O(log n) |
| Cola de prioridad | `ColaPrioridadMorosos` | Ranking automático de morosos |
| Matriz dispersa | `MatrizRecibos` | Organización de recibos por mes/propietario |
| Pila (JS) | `PilaFiltros` | Historial de filtros en búsqueda avanzada |
| Índice hash (JS) | `IndiceGastos` | Filtros rápidos de gastos por mes/tipo |

---

## Despliegue

| Componente | Plataforma |
|---|---|
| Frontend | GitHub Pages |
| Backend | Render Web Service |
| Base de datos | PostgreSQL (Render) |

**URL producción:** `https://condominiox-system.onrender.com/api`

> Si no ves cambios en el frontend, forzar recarga con `Ctrl/Cmd + Shift + R`.

---

**Versión:** 5.0 — Junio 2026
