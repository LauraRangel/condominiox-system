# CondominioX — Guía de Uso

Sistema web de gestión de un condominio residencial con dos roles: **Administrador** y **Propietario**.

Incluye recibos con pagos parciales, una pasarela de pagos emulada, reserva de áreas comunes con garantía, un asistente virtual con IA, documentos del condominio, comunicados, reportes en Excel y comprobantes imprimibles.

| | |
|---|---|
| **Aplicación** | https://laurarangel.github.io/condominiox-system/ |
| **API** | `https://condominiox-system.onrender.com/api` |
| **Versión** | 5.1 — Noviembre 2026 |

---

## Acceso

1. Abrir la aplicación (`index.html`).
2. Elegir el tipo de usuario: Administrador o Propietario.
3. Ingresar usuario y contraseña.

- La contraseña inicial de cada propietario es su **DNI**. Mientras no la cambie, el panel muestra un aviso para que lo haga.
- Tras **5 intentos fallidos** seguidos, el login queda bloqueado **15 minutos** para ese usuario y esa IP.
- La sesión dura **1 hora** por defecto. Después hay que volver a ingresar.
- El servidor del plan gratuito de Render se duerme cuando no hay uso. La primera petición puede tardar entre 30 y 60 segundos. Si aparece un error de conexión, espera unos segundos y reintenta.

---

## Casos de uso

| CU | Descripción | Rol |
|---|---|---|
| CU01 | Login con roles | Admin / Propietario |
| CU02 | CRUD de propietarios | Admin |
| CU03 | Configurar el monto de administración | Admin |
| CU04 | Registro y pago de gastos | Admin |
| CU05 | Generar recibos por fecha | Admin |
| CU06 | Recalcular los recibos del mes | Admin |
| CU07 | Registrar pago parcial o total de un recibo (efectivo/transferencia) | Admin |
| CU08 | Recuperar contraseña | Admin / Propietario |
| CU09 | Cambiar contraseña | Admin / Propietario |
| CU10 | Editar contacto (correo y teléfono) | Propietario |
| CU11 | Estado de cuenta individual | Admin |
| CU12 | Historial de pagos con filtro por mes | Admin / Propietario |
| CU13 | Comunicados con fecha de caducidad | Admin / Propietario |
| CU14 | Estado financiero resumido | Admin |
| CU15 | Exportar la morosidad a Excel | Admin |
| CU16 | Comprobante de recibo imprimible | Admin / Propietario |
| CU17 | Pago en línea por pasarela emulada (tarjeta, Yape, Mercado Pago) | Propietario |
| CU18 | Reserva de áreas comunes con garantía | Propietario / Admin |
| CU19 | Asistente virtual con IA | Propietario |
| — | Documentos del condominio (PDF y reglamento) | Admin / Propietario |

---

## Funciones del Administrador

### Dashboard
- Indicadores: total de propietarios, recibos pendientes y pagados, gastos del mes.
- Resumen financiero mensual: emitido, cobrado, saldo pendiente, porcentaje de cobranza y desglose por concepto (administración, agua, luz, mantenimiento, reservas).
- Configurar el **monto de administración** mensual.

### Propietarios
- Crear propietarios con su usuario y sus datos personales: nombre, apellido, DNI, departamento, torre, correo y teléfono.
- Editar y eliminar propietarios.
- Ver el **estado de cuenta individual** de cada uno, filtrado por rango de meses.
- Buscar por nombre, apellido, DNI o departamento, y filtrar por torre y piso.

### Gastos
- Registrar gastos de **mantenimiento**, **luz** y **agua** desde un modal con pestañas.
- Filtrar por mes, categoría y estado (pendiente o pagado).
- Pagar y eliminar gastos.

### Recibos
- **Generar recibos** para todos los propietarios en una fecha.
- **Recalcular** un mes ya generado.
- Ver recibos **pendientes** o **pagados** por mes.
- Registrar pagos manuales (efectivo o transferencia).
- Ver el **comprobante** de cualquier recibo (botón 🧾).
- **Morosos**: ranking automático por saldo pendiente y días sin pagar.
- **Exportar Excel** con el reporte de morosidad (`.xlsx`).
- Búsqueda avanzada por rango de saldo (BST o AVL), con historial de filtros.

### Pagos y Reservas
- **Transacciones** de la pasarela con indicadores y filtros por rango de fechas, área, propietario, departamento, concepto, estado del pago y estado de la reserva.
- **Reservas** de todos los propietarios: ver invitados (e imprimir la lista para portería), cancelar y **resolver la garantía** (devolución total, parcial o retención, con motivo).
- **Áreas comunes**: editar tarifa, garantía, aforo, horario, anticipación mínima, duración máxima y tipo de uso, y activar o desactivar cada área.

### Anuncios
- Crear anuncios con título, contenido, tipo (informativo, pago o mantenimiento) y fecha de caducidad.
- Eliminar anuncios. Los caducados dejan de verse en el panel del propietario.

### Documentos
- Subir **PDF de hasta 5 MB** con título, categoría, descripción y visibilidad (público o privado).
- Publicar, ocultar y eliminar documentos. El asistente IA solo lee los públicos.

### Mi Perfil
- Cambiar la contraseña.

---

## Funciones del Propietario

### Mi Información
- Ver nombre, DNI, departamento, torre, correo y teléfono.
- Editar correo y teléfono.
- Indicadores: recibos pendientes y monto total por pagar.

### Recibos Pendientes
- Ver los recibos sin pagar con su desglose (administración, agua, luz, mantenimiento, reservas y saldo).
- **Pagar en línea**: elegir el monto (o "Pagar total") y el medio de pago.
- Ver el comprobante (botón 🧾).

### Historial de Pagos
- Ver los recibos pagados con sus montos y fecha de pago, filtrados por mes.
- Ver el comprobante de cada uno.

### Reservas
- Elegir un área y un día. El calendario muestra los horarios libres y ocupados.
- Indicar el número de personas y registrar a los **invitados**, a mano o importando un CSV.
- Si el área cobra garantía, la reserva queda en espera **30 minutos** hasta pagarla. Si no se paga, se libera el horario.
- Ver y cancelar las reservas propias. Al cancelar antes del inicio, la garantía se devuelve completa.

### Asistente IA
- Responde preguntas en lenguaje natural sobre el reglamento, los documentos públicos, los recibos y pagos propios, las reservas, los gastos del edificio y la **disponibilidad de las áreas comunes**. Por ejemplo: *"¿Está libre la zona de parrillas mañana a las 3pm?"*
- Cada respuesta cita sus fuentes; al pulsar una, se abre el artículo o el PDF.
- Solo usa datos del propio propietario, nunca de otros.

### Comunicados
- Ver los anuncios activos y no caducados.
- Filtrar por tipo y estado (leído o sin leer). Un contador en el menú indica los no leídos.
- Marcar comunicados como leídos.

### Documentos
- Consultar el **reglamento** con índice y buscador.
- Ver y descargar los PDF publicados.

### Mi Perfil
- Cambiar la contraseña.
- Recuperar la contraseña desde `recuperar.html` (usuario + DNI + nueva contraseña).

---

## Pagos de prueba (pasarela emulada)

Ningún pago es real: la pasarela emula Culqi, Yape y Mercado Pago en modo sandbox.

| Medio | Aprobado | Rechazado |
|---|---|---|
| Tarjeta | `4111 1111 1111 1111` | `4000 0000 0000 0002` |
| Yape | cualquier OTP de 6 dígitos | OTP `000000` |
| Mercado Pago | cualquier correo | correo que contenga `rechazo` |

---

## Áreas comunes (valores iniciales)

El administrador puede cambiar estos valores desde "Pagos y Reservas".

| Área | Tarifa | Garantía | Uso | Aforo | Horario | Anticipación | Duración máx. |
|---|---|---|---|---|---|---|---|
| Salón de usos múltiples | S/ 80 | S/ 200 | Exclusivo | 40 | 09:00–23:00 | 48 h | 5 h |
| Zona de parrillas | S/ 50 | S/ 100 | Exclusivo | 15 | 11:00–22:00 | 24 h | 4 h |
| Gimnasio | — | — | Compartido | 8 | 06:00–22:00 | 1 h | 2 h |
| Cowork | — | — | Compartido | 12 | 07:00–22:00 | 1 h | 4 h |
| Pet shower | S/ 15 | S/ 30 | Exclusivo | 2 | 08:00–20:00 | 2 h | 1 h |

---

## Reglas de negocio

- Un recibo está **pagado** cuando `monto_pagado >= total_recibo`. Los pagos parciales actualizan el saldo al momento.
- Al pagar un recibo, el monto se reparte entre los gastos pendientes del mismo mes, del más antiguo al más reciente (**FIFO**).
- La **tarifa** de una reserva se suma al recibo del mes. La **garantía** no va al recibo: se paga aparte y se devuelve o retiene después del uso.
- Un propietario con recibos vencidos (más de 30 días sin pagar) no puede reservar.
- En un área de **uso exclusivo** no se aceptan reservas que se crucen. En una **compartida** (gimnasio, cowork) sí, mientras no se supere el aforo.
- Los comunicados caducan solos según su fecha de caducidad.

---

## Seguridad

- Sesión con **JWT** que expira y se borra al cerrar sesión.
- Contraseñas de al menos 8 caracteres, con letras y números, distintas del DNI.
- Bloqueo temporal ante intentos repetidos de login o de recuperación.
- Un propietario no puede entrar al panel de administrador ni ver datos de otros propietarios.
- Los mensajes de error del login no revelan si el usuario existe.
- El número de tarjeta nunca sale del navegador: solo viaja un token.

---

## Estructuras de datos

| Estructura | Clase | Uso |
|---|---|---|
| Lista enlazada | `ListaPropietarios` | Recorrido de propietarios |
| BST | `ArbolPropietariosBST` | Búsqueda de propietarios por DNI |
| BST | `ArbolRecibosBST` | Búsqueda de recibos por rango de saldo |
| AVL | `ArbolRecibosAVL` | Búsqueda balanceada O(log n) garantizada |
| Cola de prioridad | `ColaPrioridadMorosos` | Ranking de morosos |
| Matriz dispersa | `MatrizRecibos` | Recibos por mes y propietario |
| Pila (JS) | `PilaFiltros` | Historial de filtros de la búsqueda avanzada |
| Índice hash (JS) | `IndiceGastos` | Filtros rápidos de gastos por mes y tipo |
| Índice TF-IDF | `services/rag.py` | Búsqueda en reglamento y documentos para el asistente |

---

## Despliegue

| Componente | Plataforma |
|---|---|
| Frontend | GitHub Pages (rama `main`) |
| Backend | Render Web Service (Flask + Gunicorn) |
| Base de datos | PostgreSQL gestionado por Render |
| LLM del asistente | Groq (`openai/gpt-oss-120b`) |

Cada merge a `main` publica el frontend y redespliega el backend. El detalle está en [DEPLIEGUE.md](DEPLIEGUE.md).

> Si no ves los cambios del frontend, fuerza la recarga con `Ctrl/Cmd + Shift + R`.

---

## Más documentación

- [README_INTEGRADOR.md](README_INTEGRADOR.md): documento técnico integrador (arquitectura, endpoints, pruebas, CI, APF3).
- [DOCUMENTACION_TECNICA.md](DOCUMENTACION_TECNICA.md): detalle de HTML, CSS, JS, esquema SQL, estructuras y seguridad.
- [DEPLIEGUE.md](DEPLIEGUE.md): flujo de despliegue y operación en producción.

---

**Versión:** 5.1 — Noviembre 2026
