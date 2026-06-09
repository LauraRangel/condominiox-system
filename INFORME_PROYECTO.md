# Informe de Proyecto — Sistema CondominioX

**Proyecto:** Sistema Web de Gestión de Condominio  
**Tecnologías:** Python · Flask · PostgreSQL · HTML5 · CSS3 · JavaScript  
**Repositorio:** https://github.com/LauraRangel/condominiox-system  
**URL producción:** https://laurarangel.github.io/condominiox-system/  
**Backend API:** https://condominiox-system.onrender.com/api  

---

## 1. Descripción del Sistema

CondominioX es una aplicación web full-stack para la gestión integral de un condominio residencial. Implementa autenticación por roles (Administrador y Propietario), administración de propietarios, control de gastos comunes, generación de recibos con pagos parciales, sistema de comunicados y reportes exportables en Excel.

El sistema fue desarrollado aplicando el patrón arquitectónico **MVC + DAO**, principios **SOLID**, estructuras de datos académicas (BST, AVL, Cola de prioridad, Lista enlazada, Matriz) y librerías equivalentes a las utilizadas en entornos empresariales Java (Apache POI, Logback, Apache Commons).

---

## 2. Casos de Uso Implementados

| # | Caso de Uso | Rol | Estado |
|---|---|---|---|
| CU01 | Login con selección de rol (Administrador / Propietario) | Público | ✅ Implementado |
| CU02 | Gestión de propietarios — crear, editar, eliminar | Administrador | ✅ Implementado |
| CU03 | Configurar monto de administración mensual | Administrador | ✅ Implementado |
| CU04 | Registro y pago de gastos comunes (mantenimiento, luz, agua) | Administrador | ✅ Implementado |
| CU05 | Generación masiva de recibos por fecha | Administrador | ✅ Implementado |
| CU06 | Recalculo mensual de recibos | Administrador | ✅ Implementado |
| CU07 | Pago parcial o total de recibos | Propietario | ✅ Implementado |
| CU08 | Recuperación de contraseña por usuario + DNI | Público | ✅ Implementado |
| CU09 | Cambio de contraseña autenticado | Ambos roles | ✅ Implementado |
| CU10 | Edición de datos de contacto (correo y teléfono) | Propietario | ✅ Implementado |
| CU11 | Estado de cuenta individual por propietario | Administrador | ✅ Implementado |
| CU12 | Historial de pagos con filtro por mes | Propietario | ✅ Implementado |
| CU13 | Sistema de comunicados con fecha de caducidad | Ambos roles | ✅ Implementado |
| CU14 | Estado financiero resumido mensual con desglose | Administrador | ✅ Implementado |
| CU15 | Exportación de reporte de morosidad en Excel (.xlsx) | Administrador | ✅ Implementado |

### Funcionalidades adicionales implementadas

- Búsqueda de propietarios con árbol BST (por nombre, apellido, DNI, departamento, torre, piso)
- Búsqueda de recibos por rango de saldo con árbol AVL (inorden)
- Ranking automático de morosos con cola de prioridad (saldo + días de mora)
- Resumen mensual de recibos (emitido, cobrado, saldo, porcentaje de cobranza)
- Sistema de notificaciones toast (reemplaza todos los `alert()` nativos del navegador)
- Modal de confirmación estilizado para acciones críticas (reemplaza `confirm()` nativo)
- Guardias de rol en frontend: propietario no puede acceder al panel de administrador
- Logging de seguridad estructurado en JSON para todos los accesos no autorizados
- Toggle de visibilidad de contraseña en todos los campos tipo password

---

## 3. Qué Falta / Posibles Mejoras

Según los requerimientos típicos de un sistema de gestión de condominio y los casos de uso declarados, los siguientes elementos **no están implementados** o están **parcialmente cubiertos**:

### 3.1 Funcionalidades no implementadas

| Ítem | Descripción | Prioridad |
|---|---|---|
| **Paginación en tablas** | Las tablas de propietarios, recibos y gastos cargan todos los registros sin paginación. Con muchos datos puede degradar el rendimiento. | Media |
| **Filtro de propietarios por estado** | No existe filtro para ver solo propietarios con deuda activa vs sin deuda. | Baja |
| **Notificaciones por correo** | Los anuncios y vencimientos de recibos no generan correos automáticos a los propietarios. | Media |
| **Adjuntos en gastos** | No se puede subir comprobante o factura del gasto registrado. | Baja |
| **Pago online integrado** | El pago de recibos es registro manual; no hay integración con pasarela de pagos. | Alta (futura) |
| **Dashboard propietario** | El propietario no tiene un dashboard con indicadores visuales (gráfica de pagos, historial visual). | Baja |
| **Eliminar recibo** | El administrador puede eliminar recibos pero la UI del botón no tiene confirmación de cuáles se eliminan en cascada. | Baja |
| **Auditoría completa** | Los logs de seguridad registran accesos fallidos pero no registran quién modificó qué propietario o recibo. | Media |
| **Multicondominio** | El sistema gestiona un único condominio. No soporta múltiples edificios/condominios desde una misma instancia. | Alta (futura) |
| **Tests automatizados** | No hay suite de tests unitarios ni de integración (pytest). El plan arquitectónico los contemplaba. | Media |

### 3.2 Mejoras UX pendientes

| Ítem | Descripción |
|---|---|
| **Responsive en tablas anchas** | En móvil, las tablas de recibos con muchas columnas requieren scroll horizontal. Se puede mejorar con tarjetas en móvil. |
| **Confirmación de pago con comprobante** | Al confirmar un pago, podría generarse un PDF/comprobante descargable. |
| **Carga progresiva (skeleton)** | Las secciones muestran "Cargando..." pero sin skeleton screen visual. |

---

## 4. Estructuras de Datos Utilizadas

Todas implementadas en `backend/structures.py` y consumidas por la capa de servicios.

### 4.1 Lista Enlazada Simple — `ListaPropietarios`

**Propósito:** Encapsular el recorrido secuencial de propietarios retornados por la base de datos.

**Operaciones implementadas:**

| Operación | Complejidad |
|---|---|
| `insertar(data)` — agrega al final | O(1) con puntero a tail |
| `eliminar_por_id(id)` — recorre y desenlaza | O(n) |
| `recorrer(callback)` — aplica función a cada nodo | O(n) |
| `to_list()` — convierte a lista Python | O(n) |

```python
class NodoPropietario:
    def __init__(self, data):
        self.data = data
        self.next = None

class ListaPropietarios:
    def __init__(self):
        self.head = None
        self.tail = None
        self.length = 0

    def insertar(self, data):
        nodo = NodoPropietario(data)
        if not self.head:
            self.head = nodo
            self.tail = nodo
        else:
            self.tail.next = nodo
            self.tail = nodo
        self.length += 1
```

**Dónde se usa:** `propietario_service.list_propietarios()` — los registros de PostgreSQL se insertan uno a uno en la lista antes de retornarlos al frontend.

---

### 4.2 Árbol Binario de Búsqueda (BST) — `ArbolPropietariosBST` y `ArbolRecibosBST`

**Propósito:** Búsqueda eficiente de propietarios por clave compuesta (apellido, nombre) y de recibos por saldo.

**Operaciones implementadas:**

| Operación | Complejidad promedio | Complejidad peor caso |
|---|---|---|
| `insertar(key, data)` | O(log n) | O(n) árbol degenerado |
| `buscar(key)` | O(log n) | O(n) |
| `recorrer(modo)` — inorden/preorden/postorden | O(n) | O(n) |
| `rango(min, max)` — nodos entre dos claves | O(log n + k) | O(n) |

**Recorridos disponibles:**
- **Inorden**: retorna propietarios en orden alfabético / recibos de menor a mayor saldo.
- **Preorden**: retorna desde la raíz hacia los descendientes.
- **Postorden**: retorna hojas primero, raíz al final.

**Dónde se usa:**
- `GET /api/propietarios/busqueda` → `ArbolPropietariosBST` con clave `(apellido, nombre)`.
- `GET /api/recibos/estructura/bst` → `ArbolRecibosBST` con clave `(saldo, id)`.

---

### 4.3 Árbol AVL (Autobalanceado) — `ArbolRecibosAVL`

**Propósito:** Garantizar búsqueda balanceada en recibos por rango de saldo, independiente del orden de inserción.

El AVL extiende al BST agregando rotaciones automáticas para mantener que la diferencia de altura entre subárboles izquierdo y derecho sea máximo 1 (factor de balance ∈ {-1, 0, 1}).

**Tipos de rotación:**

| Caso | Rotación |
|---|---|
| Inserción en subárbol izquierdo-izquierdo | Simple derecha |
| Inserción en subárbol derecho-derecho | Simple izquierda |
| Inserción en subárbol izquierdo-derecho | Doble: izquierda + derecha |
| Inserción en subárbol derecho-izquierdo | Doble: derecha + izquierda |

**Complejidad garantizada (peor caso):**

| Operación | Complejidad |
|---|---|
| Insertar | O(log n) |
| Buscar | O(log n) |
| Rango | O(log n + k) |

**Dónde se usa:** `GET /api/recibos/estructura/avl` — frontend de "Búsqueda avanzada por rango de saldo".

---

### 4.4 Cola de Prioridad — `ColaPrioridadMorosos`

**Propósito:** Ordenar automáticamente los propietarios con deuda por nivel de urgencia (mayor saldo pendiente primero; en empate, más días sin pagar).

**Criterio de prioridad:** `(-saldo, -dias_pendiente)` — se invierte el signo para que Python's `heapq` (min-heap) funcione como max-heap.

**Operaciones implementadas:**

| Operación | Complejidad |
|---|---|
| `enqueue(item)` | O(log n) |
| `to_sorted_list(limit)` | O(n log n) |

**Dónde se usa:**
- `GET /api/recibos/morosos/prioridad` → top morosos en el panel.
- `GET /api/reportes/morosidad/excel` → misma cola para generar el Excel.

---

### 4.5 Matriz de Recibos — `MatrizRecibos`

**Propósito:** Organizar los recibos en una estructura bidimensional `[mes][propietario_id]` para aggregación eficiente por período.

```
MatrizRecibos:
  "2026-06" → { 101: recibo_A, 102: recibo_B, ... }
  "2026-05" → { 101: recibo_C, 103: recibo_D, ... }
```

**Operaciones implementadas:**

| Operación | Complejidad |
|---|---|
| `set_recibo(mes, pid, recibo)` | O(1) |
| `get_recibo(mes, pid)` | O(1) |
| `listar_por_propietario(pid)` | O(meses) |
| `total_por_mes(mes)` | O(propietarios del mes) |

**Dónde se usa:** `recibo_service.list_recibos_admin()` — organiza y resume recibos por mes para el resumen mensual del panel.

---

### 4.6 Pila de Filtros — `PilaFiltros` (Frontend)

**Propósito:** Mantener un historial de filtros aplicados en la búsqueda estructurada del panel administrador.

```javascript
class PilaFiltros {
    constructor() { this.items = []; }
    push(item)  { this.items.push(item); }
    pop()       { return this.items.length ? this.items.pop() : null; }
    size()      { return this.items.length; }
}
```

**Dónde se usa:** `js/admin.js` — registra cada combinación de filtros (mes, estado, tipo) aplicada en la sección de recibos.

---

### 4.7 Índice Hash de Gastos — `IndiceGastos` (Frontend)

**Propósito:** Acceso O(1) a gastos filtrados por mes y/o tipo, evitando recorrer el array completo en cada cambio de filtro.

```javascript
class IndiceGastos {
    constructor(items) {
        this.byMes = new Map();      // clave: "2026-06"
        this.byTipo = new Map();     // clave: "mantenimiento"
        this.byMesTipo = new Map();  // clave: "2026-06|mantenimiento"
    }

    query(mes = '', tipo = '') {
        if (mes && tipo) return this.byMesTipo.get(`${mes}|${tipo}`) || [];
        if (mes)         return this.byMes.get(mes) || [];
        if (tipo)        return this.byTipo.get(tipo) || [];
        return this.all.slice();
    }
}
```

**Dónde se usa:** `js/admin.js` — los filtros de gastos por mes/tipo no hacen nueva llamada al servidor; consultan el índice local.

---

## 5. Librerías Utilizadas y Equivalencias Académicas

### 5.1 openpyxl — Equivalente a Apache POI (Java)

**Apache POI** es la librería estándar de Java para leer/escribir archivos de Microsoft Office (`.xlsx`, `.docx`).  
**openpyxl** cumple exactamente el mismo rol en Python.

**Uso en el proyecto (CU15 — Exportar reporte de morosidad):**

```python
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Reporte Morosidad"

# Título mergeado y centrado (equivalente a CellRangeAddress en POI)
ws.merge_cells("A1:H1")
ws["A1"] = "REPORTE DE MOROSIDAD"
ws["A1"].font = Font(bold=True, size=14)
ws["A1"].alignment = Alignment(horizontal="center")

# Cabeceras con estilo (equivalente a CellStyle en POI)
header_fill = PatternFill(start_color="2563EB", end_color="2563EB", fill_type="solid")
header_font = Font(bold=True, color="FFFFFF")

for col, titulo in enumerate(headers, start=1):
    cell = ws.cell(row=4, column=col, value=titulo)
    cell.fill = header_fill
    cell.font = header_font

# Guardar en memoria y retornar bytes al frontend
buf = io.BytesIO()
wb.save(buf)
return buf.read()
```

**Comparación Apache POI vs openpyxl:**

| Apache POI (Java) | openpyxl (Python) |
|---|---|
| `XSSFWorkbook` | `openpyxl.Workbook()` |
| `XSSFSheet` | `wb.active` / `wb.create_sheet()` |
| `CellStyle` | `Font`, `PatternFill`, `Alignment` |
| `CellRangeAddress` | `ws.merge_cells("A1:H1")` |
| `FileOutputStream` | `io.BytesIO()` |

---

### 5.2 python-json-logger — Equivalente a Logback (Java)

**Logback** es el framework de logging estándar en aplicaciones Java empresariales. Produce logs estructurados configurables por niveles y appenders.  
**python-json-logger** cumple el mismo rol: produce logs en formato JSON estructurado, con campos configurables, sobre el sistema de logging estándar de Python.

**Configuración en el proyecto (`backend/utils/logger.py`):**

```python
import logging
from pythonjsonlogger import jsonlogger

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
```

**Uso en seguridad (`backend/middleware.py`):**

```python
_sec_log = get_logger("security")

# Acceso sin token
_sec_log.warning("Acceso sin token", extra={
    "event": "missing_token",
    "ip": request.remote_addr,
    "path": request.path,
    "method": request.method
})

# Acceso con rol incorrecto
_sec_log.warning("Acceso denegado por rol", extra={
    "event": "forbidden_role",
    "ip": request.remote_addr,
    "user": payload.get("usuario"),
    "rol_actual": payload.get("tipo"),
    "rol_requerido": list(roles)
})
```

**Salida real en producción (Render logs):**
```json
{
  "asctime": "2026-06-09T17:53:00",
  "name": "security",
  "levelname": "WARNING",
  "message": "Acceso denegado por rol",
  "event": "forbidden_role",
  "ip": "190.x.x.x",
  "user": "juan123",
  "rol_actual": "Propietario",
  "rol_requerido": ["Administrador"]
}
```

**Comparación Logback vs python-json-logger:**

| Logback (Java) | python-json-logger (Python) |
|---|---|
| `LoggerFactory.getLogger(Class)` | `get_logger(__name__)` |
| `logger.warn("msg", keyValue("k","v"))` | `logger.warning("msg", extra={"k":"v"})` |
| Appender JSON (Logstash encoder) | `JsonFormatter` |
| `logback.xml` configuración | `logging.basicConfig()` / handler setup |
| Niveles: TRACE/DEBUG/INFO/WARN/ERROR | Niveles: DEBUG/INFO/WARNING/ERROR/CRITICAL |

---

### 5.3 validators — Equivalente a Apache Commons Validator (Java)

**Apache Commons Validator** es la librería estándar de Java para validar formatos de datos (email, URL, DNI, tarjetas de crédito, etc.).  
**validators** cumple el mismo rol en Python.

**Uso en el proyecto (`backend/services/propietario_service.py`):**

```python
import validators

def create_propietario(data: dict) -> dict:
    correo = data.get("correo", "").strip()
    if correo and not validators.email(correo):
        raise ValueError("Formato de correo electrónico inválido")
    # ... resto de la lógica
```

**Comparación Apache Commons Validator vs validators:**

| Apache Commons Validator (Java) | validators (Python) |
|---|---|
| `EmailValidator.getInstance().isValid(email)` | `validators.email(email)` |
| `UrlValidator.getInstance().isValid(url)` | `validators.url(url)` |
| `GenericValidator.isBlankOrNull(str)` | `not str or not str.strip()` |

---

### 5.4 python-dateutil — Equivalente a Apache Commons Lang (Java)

**Apache Commons Lang** incluye utilidades para manejo de fechas (`DateUtils`).  
**python-dateutil** cumple el mismo rol.

**Uso en el proyecto (`backend/services/recibo_service.py`):**

```python
import datetime as dt

# Calcular días de mora entre fecha de emisión y hoy
hoy = dt.date.today()
fecha = dt.date.fromisoformat(r["fecha_emision"][:10])
dias_mora = max((hoy - fecha).days, 0)
```

---

### 5.5 PyJWT — Equivalente a JJWT (Java)

**JJWT** (Java JWT) es la librería estándar para generar y validar JSON Web Tokens en Java.  
**PyJWT** cumple exactamente el mismo rol en Python.

**Uso en el proyecto (`backend/middleware.py`):**

```python
import jwt

# Generar token al login (auth_service.py)
token = jwt.encode(
    {"usuario": "admin", "tipo": "Administrador", "exp": datetime.utcnow() + timedelta(seconds=86400)},
    JWT_SECRET,
    algorithm="HS256"
)

# Validar token en cada request protegida
payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
```

---

## 6. Consideraciones de Seguridad

### 6.1 Autenticación JWT stateless

- El token se firma con `HS256` usando `JWT_SECRET` (variable de entorno, nunca en código).
- El token expira en 24 horas (`JWT_EXPIRES_SECONDS=86400`).
- Al cerrar sesión se elimina del `localStorage` del navegador.
- Cada request protegida valida firma y expiración antes de ejecutar la lógica.

### 6.2 Control de acceso por rol (Autorización)

- Cada endpoint del backend declara explícitamente los roles permitidos con `require_roles(payload, "Administrador")`.
- Si el rol no coincide → respuesta 403 Forbidden.
- En el frontend, al cargar `admin.html` se verifica que `userData.tipo === 'Administrador'`; si no → redirige a `index.html`. Mismo patrón para `propietario.html`.

### 6.3 Sin revelación de información sensible

- Todos los errores de login (usuario incorrecto, contraseña incorrecta, rol incorrecto) retornan exactamente el mismo mensaje: `"Usuario o contraseña inválidos"`.
- El backend **no indica** si el usuario existe o si el rol es distinto al esperado.
- Esto previene ataques de enumeración de usuarios.

### 6.4 Logging de seguridad estructurado

- Cada intento fallido de autenticación o acceso no autorizado genera un evento de log con:
  - IP del cliente
  - Ruta solicitada
  - Método HTTP
  - Usuario (si está en el token)
  - Rol actual vs rol requerido
  - Timestamp ISO 8601
- Los logs se producen en formato JSON (compatible con herramientas de análisis como Elasticsearch, Datadog, etc.).

### 6.5 CORS configurado explícitamente

```python
CORS(app, resources={r"/api/*": {
    "origins": "*",
    "methods": ["GET","POST","PUT","DELETE","OPTIONS","PATCH"],
    "allow_headers": ["Content-Type","Authorization"]
}})
```

- Solo las rutas bajo `/api/*` aceptan requests cross-origin.
- El frontend en GitHub Pages (`laurarangel.github.io`) y el backend en Render son dominios distintos; CORS permite esa comunicación de forma controlada.

### 6.6 Precisión monetaria

- Todos los cálculos de montos usan el tipo `Decimal` de Python (no `float`) para evitar errores de redondeo de punto flotante.
- Los resultados se redondean a 2 decimales antes de devolver al frontend.

### 6.7 Variables de entorno

- `DATABASE_URL` y `JWT_SECRET` nunca están en el código fuente.
- Se gestionan como variables de entorno en Render (panel de environment variables).
- El archivo `.env` está en `.gitignore` para no exponerse en el repositorio.

---

## 7. Control de Versiones con Git — Evidencia de Avances

El proyecto mantiene historial completo de commits en GitHub, cubriendo el 100% de los avances:

### 7.1 Repositorio

- **URL:** https://github.com/LauraRangel/condominiox-system
- **Rama principal:** `main`
- **Total de commits:** 25+

### 7.2 Historial de commits (cronológico, más reciente primero)

| Hash | Fecha | Descripción |
|---|---|---|
| `ad5d28c` | 2026-06-09 | Mostrar error detallado en toast al fallar exportación Excel |
| `1d9c5ae` | 2026-06-09 | Actualizar documentación completa a versión 5.0 |
| `96535ef` | 2026-06-09 | Rediseñar sección Recibos en admin: más clara y amigable |
| `e00bc3d` | 2026-06-09 | Fix AttributeError en exportación Excel por MergedCell |
| `d982c9a` | 2026-06-09 | Aplicar mejoras UI al panel propietario y compartir confirmModal |
| `9553afe` | 2026-06-09 | Fix input month cortado en Estado Financiero |
| `187e41b` | 2026-06-09 | Fix CORS: quitar after_request y handle_options manuales |
| `7f23a14` | 2026-06-09 | Rediseño UI: modal gastos con tabs, modales estructurados |
| `77bd74e` | 2026-06-09 | Capturar y loguear excepciones en exportar Excel |
| `7bb10af` | 2026-06-09 | Fix information disclosure en login |
| `74f139a` | 2026-06-09 | Seguridad: guard de rol en frontend y logging de accesos |
| `0303f94` | 2026-06-09 | Reemplazar prompt de pago por modal con botón 'Pagar total' |
| `ed6cde1` | 2026-06-09 | Toast notifications, fix input mes financiero |
| `8d72396` | 2026-06-09 | Fix clave localStorage bloqueaba carga de comunicados |
| `dba3faa` | 2026-06-09 | Fix token key incorrecta en exportar Excel |
| `7cb4044` | 2026-06-09 | Agregar fecha_caducidad a anuncios (CU13) |
| `d84807c` | 2026-06-09 | Fix URL exportar Excel apuntaba a GitHub Pages |
| `c41099d` | 2026-06-09 | Fix KeyError propietario_id en estado-cuenta |
| `4cbeec3` | 2026-06-09 | Fix CORS preflight para endpoints nuevos en producción |
| `ca5321b` | 2026-06-09 | Restructurar backend a MVC+DAO+SOLID e implementar CU11-CU15 |
| `b312a1a` | 2026-05-15 | Update footer year |
| `90cd1c9` | 2026-05-15 | Update documentación técnica |
| `2036cf8` | 2026-05-14 | Merge pull request #1 |
| `86cb030` | 2026-05-13 | Agregar documentación markdown del sistema |
| `bfb2de9` | 2026-03-03 | Update saldo pagado |

### 7.3 Tipos de cambios evidenciados

| Categoría | Commits |
|---|---|
| Nuevas funcionalidades (CU11-CU15) | `ca5321b`, `7cb4044`, `0303f94` |
| Corrección de bugs | `e00bc3d`, `c41099d`, `9553afe`, `8d72396`, `dba3faa`, `d84807c`, `187e41b` |
| Seguridad | `7bb10af`, `74f139a` |
| Mejoras de UI/UX | `96535ef`, `7f23a14`, `d982c9a`, `ed6cde1` |
| Documentación | `1d9c5ae`, `90cd1c9`, `86cb030` |
| Infraestructura / CORS | `4cbeec3`, `187e41b` |

### 7.4 Buenas prácticas de Git aplicadas

- **Commits atómicos:** cada commit representa un cambio coherente y autocontenido.
- **Mensajes descriptivos:** formato `Verbo + objeto + contexto` en español. El lector entiende qué cambió sin leer el diff.
- **Co-Authored-By:** cada commit incluye autoría colaborativa.
- **Sin secretos en el repositorio:** `.env` está en `.gitignore`; las credenciales solo existen como variables de entorno en Render.
- **Tags de versión implícitos:** los commits de documentación señalan versiones (v3.0, v4.0, v5.0).

---

## 8. Arquitectura del Sistema (Resumen Visual)

```
┌──────────────────────────────────────────────────────────────────┐
│                        FRONTEND (GitHub Pages)                   │
│  index.html   admin.html   propietario.html   recuperar.html     │
│  ┌──────────┐ ┌──────────┐ ┌───────────────┐                    │
│  │config.js │ │ auth.js  │ │   admin.js    │  propietario.js    │
│  │API_URL   │ │ Login    │ │   CRUD        │  Recibos           │
│  │apiFetch  │ │ Roles    │ │   Estructuras │  Comunicados       │
│  │showToast │ │ Logout   │ │   Reportes    │                    │
│  └──────────┘ └──────────┘ └───────────────┘                    │
└────────────────────────────┬─────────────────────────────────────┘
                             │ HTTPS + Bearer JWT
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                    BACKEND (Render — Flask)                       │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Routes (Controller) — Blueprints Flask                  │    │
│  │  auth · propietarios · gastos · recibos · anuncios       │    │
│  │  configuracion · reportes · health                        │    │
│  └──────────────────────┬──────────────────────────────────┘    │
│                         │                                        │
│  ┌──────────────────────▼──────────────────────────────────┐    │
│  │  Services (Business Logic)                                │    │
│  │  auth · propietario · gasto · recibo · anuncio           │    │
│  │  configuracion · reporte                                  │    │
│  │  ┌────────────────────────────────────────────────────┐  │    │
│  │  │  structures.py                                      │  │    │
│  │  │  Lista · BST · AVL · ColaPrioridad · Matriz · Pila │  │    │
│  │  └────────────────────────────────────────────────────┘  │    │
│  └──────────────────────┬──────────────────────────────────┘    │
│                         │                                        │
│  ┌──────────────────────▼──────────────────────────────────┐    │
│  │  DAO (Data Access Object) — SQL puro                     │    │
│  │  usuario · propietario · gasto · recibo                  │    │
│  │  configuracion · anuncio                                  │    │
│  └──────────────────────┬──────────────────────────────────┘    │
│                         │                                        │
│  ┌──────────────────────▼──────────────────────────────────┐    │
│  │  middleware.py — JWT · Roles · Security logging          │    │
│  │  utils/logger.py — JSON logs (python-json-logger)        │    │
│  │  utils/money.py — Decimal precision                       │    │
│  └─────────────────────────────────────────────────────────┘    │
└────────────────────────────┬─────────────────────────────────────┘
                             │ psycopg (SQL)
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                  BASE DE DATOS (PostgreSQL — Render)             │
│  usuarios · propietarios · gastos · pagos_gastos                │
│  recibos · configuracion · anuncios · lecturas_anuncios          │
└──────────────────────────────────────────────────────────────────┘
```

---

**Versión del informe:** 1.0  
**Fecha:** Junio 2026  
**Repositorio:** https://github.com/LauraRangel/condominiox-system
