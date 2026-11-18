# CondominioX — Contexto del Proyecto

Sistema web de gestión de condominio residencial con dos roles: **Administrador** y **Propietario**.
Versión actual: **5.1 — Noviembre 2026** (APF3: pasarela emulada, reservas con garantía, asistente IA, documentos).

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Frontend | HTML + CSS + JavaScript vanilla (sin frameworks ni build) |
| Backend | Python 3 + Flask 3.1 + Gunicorn (1 worker) |
| Base de datos | PostgreSQL 18 (Render Managed); Postgres 16 en CI y local |
| Autenticación | JWT stateless HS256 (PyJWT 2.15.1) — Bearer token |
| LLM | Groq (`openai/gpt-oss-120b` vía `LLM_MODEL`), intercambiable con Gemini |
| Despliegue frontend | GitHub Pages — https://laurarangel.github.io/condominiox-system/ |
| Despliegue backend | Render Web Service (Root Directory `backend`) |
| URL producción | `https://condominiox-system.onrender.com/api` |

---

## Estructura de carpetas

```
sistema-condominio/
  index.html              ← Login (paso 1: tipo usuario, paso 2: form) + pestañas informativas
  admin.html              ← Panel administrador
  propietario.html        ← Panel propietario
  recuperar.html          ← Recuperación de contraseña
  css/
    styles.css            ← Estilos base (?v=20260716)
    innovacion.css        ← Pagos, reservas, asistente, documentos
    moderno.css           ← Capa visual moderna (glass, sombras)
  js/
    config.js             ← API_URL, apiFetch, escapeHtml, helpers auth, showToast, confirmModal, comprobante
    auth.js               ← Login, cerrarSesion, guardias de rol, toggleContrasenas
    admin.js              ← Panel admin (clases PilaFiltros, IndiceGastos)
    admin-enlinea.js      ← Admin "Pagos y Reservas": transacciones, reservas, garantías, áreas
    propietario.js        ← Panel propietario
    pasarela.js           ← Checkout emulado + tokenización de tarjeta
    reservas.js           ← Calendario de disponibilidad, reserva, invitados, garantía
    invitados.js          ← Ver/imprimir invitados (admin y propietario)
    asistente.js          ← Chat del asistente IA
    documentos.js         ← Reglamento navegable, visor y carga de PDF
    areas-img.js          ← Imagen por área común
    ui-moderno.js         ← Ajustes visuales comunes
  img/
    logo.png
  backend/
    app.py                ← Flask app, CORS, cabeceras, access log, blueprints, migraciones base
    migrations.py         ← Migraciones APF3 idempotentes + siembra de áreas
    config.py             ← JWT_SECRET, JWT_ISSUER, JWT_EXPIRES_SECONDS
    db.py                 ← Helpers SQL: execute, fetch_all, fetch_one, get_db; log de queries lentas
    middleware.py         ← Validación JWT, require_roles, json_body, logging seguridad
    security.py           ← hash_password, verify_password
    structures.py         ← Estructuras de datos académicas
    seed_demo.py          ← Datos demo (manual; NO correr en producción)
    data/reglamento.json  ← Reglamento indexado por el asistente
    utils/
      money.py            ← to_decimal, round_money, money_float (Decimal)
      logger.py           ← get_logger(name) — python-json-logger JSON estructurado
      validacion.py       ← validaciones de entrada + LimitadorIntentos
      pdf_simple.py       ← PDFs de ejemplo para la demo
    dao/                  ← usuario, propietario, gasto, recibo, configuracion, anuncio,
                            reserva, pago, asistente, documento
    services/             ← auth, propietario, gasto, recibo, configuracion, anuncio, reporte,
                            reserva, pago, pasarelas, asistente, rag, llm_client, documento
    routes/               ← auth, propietario, gasto, recibo, configuracion, anuncio, reporte,
                            health, reserva, pago, asistente, documento
    tests/
      conftest.py          ← fixture client (Flask test_client) + limpieza de tablas
      unit/                ← 147 tests sin DB
      integration/         ← 78 tests contra Postgres real
    schema.sql             ← esquema completo (base + APF3)
    requirements.txt
    requirements-dev.txt   ← pytest 9.0.3, pytest-cov, pytest-mock, freezegun
    pytest.ini
    .env.test.example      ← plantilla; .env.test real no se versiona
  README.md                ← Guía de uso
  README_INTEGRADOR.md     ← Documento técnico integrador (§13 = APF3)
  DOCUMENTACION_TECNICA.md ← HTML/CSS/JS, esquema SQL, estructuras, seguridad
  DEPLIEGUE.md             ← Flujo de despliegue, Render, verificación, rollback
.github/
  workflows/
    tests.yml              ← pytest (unit+integration) con Postgres 16 como service container
    codeql.yml             ← SAST Python + JS (push/PR + semanal)
    dependency-review.yml  ← falla el PR si se introduce una dependencia con CVE alto/crítico
  dependabot.yml           ← PRs semanales de actualización (pip + github-actions)
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

Services → structures.py (Lista, BST, AVL, Cola, Matriz) · rag.py (TF-IDF)
         → pasarelas.py (Culqi/Yape/Mercado Pago) · llm_client.py (Groq/Gemini)
```

**Regla dura:** Routes nunca tocan SQL. Services nunca importan Flask. DAO nunca tiene lógica de negocio.

---

## Base de datos — 15 tablas

| Tabla | Descripción |
|---|---|
| `usuarios` | Credenciales (`password_hash`) + rol (Administrador / Propietario) |
| `propietarios` | Datos personales, depto, torre, `usuario_id` FK |
| `gastos` | Gastos comunes: tipo (mantenimiento/luz/agua), proveedor, concepto, monto, fecha |
| `pagos_gastos` | Pagos asociados a cada gasto |
| `configuracion` | Monto de administración mensual configurable |
| `recibos` | Montos por concepto (incl. `monto_reservas`), `monto_pagado`, estado, fechas |
| `anuncios` | Título, contenido, tipo, `fecha_caducidad`, activo |
| `lecturas_anuncios` | Qué propietario leyó qué anuncio (UNIQUE anuncio+propietario) |
| `areas_comunes` | Tarifa, garantía, aforo, horario, anticipación, duración máx., `uso_exclusivo`, activo |
| `reservas` | Área, fecha, horario, asistentes, cargo, estado, garantía y su resolución |
| `reserva_invitados` | Invitados (DNI/CE) por reserva |
| `transacciones_pago` | Cobros/rechazos/devoluciones; `idempotency_key` UNIQUE, `transaccion_origen_id` |
| `documentos` | PDF en `BYTEA` + metadatos + `publico` |
| `documento_fragmentos` | Texto por página para el RAG |
| `consultas_asistente` | Auditoría de consultas (modo `ia`/`respaldo`/`privacidad`) |

Migraciones automáticas al importar `app.py`: bloque base en `app.py` (`CREATE TABLE IF NOT EXISTS` + `ALTER TABLE anuncios ADD COLUMN IF NOT EXISTS fecha_caducidad`) y `migrations.run_migrations()` (columna `monto_reservas`, 7 tablas APF3, siembra de 5 áreas con `ON CONFLICT DO NOTHING`).

---

## Casos de Uso implementados (19/19 ✅ + documentos)

| CU | Descripción | Endpoint principal |
|---|---|---|
| CU01 | Login con roles | `POST /api/login` |
| CU02 | CRUD propietarios | `GET/POST/PUT/DELETE /api/propietarios` |
| CU03 | Configurar monto administración | `GET/PUT /api/configuracion` |
| CU04 | Registro y pago de gastos | `GET/POST/DELETE /api/gastos`, `POST /api/gastos/<id>/pagar` |
| CU05 | Generar recibos por fecha | `POST /api/recibos/generar` |
| CU06 | Recalcular recibos del mes | `POST /api/recibos/recalcular` |
| CU07 | Pago manual parcial/total de recibo (admin) | `POST /api/recibos/<id>/pagar` |
| CU08 | Recuperar contraseña | `POST /api/recuperar-contrasena` |
| CU09 | Cambiar contraseña | `PUT /api/mi-contrasena` |
| CU10 | Editar contacto (correo/teléfono) | `PUT /api/mi-perfil` |
| CU11 | Estado de cuenta individual | `GET /api/propietarios/<id>/estado-cuenta` |
| CU12 | Historial de pagos con filtro mes | `GET /api/recibos/propietario/<id>?estado=pagados` |
| CU13 | Comunicados con fecha caducidad | `GET/POST/DELETE /api/anuncios`, `GET /api/comunicados` |
| CU14 | Estado financiero resumido | `GET /api/reportes/financiero` |
| CU15 | Exportar morosidad a Excel | `GET /api/reportes/morosidad/excel` |
| CU16 | Comprobante de recibo imprimible | `GET /api/recibos/<id>` |
| CU17 | Pasarela de pagos emulada (recibo/garantía) | `POST /api/pagos` |
| CU18 | Reserva de áreas comunes con garantía | `POST /api/reservas`, `GET /api/areas-comunes/<id>/disponibilidad` |
| CU19 | Asistente IA (RAG + LLM, incl. disponibilidad) | `POST /api/asistente/consulta` |
| — | Documentos del condominio | `GET/POST /api/documentos`, `GET /api/reglamento` |

---

## Endpoints completos

### Auth (`/api`)
| Método | Endpoint | Rol |
|---|---|---|
| POST | `/api/login` | Público |
| POST | `/api/recuperar-contrasena` | Público |
| GET | `/api/mi-perfil` | Autenticado |
| PUT | `/api/mi-perfil` | Propietario (correo + teléfono) |
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
| GET | `/api/recibos/propietario/<id>?estado=` | Admin / Propietario (solo el suyo) |
| POST | `/api/recibos/<id>/pagar` | Admin |
| GET | `/api/recibos/<id>` | Admin / Propietario (solo su recibo) |
| DELETE | `/api/recibos/<id>` | Admin |
| GET | `/api/recibos/estructura/bst?saldo_min=&saldo_max=&mes=&estado=` | Admin |
| GET | `/api/recibos/estructura/avl?saldo_min=&saldo_max=&mes=&estado=` | Admin |
| GET | `/api/recibos/morosos/prioridad?mes=&limit=` | Admin |

### Pagos en línea
| Método | Endpoint | Rol |
|---|---|---|
| POST | `/api/pagos` (header `Idempotency-Key`; `concepto`: `recibo` / `garantia`) | Propietario |
| GET | `/api/pagos/mios` | Propietario |
| GET | `/api/pagos?estado=` | Admin |

### Áreas comunes y reservas
| Método | Endpoint | Rol |
|---|---|---|
| GET | `/api/areas-comunes` (`?todas=1` admin) | Autenticado |
| PUT | `/api/areas-comunes/<id>` | Admin |
| GET | `/api/areas-comunes/<id>/disponibilidad?fecha=YYYY-MM-DD` | Autenticado |
| POST | `/api/reservas` | Propietario |
| GET | `/api/reservas/mias` | Propietario |
| GET | `/api/reservas` | Admin |
| DELETE | `/api/reservas/<id>` | Propietario (la suya) / Admin |
| POST | `/api/reservas/<id>/garantia/resolucion` | Admin |
| GET | `/api/reservas/<id>/invitados` | Propietario (la suya) / Admin |

### Asistente y documentos
| Método | Endpoint | Rol |
|---|---|---|
| POST | `/api/asistente/consulta` | Propietario |
| GET | `/api/documentos` | Autenticado (propietario: solo públicos) |
| POST | `/api/documentos` (multipart) | Admin |
| GET | `/api/documentos/<id>/archivo[?descargar=1]` | Autenticado |
| PUT | `/api/documentos/<id>` | Admin |
| DELETE | `/api/documentos/<id>` | Admin |
| GET | `/api/reglamento` | Autenticado |

### Anuncios
| Método | Endpoint | Rol |
|---|---|---|
| GET | `/api/anuncios` | Admin |
| POST | `/api/anuncios` | Admin |
| DELETE | `/api/anuncios/<id>` | Admin |
| GET | `/api/comunicados` | Propietario |
| POST | `/api/comunicados/<id>/leer` | Propietario |

### Reportes / Configuración / Salud
| Método | Endpoint | Rol |
|---|---|---|
| GET | `/api/reportes/financiero?mes=YYYY-MM` | Admin |
| GET | `/api/reportes/morosidad/excel?mes=&limit=` | Admin |
| GET | `/api/configuracion` | Admin |
| PUT | `/api/configuracion` | Admin |
| GET | `/api/health`, `/api/health/db` | Público |

---

## Estructuras de datos (`backend/structures.py`)

Todas implementadas desde cero en Python, sin librerías externas.

| Clase | Tipo | Complejidad clave | Usada en |
|---|---|---|---|
| `ListaPropietarios` | Lista enlazada simple (head + tail) | insertar O(1), recorrer O(n) | `propietario_service.listar_propietarios()` |
| `ArbolPropietariosBST` | BST iterativo, clave = DNI (int) | insertar/buscar O(log n) | `propietario_service.buscar_propietarios()` |
| `ArbolRecibosBST` | BST, clave = (saldo, id), inorden/preorden/postorden/rango | rango O(log n + k) | `recibo_service.buscar_recibos_bst()` |
| `ArbolRecibosAVL` | AVL autobalanceado, clave = (saldo, id) | insertar O(log n) garantizado | `recibo_service.buscar_recibos_avl()` |
| `ColaPrioridadMorosos` | Max-heap manual | enqueue O(log n), to_sorted_list O(n log n) | `recibo_service.get_morosos_prioridad()`, `reporte_service.exportar_morosidad_excel()` |
| `MatrizRecibos` | Matriz dispersa dict[mes][pid] | set/get O(1) | `recibo_service.listar_recibos_admin()` / `listar_recibos_propietario()` |

**Otras estructuras:**
- `services/rag.py` — índice TF-IDF + similitud coseno (tokenizador, stopwords, stemmer, sinónimos en español), propio.
- `PilaFiltros` (admin.js) — historial de filtros de la búsqueda estructurada.
- `IndiceGastos` (admin.js) — índice hash O(1) por mes/tipo.

**BST vs AVL:** `ArbolRecibosAVL` es una clase **independiente** (no hereda de `ArbolRecibosBST`) que expone la misma interfaz (`insertar`, `recorrer`, `rango`); `recibo_service` los usa indistintamente según el parámetro `estructura` (Estrategia). El AVL agrega `height` por nodo y `_rotate_left/_rotate_right`.

**Prioridad en `ColaPrioridadMorosos`:** `(saldo, dias_pendiente)` descendente — mayor saldo + más días sin pagar = mayor prioridad.

---

## Librerías externas (`requirements.txt`)

| Librería | Versión | Equivalente Java académico | Uso |
|---|---|---|---|
| `Flask` | 3.1.3 | Spring MVC | Framework HTTP, Blueprints |
| `Flask-Cors` | 6.0.5 | Spring Web CORS | CORS para `/api/*` |
| `gunicorn` | 26.0.0 | Tomcat | Servidor WSGI en Render |
| `psycopg[binary]` | — | JDBC | Conexión PostgreSQL |
| `PyJWT` | 2.15.1 | JJWT | Firma y valida tokens JWT |
| `openpyxl` | 3.1.5 | Apache POI | Excel morosidad con estilos |
| `python-json-logger` | 4.1.0 | Logback | Logs JSON en `utils/logger.py` |
| `validators` | 0.35.0 | Apache Commons Validator | Formato de correo |
| `python-dateutil` | 2.9.0 | Apache Commons Lang | Días pendientes en recibos |
| `pypdf` | 7.1.0 | Apache PDFBox | Extraer texto de PDFs |
| `python-dotenv` | 1.2.2 | — | `.env` en local |

RAG, cliente LLM (`urllib`) y pasarelas usan solo la librería estándar.

---

## Seguridad

- **JWT stateless:** firmado con `JWT_SECRET`, con `iss` (`JWT_ISSUER`) y `exp`; validado en `middleware.py` en cada request. Payload: `sub`, `usuario`, `tipo`, `propietario_id` (si aplica).
- **Control de roles:** `require_roles(payload, "Administrador")` → 403 si no coincide. El propietario solo accede a sus recibos, pagos, reservas e invitados.
- **Guardia frontend:** `auth.js` verifica `userData.tipo` al cargar `admin.html` / `propietario.html`.
- **Sin revelación de info:** login responde siempre `"Usuario o contraseña inválidos"`; recuperación responde igual exista o no el usuario.
- **Fuerza bruta:** `LimitadorIntentos` — 5 fallos por IP+usuario bloquean 15 min (login) / 1 h (recuperación) → 429 + `Retry-After`. En memoria del proceso (por eso 1 worker). **Al probar en producción: no fallar el login 5 veces seguidas.**
- **Contraseñas:** ≥ 8 caracteres con letras y números, distinta del DNI y de la actual; login devuelve `debe_cambiar_contrasena`.
- **XSS:** `escapeHtml()` en `config.js` para todo texto insertado con `innerHTML` + validación backend (`utils/validacion.py`).
- **Entrada:** `json_body()` normaliza el JSON; montos no finitos → 400, nunca 500. Handler global de 500 con `request_id`.
- **CORS:** solo `CORS_ORIGINS` (default GitHub Pages + localhost); headers permitidos `Content-Type`, `Authorization`, `Idempotency-Key`.
- **Cabeceras:** `nosniff`, `X-Frame-Options DENY`, HSTS, `Referrer-Policy`, `Permissions-Policy`, CSP `default-src 'none'` en la API y CSP meta en los 4 HTML.
- **Asistente:** contexto solo del `propietario_id` del JWT; sin DNI/correo/teléfono/invitados al LLM; `pregunta_sobre_otro()` bloquea preguntas por otros vecinos; 8 consultas/min; prompt anti-inyección.
- **Logging seguridad:** eventos `missing_token`, `expired_token`, `invalid_token`, `forbidden_role`, `rate_limited` — campos `event`, `request_id`, `ip`, `path`, `method`, `user`, `rol_actual`, `rol_requerido`.
- **Observabilidad:** access log JSON con `X-Request-Id`; queries lentas (`SLOW_QUERY_MS`, default 200 ms); `GET /api/health/db`.

---

## Reglas de negocio importantes

- **Contraseña inicial del propietario:** su DNI.
- **Recibo pagado:** cuando `monto_pagado >= total_recibo`; total = administración + agua + luz + mantenimiento + reservas.
- **Quién paga qué:** el propietario paga por la pasarela (`POST /api/pagos`); `POST /api/recibos/<id>/pagar` es solo del admin (efectivo/transferencia).
- **Pago FIFO:** el monto se distribuye a gastos pendientes del mismo mes en orden cronológico (`recibo_service.aplicar_pago_fifo()`), igual para pagos del admin y de la pasarela.
- **Pagos atómicos:** cobro + recibo/reserva + FIFO + `transacciones_pago` en un solo commit con `SELECT ... FOR UPDATE`; `Idempotency-Key` evita doble cobro.
- **Reservas:** reglas en `reserva_service.validar_reglas()` (horario, duración, anticipación en hora de Lima, aforo, sin deuda vencida > `DIAS_DEUDA_VENCIDA`). Exclusiva = sin cruces; compartida (`uso_exclusivo=FALSE`) = cruces hasta el aforo. La tarifa va a `recibos.monto_reservas`; la garantía no.
- **Garantía:** reserva nace `pendiente_garantia` (30 min) → se confirma al pagar la garantía → el admin la resuelve (devolución total/parcial/retención) en `pago_service.resolver_garantia()`. Cancelar antes del inicio devuelve la garantía completa; si no se paga, `expirada`.
- **Precisión monetaria:** todo con `Decimal` (`utils/money.py`), a float solo al serializar JSON.
- **Comunicados visibles para propietario:** `activo = TRUE` y `fecha_caducidad IS NULL OR fecha_caducidad >= CURRENT_DATE`.
- **Piso calculado:** `_calcular_piso(nro_departamento)` — toma los dígitos, elimina los 2 últimos.

---

## Frontend — módulos JS

### config.js (compartido por todos los HTML)
- `API_URL` — `http://localhost:5000/api` en localhost/127.0.0.1; si no, `https://condominiox-system.onrender.com/api`
- `AUTH_TOKEN_KEY = 'auth_token'`, `USER_DATA_KEY = 'user_data'`
- `apiFetch(path, options)` → `{ response, data }` — fachada sobre fetch: adjunta token, prefija URL, redirige al login en 401
- `escapeHtml(valor)` — obligatorio para texto de la API insertado con `innerHTML`
- `getAuthToken()` / `setAuthToken()` / `removeAuthToken()` / `getUserData()` / `setUserData()` / `isAuthenticated()` / `requireAuth()`
- `formatDate()` / `formatMonthYear()` / `formatCurrency()`
- `showToast(message, type, title)`, `confirmModal(message, title, tipo)` / `cerrarConfirmModal(accepted)`
- `verComprobante(reciboId)` / `cerrarComprobante()` / `imprimirComprobante()` — CU16 compartido

### auth.js
- Submit de `#loginForm` → `POST /api/login` → guarda token + userData → redirige por rol
- `cerrarSesion()`, `mostrarSeccion(id)`, `inicializarToggleContrasenas()`, `toggleSidebarMenu()`
- Guardias de rol al cargar `admin.html` y `propietario.html`

### admin.js
- `class PilaFiltros`, `class IndiceGastos`
- `cargarDashboard`, `cargarPropietarios`, `buscarPropietariosBackend`, `editarPropietario`, `eliminarPropietario`, `abrirModalGasto`, `switchGastoTab`, `submitGasto`, `pagarGasto`, `generarRecibos`, `recalcularRecibos`, `cargarRecibos`, `buscarConEstructura`, `guardarFiltroEstructura`, `deshacerFiltroEstructura`, `cargarTopMorosos`, `exportarMorosidadExcel`, `cargarAnuncios`, `crearAnuncio`, `eliminarAnuncio`, `verEstadoCuenta`, `filtrarEstadoCuenta`, `cargarResumenFinanciero`

### admin-enlinea.js
- `cargarPanelEnLinea`, `aplicarFiltrosEnLinea`, `limpiarFiltrosEnLinea`, `filtroRapido`, `abrirModalGarantia`, `resolverGarantia`, `cancelarReservaAdmin`, `cargarAreasAdmin`, `abrirModalArea`, `guardarArea`

### propietario.js
- `getPropietarioId()`, `cargarInformacionPersonal`, `activarEdicionContacto`, `guardarContacto` (`PUT /api/mi-perfil`), `cargarEstadisticas`, `cargarRecibosPendientes`, `cargarRecibosPagados`, `filtrarPagadosPorMes`, `renderTablaRecibosPagados`, `cargarComunicados`, `filtrarComunicados`, `marcarLeido`, `cargarDatosSeccion`

### pasarela.js / reservas.js / asistente.js / documentos.js / invitados.js
- pasarela: `pagarRecibo`, `pagarGarantia`, `usarMontoTotal`, `elegirMedio`, `cerrarModalPago`, `confirmarPago` (`POST /api/pagos` + `Idempotency-Key`)
- reservas: `cargarReservas`, `seleccionarArea`, `abrirReserva`, `elegirDia`, `tocarSlot`, `cambiarPersonas`, `agregarInvitado`, `importarInvitados`, `crearReserva`, `cargarMisReservas`, `cancelarReserva`, `pagarGarantiaDeReserva`
- asistente: `iniciarAsistente`, `preguntaSugerida`, `enviarPregunta`; `_ICONO_FUENTE` por tipo de fuente (incl. `disponibilidad`)
- documentos: `cargarDocumentos`, `cargarReglamento`, `filtrarReglamento`, `verPdf`, `descargarPdf`, `subirDocumento`, `alternarPublico`, `eliminarDocumento`, `abrirFuente`
- invitados: `verInvitados`, `imprimirInvitados`

**Cache-busting:** los HTML cargan CSS/JS con `?v=AAAAMMDD`; al modificar un archivo, subir su sufijo en todos los HTML que lo cargan.

---

## Patrones de diseño aplicados

| Patrón | Dónde |
|---|---|
| MVC | `routes/` (C) + `services/` (M lógica) + `HTML+JS` (V) |
| DAO | `dao/*.py` — SQL puro por entidad |
| SOLID SRP | Cada archivo tiene una sola responsabilidad |
| SOLID OCP | Nuevo CU = nuevo archivo; nueva pasarela = nueva clase en `pasarelas.py` |
| SOLID DIP | Routes→Services→DAO, nunca al revés |
| Fachada | `config.js → apiFetch()` |
| Estrategia | `recibo_service` elige BST o AVL; `obtener_pasarela()` elige adaptador; `llm_client` elige Groq/Gemini |
| Adaptador | `pasarelas.py` — Culqi / Yape / Mercado Pago con interfaz común `PasarelaBase` |
| FIFO | `recibo_service.aplicar_pago_fifo()` |
| Idempotencia | `Idempotency-Key` + `transacciones_pago.idempotency_key UNIQUE` |
| Seguridad en capas | `middleware.py` + `auth.js` + `utils/validacion.py` + `utils/logger.py` |

---

## Testing y CI

- **225 tests** en `backend/tests/`: 147 unitarias (`tests/unit/`, sin DB; 100% cobertura en `structures.py`/`utils/money.py`/`security.py`) + 78 de integración (`tests/integration/`, Flask `test_client()` contra Postgres real).
- Unitarias: `test_structures`, `test_money`, `test_security`, `test_pasarelas`, `test_rag`, `test_reglas_reserva`, `test_llm_client`, `test_documentos`, `test_asistente_disponibilidad`. Integración: `test_auth_routes`, `test_propietario_routes`, `test_innovacion_routes`, `test_seguridad`.
- Correr local: `cd backend && .venv/bin/pytest tests/unit -v` (sin dependencias) o `.venv/bin/pytest tests/integration -v` (requiere Postgres con `schema.sql` aplicado y `.env.test` — ver `.env.test.example`).
- El entorno de desarrollo usa **podman**, no Docker: `podman machine start`, luego `podman run -d --rm --name condominiox-test-pg -e POSTGRES_USER=test -e POSTGRES_PASSWORD=... -e POSTGRES_DB=condominiox_test -p 5439:5432 docker.io/library/postgres:16`, aplicar `schema.sql` con `podman exec -i ... psql`, y al final `podman stop` + `podman machine stop`.
- CI en `.github/workflows/tests.yml`: Python 3.12 + Postgres 16 como *service container*, `pytest --cov=.` en cada push/PR a `main`. CodeQL y Dependency Review también corren en cada PR.
- `main` tiene un ruleset que exige PR + 1 aprobación; el merge lo hace la dueña del repo. Render redespliega al mergear a `main` (si no arranca, deploy manual).

---

## Variables de entorno (backend)

| Variable | Descripción | Default | Requerida |
|---|---|---|---|
| `DATABASE_URL` | Cadena conexión PostgreSQL | — | Sí |
| `JWT_SECRET` | Clave firma tokens (≥ 32 caracteres, avisa si es menor) | — | Sí |
| `JWT_EXPIRES_SECONDS` | TTL token | `3600` | No |
| `JWT_ISSUER` | Claim `iss` | `condominiox` | No |
| `CORS_ORIGINS` | Orígenes permitidos (coma) | GitHub Pages + localhost:8080/5500 | No |
| `SLOW_QUERY_MS` | Umbral de query lenta | `200` | No |
| `LLM_PROVIDER` | `groq` / `gemini` / `none` | `groq` | No |
| `GROQ_API_KEY` / `GEMINI_API_KEY` | API key del LLM (sin ella: modo respaldo) | — | Para modo IA |
| `LLM_MODEL` | Modelo | `llama-3.3-70b-versatile` / `gemini-2.5-flash` | En producción: `openai/gpt-oss-120b` |
| `LLM_TIMEOUT` | Segundos de espera al LLM | `12` | No |
| `DIAS_DEUDA_VENCIDA` | Días para considerar vencido un recibo | `30` | No |
| `FLASK_DEBUG` | `1` activa debug en `python app.py` local | — | No |

---

## Archivos de documentación existentes

| Archivo | Contenido |
|---|---|
| `README.md` | Guía de uso para el usuario final (v5.1) |
| `README_INTEGRADOR.md` | Documento técnico integrador v5.1 (CU, arquitectura, endpoints, SOLID, testing, CI; §13 APF3, §13.8 seguridad) |
| `DOCUMENTACION_TECNICA.md` | Documentación técnica v5.1 (HTML/CSS/JS, SQL schema completo, estructuras, seguridad) |
| `DEPLIEGUE.md` | Flujo de despliegue, configuración Render, backup, smoke tests, rollback, lecciones APF3 |

Al cambiar funcionalidad, mantener sincronizados estos 4 archivos y este CLAUDE.md (conteo de tests, endpoints, tablas, versiones de librerías).

---

## Historial de decisiones importantes

- `confirmModal` y `cerrarConfirmModal` están en `config.js` (no en `admin.js`) para que también funcionen en `propietario.html`.
- `openpyxl` usa `merge_cells("A1:H1")` en el reporte Excel — al iterar `ws.columns` hay que hacer `try/except AttributeError` en `col[0].column_letter` porque las `MergedCell` no tienen ese atributo.
- Precisión monetaria: nunca usar `float` para operaciones intermedias — siempre `Decimal` y convertir al final con `money_float()`.
- La búsqueda de propietarios por DNI de 8 dígitos usa `arbol.buscar(int(q))` (O(log n)); cualquier otro texto usa `arbol.inorden()` + filtro lineal.
- El Excel de morosidad se genera en memoria (`BytesIO`), nunca se escribe en disco.
- `auth_service.generar_token()` usa `datetime.now(timezone.utc)`, nunca `datetime.utcnow()`: `.timestamp()` sobre un datetime naive lo reinterpreta con la zona horaria *local* del sistema — corría `iat`/`exp` del JWT (bug real detectado por los tests de integración).
- Los PDF se guardan en Postgres (`BYTEA`) porque el disco del plan gratis de Render se borra en cada deploy. `documento_service` distingue `PdfProtegido` (subclase de `ValueError`) de un PDF inválido, y loguea el detalle sin exponerlo (fix CodeQL).
- `js/pasarela.js` genera el token aleatorio con un alfabeto de 32 caracteres (`b % 32`, sin sesgo de módulo; fix CodeQL); el backend valida `[a-z0-9]{12}`.
- Groq retiró `llama-3.3-70b-versatile` para la organización del proyecto → en Render `LLM_MODEL=openai/gpt-oss-120b`. Síntoma de modelo inexistente: el asistente responde `modo: "respaldo"` en ~1 s. Los `llama-prompt-guard-*` son clasificadores, no chat.
- Algunos modelos insertan caracteres invisibles (`​`, `⁠`...) dentro de las citas `[F1]` → `asistente_service.limpiar_respuesta()` los quita antes de detectar fuentes citadas.
- Fechas del asistente: `extraer_fecha()` sin año asume el próximo si la fecha ya pasó; `extraer_hora()` interpreta "a las 1–5" sin am/pm como tarde e ignora duraciones ("3 horas"). Hora de referencia: Lima (UTC−5).
- Un "error de CORS" en el navegador justo tras un merge suele ser Render respondiendo 502/503 sin cabeceras CORS durante el deploy/cold start — esperar a *Live* antes de tocar `CORS_ORIGINS`.
- Gunicorn con 1 worker: `LimitadorIntentos` y el límite del asistente viven en memoria del proceso.
- Antes de mergear migraciones: backup con `pg_dump` (cliente ≥ versión del servidor, hoy 18; `brew install libpq`). Nunca correr `seed_demo.py` en producción (modifica recibos existentes).

---

## Componentes innovadores APF3 (noviembre 2026)

Ver sección 13 de `README_INTEGRADOR.md`. Resumen:
- **Pasarela emulada:** `services/pasarelas.py` (adaptadores) + `services/pago_service.py` (`procesar_pago`, `resolver_garantia`) + `routes/pago_routes.py` + `js/pasarela.js`. El propietario ya NO usa `POST /api/recibos/<id>/pagar` (ahora solo Admin).
- **Reservas:** `services/reserva_service.py` (`validar_reglas`, `validar_area`, `validar_invitados` son puras; `disponibilidad()` arma el calendario del día) + `dao/reserva_dao.py` + `js/reservas.js`. `recibos.monto_reservas` entra en todos los totales (DAO, servicios, structures, JS). Áreas: salón, parrillas, gimnasio, cowork, pet shower; `uso_exclusivo=FALSE` permite reservas cruzadas hasta el aforo.
- **Garantías:** `areas_comunes.garantia`; la reserva nace `pendiente_garantia` (30 min), se confirma al pagar la garantía por `POST /api/pagos` con `concepto: "garantia"` y el admin la resuelve (devolución total/parcial/retención) en `pago_service.resolver_garantia()`. Cancelar devuelve la garantía completa. Los pagos son atómicos (un commit, `FOR UPDATE`).
- **Invitados:** `reserva_invitados` (DNI 8 dígitos o CE 9–12), máximo `asistentes - 1`, visibles solo para titular y admin, nunca al asistente.
- **Asistente IA:** `services/rag.py` (TF-IDF propio) + `services/asistente_service.py` + `services/llm_client.py` (Groq/Gemini por env) + `js/asistente.js`. Responde disponibilidad de áreas por fecha/hora (`extraer_fecha`, `extraer_hora`, `describir_disponibilidad` — puras, en `tests/unit/test_asistente_disponibilidad.py`). Sin API key responde en modo respaldo.
- **Documentos:** `services/documento_service.py` + `dao/documento_dao.py` + `routes/documento_routes.py` + `js/documentos.js`; PDF ≤ 5 MB en `BYTEA`, fragmentos indexados para el RAG (solo públicos).
- **Migraciones:** `migrations.py`, llamado desde `app.py`. Tablas: `areas_comunes`, `reservas`, `reserva_invitados`, `transacciones_pago`, `documentos`, `documento_fragmentos`, `consultas_asistente`.
- **Admin:** sección "Pagos y Reservas" en `admin.html` + `js/admin-enlinea.js`: transacciones, configuración editable de áreas (`PUT /api/areas-comunes/<id>`) y reservas.
- **Demo:** `seed_demo.py`. En `localhost`, `js/config.js` apunta a `http://localhost:5000/api`.
