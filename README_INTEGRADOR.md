# CondominioX System — Documento Integrador

Sistema web de gestión de un condominio con autenticación JWT, arquitectura MVC + DAO, principios SOLID y estructuras de datos académicas integradas en el backend. El avance APF3 suma pasarela de pagos emulada, reservas de áreas comunes con garantía, asistente virtual con IA y documentos del condominio.

**Versión:** 5.1 — Noviembre 2026

---

## 1. Alcance funcional (casos de uso implementados)

| CU | Descripción | Estado |
|---|---|---|
| CU01 | Login con roles (Administrador / Propietario) | ✅ |
| CU02 | Gestión de propietarios (CRUD) | ✅ |
| CU03 | Configuración del monto de administración | ✅ |
| CU04 | Registro y pago de gastos (mantenimiento, luz, agua) | ✅ |
| CU05 | Generación de recibos por fecha | ✅ |
| CU06 | Recálculo mensual de recibos | ✅ |
| CU07 | Pago parcial o total de recibos registrado por el administrador | ✅ |
| CU08 | Recuperación de contraseña | ✅ |
| CU09 | Cambio de contraseña | ✅ |
| CU10 | Edición de contacto (correo y teléfono) | ✅ |
| CU11 | Estado de cuenta individual por propietario | ✅ |
| CU12 | Historial de pagos con filtro por mes | ✅ |
| CU13 | Comunicados con fecha de caducidad | ✅ |
| CU14 | Estado financiero resumido por mes | ✅ |
| CU15 | Exportación del reporte de morosidad a Excel | ✅ |
| CU16 | Comprobante de recibo imprimible | ✅ |
| CU17 | Pasarela de pagos emulada (recibos y garantías) | ✅ APF3 |
| CU18 | Reserva de áreas comunes con garantía e invitados | ✅ APF3 |
| CU19 | Asistente virtual con IA (RAG + LLM), incluida la disponibilidad de áreas | ✅ APF3 |
| — | Documentos del condominio (PDF en PostgreSQL + reglamento navegable) | ✅ APF3 |

Desde APF3, el propietario paga por la pasarela (`POST /api/pagos`). `POST /api/recibos/<id>/pagar` queda solo para el administrador, que registra pagos en efectivo o por transferencia.

---

## 2. Arquitectura técnica

### Patrón MVC + DAO

```
Frontend JS  →  HTTP REST/JSON (Bearer JWT)  →  routes/ (Controller)
                                                    ↓ delega
                                               services/ (lógica de negocio)
                                                    ↓ consulta
                                                  dao/ (SQL)
                                                    ↓
                                                PostgreSQL

services/ → instancian → structures.py (Lista, BST, AVL, Cola de prioridad, Matriz)
services/ → rag.py (TF-IDF) → llm_client.py (Groq / Gemini)
services/ → pasarelas.py (adaptadores Culqi / Yape / Mercado Pago)
```

**Regla dura:** las rutas nunca tocan SQL, los servicios nunca importan Flask y el DAO nunca tiene lógica de negocio.

### Estructura de carpetas

```
backend/
  app.py                  ← Crea la app Flask, CORS, cabeceras, access log, blueprints, migraciones base
  migrations.py           ← Migraciones idempotentes APF3 + siembra de áreas comunes
  config.py               ← JWT_SECRET, JWT_ISSUER, JWT_EXPIRES_SECONDS
  db.py                   ← Conexión y helpers SQL; log de consultas lentas
  middleware.py           ← Validación JWT, require_roles, json_body, logging de seguridad
  security.py             ← hash_password, verify_password
  structures.py           ← Estructuras de datos (Lista, BST, AVL, Cola, Matriz)
  seed_demo.py            ← Datos de demostración (manual, no corre solo)
  schema.sql              ← Esquema completo (base + APF3)
  data/reglamento.json    ← Reglamento interno indexado por el asistente
  utils/
    money.py              ← to_decimal, round_money, money_float
    logger.py             ← Logger JSON estructurado
    validacion.py         ← Validaciones de entrada + LimitadorIntentos
    pdf_simple.py         ← Generación de PDF de ejemplo para la demo
  dao/                    ← usuario, propietario, gasto, recibo, configuracion, anuncio,
                            reserva, pago, asistente, documento
  services/               ← auth, propietario, gasto, recibo, configuracion, anuncio, reporte,
                            reserva, pago, pasarelas, asistente, rag, llm_client, documento
  routes/                 ← auth, propietario, gasto, recibo, configuracion, anuncio, reporte,
                            health, reserva, pago, asistente, documento
  tests/
    unit/                 ← 147 tests sin base de datos
    integration/          ← 78 tests contra Postgres real

Frontend (estático, GitHub Pages):
  index.html              ← Login (tipo de usuario + formulario) y páginas informativas
  admin.html              ← Panel administrador
  propietario.html        ← Panel propietario
  recuperar.html          ← Recuperación de contraseña
  css/styles.css          ← Estilos base
  css/innovacion.css      ← Estilos de pagos, reservas, asistente y documentos
  css/moderno.css         ← Capa visual moderna (superficies, sombras, glass)
  js/config.js            ← API_URL, apiFetch, escapeHtml, auth, toast, confirmModal, comprobante
  js/auth.js              ← Login, guardias de rol, toggles de contraseña, menú
  js/admin.js             ← Panel admin (PilaFiltros, IndiceGastos)
  js/admin-enlinea.js     ← Admin: transacciones, reservas, garantías, áreas comunes
  js/propietario.js       ← Panel propietario
  js/pasarela.js          ← Checkout emulado y tokenización de tarjeta en el navegador
  js/reservas.js          ← Calendario de disponibilidad, reserva, invitados, garantía
  js/invitados.js         ← Ver e imprimir la lista de invitados (admin y propietario)
  js/asistente.js         ← Chat del asistente con fuentes citadas
  js/documentos.js        ← Reglamento navegable, visor y carga de PDF
  js/areas-img.js         ← Imágenes de cada área común
  js/ui-moderno.js        ← Ajustes visuales comunes
```

### Principios SOLID

| Principio | Aplicación concreta |
|---|---|
| **SRP**: responsabilidad única | El DAO solo hace SQL, el servicio solo lógica y la ruta solo HTTP |
| **OCP**: abierto/cerrado | Un caso de uso nuevo es un archivo nuevo; agregar una pasarela es una clase nueva en `pasarelas.py` |
| **LSP**: sustitución | Cualquier `PasarelaBase` (Culqi, Yape, Mercado Pago) se usa igual en `pago_service`; `ArbolRecibosAVL` y `ArbolRecibosBST` comparten interfaz y son intercambiables |
| **DIP**: inversión de dependencias | Las rutas dependen de los servicios y los servicios del DAO, nunca al revés; el LLM se elige por variable de entorno |

### Patrones de diseño

| Patrón | Dónde |
|---|---|
| MVC | `routes/` (C) + `services/` (M) + HTML/JS (V) |
| DAO | `dao/*.py` |
| Fachada | `apiFetch()` en `js/config.js` |
| Estrategia | `recibo_service` elige BST o AVL; `pasarelas.obtener_pasarela()` elige el adaptador; `llm_client` elige Groq o Gemini |
| Adaptador | `pasarelas.py` unifica la interfaz de tres proveedores |
| FIFO | `recibo_service.aplicar_pago_fifo()` |
| Idempotencia | `Idempotency-Key` en `POST /api/pagos` |

---

## 3. Modelo de datos

### Tablas (15)

| Tabla | Descripción | Origen |
|---|---|---|
| `usuarios` | Credenciales y rol | Base |
| `propietarios` | Datos personales, departamento, torre, `usuario_id` | Base |
| `gastos` | Gastos comunes por tipo y fecha | Base |
| `pagos_gastos` | Pagos aplicados a cada gasto | Base |
| `configuracion` | Monto de administración mensual | Base |
| `recibos` | Montos por concepto (incluye `monto_reservas`), `monto_pagado`, estado, fechas | Base + APF3 |
| `anuncios` | Comunicados con tipo, `fecha_caducidad` y `activo` | Base |
| `lecturas_anuncios` | Qué propietario leyó qué anuncio | Base |
| `areas_comunes` | Tarifa, garantía, aforo, horario, reglas y tipo de uso | APF3 |
| `reservas` | Reserva por área, fecha y horario, con estado y garantía | APF3 |
| `reserva_invitados` | Invitados de cada reserva | APF3 |
| `transacciones_pago` | Cobros, rechazos y devoluciones de la pasarela | APF3 |
| `documentos` | PDF (`BYTEA`) con metadatos y visibilidad | APF3 |
| `documento_fragmentos` | Texto extraído por página, indexado por el asistente | APF3 |
| `consultas_asistente` | Auditoría de cada consulta al asistente | APF3 |

### Migraciones automáticas

Al importar `app.py`, antes de atender tráfico, corren dos bloques idempotentes:

1. `app.py`: `CREATE TABLE IF NOT EXISTS` de `pagos_gastos`, `anuncios` y `lecturas_anuncios`, más `ALTER TABLE anuncios ADD COLUMN IF NOT EXISTS fecha_caducidad`.
2. `migrations.py` (`run_migrations()`):
   - agrega `recibos.monto_reservas`;
   - crea las 7 tablas APF3;
   - siembra las 5 áreas comunes con `ON CONFLICT DO NOTHING`.

Correrlas en cada deploy es seguro: no tocan datos existentes. `schema.sql` contiene el esquema completo y es el que aplica CI.

---

## 4. Reglas de negocio

### Recibos
- Se generan para todos los propietarios en una fecha dada.
- El recálculo usa los gastos del mes y el monto de administración vigente; el cargo de reservas (`monto_reservas`) se conserva.
- Total del recibo = administración + agua + luz + mantenimiento + reservas.
- Un recibo pasa a **pagado** cuando `monto_pagado >= total_recibo`.

### Pago FIFO
- Al pagar un recibo, el monto se reparte entre los gastos pendientes del mismo mes por fecha e id (`recibo_service.aplicar_pago_fifo()`).
- Aplica igual a pagos manuales del admin y a pagos por la pasarela.

### Reservas y garantías
- Ver la sección 13.2.

### Anuncios
- El propietario solo ve `activo = TRUE` y `fecha_caducidad IS NULL OR fecha_caducidad >= CURRENT_DATE`.

### Precisión monetaria
- Todos los cálculos usan `Decimal` (`utils/money.py`); se convierte a `float` solo al serializar JSON.
- Montos no finitos (`NaN`, `Infinity`) se rechazan con 400.

### Otros
- Contraseña inicial del propietario = DNI; el login devuelve `debe_cambiar_contrasena`.
- Piso calculado: `_calcular_piso(nro_departamento)` quita los dos últimos dígitos.
- Hora de referencia para reservas y asistente: Lima (UTC−5, sin horario de verano).

---

## 5. Estructuras de datos

| Estructura | Clase | Uso | Complejidad |
|---|---|---|---|
| Lista enlazada | `ListaPropietarios` | Listado de propietarios | insertar O(1), recorrer O(n) |
| BST | `ArbolPropietariosBST` | Búsqueda por DNI | O(log n) promedio |
| BST | `ArbolRecibosBST` | Recibos por rango de saldo | rango O(log n + k) |
| AVL | `ArbolRecibosAVL` | Igual que el BST, balanceado | O(log n) garantizado |
| Cola de prioridad | `ColaPrioridadMorosos` | Ranking de morosos y Excel | enqueue O(log n) |
| Matriz dispersa | `MatrizRecibos` | Recibos por mes y propietario | set/get O(1) |
| Índice invertido TF-IDF | `services/rag.py` | Recuperación de reglamento y documentos | consulta O(t · d) |
| Pila (JS) | `PilaFiltros` | Historial de filtros | O(1) |
| Índice hash (JS) | `IndiceGastos` | Gastos por mes y tipo | O(1) |

`ArbolRecibosAVL` y `ArbolRecibosBST` exponen la misma interfaz (`insertar()`, `recorrer()`, `rango()`), así que `recibo_service` los usa de forma intercambiable según el parámetro `estructura` (patrón Estrategia). El AVL agrega altura por nodo y rotaciones al insertar para mantener el balance.

---

## 6. Librerías y equivalencias académicas

| Librería Python | Versión | Equivalente académico | Uso |
|---|---|---|---|
| `Flask` | 3.1.3 | Spring MVC | Framework HTTP, blueprints |
| `Flask-Cors` | 6.0.5 | Spring Web CORS | CORS restringido a `/api/*` |
| `gunicorn` | 26.0.0 | Tomcat | Servidor WSGI en Render |
| `psycopg[binary]` | — | JDBC | Conexión a PostgreSQL |
| `PyJWT` | 2.15.1 | JJWT | Firma y validación de JWT |
| `openpyxl` | 3.1.5 | Apache POI | Reporte Excel de morosidad |
| `python-json-logger` | 4.1.0 | Logback | Logs JSON estructurados |
| `validators` | 0.35.0 | Apache Commons Validator | Formato de correo |
| `python-dateutil` | 2.9.0 | Apache Commons Lang | Días pendientes de recibos |
| `pypdf` | 7.1.0 | Apache PDFBox | Extraer texto de los PDF |
| `python-dotenv` | 1.2.2 | — | Variables de entorno en local |

El RAG (TF-IDF, stemmer, sinónimos), el cliente LLM (`urllib`) y las pasarelas usan solo la librería estándar.

Desarrollo (`requirements-dev.txt`): `pytest` 9.0.3, `pytest-cov` 6.0.0, `pytest-mock` 3.14.0, `freezegun` 1.5.1.

---

## 7. Seguridad

- **JWT stateless** firmado con `JWT_SECRET`, con `iss` y expiración (1 h por defecto); validado en cada request por `middleware.py`.
- **Control de roles**: `require_roles()` en cada endpoint protegido; si el rol no coincide, responde 403. Un propietario solo accede a sus recibos, pagos, reservas e invitados.
- **Guardias en el frontend**: `auth.js` verifica `userData.tipo` al cargar `admin.html` y `propietario.html`.
- **Sin revelación de información**: el login responde siempre `"Usuario o contraseña inválidos"`.
- **Logging de seguridad**: token ausente, expirado o inválido, rol incorrecto y bloqueos por intentos quedan en log JSON con `event`, `ip`, `path`, `method`, `user`, `rol_actual` y `rol_requerido`.
- **Observabilidad**: access log JSON con `X-Request-Id`, log de consultas lentas (`SLOW_QUERY_MS`, 200 ms por defecto), `GET /api/health` y `GET /api/health/db`.
- Endurecimiento APF3: ver sección 13.8.

---

## 8. Endpoints completos

### Auth
| Método | Endpoint | Rol |
|---|---|---|
| POST | `/api/login` | Público |
| POST | `/api/recuperar-contrasena` | Público |
| GET | `/api/mi-perfil` | Autenticado |
| PUT | `/api/mi-perfil` | Propietario (correo y teléfono) |
| PUT | `/api/mi-contrasena` | Autenticado |

### Propietarios
| Método | Endpoint | Rol |
|---|---|---|
| GET | `/api/propietarios` | Admin |
| GET | `/api/propietarios/busqueda?q=&torre=&piso=` | Admin |
| POST | `/api/propietarios` | Admin |
| PUT | `/api/propietarios/<id>` | Admin |
| DELETE | `/api/propietarios/<id>` | Admin |
| GET | `/api/propietarios/<id>/estado-cuenta?desde=YYYY-MM&hasta=YYYY-MM` | Admin |

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
| POST | `/api/recibos/generar` | Admin |
| POST | `/api/recibos/recalcular` | Admin |
| GET | `/api/recibos?estado=&mes=` | Admin |
| GET | `/api/recibos/propietario/<id>?estado=` | Admin / Propietario (solo el suyo) |
| GET | `/api/recibos/<id>` | Admin / Propietario (solo el suyo) |
| POST | `/api/recibos/<id>/pagar` | Admin |
| DELETE | `/api/recibos/<id>` | Admin |
| GET | `/api/recibos/estructura/bst?saldo_min=&saldo_max=&mes=&estado=` | Admin |
| GET | `/api/recibos/estructura/avl?saldo_min=&saldo_max=&mes=&estado=` | Admin |
| GET | `/api/recibos/morosos/prioridad?mes=&limit=` | Admin |

### Pagos en línea (CU17)
| Método | Endpoint | Rol |
|---|---|---|
| POST | `/api/pagos` (header `Idempotency-Key`) | Propietario |
| GET | `/api/pagos/mios` | Propietario |
| GET | `/api/pagos?estado=` | Admin |

### Áreas comunes y reservas (CU18)
| Método | Endpoint | Rol |
|---|---|---|
| GET | `/api/areas-comunes` (`?todas=1` incluye inactivas, solo admin) | Autenticado |
| PUT | `/api/areas-comunes/<id>` | Admin |
| GET | `/api/areas-comunes/<id>/disponibilidad?fecha=YYYY-MM-DD` | Autenticado |
| POST | `/api/reservas` | Propietario |
| GET | `/api/reservas/mias` | Propietario |
| GET | `/api/reservas` | Admin |
| DELETE | `/api/reservas/<id>` | Propietario (la suya) / Admin |
| POST | `/api/reservas/<id>/garantia/resolucion` | Admin |
| GET | `/api/reservas/<id>/invitados` | Propietario (la suya) / Admin |

### Asistente (CU19)
| Método | Endpoint | Rol |
|---|---|---|
| POST | `/api/asistente/consulta` | Propietario |

### Documentos
| Método | Endpoint | Rol |
|---|---|---|
| GET | `/api/documentos` | Autenticado (el propietario solo ve los públicos) |
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

### Reportes y configuración
| Método | Endpoint | Rol |
|---|---|---|
| GET | `/api/reportes/financiero?mes=YYYY-MM` | Admin |
| GET | `/api/reportes/morosidad/excel?mes=&limit=` | Admin |
| GET | `/api/configuracion` | Admin |
| PUT | `/api/configuracion` | Admin |

### Salud
| Método | Endpoint | Rol |
|---|---|---|
| GET | `/api/health` | Público |
| GET | `/api/health/db` | Público |

---

## 9. Testing

### Suite de pruebas (`backend/tests/`): 225 tests

| Tipo | Archivos | Tests | Requiere DB |
|---|---|---|---|
| Unitarias | `test_structures.py`, `test_money.py`, `test_security.py`, `test_pasarelas.py`, `test_rag.py`, `test_reglas_reserva.py`, `test_llm_client.py`, `test_documentos.py`, `test_asistente_disponibilidad.py` | 147 | No |
| Integración | `test_auth_routes.py`, `test_propietario_routes.py`, `test_innovacion_routes.py`, `test_seguridad.py` | 78 | Sí (Postgres) |

`structures.py`, `utils/money.py` y `security.py` tienen 100 % de cobertura.

### Correr en local

El entorno de desarrollo usa **podman** (no Docker).

```bash
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt

# Solo unitarias (sin base de datos)
.venv/bin/pytest tests/unit -v

# Integración: Postgres 16 en el puerto 5439 con el schema aplicado
podman machine start
podman run -d --rm --name condominiox-test-pg \
  -e POSTGRES_USER=test -e POSTGRES_PASSWORD=test -e POSTGRES_DB=condominiox_test \
  -p 5439:5432 docker.io/library/postgres:16
podman exec -i condominiox-test-pg psql -U test -d condominiox_test < schema.sql

cp .env.test.example .env.test   # ajustar usuario, clave o puerto si cambian
.venv/bin/pytest tests/integration -v

# Todo junto + cobertura
.venv/bin/pytest --cov=. --cov-report=term-missing

# Al terminar
podman stop condominiox-test-pg && podman machine stop
```

`backend/.env.test` no se versiona; `backend/.env.test.example` sí, como plantilla.

### Pipeline de CI (GitHub Actions)

| Workflow | Dispara en | Qué hace |
|---|---|---|
| `tests.yml` | push y PR a `main` | Python 3.12 + Postgres 16 como *service container*, aplica `schema.sql`, corre `pytest --cov=.` |
| `codeql.yml` | push y PR a `main`, semanal | SAST de Python y JavaScript |
| `dependency-review.yml` | PR a `main` | Falla si el PR introduce una dependencia con CVE alto o crítico |
| `dependabot.yml` | semanal | PRs de actualización para pip (`/backend`) y GitHub Actions |

Dependabot actualiza con el tiempo; Dependency Review bloquea en el momento en que se introduce una dependencia vulnerable. En noviembre de 2026 se cerraron todas las alertas de Dependabot (PyJWT 2.15.1, pytest 9.0.3).

`main` está protegida por un *ruleset* que exige un PR con una aprobación.

---

## 10. Variables de entorno (backend)

| Variable | Descripción | Default | Requerida |
|---|---|---|---|
| `DATABASE_URL` | Conexión a PostgreSQL | — | Sí |
| `JWT_SECRET` | Clave de firma de tokens (32+ caracteres) | — | Sí |
| `JWT_EXPIRES_SECONDS` | Vida del token en segundos | `3600` | No |
| `JWT_ISSUER` | Emisor (`iss`) del token | `condominiox` | No |
| `CORS_ORIGINS` | Orígenes permitidos, separados por coma | GitHub Pages + localhost | No |
| `SLOW_QUERY_MS` | Umbral de consulta lenta en ms | `200` | No |
| `LLM_PROVIDER` | `groq`, `gemini` o `none` | `groq` | No |
| `GROQ_API_KEY` | API key de Groq | — | Para modo IA |
| `GEMINI_API_KEY` | API key de Google AI Studio | — | Si `LLM_PROVIDER=gemini` |
| `LLM_MODEL` | Modelo del LLM | `llama-3.3-70b-versatile` / `gemini-2.5-flash` | No (en producción: `openai/gpt-oss-120b`) |
| `LLM_TIMEOUT` | Espera máxima al LLM en segundos | `12` | No |
| `DIAS_DEUDA_VENCIDA` | Días para considerar vencido un recibo | `30` | No |

Para tests (`backend/.env.test`): las mismas variables apuntando al Postgres de prueba.

---

## 11. Despliegue

| Componente | Plataforma |
|---|---|
| Frontend | GitHub Pages: https://laurarangel.github.io/condominiox-system/ |
| Backend API | Render Web Service: `https://condominiox-system.onrender.com/api` |
| Base de datos | PostgreSQL gestionado por Render |
| LLM | Groq (`openai/gpt-oss-120b`) |

`js/config.js` apunta a `http://localhost:5000/api` cuando la página se abre en `localhost` y a Render en cualquier otro caso. El flujo completo (CI, merge, migraciones, verificación y rollback) está en [DEPLIEGUE.md](DEPLIEGUE.md).

---

## 12. Referencias internas

- [backend/structures.py](backend/structures.py): estructuras de datos
- [backend/app.py](backend/app.py) y [backend/migrations.py](backend/migrations.py): arranque y migraciones
- [backend/middleware.py](backend/middleware.py): autenticación y seguridad
- [backend/services/](backend/services/): lógica de negocio, pasarela, reservas, asistente
- [backend/tests/](backend/tests/): pruebas unitarias e integración
- [js/config.js](js/config.js): helpers del frontend
- [DOCUMENTACION_TECNICA.md](DOCUMENTACION_TECNICA.md): detalle de HTML, CSS, JS y SQL
- [DEPLIEGUE.md](DEPLIEGUE.md): despliegue y operación

---

## 13. Componentes innovadores (APF3)

Cuatro módulos sobre la plataforma base. La única dependencia nueva es `pypdf`; el resto usa la librería estándar de Python.

### 13.1 Pasarela de pagos emulada (CU17)

| Pieza | Archivo |
|---|---|
| Adaptadores sandbox Culqi / Yape / Mercado Pago (Estrategia + Adaptador) | `backend/services/pasarelas.py` |
| Orquestación: valida, cobra, concilia con FIFO, registra | `backend/services/pago_service.py` |
| Rutas | `backend/routes/pago_routes.py` |
| Checkout y tokenización de tarjeta en el navegador (Culqi.js emulado) | `js/pasarela.js` |

- `POST /api/pagos` (Propietario) con `concepto`:
  - `recibo`: pago total o parcial;
  - `garantia`: monto completo de la garantía de una reserva.
- El header `Idempotency-Key` evita cobrar dos veces un reintento con la misma clave.
- **Atómico:** todo se confirma en un solo commit, con el recibo o la reserva bloqueados (`SELECT ... FOR UPDATE`):
  - el cobro aprobado;
  - la actualización del recibo o de la reserva;
  - el reparto FIFO a los gastos;
  - el registro en `transacciones_pago`.
- `transacciones_pago.concepto` distingue `recibo`, `garantia` y `devolucion`.
- El número de tarjeta nunca llega al backend: el navegador genera `tkn_test_<marca>_<last4>_<azar>`.
- Datos de prueba:

  | Medio | Aprobado | Rechazado |
  |---|---|---|
  | Tarjeta | `4111 1111 1111 1111` | `4000 0000 0000 0002` |
  | Yape | OTP de 6 dígitos | OTP `000000` |
  | Mercado Pago | cualquier correo | correo con `rechazo` |

### 13.2 Reserva de áreas comunes y garantías (CU18)

| Área | Tarifa | Garantía | Uso | Aforo | Horario | Anticip. | Máx. |
|---|---|---|---|---|---|---|---|
| Salón de usos múltiples | S/ 80 | S/ 200 | Exclusivo | 40 | 09:00–23:00 | 48 h | 5 h |
| Zona de parrillas | S/ 50 | S/ 100 | Exclusivo | 15 | 11:00–22:00 | 24 h | 4 h |
| Gimnasio | — | — | Compartido | 8 | 06:00–22:00 | 1 h | 2 h |
| Cowork | — | — | Compartido | 12 | 07:00–22:00 | 1 h | 4 h |
| Pet shower | S/ 15 | S/ 30 | Exclusivo | 2 | 08:00–20:00 | 2 h | 1 h |

`migrations.py` siembra estos valores iniciales. El administrador los edita desde "Pagos y Reservas" (`PUT /api/areas-comunes/<id>`, validado con `reserva_service.validar_area()`) y puede activar o desactivar cada área. Los cambios aplican solo a reservas nuevas.

- **Reglas** (`reserva_service.validar_reglas()`, función pura):
  - horario de atención del área;
  - duración máxima;
  - anticipación mínima (hora de Lima);
  - aforo;
  - sin deuda vencida (`DIAS_DEUDA_VENCIDA`, 30 días por defecto).
- **Uso exclusivo o compartido:**
  - En un área exclusiva no se aceptan reservas que se crucen.
  - En una compartida (gimnasio, cowork) se aceptan mientras la suma de personas no supere el aforo.
  - El cruce se valida dentro de la transacción, con `SELECT ... FOR UPDATE` sobre el área.
- **Tarifa:** va al recibo del mes (`recibos.monto_reservas`). Si el recibo ya existe, se suma al confirmar la reserva; si no, se incluye al generarlo. Cancelar la reserva descuenta la tarifa.
- **Garantía** (no va al recibo):
  1. Si el área tiene garantía, la reserva nace en `pendiente_garantia` y bloquea el horario 30 minutos.
  2. El propietario paga la garantía completa por la pasarela (`POST /api/pagos` con `concepto: "garantia"`). Al aprobarse el pago, en una sola transacción:
     - la reserva pasa a `confirmada`;
     - la tarifa entra al recibo.
  3. Si no se paga a tiempo, la reserva pasa a `expirada` y se libera el horario.
  4. Después del uso, el administrador la resuelve con `POST /api/reservas/<id>/garantia/resolucion`, indicando `retener` y `motivo`:
     - devolución total;
     - devolución parcial;
     - retención total.

     La devolución se emula como un `refund` por el mismo medio del cobro, enlazado al cargo original (`transaccion_origen_id`).
  5. Si la reserva se cancela antes de empezar, la garantía se devuelve completa automáticamente.
- **Invitados:**
  - Al reservar, el propietario registra nombres, apellidos y documento de cada invitado: DNI de 8 dígitos o carné de extranjería de 9 a 12 caracteres. Puede hacerlo a mano o importando un CSV.
  - Se validan con `reserva_service.validar_invitados()`: como máximo `asistentes - 1` y sin documentos repetidos.
  - Solo los ven el titular y el administrador, que puede imprimir la lista para portería.
  - Nunca se envían al asistente IA.
- **Estados de garantía:**
  - `no_aplica`;
  - `pendiente`;
  - `pagada` (en custodia);
  - `devuelta`;
  - `devuelta_parcial`;
  - `retenida`;
  - `no_pagada`.
- **Calendario:** `GET /api/areas-comunes/<id>/disponibilidad?fecha=` devuelve los bloques ocupados del día (inicio, fin, personas), sin datos de quién reservó.

### 13.3 Asistente virtual con IA (CU19)

```
Pregunta → filtro de privacidad (¿pregunta por otro vecino?) → detección de intención
         → RAG propio (TF-IDF sobre reglamento + PDF públicos)
         + datos SOLO del propietario del JWT (recibos, pagos, reservas) + gastos del edificio
         + configuración y calendario de áreas comunes (si pregunta por fecha/hora)
         → LLM (Groq u otro proveedor) con fuentes [F1], [F2]...
         → respuesta citada · si el LLM falla: modo respaldo con plantillas
         → auditoría en consultas_asistente
```

- `services/rag.py`: tokenizador, stopwords, stemmer y sinónimos en español, TF-IDF y similitud coseno implementados desde cero.
- `services/llm_client.py`: cliente HTTP con `urllib` para Groq (API compatible con OpenAI) o Gemini, intercambiable por variable de entorno. En producción: Groq con `openai/gpt-oss-120b`.
- **Disponibilidad de áreas:**
  - `asistente_service` reconoce en la pregunta:
    - la fecha (`extraer_fecha()`): hoy, mañana, pasado mañana, "20 de noviembre", `20/11`, `2026-12-01`;
    - la hora (`extraer_hora()`): "2pm", "3 de la tarde", "14:30", "a las 2".
  - Consulta el calendario del área con `reserva_service.disponibilidad()`.
  - `describir_disponibilidad()` arma una fuente "Calendario de reservas" (función pura) que dice:
    - si a esa hora el área está LIBRE (y hasta cuándo), OCUPADA o cerrada;
    - en áreas compartidas, cuántos cupos quedan;
    - si no se cumple la anticipación mínima.
  - Nunca revela quién reservó.
- **Respuestas:** `limpiar_respuesta()` quita caracteres invisibles que algunos modelos insertan dentro de las citas `[F1]` y normaliza espacios estrechos.
- **Minimización de datos:**
  - Al LLM no se envían DNI, correo ni teléfono, ni datos de otros propietarios.
  - Si la pregunta nombra a otro vecino o a otro departamento, se responde con un aviso de privacidad sin llamar al LLM (modo `privacidad`).
- **Límites:** 8 consultas por minuto por propietario y preguntas de hasta 500 caracteres.
- **Endpoint:** `POST /api/asistente/consulta` (Propietario). Responde `respuesta`, `fuentes`, `modo` (`ia`, `respaldo` o `privacidad`), `proveedor` y `latencia_ms`.

### 13.4 Variables de entorno nuevas

| Variable | Descripción | Default |
|---|---|---|
| `LLM_PROVIDER` | `groq`, `gemini` o `none` | `groq` |
| `GROQ_API_KEY` | API key de console.groq.com (sin ella, modo respaldo) | — |
| `GEMINI_API_KEY` | API key de Google AI Studio (si `LLM_PROVIDER=gemini`) | — |
| `LLM_MODEL` | Modelo a usar | `llama-3.3-70b-versatile` / `gemini-2.5-flash` |
| `LLM_TIMEOUT` | Segundos de espera al LLM | `12` |
| `DIAS_DEUDA_VENCIDA` | Días para considerar un recibo vencido | `30` |
| `CORS_ORIGINS` | Orígenes permitidos | GitHub Pages + localhost |

> Groq retiró `llama-3.3-70b-versatile` para la organización del proyecto, así que en Render se configura `LLM_MODEL=openai/gpt-oss-120b`. Si el modelo no existe, el asistente responde en `modo: "respaldo"` en ~1 s. Los modelos `llama-prompt-guard-*` son clasificadores y no sirven para chat.

### 13.5 Datos de demostración

`cd backend && python seed_demo.py` (idempotente) crea:

- el admin `admin / Admin2026!`, si no hay ninguno;
- 8 propietarios (contraseña = DNI);
- gastos y recibos de los dos últimos meses;
- un acta de junta y un manual del gimnasio en PDF.

Casos preparados para la demo:

- `maria.quispe / 45678912` tiene el recibo del mes pendiente.
- `carlos.rojas / 41236587` queda moroso, para mostrar el bloqueo de reservas.

> **No se corre en producción**: modifica los recibos existentes.

### 13.6 Pruebas

| Archivo | Qué cubre |
|---|---|
| `tests/unit/test_pasarelas.py` | Los tres medios de pago |
| `tests/unit/test_rag.py` | El RAG |
| `tests/unit/test_reglas_reserva.py` | Las reglas de reserva |
| `tests/unit/test_llm_client.py` | El cliente LLM |
| `tests/unit/test_documentos.py` | Los documentos PDF |
| `tests/unit/test_asistente_disponibilidad.py` | Fecha, hora y disponibilidad en el asistente |
| `tests/integration/test_innovacion_routes.py` | Los flujos completos (lista abajo) |

`test_innovacion_routes.py` prueba contra Postgres:

- pagos aprobados y rechazados;
- idempotencia;
- cargo de reservas al recibo;
- garantías;
- morosidad;
- cruce de horarios;
- invitados;
- documentos;
- asistente con y sin LLM;
- disponibilidad por fecha y hora;
- minimización de datos.

Total de la suite: **225 tests** (147 unitarias + 78 de integración).

### 13.7 Documentos del condominio (PDF en PostgreSQL)

- Solo se aceptan **PDF de hasta 5 MB**:
  - se valida la extensión y el contenido real (`%PDF-`);
  - se rechazan los PDF protegidos con contraseña (`PdfProtegido`).
- **Almacenamiento:**
  - El archivo se guarda en PostgreSQL (`documentos.contenido BYTEA`), porque el disco del plan gratuito de Render se borra en cada deploy.
  - En una versión productiva iría a un almacenamiento tipo S3 y la tabla guardaría solo la referencia.
- **Indexación para el asistente:**
  - Al subir, `pypdf` extrae el texto por página y lo parte en fragmentos de ~800 caracteres (`documento_fragmentos`).
  - El asistente indexa con TF-IDF los fragmentos de los documentos **públicos** y los cita como "Título, pág. N".
  - El índice se reconstruye solo cuando cambia algún documento.
  - Un PDF escaneado (sin texto) se guarda y se puede ver, pero el asistente no lo lee: haría falta OCR.
- **Acceso:**
  - Se descarga por `GET /api/documentos/<id>/archivo` con token.
  - El propietario solo accede a los públicos.
  - En el navegador se muestra en un visor embebido a partir de un blob, sin URL pública.
- **Sección "Documentos" del propietario:**
  - reglamento navegable, con índice y buscador con resaltado;
  - los PDF publicados.

  Las fuentes que cita el asistente abren el artículo o el PDF correspondiente.

### 13.8 Seguridad (endurecimiento APF3)

| Riesgo | Control aplicado |
|---|---|
| XSS almacenado (datos del usuario dibujados con innerHTML) | `escapeHtml()` en `js/config.js` para todo dato de texto + validación en backend (`utils/validacion.py`) de nombre, apellido, usuario, torre, depto, teléfono y correo |
| Fuerza bruta en login y recuperación | `LimitadorIntentos`: 5 fallos por IP+usuario bloquean 15 min (login) o 1 h (recuperación), responde 429 con `Retry-After` y deja log `rate_limited` |
| Enumeración de cuentas | La recuperación responde el mismo mensaje exista o no el usuario |
| Contraseñas débiles | Mínimo 8 caracteres con letras y números; no puede ser el DNI ni repetir la actual |
| Contraseña inicial = DNI | El login devuelve `debe_cambiar_contrasena` y el panel muestra un aviso hasta que se cambie |
| CORS abierto | Solo orígenes de `CORS_ORIGINS` (por defecto GitHub Pages y localhost) |
| Cabeceras | `nosniff`, `X-Frame-Options DENY`, `HSTS`, `Referrer-Policy`, `Permissions-Policy`, CSP `default-src 'none'` en la API y CSP en los 4 HTML |
| Fuga de errores | Handler global: 500 genérico con `request_id`, el detalle solo va al log |
| JSON con tipos inesperados (lista donde va texto, `NaN` en montos) | `json_body()` en `middleware.py` normaliza el cuerpo y los montos no finitos se rechazan: responde 400, nunca 500 |
| Secreto JWT corto | Aviso al arrancar si `JWT_SECRET` tiene menos de 32 caracteres |
| Inyección de instrucciones al LLM | El system prompt ordena tratar la pregunta y los documentos como información, no como instrucciones; el LLM no puede pagar ni reservar |
| Fuga de datos de terceros por el asistente | Filtro `pregunta_sobre_otro()` + contexto armado solo con el `propietario_id` del JWT |
| Dependencias vulnerables | Dependabot + Dependency Review + CodeQL; 0 alertas abiertas (noviembre 2026) |

Pruebas: `tests/integration/test_seguridad.py` (10 casos) más los casos de privacidad del asistente en `test_innovacion_routes.py`.

**Pendiente recomendado** (fuera del alcance del avance):

- guardar el token en una `httpOnly cookie` en vez de `localStorage`;
- revocar el JWT al cerrar sesión;
- recuperación de contraseña por correo con código temporal;
- limitador de intentos en Redis si hay varias instancias;
- reintento automático en `apiFetch` ante 502/503 durante un *cold start* de Render.
