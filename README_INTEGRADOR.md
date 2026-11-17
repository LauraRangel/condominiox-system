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

## 9. Testing

### Suite de pruebas (`backend/tests/`)

| Tipo | Ubicación | Qué cubre | Requiere DB |
|---|---|---|---|
| Unitarias | `tests/unit/` | `structures.py` (BST, AVL, cola de prioridad, lista, matriz), `utils/money.py` (redondeo `Decimal`), `security.py` (hash/verify password) | No |
| Integración | `tests/integration/` | Rutas Flask reales vía `test_client()`: login, middleware JWT (token ausente/inválido/expirado), control de roles, CRUD de propietarios | Sí (Postgres) |

Cobertura actual: **100%** en `structures.py`, `utils/money.py` y `security.py`. Total: 90 tests (70 unitarias + 20 integración).

### Correr en local

```bash
cd backend
.venv/bin/pip install -r requirements-dev.txt

# Solo unitarias (no requieren base de datos)
.venv/bin/pytest tests/unit -v

# Integración: requiere Postgres corriendo con el schema aplicado.
# Ejemplo con podman/docker, puerto 5439:
podman run -d --name condominiox-postgres-test \
  -e POSTGRES_USER=test -e POSTGRES_PASSWORD=test -e POSTGRES_DB=condominiox_test \
  -p 5439:5432 postgres:16
podman exec -i condominiox-postgres-test psql -U test -d condominiox_test < schema.sql

cp .env.test.example .env.test   # ajustar si el puerto es distinto
.venv/bin/pytest tests/integration -v

# Todo junto + cobertura
.venv/bin/pytest --cov=. --cov-report=term-missing
```

`backend/.env.test` no se versiona (está en `.gitignore`); `backend/.env.test.example` sí, como plantilla.

### Pipeline de CI (GitHub Actions)

| Workflow | Dispara en | Qué hace |
|---|---|---|
| `.github/workflows/tests.yml` | push/PR a `main` | Levanta Postgres 16 como *service container*, aplica `schema.sql`, corre `pytest --cov=.` (unit + integración) |
| `.github/workflows/codeql.yml` | push/PR a `main`, semanal | Análisis estático de seguridad (SAST) para Python y JS/TS |
| `.github/workflows/dependency-review.yml` | PR a `main` | Falla el PR si el diff introduce una dependencia con CVE de severidad alta/crítica |
| `.github/dependabot.yml` | semanal | Abre PRs automáticos de actualización para dependencias pip y GitHub Actions |

`Dependabot` y `Dependency Review` son complementarios: Dependabot mantiene las dependencias al día con el tiempo; Dependency Review es un gate que bloquea en el momento en que alguien introduce una dependencia nueva vulnerable, dentro del mismo PR.

---

## 10. Variables de Entorno (Backend)

| Variable | Descripción | Requerida |
|---|---|---|
| `DATABASE_URL` | Cadena de conexión PostgreSQL | Sí |
| `JWT_SECRET` | Clave para firmar tokens | Sí |
| `JWT_EXPIRES_SECONDS` | Tiempo de vida del token (default: 86400) | No |

Para tests (`backend/.env.test`, no versionado): mismas variables apuntando a un Postgres de prueba. Ver `backend/.env.test.example`.

---

## 11. Despliegue

| Componente | Plataforma |
|---|---|
| Frontend | GitHub Pages (`LauraRangel/condominiox-system`) |
| Backend API | Render Web Service |
| Base de datos | PostgreSQL en Render |

**URL producción:** `https://condominiox-system.onrender.com/api`

---

## 12. Referencias internas

- [backend/structures.py](backend/structures.py) — Estructuras de datos
- [backend/app.py](backend/app.py) — Init y migraciones
- [backend/middleware.py](backend/middleware.py) — Auth y seguridad
- [backend/tests/](backend/tests/) — Suite de pruebas unitarias e integración
- [js/config.js](js/config.js) — Helpers frontend, toast, confirmModal
- [DOCUMENTACION_TECNICA.md](DOCUMENTACION_TECNICA.md) — Detalle HTML/CSS/JS

---

**Versión integrador:** 5.0  
**Fecha:** Junio 2026

---

## 13. Componentes innovadores (APF3)

Tres módulos nuevos sobre la plataforma base. No agregan dependencias: todo usa la librería estándar de Python.

### 13.1 Pasarela de pagos emulada (CU17)

| Pieza | Archivo |
|---|---|
| Adaptadores sandbox Culqi / Yape / Mercado Pago (patrón Strategy) | `backend/services/pasarelas.py` |
| Orquestación: valida, cobra, concilia con FIFO, registra | `backend/services/pago_service.py` |
| Tokenización de tarjeta en el navegador (Culqi.js emulado) | `js/pasarela.js` |

- `POST /api/pagos` (Propietario) con `concepto` `recibo` (pago total o parcial) o `garantia` (monto completo de la garantía de una reserva), y header `Idempotency-Key`: un reintento con la misma clave no cobra dos veces.
- **Atómico:** el cobro aprobado, la actualización del recibo o la reserva, el reparto FIFO a los gastos y el registro en `transacciones_pago` se confirman en un solo commit, con el recibo o la reserva bloqueados (`SELECT ... FOR UPDATE`).
- `transacciones_pago.concepto` distingue `recibo`, `garantia` y `devolucion`.
- `GET /api/pagos/mios` (Propietario) y `GET /api/pagos?estado=` (Admin, con resumen de conciliación).
- El número de tarjeta nunca llega al backend: el navegador genera `tkn_test_<marca>_<last4>_<azar>`.
- `POST /api/recibos/<id>/pagar` queda solo para el Administrador (registro manual de efectivo o transferencia).
- Datos de prueba: tarjeta `4111 1111 1111 1111` aprobada, `4000 0000 0000 0002` rechazada; Yape OTP `000000` rechazado; Mercado Pago con correo que contenga `rechazo` rechazado.

### 13.2 Reserva de áreas comunes y garantías (CU18)

| Área | Tarifa | Garantía | Uso | Aforo | Horario | Anticip. | Máx. |
|---|---|---|---|---|---|---|---|
| Salón de usos múltiples | S/ 80 | S/ 200 | Exclusivo | 40 | 09:00-23:00 | 48 h | 5 h |
| Zona de parrillas | S/ 50 | S/ 100 | Exclusivo | 15 | 11:00-22:00 | 24 h | 4 h |
| Gimnasio | — | — | Compartido | 8 | 06:00-22:00 | 1 h | 2 h |
| Cowork | — | — | Compartido | 12 | 07:00-22:00 | 1 h | 4 h |
| Pet shower | S/ 15 | S/ 30 | Exclusivo | 2 | 08:00-20:00 | 2 h | 1 h |

Valores iniciales sembrados por `migrations.py`; el administrador los edita todos desde "Pagos y Reservas" (`PUT /api/areas-comunes/<id>`, validado con `reserva_service.validar_area()`), además de activar o desactivar cada área. Los cambios aplican solo a reservas nuevas.

- **Reglas** (`reserva_service.validar_reglas()`, función pura): horario, duración máxima, anticipación mínima (hora de Lima), aforo y deuda vencida (`DIAS_DEUDA_VENCIDA`, default 30).
- **Uso exclusivo vs compartido:** en un área exclusiva no se aceptan reservas que se crucen; en una compartida (gimnasio, cowork) se aceptan mientras la suma de personas no supere el aforo. Se valida dentro de la transacción con `SELECT ... FOR UPDATE` sobre el área.
- **Tarifa:** va al recibo del mes (`recibos.monto_reservas`). Si el recibo ya existe se suma al confirmar la reserva; si no, se incluye al generarlo. Cancelar la descuenta.
- **Garantía** (no va al recibo):
  1. Si el área tiene garantía, la reserva nace en `pendiente_garantia` y bloquea el horario 30 minutos.
  2. El propietario la paga completa por la pasarela (`POST /api/pagos` con `concepto: "garantia"`); al aprobarse, la reserva pasa a `confirmada` y la tarifa entra al recibo, todo en una sola transacción.
  3. Si no se paga a tiempo, la reserva pasa a `expirada` y el horario se libera.
  4. Después del uso, el administrador la resuelve (`POST /api/reservas/<id>/garantia/resolucion` con `retener` y `motivo`): devolución total, parcial o retención total. La devolución se emula como un objeto `refund` por el mismo medio del cobro y queda enlazada al cargo original (`transaccion_origen_id`).
  5. Si la reserva se cancela antes de empezar, la garantía se devuelve completa automáticamente.
- **Invitados:** al reservar, el propietario puede registrar la lista de invitados (nombres, apellidos y DNI de 8 dígitos o carné de extranjería de 9 a 12 caracteres), a mano o importando un CSV. Se guardan en `reserva_invitados`, validados con `reserva_service.validar_invitados()` (máximo `asistentes - 1`, sin documentos repetidos). Solo los ven el titular y el administrador (`GET /api/reservas/<id>/invitados`), que puede imprimir la lista para portería. Estos datos nunca se envían al asistente IA.
- Estados de garantía: `no_aplica`, `pendiente`, `pagada` (en custodia), `devuelta`, `devuelta_parcial`, `retenida`, `no_pagada`.
- Endpoints: `GET /api/areas-comunes` (`?todas=1` para el admin), `PUT /api/areas-comunes/<id>` (Admin), `GET /api/areas-comunes/<id>/disponibilidad?fecha=`, `POST /api/reservas`, `GET /api/reservas/mias`, `GET /api/reservas` (Admin), `DELETE /api/reservas/<id>`, `POST /api/reservas/<id>/garantia/resolucion` (Admin).

### 13.3 Asistente virtual con IA (CU19)

```
Pregunta → detección de intención → RAG propio (TF-IDF sobre data/reglamento.json)
         + datos SOLO del propietario del JWT (recibos, pagos, reservas) + gastos del edificio
         → LLM (Groq Llama 3.3 70B o Gemini) con fuentes [F1], [F2]...
         → respuesta citada · si el LLM falla: modo respaldo con plantillas
         → auditoría en consultas_asistente
```

- `services/rag.py`: tokenizador, stopwords, stemmer y sinónimos en español, TF-IDF y similitud coseno implementados desde cero.
- `services/llm_client.py`: cliente HTTP con `urllib` para Groq (API compatible con OpenAI) o Gemini, intercambiable por variable de entorno.
- Minimización de datos: al LLM no se envían DNI, correo ni teléfono, y nunca datos de otros propietarios.
- Límite de 8 consultas por minuto por propietario. Endpoint: `POST /api/asistente/consulta` (Propietario). Cada consulta queda registrada en `consultas_asistente` (trazabilidad), sin pantalla en el admin.

### 13.4 Variables de entorno nuevas

| Variable | Descripción | Default |
|---|---|---|
| `LLM_PROVIDER` | `groq` o `gemini` | `groq` |
| `GROQ_API_KEY` | API key de console.groq.com (si falta, el asistente responde en modo respaldo) | — |
| `GEMINI_API_KEY` | API key de Google AI Studio (si `LLM_PROVIDER=gemini`) | — |
| `LLM_MODEL` | Modelo a usar | `llama-3.3-70b-versatile` / `gemini-2.5-flash` |
| `LLM_TIMEOUT` | Segundos de espera al LLM | `12` |
| `DIAS_DEUDA_VENCIDA` | Días para considerar un recibo vencido | `30` |

### 13.5 Datos de demostración

`cd backend && python seed_demo.py` (idempotente) crea el admin `admin / Admin2026!` si no hay ninguno, 8 propietarios (contraseña = DNI), gastos y recibos de los dos últimos meses. `maria.quispe / 45678912` tiene el recibo del mes pendiente; `carlos.rojas / 41236587` queda moroso para mostrar el bloqueo de reservas.

### 13.7 Documentos del condominio (PDF en PostgreSQL)

- Solo se aceptan **PDF de hasta 5 MB**. Se valida la extensión y el contenido real (`%PDF-`), y se rechazan PDFs protegidos con contraseña.
- El archivo se guarda en PostgreSQL (`documentos.contenido BYTEA`), porque el disco del plan gratis de Render se borra en cada deploy. En producción se movería a un almacenamiento tipo S3 y la tabla guardaría solo la referencia.
- Al subir, `pypdf` extrae el texto por página y lo parte en fragmentos de ~800 caracteres (`documento_fragmentos`). El asistente IA indexa con TF-IDF los fragmentos de los documentos **públicos** y los cita como "Título, pág. N". El índice se reconstruye solo cuando cambia algún documento.
- Un PDF escaneado (sin texto) se guarda y se puede ver, pero el asistente no lo lee (haría falta OCR).
- El archivo se descarga por `GET /api/documentos/<id>/archivo` con token; el propietario solo accede a los públicos. En el navegador se muestra en un visor embebido a partir de un blob, sin exponer una URL pública.
- El propietario tiene la sección "Documentos" con el reglamento navegable (índice, buscador con resaltado) y los PDFs publicados. Las fuentes que cita el asistente abren el artículo o el PDF correspondiente.
- Endpoints: `GET /api/documentos`, `POST /api/documentos` (Admin, multipart), `GET /api/documentos/<id>/archivo`, `PUT /api/documentos/<id>` (Admin), `DELETE /api/documentos/<id>` (Admin), `GET /api/reglamento`.
- Dependencia nueva: `pypdf`. `seed_demo.py` carga un acta de junta y un manual del gimnasio de ejemplo.

### 13.6 Pruebas

`tests/unit/test_pasarelas.py`, `test_rag.py`, `test_reglas_reserva.py`, `test_llm_client.py` y `tests/integration/test_innovacion_routes.py` (pagos aprobados y rechazados, idempotencia, cargo de reservas, morosidad, cruce de horarios, asistente con y sin LLM, minimización de datos). Total de la suite: 175 tests (185 con las de seguridad, ver 13.8).

### 13.8 Seguridad (endurecimiento APF3)

| Riesgo | Control aplicado |
|---|---|
| XSS almacenado (datos del usuario dibujados con innerHTML) | `escapeHtml()` en `js/config.js` para todo dato de texto + validación en backend (`utils/validacion.py`) de nombre, apellido, usuario, torre, depto, teléfono y correo |
| Fuerza bruta en login y recuperación | `LimitadorIntentos`: 5 fallos por IP+usuario bloquean 15 min (login) o 1 h (recuperación), responde 429 con `Retry-After` y deja log `rate_limited` |
| Enumeración de cuentas | La recuperación responde el mismo mensaje exista o no el usuario |
| Contraseñas débiles | Mínimo 8 caracteres con letras y números; no puede ser el DNI ni repetir la actual |
| Contraseña inicial = DNI | El login devuelve `debe_cambiar_contrasena` y el panel muestra un aviso hasta que se cambie |
| CORS abierto | Solo orígenes de `CORS_ORIGINS` (por defecto GitHub Pages y localhost) |
| Cabeceras | `nosniff`, `X-Frame-Options DENY`, `HSTS`, `Referrer-Policy`, CSP `default-src 'none'` en la API y CSP en los 4 HTML |
| Fuga de errores | Handler global: 500 genérico con `request_id`, el detalle solo va al log |
| JSON con tipos inesperados (lista donde va texto, `NaN` en montos) | `json_body()` en `middleware.py` normaliza el cuerpo y los montos no finitos se rechazan: responde 400, nunca 500 |
| Secreto JWT corto | Aviso al arrancar si `JWT_SECRET` tiene menos de 32 caracteres |

Pruebas: `tests/integration/test_seguridad.py` (10 casos). Total suite: 185 tests.

Pendiente recomendado (fuera del alcance del avance): token en `httpOnly cookie` en vez de `localStorage`, revocación de JWT al cerrar sesión, recuperación por correo con código temporal y limitador en Redis si hay varias instancias.
