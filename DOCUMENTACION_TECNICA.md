# Documentación Técnica — Sistema CondominioX

## 0. Arquitectura General

### Stack tecnológico

| Capa | Tecnología |
|---|---|
| Frontend | HTML5 + CSS3 + JavaScript (vanilla) |
| Backend | Python 3 + Flask (API REST) |
| Base de datos | PostgreSQL |
| Autenticación | JWT (Bearer token) |
| Hosting frontend | GitHub Pages |
| Hosting backend | Render Web Service |

### Patrón arquitectónico: MVC + DAO

```
Routes (Controller) → Services (Business Logic) → DAO (Data Access) → PostgreSQL
                                                  ↕
                                          structures.py (BST, AVL, Cola, etc.)
```

- **Routes** (`backend/routes/`): reciben la request HTTP, validan auth/rol, delegan al service.
- **Services** (`backend/services/`): contienen la lógica de negocio pura, sin conocer Flask ni SQL.
- **DAO** (`backend/dao/`): SQL puro, sin lógica de negocio. Un archivo por entidad.
- **Structures** (`backend/structures.py`): estructuras de datos académicas usadas por los services.

### Variables de entorno (backend)

```
DATABASE_URL=postgresql://user:pass@host/db
JWT_SECRET=clave_secreta
JWT_EXPIRES_SECONDS=86400   # opcional, default 24h
```

---

## 1. HTML: Estructura y Elementos

### Checklist de requisitos

| Requisito | Dónde se aplica |
|---|---|
| Estructura básica + meta tags | `index.html`, `admin.html`, `propietario.html`, `recuperar.html` |
| Etiquetas de texto (`h1`–`h3`, `p`, `span`, `small`) | Todos los archivos HTML |
| Enlace a página externa | `index.html` → `recuperar.html` |
| Encabezado/menú/cuerpo semántico | `<aside>`, `<nav>`, `<main>`, `<section>` en admin y propietario |
| Menú hamburguesa responsive | `.menu-toggle` + `toggleSidebarMenu()` en `auth.js` |
| Formularios con validación | Login, propietarios, gastos, cambio de contraseña |
| Tablas | Propietarios, gastos, recibos, morosos, resumen mensual |
| Multimedia (imágenes) | `img/logo.png` en todas las páginas |
| Accesibilidad (`aria-*`, `role`, `label for`) | Modales, inputs, botones de contraseña |

### 1.1 Estructura del documento

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Panel de Administrador - CondominioX">
    <title>Panel Administrador - CondominioX</title>
    <link rel="stylesheet" href="css/styles.css?v=20260306">
</head>
<body>
    <div class="app-container">
        <aside class="sidebar">...</aside>
        <main class="panel-content">...</main>
    </div>
    <!-- Modales al final del body -->
    <div id="confirmModal" class="modal-overlay hidden">...</div>
    <div id="toast-container"></div>
    <script src="js/config.js?v=20260306"></script>
    <script src="js/auth.js?v=20260306"></script>
    <script src="js/admin.js?v=20260306"></script>
</body>
</html>
```

**Nota sobre versioning:** El sufijo `?v=20260306` en CSS y JS fuerza al navegador a descargar la versión más reciente tras un deploy, evitando servir archivos en caché.

### 1.2 Layout de dos columnas

```
┌─────────────────────────────────────────────────┐
│  <aside class="sidebar">    │  <main>            │
│  Logo + nav + usuario       │  Secciones         │
│  (280px fijo)               │  (flex: 1)         │
└─────────────────────────────────────────────────┘
```

```css
.app-container {
    display: flex;
    min-height: 100vh;
}
.sidebar {
    width: 280px;
    flex-shrink: 0;
}
.panel-content {
    flex: 1;
    overflow-y: auto;
}
```

### 1.3 Tipos de inputs usados

| Tipo | Ejemplo de uso |
|---|---|
| `text` | Nombre, usuario, DNI, proveedor |
| `password` | Contraseñas (con toggle ver/ocultar) |
| `email` | Correo electrónico |
| `tel` | Teléfono |
| `number` | Montos, min/step |
| `date` | Fecha de emisión de recibo |
| `month` | Filtro por mes (YYYY-MM) |
| `select` | Tipo de usuario, tipo de gasto, tipo de anuncio |
| `textarea` | Contenido de anuncio |
| `hidden` | Tipo de usuario en login |

### 1.4 Modales: estructura estándar

Todos los modales del sistema usan esta estructura consistente:

```html
<div id="miModal" class="modal-overlay hidden" role="dialog" aria-modal="true" aria-labelledby="miModalTitulo">
    <div class="modal-card" onclick="event.stopPropagation()">
        <div class="modal-header">
            <h3>
                <span class="modal-icon success">✅</span>
                <span id="miModalTitulo">Título</span>
            </h3>
            <button type="button" class="btn-close" onclick="cerrarModal()" aria-label="Cerrar">×</button>
        </div>
        <div class="modal-body">
            <!-- Contenido -->
        </div>
        <div class="modal-footer">
            <button class="btn btn-secondary" onclick="cerrarModal()">Cancelar</button>
            <button class="btn btn-primary" onclick="confirmar()">Confirmar</button>
        </div>
    </div>
</div>
```

- `modal-overlay`: fondo semitransparente, cierre al hacer click fuera.
- `onclick="event.stopPropagation()"` en `modal-card` evita que el click se propague al overlay.
- `aria-modal`, `role="dialog"`, `aria-labelledby`: accesibilidad.

---

## 2. CSS: Estilos y Diseño

### 2.1 Variables CSS

```css
:root {
    --primary-dark: #1e3a3a;
    --primary: #2d4a4a;
    --accent-gold: #c9a227;
    --accent-gold-dark: #a07d1a;
    --white: #ffffff;
    --off-white: #f8f9fa;
    --light-gray: #e2e8f0;
    --text-dark: #1e293b;
    --text-muted: #64748b;
    --radius: 12px;
    --radius-lg: 16px;
    --shadow: 0 4px 20px rgba(0,0,0,.1);
    --transition: all 0.3s ease;
}
```

### 2.2 Checklist CSS

| Requisito | Dónde |
|---|---|
| Variables CSS (custom properties) | `:root` en `styles.css` |
| Selectores de clase, ID, pseudo-clase | `.btn:hover`, `#loginForm`, `tr:nth-child(even)` |
| Tipografía y colores | Variables + clases de texto |
| Flexbox | Sidebar, nav, cards, filter-bar |
| Grid | Stats grid, forms, recibos-actions-row |
| Transiciones | Botones, modales, sidebar |
| Animaciones (`@keyframes`) | `fadeInOverlay`, `slideUpModal`, toast entrada/salida |
| Responsive (media queries) | `@media (max-width: 992px)`, `@media (max-width: 576px)` |
| Menú hamburguesa | `.menu-toggle` visible solo en móvil |

### 2.3 Sistema de botones

```css
.btn           /* base: padding, border-radius, cursor */
.btn-primary   /* dorado — acción principal */
.btn-secondary /* gris — acción secundaria / cancelar */
.btn-success   /* verde — acción positiva */
.btn-danger    /* rojo — eliminar / acción destructiva */
.btn-sm        /* tamaño reducido para tablas y barras */
```

### 2.4 Sistema de notificaciones Toast

Los toasts reemplazan todos los `alert()` del sistema. Se invocan con:

```javascript
showToast('Mensaje', 'success' | 'error' | 'warning' | 'info', 'Título opcional');
```

Estructura CSS:
```css
.toast              /* contenedor base, posición fixed bottom-right */
.toast-success      /* borde e ícono verde */
.toast-error        /* borde e ícono rojo */
.toast-warning      /* borde e ícono amarillo */
.toast-info         /* borde e ícono azul */
```

Auto-desaparece a los 4 segundos con animación de salida.

### 2.5 Animaciones de modales

```css
@keyframes fadeInOverlay {
    from { opacity: 0; }
    to   { opacity: 1; }
}

@keyframes slideUpModal {
    from { transform: translateY(30px); opacity: 0; }
    to   { transform: translateY(0);    opacity: 1; }
}

.modal-overlay { animation: fadeInOverlay .2s ease; }
.modal-card    { animation: slideUpModal .25s ease; }
```

### 2.6 Cards financieras (Dashboard)

```css
.financiero-card     /* base: border-radius, padding, shadow */
.fc-blue             /* azul — total emitido */
.fc-green            /* verde — total cobrado */
.fc-red              /* rojo — saldo pendiente */
.fc-amber            /* amarillo — porcentaje cobranza */
```

### 2.7 Modal con tabs (Gastos)

```css
.gasto-tabs    /* contenedor de pestañas */
.gasto-tab     /* pestaña individual */
.gasto-tab.active  /* pestaña activa */
.gasto-panel   /* contenido de cada pestaña (hidden por default) */
.gasto-panel.active /* panel visible */
```

---

## 3. JavaScript: Organización y Funciones

### 3.1 config.js — Funciones compartidas

```javascript
// URL del backend
const API_URL = 'https://condominiox-system.onrender.com/api';

// Fetch autenticado — agrega Bearer token y maneja 401
async function apiFetch(path, options = {}) { ... }

// Helpers de localStorage
function getAuthToken()          // lee 'auth_token'
function setAuthToken(token)     // guarda 'auth_token'
function removeAuthToken()       // borra token + user_data
function getUserData()           // lee y parsea 'user_data'
function setUserData(data)       // guarda como JSON

// Formato
function formatDate(dateString)       // DD/MM/YYYY
function formatMonthYear(dateString)  // "junio 2026"
function formatCurrency(amount)       // "S/ 120.00"

// Notificaciones
function showToast(message, type, title)  // toast no-bloqueante

// Modal de confirmación (compartido admin + propietario)
function confirmModal(message, title, tipo)  // retorna Promise<boolean>
function cerrarConfirmModal(accepted)
```

### 3.2 auth.js — Autenticación y UI común

```javascript
// Login: POST /api/login → guarda token y userData → redirige por rol
document.getElementById('loginForm').addEventListener('submit', ...)

// Guardia de rol: se ejecuta al cargar admin.html / propietario.html
if (window.location.pathname.includes('admin.html')) {
    requireAuth();
    const userData = getUserData();
    if (!userData || userData.tipo !== 'Administrador') {
        removeAuthToken();
        window.location.replace('index.html');
    }
}

// Cerrar sesión con confirmación modal
async function cerrarSesion() {
    const ok = await confirmModal('¿Está seguro que desea cerrar sesión?', 'Cerrar sesión');
    if (ok) { removeAuthToken(); window.location.replace('index.html'); }
}

// Toggle de visibilidad de contraseña
function inicializarToggleContrasenas()  // busca todos los .password-toggle-btn

// Responsive sidebar
function toggleSidebarMenu()
```

### 3.3 admin.js — Panel administrador

Principales grupos de funciones:

```javascript
// Dashboard
cargarDashboard()          // propietarios, recibos, gastos
actualizarResumenFinanciero()  // GET /api/reportes/financiero

// Propietarios
cargarPropietarios()
crearPropietario()
editarPropietario(id)
eliminarPropietario(id)    // usa confirmModal
abrirEstadoCuenta(id)      // modal con recibos del propietario

// Gastos
cargarGastos()
abrirModalGasto(tipo)      // abre modal con pestaña activa
switchGastoTab(tipo)       // cambia entre mantenimiento/luz/agua
submitGasto(event, tipo)   // envía el formulario del panel activo
pagarGasto(id)

// Recibos
generarRecibos()
recalcularRecibos()
setRecibosVista('pendientes'|'pagados')
setFiltroMesRecibos()
buscarConEstructura()      // GET /api/recibos/estructura/avl
cargarTopMorosos()         // GET /api/recibos/morosos/prioridad
exportarMorosidadExcel()   // GET /api/reportes/morosidad/excel → blob → descarga

// Anuncios
cargarAnuncios()
crearAnuncio()
eliminarAnuncio(id)

// Estructuras de datos JS
class PilaFiltros          // historial de filtros aplicados
class IndiceGastos         // Map por mes/tipo para búsqueda O(1)
```

### 3.4 propietario.js — Panel propietario

```javascript
// Información personal
cargarInformacionPersonal()    // GET /api/mi-perfil
activarEdicionContacto(true|false)
guardarContacto()              // PUT /api/propietarios/:id/contacto

// Recibos
cargarRecibosPendientes()
cargarRecibosPagados()
filtrarPagadosPorMes()
pagarRecibo(idRecibo, saldo)   // abre modal de pago
usarMontoTotal()               // rellena el input con el saldo completo
confirmarPago()                // POST /api/recibos/:id/pagar

// Comunicados
cargarComunicados()            // GET /api/comunicados
marcarLeido(id)                // POST /api/comunicados/:id/leer
filtrarComunicados()

// Perfil
// Cambio de contraseña: PUT /api/mi-contrasena
```

### 3.5 Patrón de fetch con manejo de errores

```javascript
// apiFetch agrega token y redirige en 401 automáticamente
const { response, data } = await apiFetch('/recibos', {
    method: 'POST',
    body: JSON.stringify({ fecha: '2026-06-09' })
});

if (!response.ok) {
    showToast(data.error || 'Error al procesar', 'error');
    return;
}
showToast('Recibos generados', 'success');
```

---

## 4. Formularios

### 4.1 Atributos de validación usados

```html
<input type="text"     required maxlength="8">          <!-- DNI -->
<input type="password" required minlength="6">          <!-- Contraseña -->
<input type="number"   required min="0.01" step="0.01"> <!-- Montos -->
<input type="email"    required>                         <!-- Correo -->
<input type="month"    onchange="filtrar()">             <!-- Filtro mes -->
```

### 4.2 Formularios en modal con tabs (Gastos)

Los tres tipos de gasto (mantenimiento, luz, agua) comparten un único modal con tres paneles. Solo uno es visible a la vez:

```javascript
function switchGastoTab(tipo) {
    // quita .active de todos los tabs y paneles
    // activa el tab e ícono del tipo seleccionado
}
```

```html
<div class="gasto-tabs">
    <button class="gasto-tab active" onclick="switchGastoTab('mantenimiento')">🔧 Mantenimiento</button>
    <button class="gasto-tab"        onclick="switchGastoTab('luz')">⚡ Luz</button>
    <button class="gasto-tab"        onclick="switchGastoTab('agua')">💧 Agua</button>
</div>
<div class="gasto-panel active" id="panelMant">...</div>
<div class="gasto-panel"        id="panelLuz">...</div>
<div class="gasto-panel"        id="panelAgua">...</div>
```

---

## 5. Tablas

### 5.1 Estructura estándar

```html
<div class="data-table-container">
    <table class="data-table">
        <thead>
            <tr>
                <th>ID</th>
                <th>Propietario</th>
                ...
            </tr>
        </thead>
        <tbody id="tablaRecibos">
            <tr>
                <td colspan="10" class="empty-state">Sin datos</td>
            </tr>
        </tbody>
    </table>
</div>
```

### 5.2 Tablas del sistema

| ID del tbody | Sección | Columnas |
|---|---|---|
| `tablaPropietarios` | Propietarios | ID, nombre, DNI, depto., torre, teléfono, acciones |
| `tablaGastos` | Gastos | ID, tipo, proveedor, mes, monto, pagado, saldo, estado, acciones |
| `tablaRecibos` | Recibos | ID, propietario, depto., total, pagado, saldo, estado, emisión, pago, acciones |
| `tablaTopMorosos` | Recibos | #, propietario, depto., saldo, días sin pagar |
| `tablaEstructuraRecibos` | Recibos (avanzado) | Recibo, propietario, depto., saldo, emisión, estado |
| `tablaResumenMensual` | Recibos | Mes, total emitido, total pagado, saldo pendiente, recibos |
| `tablaRecibosPendientes` | Propietario | ID, mes/año, admin, agua, luz, mant., total, pagado, saldo, acciones |
| `tablaRecibosPagados` | Propietario | ID, mes/año, total, pagado, saldo, fecha pago, desglose |

---

## 6. Base de Datos (PostgreSQL)

### 6.1 Esquema de tablas

```sql
-- Credenciales y roles
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('Administrador','Propietario'))
);

-- Datos personales vinculados a un usuario
CREATE TABLE propietarios (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    dni VARCHAR(8) UNIQUE NOT NULL,
    nro_departamento VARCHAR(10) NOT NULL,
    torre VARCHAR(10),
    correo VARCHAR(150),
    telefono VARCHAR(20)
);

-- Gastos comunes
CREATE TABLE gastos (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('mantenimiento','luz','agua')),
    proveedor VARCHAR(150),
    monto NUMERIC(10,2) NOT NULL,
    fecha_registro DATE NOT NULL DEFAULT CURRENT_DATE
);

-- Pagos de cada gasto
CREATE TABLE pagos_gastos (
    id SERIAL PRIMARY KEY,
    gasto_id INTEGER REFERENCES gastos(id) ON DELETE CASCADE,
    monto NUMERIC(10,2) NOT NULL CHECK (monto > 0),
    fecha_pago DATE NOT NULL DEFAULT CURRENT_DATE
);

-- Monto de administración mensual
CREATE TABLE configuracion (
    id SERIAL PRIMARY KEY,
    monto_administracion NUMERIC(10,2) NOT NULL DEFAULT 0
);

-- Recibos de cada propietario
CREATE TABLE recibos (
    id SERIAL PRIMARY KEY,
    propietario_id INTEGER REFERENCES propietarios(id) ON DELETE CASCADE,
    monto_administracion NUMERIC(10,2) NOT NULL DEFAULT 0,
    monto_agua NUMERIC(10,2) NOT NULL DEFAULT 0,
    monto_luz NUMERIC(10,2) NOT NULL DEFAULT 0,
    monto_mantenimiento NUMERIC(10,2) NOT NULL DEFAULT 0,
    monto_pagado NUMERIC(10,2) NOT NULL DEFAULT 0,
    pagado BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_emision DATE NOT NULL,
    fecha_pago DATE
);

-- Anuncios / comunicados
CREATE TABLE anuncios (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    contenido TEXT NOT NULL,
    tipo VARCHAR(30) NOT NULL CHECK (tipo IN ('mantenimiento','pago','informativo')),
    fecha_publicacion DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_caducidad DATE,
    activo BOOLEAN DEFAULT TRUE
);

-- Registro de lecturas por propietario
CREATE TABLE lecturas_anuncios (
    id SERIAL PRIMARY KEY,
    anuncio_id INTEGER REFERENCES anuncios(id) ON DELETE CASCADE,
    propietario_id INTEGER REFERENCES propietarios(id) ON DELETE CASCADE,
    fecha_lectura TIMESTAMP DEFAULT NOW(),
    UNIQUE(anuncio_id, propietario_id)
);
```

### 6.2 Campos clave

| Campo | Tabla | Significado |
|---|---|---|
| `monto_pagado` | `recibos` | Suma de pagos recibidos (parciales o total) |
| `pagado` | `recibos` | `TRUE` cuando `monto_pagado >= total_recibo` |
| `monto_administracion` | `configuracion` | Se copia al generar cada recibo |
| `fecha_caducidad` | `anuncios` | Nulo = sin caducidad; si es pasada, no se muestra al propietario |

---

## 7. Estructuras de Datos (Backend)

Todas implementadas en `backend/structures.py`.

### 7.1 Lista enlazada — `ListaPropietarios`

```python
class NodoPropietario:
    def __init__(self, dato): self.dato = dato; self.siguiente = None

class ListaPropietarios:
    def insertar(self, dato)           # agrega al final
    def eliminar_por_id(self, pid)     # recorre y desenlaza
    def to_list(self) -> list          # convierte a lista Python
```

Usada en `propietario_service.list_propietarios()` para encapsular el recorrido.

### 7.2 BST — `ArbolPropietariosBST` y `ArbolRecibosBST`

```python
class NodoBST:
    def __init__(self, clave, dato): ...

class ArbolBST:
    def insertar(self, clave, dato)
    def buscar(self, clave) -> dato | None
    def recorrer(self, modo='inorden') -> list   # inorden/preorden/postorden
    def rango(self, min_clave, max_clave) -> list
```

- `ArbolPropietariosBST`: clave = (apellido, nombre), usado en búsquedas por texto.
- `ArbolRecibosBST`: clave = (saldo, id), usado en consultas `/api/recibos/estructura/bst`.

### 7.3 AVL — `ArbolRecibosAVL`

Extiende `ArbolBST` con rotaciones para mantener balance:

```python
class ArbolRecibosAVL(ArbolBST):
    def _altura(self, nodo)
    def _balance(self, nodo)
    def _rotar_derecha(self, y)
    def _rotar_izquierda(self, x)
    def insertar(self, clave, dato)  # rebalancea tras insertar
```

Usado en `/api/recibos/estructura/avl` — recorrido inorden garantiza orden ascendente de saldo.

### 7.4 Cola de prioridad — `ColaPrioridadMorosos`

```python
class ColaPrioridadMorosos:
    def enqueue(self, item)            # inserta con prioridad (saldo, dias)
    def to_sorted_list(self, limit)    # retorna top N ordenados
```

Criterio de prioridad: mayor saldo pendiente primero; en empate, más días sin pagar. Usado en `/api/recibos/morosos/prioridad` y exportación Excel.

### 7.5 Matriz de recibos — `MatrizRecibos`

```python
class MatrizRecibos:
    # dict of dicts: meses[YYYY-MM][propietario_id] = recibo
    def set_recibo(self, mes, propietario_id, recibo)
    def get_recibo(self, mes, propietario_id)
    def listar_por_propietario(self, propietario_id) -> list
    def total_por_mes(self, mes) -> dict   # emitido, cobrado, saldo
```

Usada en `recibo_service.list_recibos_admin()` para agrupar y resumir por mes.

---

## 8. Seguridad

### 8.1 JWT

```python
# middleware.py
def get_payload() -> (dict, error):
    auth = request.headers.get('Authorization', '')
    token = auth.removeprefix('Bearer ').strip()
    if not token:
        log_sec.warning("Acceso sin token", extra={"event": "missing_token", ...})
        return None, {"error": "Token requerido", "code": 401}
    payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    return payload, None

def require_roles(payload, *roles) -> error | None:
    if payload.get('tipo') not in roles:
        log_sec.warning("Acceso denegado por rol", extra={"event": "forbidden_role", ...})
        return {"error": "Acceso denegado", "code": 403}
    return None
```

### 8.2 Logging de seguridad estructurado

```python
# utils/logger.py — usa python-json-logger
import logging
from pythonjsonlogger import jsonlogger

def get_logger(name):
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    handler.setFormatter(jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    ))
    logger.addHandler(handler)
    return logger
```

Cada evento de seguridad incluye: `event`, `ip`, `path`, `method`, `user`, `rol_actual`, `rol_requerido`.

### 8.3 Sin revelación de información en login

```python
# auth_service.py
# Todos los casos de fallo retornan el mismo mensaje
return {"error": "Usuario o contraseña inválidos"}, 401
# Cada caso se loguea internamente con detalle
```

---

## 9. Responsive Design

### 9.1 Breakpoints

```css
@media (max-width: 992px) {
    /* Tablet: sidebar colapsa, hamburguesa visible */
    .sidebar { position: fixed; transform: translateX(-100%); }
    .sidebar.menu-open { transform: translateX(0); }
    .menu-toggle { display: inline-flex; }
    .panel-content { margin-left: 0; }
}

@media (max-width: 576px) {
    /* Móvil: grids a 1 columna */
    .stats-grid { grid-template-columns: 1fr; }
    .form-row { grid-template-columns: 1fr; }
    .recibos-actions-row { grid-template-columns: 1fr; }
}
```

### 9.2 Menú hamburguesa

```javascript
// auth.js
function toggleSidebarMenu() {
    document.querySelector('.sidebar').classList.toggle('menu-open');
}
// Se cierra automáticamente al seleccionar ítem en móvil
// y al redimensionar la ventana > 992px
```

---

## 10. Animaciones CSS

```css
/* Entrada de secciones */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
.panel-section.active { animation: fadeIn 0.3s ease; }

/* Entrada de modales */
@keyframes fadeInOverlay { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUpModal {
    from { transform: translateY(30px); opacity: 0; }
    to   { transform: translateY(0); opacity: 1; }
}

/* Toasts */
@keyframes toastSlideIn {
    from { transform: translateX(110%); opacity: 0; }
    to   { transform: translateX(0); opacity: 1; }
}
@keyframes toastFadeOut {
    from { opacity: 1; }
    to   { opacity: 0; transform: translateX(30px); }
}
```

---

## 11. Exportación Excel (CU15)

### Backend — `reporte_service.exportar_morosidad_excel()`

```python
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

wb = openpyxl.Workbook()
ws = wb.active
ws.merge_cells("A1:H1")            # título centrado
ws["A1"] = "REPORTE DE MOROSIDAD"
# cabeceras con fill azul + fuente blanca
# filas con fill alternado
# ajuste de ancho con manejo de MergedCell
for col in ws.columns:
    try:
        letter = col[0].column_letter  # MergedCell no tiene este atributo
    except AttributeError:
        continue
    ws.column_dimensions[letter].width = min(max_len + 4, 40)

buf = io.BytesIO()
wb.save(buf)
return buf.read()   # bytes → send_file
```

### Frontend

```javascript
async function exportarMorosidadExcel() {
    const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${getAuthToken()}` }
    });
    if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        showToast(errData.error || `Error ${response.status}`, 'error');
        return;
    }
    const blob = await response.blob();
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `morosidad_${mes || 'todos'}.xlsx`;
    link.click();
    URL.revokeObjectURL(link.href);
}
```

---

## 12. Resumen de Archivos

| Archivo | Descripción |
|---|---|
| `index.html` | Login con selección de rol |
| `admin.html` | Panel administrador completo |
| `propietario.html` | Panel propietario |
| `recuperar.html` | Recuperación de contraseña |
| `css/styles.css` | Todos los estilos del sistema |
| `js/config.js` | API URL, helpers auth, formateo, toast, confirmModal |
| `js/auth.js` | Login, guardias de rol, toggle contraseña, sidebar |
| `js/admin.js` | Lógica completa del panel administrador |
| `js/propietario.js` | Lógica completa del panel propietario |
| `backend/app.py` | Inicialización Flask, blueprints, migraciones |
| `backend/middleware.py` | Validación JWT, roles, logging seguridad |
| `backend/structures.py` | BST, AVL, Cola, Lista, Matriz |
| `backend/dao/*.py` | SQL puro por entidad |
| `backend/services/*.py` | Lógica de negocio por dominio |
| `backend/routes/*.py` | Endpoints HTTP (Blueprints) |
| `backend/utils/logger.py` | Logger JSON estructurado |
| `backend/utils/money.py` | Helpers de precisión monetaria |

---

**Versión:** 5.0  
**Fecha:** Junio 2026
