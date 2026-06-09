# CondominioX System — Documento Integrador

Sistema web de gestión de condominio con autenticación JWT, arquitectura MVC+DAO, principios SOLID y estructuras de datos académicas integradas en el backend.

---

## 1. Alcance Funcional (Casos de Uso implementados)

| CU | Descripción | Estado |
|---|---|---|
| CU01 | Login con roles (Administrador / Propietario) | ✅ |
| CU02 | Gestión de propietarios (CRUD) | ✅ |
| CU03 | Configuración de monto de administración | ✅ |
| CU04 | Registro y pago de gastos (mantenimiento, luz, agua) | ✅ |
| CU05 | Generación de recibos por fecha | ✅ |
| CU06 | Recalculo mensual de recibos | ✅ |
| CU07 | Pago parcial/total de recibos (propietario) | ✅ |
| CU08 | Recuperación de contraseña | ✅ |
| CU09 | Cambio de contraseña | ✅ |
| CU10 | Edición de contacto (correo/teléfono) | ✅ |
| CU11 | Estado de cuenta individual por propietario | ✅ |
| CU12 | Historial de pagos con filtro por mes | ✅ |
| CU13 | Comunicados/Anuncios con fecha de caducidad | ✅ |
| CU14 | Estado financiero resumido por mes | ✅ |
| CU15 | Exportación de reporte de morosidad a Excel | ✅ |

---

## 2. Arquitectura Técnica

### Patrón MVC + DAO

```
backend/
  app.py                  ← Inicialización Flask, registro de blueprints, migraciones
  db.py                   ← Conexión y helpers SQL (fetch_all, fetch_one, execute_returning)
  middleware.py           ← Validación JWT, control de roles, logging de seguridad
  structures.py           ← Estructuras de datos (BST, AVL, Cola, Lista, Matriz)
  utils/
    money.py              ← to_decimal, money_float, round_money
    logger.py             ← Logger JSON estructurado (python-json-logger)
  dao/                    ← Acceso a datos (SQL puro)
    usuario_dao.py
    propietario_dao.py
    gasto_dao.py
    recibo_dao.py
    configuracion_dao.py
    anuncio_dao.py
  services/               ← Lógica de negocio pura
    auth_service.py
    propietario_service.py
    gasto_service.py
    recibo_service.py
    configuracion_service.py
    anuncio_service.py
    reporte_service.py
  routes/                 ← Controladores HTTP (Blueprints Flask)
    auth_routes.py
    propietario_routes.py
    gasto_routes.py
    recibo_routes.py
    configuracion_routes.py
    anuncio_routes.py
    reporte_routes.py
    health_routes.py

Frontend (estático — GitHub Pages):
  index.html              ← Login
  admin.html              ← Panel administrador
  propietario.html        ← Panel propietario
  recuperar.html          ← Recuperación de contraseña
  css/styles.css
  js/
    config.js             ← API_URL, helpers de auth, showToast, confirmModal
    auth.js               ← Login, guardias de rol, funciones UI comunes
    admin.js              ← Lógica panel administrador
    propietario.js        ← Lógica panel propietario
```

### Principios SOLID aplicados

| Principio | Aplicación concreta |
|---|---|
| **SRP** — Responsabilidad única | Cada archivo tiene una sola función: dao solo SQL, service solo lógica, route solo HTTP |
| **OCP** — Abierto/cerrado | Services reciben datos del DAO sin acoplarse a la BD; nuevos casos de uso = nuevos archivos |
| **DIP** — Inversión de dependencias | Routes dependen de services (no de DAO directamente); services dependen de DAO (no de Flask) |

---

## 3. Modelo de Datos

### Tablas activas

| Tabla | Descripción |
|---|---|
| `usuarios` | Credenciales y rol (Administrador / Propietario) |
| `propietarios` | Datos personales, depto., torre, vínculo a `usuario_id` |
| `gastos` | Gastos comunes con tipo (mantenimiento/luz/agua) y fecha |
| `pagos_gastos` | Pagos asociados a cada gasto |
| `configuracion` | Monto de administración mensual configurable |
| `recibos` | Montos por concepto, `monto_pagado`, estado y fechas |
| `anuncios` | Comunicados con tipo, `fecha_caducidad` y estado activo |
| `lecturas_anuncios` | Registro de qué propietario leyó qué anuncio |

### Migraciones automáticas

Al iniciar `app.py` se ejecutan:
- `CREATE TABLE IF NOT EXISTS` para las tablas opcionales.
- `ALTER TABLE anuncios ADD COLUMN IF NOT EXISTS fecha_caducidad DATE` para compatibilidad con bases de datos antiguas.

---

## 4. Reglas de Negocio

### Recibos
- Se generan para todos los propietarios activos en una fecha dada.
- Recalculo: recalcula usando gastos del mes + monto de administración vigente.
- Un recibo pasa a estado **pagado** cuando `monto_pagado >= total_recibo`.
- Pagos parciales dejan saldo pendiente visible al propietario.

### Pago FIFO
- Al pagar un recibo, el monto se distribuye a gastos pendientes del mismo mes en orden de fecha/id (First In, First Out).
- Implementado en `recibo_service.aplicar_pago_fifo()`.

### Gastos
- Cada gasto tiene saldo propio basado en `pagos_gastos`.
- El administrador puede pagar gastos manualmente desde el panel.

### Anuncios
- El propietario solo ve anuncios con `activo = TRUE` y `fecha_caducidad IS NULL OR fecha_caducidad >= CURRENT_DATE`.
- El administrador ve y gestiona todos.

### Precisión monetaria
- Todos los cálculos usan `Decimal` de Python para evitar errores de punto flotante.
- Resultados redondeados a 2 decimales antes de devolver al frontend.

---

## 5. Estructuras de Datos

| Estructura | Clase | Uso |
|---|---|---|
| Lista enlazada | `ListaPropietarios` | Recorrido secuencial de propietarios |
| BST | `ArbolPropietariosBST` | Búsqueda de propietarios por DNI/nombre |
| BST | `ArbolRecibosBST` | Consultas de recibos por rango de saldo |
| AVL | `ArbolRecibosAVL` | Búsqueda balanceada por deuda |
| Cola de prioridad | `ColaPrioridadMorosos` | Ranking de morosos (mayor saldo + más días) |
| Matriz | `MatrizRecibos` | Organización de recibos por mes/propietario |
| Pila (`PilaFiltros`) | JS frontend | Historial de filtros aplicados |
| Índice hash (`IndiceGastos`) | JS frontend | Acceso O(1) a gastos por mes/tipo |

---

## 6. Librerías y Equivalencias Académicas

| Librería Python | Equivalente académico | Uso en el proyecto |
|---|---|---|
| `openpyxl` | Apache POI (Java) | Generar reporte Excel de morosidad |
| `python-json-logger` | Logback (Java) | Logs estructurados JSON en backend |
| `validators` | Apache Commons Validator | Validación de formato de correo |
| `python-dateutil` | Apache Commons Lang | Manejo de fechas |
| `PyJWT` | JJWT (Java) | Firma y validación de tokens JWT |
| `psycopg[binary]` | JDBC (Java) | Conexión a PostgreSQL |

---

## 7. Seguridad

- **JWT stateless**: tokens firmados con `JWT_SECRET`, validados en cada request por `middleware.py`.
- **Control de roles**: `require_roles()` en cada endpoint protegido; si el rol no coincide → 403.
- **Guardias frontend**: `auth.js` verifica `userData.tipo` al cargar `admin.html` y `propietario.html` — redirige a login si no coincide.
- **Sin revelación de información**: todos los errores de login retornan `"Usuario o contraseña inválidos"` sin indicar si el usuario existe o qué rol tiene.
- **Logging de seguridad**: cada intento fallido (token ausente, rol incorrecto, credenciales inválidas) se registra con IP, ruta, método y usuario en formato JSON estructurado.

---

## 8. Endpoints Completos

### Auth
| Método | Endpoint | Rol |
|---|---|---|
| POST | `/api/login` | Público |
| POST | `/api/recuperar-contrasena` | Público |
| GET | `/api/mi-perfil` | Autenticado |
| PUT | `/api/mi-contrasena` | Autenticado |

### Propietarios
| Método | Endpoint | Rol |
|---|---|---|
| GET | `/api/propietarios` | Admin |
| POST | `/api/propietarios` | Admin |
| PUT | `/api/propietarios/<id>` | Admin |
| DELETE | `/api/propietarios/<id>` | Admin |
| GET | `/api/propietarios/busqueda` | Admin |
| GET | `/api/propietarios/<id>/estado-cuenta` | Admin |
| PUT | `/api/propietarios/<id>/contacto` | Propietario |

### Gastos
| Método | Endpoint | Rol |
|---|---|---|
| GET | `/api/gastos` | Admin |
| POST | `/api/gastos` | Admin |
| DELETE | `/api/gastos/<id>` | Admin |
| POST | `/api/gastos/<id>/pagar` | Admin |

### Recibos
| Método | Endpoint | Rol |
|---|---|---|
| GET | `/api/recibos` | Admin |
| POST | `/api/recibos/generar` | Admin |
| POST | `/api/recibos/recalcular` | Admin |
| DELETE | `/api/recibos/<id>` | Admin |
| POST | `/api/recibos/<id>/pagar` | Admin / Propietario |
| GET | `/api/recibos/propietario/<id>` | Admin / Propietario |
| GET | `/api/recibos/estructura/bst` | Admin |
| GET | `/api/recibos/estructura/avl` | Admin |
| GET | `/api/recibos/morosos/prioridad` | Admin |

### Anuncios
| Método | Endpoint | Rol |
|---|---|---|
| GET | `/api/anuncios` | Admin |
| POST | `/api/anuncios` | Admin |
| DELETE | `/api/anuncios/<id>` | Admin |
| GET | `/api/comunicados` | Propietario |
| POST | `/api/comunicados/<id>/leer` | Propietario |

### Reportes
| Método | Endpoint | Rol |
|---|---|---|
| GET | `/api/reportes/financiero` | Admin |
| GET | `/api/reportes/morosidad/excel` | Admin |

### Configuración
| Método | Endpoint | Rol |
|---|---|---|
| GET | `/api/configuracion` | Admin |
| PUT | `/api/configuracion` | Admin |

---

## 9. Variables de Entorno (Backend)

| Variable | Descripción | Requerida |
|---|---|---|
| `DATABASE_URL` | Cadena de conexión PostgreSQL | Sí |
| `JWT_SECRET` | Clave para firmar tokens | Sí |
| `JWT_EXPIRES_SECONDS` | Tiempo de vida del token (default: 86400) | No |

---

## 10. Despliegue

| Componente | Plataforma |
|---|---|
| Frontend | GitHub Pages (`LauraRangel/condominiox-system`) |
| Backend API | Render Web Service |
| Base de datos | PostgreSQL en Render |

**URL producción:** `https://condominiox-system.onrender.com/api`

---

## 11. Referencias internas

- [backend/structures.py](backend/structures.py) — Estructuras de datos
- [backend/app.py](backend/app.py) — Init y migraciones
- [backend/middleware.py](backend/middleware.py) — Auth y seguridad
- [js/config.js](js/config.js) — Helpers frontend, toast, confirmModal
- [DOCUMENTACION_TECNICA.md](DOCUMENTACION_TECNICA.md) — Detalle HTML/CSS/JS

---

**Versión integrador:** 5.0  
**Fecha:** Junio 2026
