# CondominioX — Contexto del Proyecto

Sistema web de gestión de condominio residencial con dos roles: **Administrador** y **Propietario**.
Versión actual: **5.0 — Junio 2026**.

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Frontend | HTML + CSS + JavaScript vanilla (sin frameworks) |
| Backend | Python 3 + Flask 3.1 + Gunicorn |
| Base de datos | PostgreSQL (Render Managed) |
| Autenticación | JWT stateless (PyJWT) — Bearer token |
| Despliegue frontend | GitHub Pages |
| Despliegue backend | Render Web Service |
| URL producción | `https://condominiox-system.onrender.com/api` |

---

## Estructura de carpetas

```
sistema-condominio/
  index.html              ← Login (paso 1: tipo usuario, paso 2: form)
  admin.html              ← Panel administrador
  propietario.html        ← Panel propietario
  recuperar.html          ← Recuperación de contraseña
  css/
    styles.css            ← Estilos únicos (versión ?v=20260609)
  js/
    config.js             ← API_URL, apiFetch, helpers auth, showToast, confirmModal
    auth.js               ← Login, cerrarSesion, guardias de rol, toggleContrasenas
    admin.js              ← Lógica completa panel admin (clases PilaFiltros, IndiceGastos)
    propietario.js        ← Lógica completa panel propietario
  img/
    logo.png
  backend/
    app.py                ← Solo crea Flask app, registra blueprints, migraciones
    config.py             ← Variables de entorno (JWT_SECRET, DATABASE_URL)
    db.py                 ← Helpers SQL: execute, fetch_all, fetch_one, get_db
    middleware.py         ← Validación JWT, require_roles, logging seguridad
    security.py           ← hash_password, verify_password
    structures.py         ← Todas las estructuras de datos
    utils/
      money.py            ← to_decimal, round_money, money_float (usa Decimal Python)
      logger.py           ← get_logger(name) — python-json-logger JSON estructurado
    dao/
      usuario_dao.py
      propietario_dao.py
      gasto_dao.py
      recibo_dao.py
      configuracion_dao.py
      anuncio_dao.py
    services/
      auth_service.py
      propietario_service.py
      gasto_service.py
      recibo_service.py
      configuracion_service.py
      anuncio_service.py
      reporte_service.py
    routes/
      auth_routes.py
      propietario_routes.py
      gasto_routes.py
      recibo_routes.py
      configuracion_routes.py
      anuncio_routes.py
      reporte_routes.py
      health_routes.py
    tests/
      conftest.py          ← fixture client (Flask test_client) + limpieza de tablas
      unit/                ← structures.py, money.py, security.py (sin DB, 100% cobertura)
      integration/          ← rutas Flask reales contra Postgres (auth, CRUD propietarios)
    schema.sql
    requirements.txt
    requirements-dev.txt   ← pytest, pytest-cov, pytest-mock, freezegun
    pytest.ini
    .env.test.example      ← plantilla; .env.test real no se versiona
.github/
  workflows/
    tests.yml              ← pytest (unit+integration) con Postgres como service container
    codeql.yml              ← SAST Python + JS/TS
    dependency-review.yml   ← falla el PR si se introduce una dependencia con CVE alto/crítico
  dependabot.yml            ← PRs semanales de actualización (pip + github-actions)
```

---

## Arquitectura: MVC + DAO

```
Frontend JS  →  HTTP REST/JSON (Bearer JWT)  →  Routes (Controller)
                                                      ↓ delega
                                                 Services (Lógica)
                                                      ↓ consulta
                                                   DAO (SQL)
                                                      ↓
                                                  PostgreSQL

Services  →  instancia  →  Estructuras de datos (BST, AVL, Cola, Matriz, Lista)
```

**Regla dura:** Routes nunca tocan SQL. Services nunca importan Flask. DAO nunca tiene lógica de negocio.

---

## Base de datos — 8 tablas

| Tabla | Descripción |
|---|---|
| `usuarios` | Credenciales + rol (Administrador / Propietario) |
| `propietarios` | Datos personales, depto, torre, `usuario_id` FK |
| `gastos` | Gastos comunes: tipo (mantenimiento/luz/agua), monto, fecha |
| `pagos_gastos` | Pagos asociados a cada gasto (creada por migración automática) |
| `configuracion` | Monto de administración mensual configurable |
| `recibos` | Montos por concepto, `monto_pagado`, estado pagado, fechas |
| `anuncios` | Título, contenido, tipo, `fecha_caducidad`, activo |
| `lecturas_anuncios` | Qué propietario leyó qué anuncio (UNIQUE anuncio+propietario) |

Migraciones automáticas en `app.py`: `CREATE TABLE IF NOT EXISTS` + `ALTER TABLE anuncios ADD COLUMN IF NOT EXISTS fecha_caducidad`.

---

## Casos de Uso implementados (15/15 ✅)

| CU | Descripción | Endpoint principal |
|---|---|---|
| CU01 | Login con roles | `POST /api/login` |
| CU02 | CRUD propietarios | `GET/POST/PUT/DELETE /api/propietarios` |
| CU03 | Configurar monto administración | `GET/PUT /api/configuracion` |
| CU04 | Registro y pago de gastos | `GET/POST/DELETE /api/gastos`, `POST /api/gastos/<id>/pagar` |
| CU05 | Generar recibos por fecha | `POST /api/recibos/generar` |
| CU06 | Recalcular recibos del mes | `POST /api/recibos/recalcular` |
| CU07 | Pago parcial/total de recibo | `POST /api/recibos/<id>/pagar` |
| CU08 | Recuperar contraseña | `POST /api/recuperar-contrasena` |
| CU09 | Cambiar contraseña | `PUT /api/mi-contrasena` |
| CU10 | Editar contacto (correo/teléfono) | `PUT /api/mi-perfil` |
| CU11 | Estado de cuenta individual | `GET /api/propietarios/<id>/estado-cuenta` |
| CU12 | Historial de pagos con filtro mes | `GET /api/recibos/propietario/<id>?estado=pagados` |
| CU13 | Comunicados con fecha caducidad | `GET/POST/DELETE /api/anuncios`, `GET /api/comunicados` |
| CU14 | Estado financiero resumido | `GET /api/reportes/financiero` |
| CU15 | Exportar morosidad a Excel | `GET /api/reportes/morosidad/excel` |

---

## Endpoints completos

### Auth (`/api`)
| Método | Endpoint | Rol |
|---|---|---|
| POST | `/api/login` | Público |
| POST | `/api/recuperar-contrasena` | Público |
| GET | `/api/mi-perfil` | Autenticado |
| PUT | `/api/mi-perfil` | Autenticado (correo + teléfono) |
| PUT | `/api/mi-contrasena` | Autenticado |

### Propietarios (`/api/propietarios`)
| Método | Endpoint | Rol |
|---|---|---|
| GET | `/api/propietarios` | Admin |
| GET | `/api/propietarios/busqueda?q=&torre=&piso=` | Admin |
| POST | `/api/propietarios` | Admin |
| PUT | `/api/propietarios/<id>` | Admin |
| DELETE | `/api/propietarios/<id>` | Admin |
| GET | `/api/propietarios/<id>/estado-cuenta?desde=YYYY-MM&hasta=YYYY-MM` | Admin |

### Gastos (`/api/gastos`)
| Método | Endpoint | Rol |
|---|---|---|
| GET | `/api/gastos` | Admin |
| POST | `/api/gastos` | Admin |
| DELETE | `/api/gastos/<id>` | Admin |
| POST | `/api/gastos/<id>/pagar` | Admin |

### Recibos (`/api/recibos`)
| Método | Endpoint | Rol |
|---|---|---|
| POST | `/api/recibos/generar` | Admin |
| POST | `/api/recibos/recalcular` | Admin |
| GET | `/api/recibos?estado=&mes=` | Admin |
| GET | `/api/recibos/propietario/<id>?estado=` | Admin / Propietario |
| POST | `/api/recibos/<id>/pagar` | Admin / Propietario |
| DELETE | `/api/recibos/<id>` | Admin |
| GET | `/api/recibos/estructura/bst?saldo_min=&saldo_max=&mes=&estado=` | Admin |
| GET | `/api/recibos/estructura/avl?saldo_min=&saldo_max=&mes=&estado=` | Admin |
| GET | `/api/recibos/morosos/prioridad?mes=&limit=` | Admin |

### Anuncios
| Método | Endpoint | Rol |
|---|---|---|
| GET | `/api/anuncios` | Admin |
| POST | `/api/anuncios` | Admin |
| DELETE | `/api/anuncios/<id>` | Admin |
| GET | `/api/comunicados` | Propietario |
| POST | `/api/comunicados/<id>/leer` | Propietario |

### Reportes / Configuración
| Método | Endpoint | Rol |
|---|---|---|
| GET | `/api/reportes/financiero?mes=YYYY-MM` | Admin |
| GET | `/api/reportes/morosidad/excel?mes=&limit=` | Admin |
| GET | `/api/configuracion` | Admin |
| PUT | `/api/configuracion` | Admin |

---

## Estructuras de datos (`backend/structures.py`)

Todas implementadas desde cero en Python, sin librerías externas.

| Clase | Tipo | Complejidad clave | Usada en |
|---|---|---|---|
| `ListaPropietarios` | Lista enlazada simple | insertar O(1), recorrer O(n) | `propietario_service.listar_propietarios()` |
| `ArbolPropietariosBST` | BST iterativo | insertar/buscar O(log n) | `propietario_service.buscar_propietarios()` |
| `ArbolRecibosBST` | BST con inorden/preorden/postorden/rango | rango O(log n + k) | `recibo_service.buscar_recibos_bst()` |
| `ArbolRecibosAVL` | AVL autobalanceado (hereda BST) | insertar O(log n) garantizado | `recibo_service.buscar_recibos_avl()` |
| `ColaPrioridadMorosos` | Max-heap manual | enqueue O(log n), to_sorted_list O(n log n) | `recibo_service.get_morosos_prioridad()`, `reporte_service.exportar_morosidad_excel()` |
| `MatrizRecibos` | Matriz dispersa dict[mes][pid] | set/get O(1) | `recibo_service.listar_recibos_admin()` |

**Estructuras JS (frontend):**
- `PilaFiltros` — historial de filtros aplicados en búsqueda estructurada (admin.js)
- `IndiceGastos` — índice hash O(1) por mes/tipo para filtros de gastos (admin.js)

**Herencia:** `ArbolRecibosAVL` hereda métodos `recorrer()` y `rango()` de `ArbolRecibosBST`, sobreescribe solo `insertar()` para agregar balanceo.

**Prioridad en `ColaPrioridadMorosos`:** `(saldo_pendiente, dias_pendiente)` descendente — mayor saldo + más días sin pagar = mayor prioridad.

---

## Librerías externas (`requirements.txt`)

| Librería | Versión | Equivalente Java académico | Uso |
|---|---|---|---|
| `openpyxl` | 3.1.5 | Apache POI | Genera reporte Excel morosidad con estilos |
| `python-json-logger` | 4.1.0 | Logback | Logs JSON estructurados en `utils/logger.py` |
| `validators` | 0.35.0 | Apache Commons Validator | Valida formato correo en `propietario_service` |
| `python-dateutil` | 2.9.0 | Apache Commons Lang | Calcula días pendientes en recibos |
| `PyJWT` | 2.13.0 | JJWT | Firma y valida tokens JWT |
| `psycopg[binary]` | — | JDBC | Conexión PostgreSQL |
| `Flask` | 3.1.3 | Spring MVC | Framework HTTP, Blueprints |
| `Flask-Cors` | 6.0.5 | Spring Web CORS | CORS para `/api/*` |

---

## Seguridad

- **JWT stateless:** token firmado con `JWT_SECRET`, validado en `middleware.py` en cada request.
- **Control de roles:** `require_roles(payload, "Administrador")` en endpoints protegidos → 403 si no coincide.
- **Guardia frontend:** `auth.js` verifica `userData.tipo` al cargar `admin.html` / `propietario.html` → redirige a login si el rol no coincide.
- **Sin revelación de info:** todos los errores de login retornan `"Usuario o contraseña inválidos"` sin indicar si existe el usuario o el rol.
- **Logging seguridad:** `middleware.py` registra con `python-json-logger` cada token ausente, expirado, inválido o rol incorrecto — campos: `event`, `ip`, `path`, `method`, `user`, `rol_actual`, `rol_requerido`.

---

## Reglas de negocio importantes

- **Contraseña inicial del propietario:** su DNI.
- **Recibo pagado:** cuando `monto_pagado >= total_recibo`.
- **Pago FIFO:** al pagar un recibo, el monto se distribuye a gastos pendientes del mismo mes en orden cronológico de registro (`recibo_service.aplicar_pago_fifo()`).
- **Precisión monetaria:** todos los cálculos usan `Decimal` de Python (`utils/money.py`), se convierten a float solo al serializar JSON.
- **Comunicados visibles para propietario:** solo `activo = TRUE` y `fecha_caducidad IS NULL OR fecha_caducidad >= CURRENT_DATE`.
- **Piso calculado:** función `_calcular_piso(nro_departamento)` — toma los dígitos, elimina los 2 últimos.

---

## Frontend — módulos JS

### config.js (compartido por todos los HTML)
- `API_URL = 'https://condominiox-system.onrender.com/api'`
- `AUTH_TOKEN_KEY = 'auth_token'`, `USER_DATA_KEY = 'user_data'`
- `apiFetch(path, options)` — fachada sobre fetch: adjunta token, prefija URL, maneja errores
- `getAuthToken()` / `setAuthToken()` / `removeAuthToken()`
- `getUserData()` / `setUserData()`
- `isAuthenticated()` / `requireAuth()`
- `formatDate()` / `formatMonthYear()` / `formatCurrency()`
- `showToast(message, type, title)` — notificaciones tipo toast
- `confirmModal(message, title, tipo)` — modal de confirmación Promise-based (compartido admin+propietario)
- `cerrarConfirmModal(accepted)`

### auth.js
- Maneja submit del `#loginForm` → POST `/api/login` → guarda token + userData → redirige por rol
- `cerrarSesion()`, `mostrarSeccion(id)`, `inicializarToggleContrasenas()`
- Guardias de rol al cargar `admin.html` y `propietario.html`

### admin.js
- `class PilaFiltros` — push/pop/peek/isEmpty para historial de filtros
- `class IndiceGastos` — Map indexado por `${mes}-${tipo}` para acceso O(1)
- Funciones principales: `cargarDashboard`, `cargarPropietarios`, `buscarPropietariosBackend`, `editarPropietario`, `eliminarPropietario`, `abrirModalGasto`, `switchGastoTab`, `submitGasto`, `pagarGasto`, `generarRecibos`, `recalcularRecibos`, `cargarRecibos`, `buscarConEstructura`, `guardarFiltroEstructura`, `deshacerFiltroEstructura`, `cargarTopMorosos`, `exportarMorosidadExcel`, `cargarAnuncios`, `crearAnuncio`, `eliminarAnuncio`, `verEstadoCuenta`, `filtrarEstadoCuenta`, `cargarResumenFinanciero`

### propietario.js
- `getPropietarioId()` — extrae id del userData en localStorage
- Funciones: `cargarInformacionPersonal`, `activarEdicionContacto`, `guardarContacto`, `cargarEstadisticas`, `cargarRecibosPendientes`, `pagarRecibo`, `usarMontoTotal`, `cerrarModalPago`, `confirmarPago`, `cargarRecibosPagados`, `filtrarPagadosPorMes`, `renderTablaRecibosPagados`, `cargarComunicados`, `filtrarComunicados`, `marcarLeido`, `cargarDatosSeccion`

---

## Patrones de diseño aplicados

| Patrón | Dónde |
|---|---|
| MVC | `routes/` (C) + `services/` (M lógica) + `HTML+JS` (V) |
| DAO | `dao/*.py` — SQL puro por entidad |
| SOLID SRP | Cada archivo tiene una sola responsabilidad |
| SOLID OCP | Nuevo CU = nuevo archivo, sin modificar existentes |
| SOLID DIP | Routes→Services→DAO, nunca al revés |
| Fachada | `config.js → apiFetch()` oculta detalles HTTP al resto del frontend |
| Estrategia | `recibo_service` elige BST o AVL según parámetro `estructura` |
| FIFO | `recibo_service.aplicar_pago_fifo()` distribuye pagos a gastos por fecha/id |
| Seguridad en capas | `middleware.py` + `auth.js` + `utils/logger.py` |

---

## Testing y CI

- **90 tests** en `backend/tests/`: 70 unitarias (`tests/unit/`, sin DB, 100% cobertura en `structures.py`/`utils/money.py`/`security.py`) + 20 de integración (`tests/integration/`, Flask `test_client()` contra Postgres real).
- Correr local: `cd backend && .venv/bin/pytest tests/unit -v` (unitarias, sin dependencias) o `.venv/bin/pytest tests/integration -v` (requiere Postgres con `schema.sql` aplicado y `.env.test` — ver `.env.test.example`).
- El entorno de desarrollo usa **podman**, no Docker — comandos `podman run` / `podman exec` en vez de `docker`.
- CI en `.github/workflows/tests.yml`: Postgres 16 como *service container*, corre `pytest --cov=.` en cada push/PR a `main`.
- `dependency-review.yml` complementa a `dependabot.yml`: Dependabot actualiza dependencias por schedule; Dependency Review bloquea un PR que introduce una dependencia nueva con CVE alto/crítico.

---

## Variables de entorno (backend)

| Variable | Descripción | Requerida |
|---|---|---|
| `DATABASE_URL` | Cadena conexión PostgreSQL | Sí |
| `JWT_SECRET` | Clave firma tokens | Sí |
| `JWT_EXPIRES_SECONDS` | TTL token (default: 86400) | No |

---

## Archivos de documentación existentes

| Archivo | Contenido |
|---|---|
| `README.md` | Guía de uso para el usuario final |
| `README_INTEGRADOR.md` | Documento técnico integrador v5.0 (CU, arquitectura, endpoints, SOLID, testing y CI) |
| `DOCUMENTACION_TECNICA.md` | Documentación técnica completa v5.0 (SQL schema, estructuras, seguridad) |
| `temp.md` | Secciones de informe académico: arquitectura, patrones, librerías (borrar después de usar) |

---

## Historial de decisiones importantes

- `confirmModal` y `cerrarConfirmModal` están en `config.js` (no en `admin.js`) para que también funcionen en `propietario.html`.
- `openpyxl` usa `merge_cells("A1:H1")` en el reporte Excel — al iterar `ws.columns` hay que hacer `try/except AttributeError` en `col[0].column_letter` porque las `MergedCell` no tienen ese atributo.
- Precisión monetaria: nunca usar `float` para operaciones intermedias — siempre `Decimal` y convertir al final con `money_float()`.
- La búsqueda de propietarios por DNI de 8 dígitos usa `arbol.buscar(int(q))` (O(log n)); cualquier otro texto usa `arbol.inorden()` + filtro lineal.
- El Excel de morosidad se genera en memoria (`BytesIO`), nunca se escribe en disco.
- `auth_service.generar_token()` usa `datetime.now(timezone.utc)`, nunca `datetime.utcnow()`: `.timestamp()` sobre un datetime naive lo reinterpreta con la zona horaria *local* del sistema, no UTC — esto corría el `iat`/`exp` del JWT por el offset horario del servidor (bug real detectado por los tests de integración, pasaba desapercibido en Render porque corre en UTC).
