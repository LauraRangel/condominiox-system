# CondominioX — Guía de Uso

Sistema web para gestión de condominio con roles `Administrador` y `Propietario`, autenticación JWT, pagos parciales, comunicados y reportes en Excel.

## Acceso

1. Abrir `index.html`.
2. Seleccionar tipo de usuario.
3. Ingresar usuario y contraseña.

> La contraseña inicial de cada propietario es su **DNI**.

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
- **Generar recibos** para todos los propietarios en una fecha específica.
- **Recalcular mes**: actualiza montos de un mes ya generado.
- Ver recibos **pendientes** o **pagados**, filtrados por mes.
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

### Historial de Pagos
- Ver recibos pagados con detalle de montos y fecha de pago.
- Filtrar por mes.

### Comunicados
- Ver anuncios publicados por el administrador (solo los activos/no caducados).
- Filtrar por tipo y estado (leído / sin leer).
- Badge en el menú indica cuántos comunicados no han sido leídos.

### Mi Perfil
- Cambiar contraseña.

---

## Reglas de pago

- Un recibo se marca como **pagado** cuando `monto_pagado >= total_recibo`.
- Los pagos parciales actualizan el saldo en tiempo real.
- Al pagar un recibo, el monto se distribuye automáticamente a los gastos pendientes del mismo mes (**FIFO**).

## Recuperación de contraseña

Flujo en `recuperar.html`: ingresar usuario + DNI + nueva contraseña.

## Seguridad

- JWT stateless — el token expira y se elimina al cerrar sesión.
- Guardias de rol en el frontend: un propietario que intente acceder a `admin.html` es redirigido a login.
- Todos los intentos de acceso no autorizado se registran en el backend con logs estructurados JSON.
- Los mensajes de error de login son genéricos (no revelan si el usuario existe o el rol incorrecto).

## Estructuras de datos en uso

| Estructura | Dónde |
|---|---|
| BST (árbol binario de búsqueda) | Búsqueda de propietarios en backend |
| AVL (árbol balanceado) | Búsqueda de recibos por rango de saldo |
| Cola de prioridad | Ranking automático de morosos |
| Pila | Historial de filtros en búsqueda estructurada |
| Índice hash (`Map`) | Filtros rápidos de gastos por mes/tipo |
| Lista enlazada | Recorrido secuencial de propietarios |
| Matriz | Organización de recibos por mes y propietario |

## Despliegue

| Componente | Plataforma |
|---|---|
| Frontend | GitHub Pages |
| Backend | Render Web Service |
| Base de datos | PostgreSQL (Render) |

> Si no ves cambios de frontend, forzar recarga con `Ctrl/Cmd + Shift + R`.

---

**Versión:** 5.0  
**Fecha:** Junio 2026
