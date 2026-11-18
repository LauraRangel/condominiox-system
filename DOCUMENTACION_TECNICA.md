# Documentación Técnica — Sistema CondominioX

**Versión:** 5.1 — Noviembre 2026

## 0. Arquitectura general

### Stack tecnológico

| Capa | Tecnología |
|---|---|
| Frontend | HTML5 + CSS3 + JavaScript vanilla (sin frameworks ni build) |
| Backend | Python 3 + Flask 3.1 (API REST) + Gunicorn |
| Base de datos | PostgreSQL (servidor 18 en Render; 16 en CI) |
| Autenticación | JWT HS256 (PyJWT 2.15.1), Bearer token |
| LLM del asistente | Groq (`openai/gpt-oss-120b`), intercambiable con Gemini |
| Hosting frontend | GitHub Pages |
| Hosting backend | Render Web Service |

### Patrón arquitectónico: MVC + DAO

```
Routes (Controller) → Services (lógica de negocio) → DAO (acceso a datos) → PostgreSQL
                              ↕
          structures.py (Lista, BST, AVL, Cola, Matriz) · rag.py (TF-IDF)
          pasarelas.py (Culqi / Yape / Mercado Pago) · llm_client.py (Groq / Gemini)
```

- **Routes** (`backend/routes/`): reciben la request HTTP, validan el JWT y el rol, y delegan al servicio.
- **Services** (`backend/services/`): lógica de negocio pura, sin Flask ni SQL. Las reglas críticas son funciones puras testeables sin base de datos:
  - `validar_reglas()` y `validar_area()` en `reserva_service`;
  - `extraer_fecha()`, `extraer_hora()` y `describir_disponibilidad()` en `asistente_service`.
- **DAO** (`backend/dao/`): SQL puro, un archivo por entidad.
- **Structures** (`backend/structures.py`): estructuras de datos académicas usadas por los servicios.

### Variables de entorno (backend)

```
DATABASE_URL=postgresql://user:pass@host/db
JWT_SECRET=clave_larga_y_aleatoria_de_32+_caracteres
JWT_EXPIRES_SECONDS=3600        # opcional, default 1 h
JWT_ISSUER=condominiox          # opcional
CORS_ORIGINS=https://laurarangel.github.io   # opcional, separado por comas
SLOW_QUERY_MS=200               # opcional
LLM_PROVIDER=groq               # groq | gemini | none
GROQ_API_KEY=gsk_...            # sin key: modo respaldo
LLM_MODEL=openai/gpt-oss-120b   # opcional
LLM_TIMEOUT=12                  # opcional
DIAS_DEUDA_VENCIDA=30           # opcional
```

---

## 1. HTML: estructura y elementos

### Checklist de requisitos

| Requisito | Dónde se aplica |
|---|---|
| Estructura básica + meta tags | `index.html`, `admin.html`, `propietario.html`, `recuperar.html` |
| Etiquetas de texto (`h1`–`h3`, `p`, `span`, `small`) | Todos los archivos HTML |
| Enlace a página externa | `index.html` → `recuperar.html`; Google Fonts (Inter) |
| Encabezado, menú y cuerpo semánticos | `<aside>`, `<nav>`, `<main>`, `<section>` en admin y propietario |
| Menú hamburguesa responsive | `.menu-toggle` + `toggleSidebarMenu()` en `auth.js` |
| Formularios con validación | Login, propietarios, gastos, contraseña, reserva, invitados, pago, documentos, áreas |
| Tablas | 15 tablas (ver 5.2) |
| Multimedia | `img/logo.png`, imágenes de áreas comunes (`js/areas-img.js`), visor PDF embebido |
| Accesibilidad (`aria-*`, `role`, `label for`) | Modales, inputs, botones de contraseña, chat del asistente |
| Seguridad | Meta `Content-Security-Policy` en los 4 HTML |

### 1.1 Estructura del documento

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="...">
    <title>Panel Propietario - CondominioX</title>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap">
    <link rel="stylesheet" href="css/styles.css?v=20260716">
    <link rel="stylesheet" href="css/innovacion.css?v=20261116">
    <link rel="stylesheet" href="css/moderno.css?v=20261116">
</head>
<body>
    <div class="app-container">
        <aside class="sidebar">...</aside>
        <main class="panel-content">...</main>
    </div>
    <!-- Modales al final del body -->
    <div id="confirmModal" class="modal-overlay hidden">...</div>
    <div id="toast-container"></div>
    <script src="js/config.js?v=20261116"></script>
    <script src="js/auth.js?v=20260716"></script>
    <script src="js/propietario.js?v=20261116"></script>
    <script src="js/pasarela.js?v=20261116"></script>
    <script src="js/areas-img.js?v=20261116"></script>
    <script src="js/invitados.js?v=20261116"></script>
    <script src="js/documentos.js?v=20261116"></script>
    <script src="js/reservas.js?v=20261116"></script>
    <script src="js/asistente.js?v=20261117"></script>
    <script src="js/ui-moderno.js?v=20261116"></script>
</body>
</html>
```

**Versionado:** el sufijo `?v=AAAAMMDD` obliga al navegador a descargar la versión nueva tras un deploy. Al cambiar un archivo CSS o JS, hay que subir su sufijo en todos los HTML que lo cargan.

### 1.2 Secciones de cada panel

| Panel | Secciones (`data-section`) |
|---|---|
| `admin.html` | `dashboard`, `propietarios`, `gastos`, `recibos`, `enlinea` (Pagos y Reservas), `anuncios`, `documentos`, `perfil` |
| `propietario.html` | `informacion`, `pendientes`, `pagados`, `reservas`, `asistente`, `comunicados`, `documentos`, `perfil` |
| `index.html` | Pestañas `inicio`, `informacion`, `acerca` + login en dos pasos |

### 1.3 Layout de dos columnas

```
┌─────────────────────────────────────────────────┐
│  <aside class="sidebar">    │  <main>            │
│  Logo + nav + usuario       │  Secciones         │
│  (280px fijo)               │  (flex: 1)         │
└─────────────────────────────────────────────────┘
```

```css
.app-container { display: flex; min-height: 100vh; }
.sidebar       { width: 280px; flex-shrink: 0; }
.panel-content { flex: 1; overflow-y: auto; }
```

### 1.4 Tipos de inputs usados

| Tipo | Ejemplo de uso |
|---|---|
| `text` | Nombre, usuario, DNI, proveedor, invitados |
| `password` | Contraseñas (con botón ver/ocultar), `minlength="8"` |
| `email` | Correo electrónico, correo de Mercado Pago |
| `tel` | Teléfono, celular de Yape |
| `number` | Montos (`min`/`step`), aforo, tarifa, garantía, personas |
| `date` | Fecha de emisión de recibo, filtros de transacciones |
| `time` | Hora de apertura y cierre de áreas comunes |
| `month` | Filtro por mes (AAAA-MM) |
| `search` | Buscador del reglamento y filtros |
| `file` | PDF (`accept="application/pdf,.pdf"`) e invitados (`accept=".csv,.txt"`) |
| `checkbox` | Documento público, área activa, uso exclusivo |
| `select` | Tipo de usuario, gasto, anuncio, categoría de documento |
| `textarea` | Contenido de anuncio, pregunta al asistente, motivo de retención |
| `hidden` | Tipo de usuario en el login |

### 1.5 Modales: estructura estándar

```html
<div id="miModal" class="modal-overlay hidden" role="dialog" aria-modal="true" aria-labelledby="miModalTitulo">
    <div class="modal-card" onclick="event.stopPropagation()">
        <div class="modal-header">
            <h3><span class="modal-icon success">✅</span><span id="miModalTitulo">Título</span></h3>
            <button type="button" class="btn-close" onclick="cerrarModal()" aria-label="Cerrar">×</button>
        </div>
        <div class="modal-body"><!-- Contenido --></div>
        <div class="modal-footer">
            <button class="btn btn-secondary" onclick="cerrarModal()">Cancelar</button>
            <button class="btn btn-primary" onclick="confirmar()">Confirmar</button>
        </div>
    </div>
</div>
```

- `modal-overlay`: fondo semitransparente; un clic fuera cierra el modal.
- `event.stopPropagation()` en `modal-card` evita que el clic llegue al overlay.
- `role="dialog"`, `aria-modal` y `aria-labelledby` dan accesibilidad.
- Modales del sistema:
  - confirmación;
  - comprobante (CU16);
  - pago (pasarela, en pasos);
  - reserva (calendario + invitados);
  - invitados;
  - visor PDF;
  - garantía;
  - área común;
  - gasto (con pestañas);
  - estado de cuenta.

---

## 2. CSS: estilos y diseño

Tres hojas, en este orden de carga:

| Archivo | Rol |
|---|---|
| `css/styles.css` | Base: variables, layout, botones, tablas, modales, toasts, responsive |
| `css/innovacion.css` | Componentes APF3: checkout, calendario de reservas, chat, documentos, transacciones |
| `css/moderno.css` | Capa visual: superficies translúcidas (*glass*), sombras suaves, radios, tipografía Inter |

### 2.1 Variables CSS

```css
/* styles.css */
:root {
    --primary-dark: #1e3a3a;
    --primary: #2d4a4a;
    --primary-light: #3d5a5a;
    --accent-gold: #c9a227;
    --accent-gold-light: #d4b84a;
    --accent-gold-dark: #a88a1f;
    --white: #ffffff;
    --off-white: #f8f9fa;
    --light-gray: #e9ecef;
    --text-dark: #1a1a2e;
    --text-muted: #6c757d;
    --shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 40px rgba(0, 0, 0, 0.15);
    --radius: 12px;
    --radius-lg: 20px;
    --transition: all 0.3s ease;
}

/* moderno.css */
:root {
    --bg: #eef3f2;
    --surface: rgba(255, 255, 255, 0.78);
    --ink: #17302f;
    --ink-soft: #5c706e;
    --r-lg: 22px; --r-md: 14px; --r-sm: 10px;
    --glass: rgba(255, 255, 255, 0.42);
    --glass-blur: blur(22px) saturate(165%);
}
```

### 2.2 Checklist CSS

| Requisito | Dónde |
|---|---|
| Variables CSS | `:root` en `styles.css` y `moderno.css` |
| Selectores de clase, ID y pseudo-clase | `.btn:hover`, `#loginForm`, `tr:nth-child(even)` |
| Tipografía y colores | Inter (Google Fonts) + variables |
| Flexbox | Sidebar, nav, cards, barras de filtros, chat |
| Grid | Stats, formularios, calendario de horarios, tarjetas de áreas |
| Transiciones | Botones, modales, sidebar, slots del calendario |
| Animaciones (`@keyframes`) | `fadeInOverlay`, `slideUpModal`, `toastIn`, `girar`, `rebote` (ver sección 10) |
| Efectos modernos | `backdrop-filter` (glass), sombras en capas |
| Responsive | `@media (max-width: 992px / 760px / 700px / 640px / 576px)` |
| Accesibilidad | `@media (prefers-reduced-motion: reduce)` desactiva animaciones |

### 2.3 Sistema de botones

```css
.btn           /* base: padding, border-radius, cursor */
.btn-primary   /* dorado: acción principal */
.btn-secondary /* gris: secundaria / cancelar */
.btn-success   /* verde: acción positiva */
.btn-danger    /* rojo: eliminar / destructiva */
.btn-sm        /* tamaño reducido para tablas y barras */
```

### 2.4 Notificaciones toast

Reemplazan todos los `alert()`:

```javascript
showToast('Mensaje', 'success' | 'error' | 'warning' | 'info', 'Título opcional');
```

```css
.toast         /* contenedor base, fixed abajo a la derecha */
.toast-success /* verde */   .toast-error   /* rojo */
.toast-warning /* amarillo */ .toast-info   /* azul */
```

Desaparece a los 4 segundos con animación de salida.

### 2.5 Animaciones de modales

```css
@keyframes fadeInOverlay { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUpModal {
    from { transform: translateY(30px); opacity: 0; }
    to   { transform: translateY(0);    opacity: 1; }
}
.modal-overlay { animation: fadeInOverlay .2s ease; }
.modal-card    { animation: slideUpModal .25s ease; }
```

### 2.6 Cards financieras (dashboard)

```css
.financiero-card /* base */
.fc-blue  /* total emitido */   .fc-green /* total cobrado */
.fc-red   /* saldo pendiente */ .fc-amber /* % cobranza */
```

### 2.7 Modal con pestañas (gastos)

```css
.gasto-tabs / .gasto-tab / .gasto-tab.active
.gasto-panel / .gasto-panel.active
```

---

## 3. JavaScript: organización y funciones

| Archivo | Carga en | Responsabilidad |
|---|---|---|
| `config.js` | Todos | API, auth, formato, toast, modales compartidos |
| `auth.js` | Todos | Login, guardias de rol, contraseñas, menú |
| `admin.js` | admin | Panel administrador |
| `admin-enlinea.js` | admin | Pagos y Reservas: transacciones, reservas, garantías, áreas |
| `propietario.js` | propietario | Panel propietario |
| `pasarela.js` | propietario | Checkout emulado y tokenización |
| `reservas.js` | propietario | Calendario, reserva, invitados, garantía |
| `asistente.js` | propietario | Chat del asistente IA |
| `invitados.js` | admin, propietario | Ver e imprimir invitados |
| `documentos.js` | admin, propietario | Reglamento, visor y carga de PDF |
| `areas-img.js` | admin, propietario | Imagen de cada área común |
| `ui-moderno.js` | Todos | Ajustes visuales comunes |

### 3.1 config.js: funciones compartidas

```javascript
// URL del backend: localhost en desarrollo, Render en GitHub Pages
const API_URL = ['localhost', '127.0.0.1'].includes(window.location.hostname)
    ? 'http://localhost:5000/api'
    : 'https://condominiox-system.onrender.com/api';

// Fachada sobre fetch: agrega Bearer token y Content-Type, redirige al login en 401
async function apiFetch(path, options = {})   // → { response, data }

// Seguridad
function escapeHtml(valor)       // escapa & < > " ' ` antes de usar innerHTML

// localStorage
function getAuthToken() / setAuthToken(token) / removeAuthToken()
function getUserData() / setUserData(data)
function isAuthenticated() / requireAuth()

// Formato
function formatDate(dateString)       // DD/MM/AAAA
function formatMonthYear(dateString)  // "noviembre 2026"
function formatCurrency(amount)       // "S/ 120.00"

// UI compartida (admin + propietario)
function showToast(message, type, title)
function confirmModal(message, title, tipo)   // Promise<boolean>
function cerrarConfirmModal(accepted)
async function verComprobante(reciboId)       // CU16
function cerrarComprobante() / imprimirComprobante()
```

### 3.2 auth.js: autenticación y UI común

```javascript
// Login: POST /api/login → guarda token y userData → redirige por rol
document.getElementById('loginForm').addEventListener('submit', ...)

// Guardia de rol al cargar admin.html / propietario.html
if (window.location.pathname.includes('admin.html')) {
    requireAuth();
    const userData = getUserData();
    if (!userData || userData.tipo !== 'Administrador') {
        removeAuthToken();
        window.location.replace('index.html');
    }
}

async function cerrarSesion()            // confirma con confirmModal
function mostrarSeccion(id, boton)
function inicializarToggleContrasenas()  // botones ver/ocultar contraseña
function toggleSidebarMenu()
```

### 3.3 admin.js: panel administrador

```javascript
// Dashboard
cargarDashboard() / cargarResumenFinanciero()       // GET /api/reportes/financiero

// Propietarios
cargarPropietarios() / buscarPropietariosBackend()  // GET /api/propietarios/busqueda
editarPropietario(id) / eliminarPropietario(id)
verEstadoCuenta(id) / filtrarEstadoCuenta()         // GET /api/propietarios/:id/estado-cuenta

// Gastos
abrirModalGasto(tipo) / switchGastoTab(tipo) / submitGasto(event, tipo) / pagarGasto(id)

// Recibos
generarRecibos() / recalcularRecibos() / cargarRecibos()
buscarConEstructura()          // GET /api/recibos/estructura/{bst|avl}
guardarFiltroEstructura() / deshacerFiltroEstructura()   // PilaFiltros
cargarTopMorosos()             // GET /api/recibos/morosos/prioridad
exportarMorosidadExcel()       // GET /api/reportes/morosidad/excel → blob

// Anuncios
cargarAnuncios() / crearAnuncio() / eliminarAnuncio(id)

// Estructuras de datos JS
class PilaFiltros    // push / pop / peek / isEmpty
class IndiceGastos   // Map por `${mes}-${tipo}`, acceso O(1)
```

### 3.4 admin-enlinea.js: Pagos y Reservas

```javascript
cargarPanelEnLinea()                 // GET /api/pagos + GET /api/reservas
aplicarFiltrosEnLinea() / limpiarFiltrosEnLinea() / filtroRapido()
// filtros: desde, hasta, área, persona, depto, concepto, estado de pago, estado de reserva
abrirModalGarantia(id) / actualizarDevolucion() / resolverGarantia()
                                     // POST /api/reservas/:id/garantia/resolucion
cancelarReservaAdmin(id)             // DELETE /api/reservas/:id
cargarAreasAdmin() / abrirModalArea(id) / guardarArea()   // PUT /api/areas-comunes/:id
```

### 3.5 propietario.js: panel propietario

```javascript
getPropietarioId()                     // del userData en localStorage
cargarInformacionPersonal()            // GET /api/mi-perfil
activarEdicionContacto(true|false)
guardarContacto()                      // PUT /api/mi-perfil
cargarEstadisticas()
cargarRecibosPendientes() / cargarRecibosPagados()
filtrarPagadosPorMes() / renderTablaRecibosPagados()
cargarComunicados() / filtrarComunicados() / marcarLeido(id)   // POST /api/comunicados/:id/leer
cargarDatosSeccion(id)
// Aviso de cambio de contraseña mientras debe_cambiar_contrasena = true
```

### 3.6 pasarela.js: pago en línea (CU17)

```javascript
pagarRecibo(idRecibo, saldo) / pagarGarantia(reservaId, monto)   // abren el checkout
usarMontoTotal() / elegirMedio(medio) / cerrarModalPago()
confirmarPago()   // POST /api/pagos con header Idempotency-Key (crypto.randomUUID)
```

La tarjeta se tokeniza en el navegador (`tkn_test_<marca>_<last4>_<azar>`). Al backend solo llegan el token, la marca y los 4 últimos dígitos.

### 3.7 reservas.js: reservas (CU18)

```javascript
cargarReservas() / seleccionarArea(id) / abrirReserva(id)
elegirDia(fecha)               // GET /api/areas-comunes/:id/disponibilidad?fecha=
tocarSlot(hora)                // selección de bloque horario en el calendario
cambiarPersonas(delta)
agregarInvitado() / editarInvitado() / quitarInvitado() / importarInvitados()  // CSV
crearReserva()                 // POST /api/reservas
cargarMisReservas() / cancelarReserva(id) / pagarGarantiaDeReserva(id)
```

### 3.8 asistente.js: asistente IA (CU19)

```javascript
iniciarAsistente()
preguntaSugerida(texto)        // chips de ejemplo
enviarPregunta()               // POST /api/asistente/consulta
// _formatearRespuesta: escapa el texto y convierte [F1] en chips de fuente
// _ICONO_FUENTE: reglamento, documento, recibo, pago, reserva, gasto, área, disponibilidad 🗓️
```

### 3.9 documentos.js

```javascript
cargarDocumentos() / cargarReglamento() / filtrarReglamento() / irArticulo(id)
verPdf(id) / descargarPdf(id)  // GET /api/documentos/:id/archivo → blob → visor embebido
subirDocumento()               // POST /api/documentos (FormData)
alternarPublico(id) / eliminarDocumento(id)
abrirFuente(fuente)            // abre la fuente citada por el asistente
```

### 3.10 Patrón de fetch con manejo de errores

```javascript
const { response, data } = await apiFetch('/recibos/generar', {
    method: 'POST',
    body: JSON.stringify({ fecha: '2026-11-01' })
});
if (!response.ok) {
    showToast(data.error || 'Error al procesar', 'error');
    return;
}
showToast('Recibos generados', 'success');
```

Todo texto que viene de la API se inserta con `escapeHtml()` cuando se usa `innerHTML`.

---

## 4. Formularios

### 4.1 Atributos de validación

```html
<input type="text"     required maxlength="8">                  <!-- DNI -->
<input type="password" required minlength="8">                  <!-- Contraseña -->
<input type="number"   required min="0.01" step="0.01">         <!-- Montos -->
<input type="email"    required>                                <!-- Correo -->
<input type="month"    onchange="filtrar()">                    <!-- Filtro mes -->
<input type="file"     accept="application/pdf,.pdf">           <!-- Documento -->
```

La validación del navegador es solo una ayuda: el backend vuelve a validar todo (`utils/validacion.py`, `json_body()`, servicios).

### 4.2 Formularios en modal con pestañas (gastos)

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

### 4.3 Formulario de pago en pasos

1. Monto: parcial o "Pagar total".
2. Medio: tarjeta, Yape o Mercado Pago.
3. Datos del medio.
4. Procesando.
5. Resultado (aprobado o rechazado, con código de operación).

---

## 5. Tablas

### 5.1 Estructura estándar

```html
<div class="data-table-container">
    <table class="data-table">
        <thead><tr><th>ID</th><th>Propietario</th>...</tr></thead>
        <tbody id="tablaRecibos">
            <tr><td colspan="10" class="empty-state">Sin datos</td></tr>
        </tbody>
    </table>
</div>
```

### 5.2 Tablas del sistema

| ID del tbody | Panel / sección |
|---|---|
| `tablaPropietarios` | Admin: propietarios |
| `tablaEstadoCuenta` | Admin: estado de cuenta (modal) |
| `tablaGastos` | Admin: gastos |
| `tablaRecibos` | Admin: recibos |
| `tablaTopMorosos` | Admin: ranking de morosos |
| `tablaEstructuraRecibos` | Admin: búsqueda BST/AVL |
| `tablaResumenMensual` | Admin: resumen por mes |
| `tablaDesgloseConceptos` | Admin: dashboard financiero |
| `tablaTransacciones` | Admin: Pagos y Reservas |
| `tablaReservasAdmin` | Admin: Pagos y Reservas |
| `tablaAreasAdmin` | Admin: configuración de áreas |
| `tablaAnuncios` | Admin: anuncios |
| `tablaRecibosPendientes` | Propietario: pendientes |
| `tablaRecibosPagados` | Propietario: historial |
| `tablaMisReservas` | Propietario: reservas |

---

## 6. Base de datos (PostgreSQL)

### 6.1 Esquema de tablas

Fuente: `backend/schema.sql`. Las tablas APF3 también las crea `migrations.py` al arrancar.

```sql
-- ===== Base =====
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('Administrador', 'Propietario')),
    activo BOOLEAN DEFAULT TRUE,
    creado_en TIMESTAMP DEFAULT NOW()
);

CREATE TABLE propietarios (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER UNIQUE REFERENCES usuarios(id) ON DELETE SET NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    dni VARCHAR(8) UNIQUE NOT NULL,
    correo VARCHAR(120),
    telefono VARCHAR(20),
    nro_departamento VARCHAR(10) NOT NULL,
    torre VARCHAR(5) NOT NULL
);

CREATE TABLE gastos (
    id SERIAL PRIMARY KEY,
    proveedor VARCHAR(120) NOT NULL,
    concepto TEXT NOT NULL,
    monto NUMERIC(10,2) NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('mantenimiento', 'luz', 'agua')),
    fecha_registro DATE NOT NULL
);

CREATE TABLE pagos_gastos (
    id SERIAL PRIMARY KEY,
    gasto_id INTEGER NOT NULL REFERENCES gastos(id) ON DELETE CASCADE,
    monto NUMERIC(10,2) NOT NULL CHECK (monto > 0),
    fecha_pago DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE configuracion (
    id SERIAL PRIMARY KEY,
    monto_administracion NUMERIC(10,2) NOT NULL
);

CREATE TABLE recibos (
    id SERIAL PRIMARY KEY,
    propietario_id INTEGER NOT NULL REFERENCES propietarios(id) ON DELETE CASCADE,
    monto_administracion NUMERIC(10,2) NOT NULL,
    monto_agua NUMERIC(10,2) NOT NULL,
    monto_luz NUMERIC(10,2) NOT NULL,
    monto_mantenimiento NUMERIC(10,2) NOT NULL,
    monto_reservas NUMERIC(10,2) NOT NULL DEFAULT 0,     -- APF3
    monto_pagado NUMERIC(10,2) NOT NULL DEFAULT 0,
    fecha_emision DATE NOT NULL,
    fecha_pago DATE,
    pagado BOOLEAN DEFAULT FALSE
);

CREATE TABLE anuncios (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    contenido TEXT NOT NULL,
    tipo VARCHAR(30) NOT NULL CHECK (tipo IN ('mantenimiento','pago','informativo')),
    fecha_publicacion DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_caducidad DATE,                                -- migración en app.py
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE lecturas_anuncios (
    id SERIAL PRIMARY KEY,
    anuncio_id INTEGER NOT NULL REFERENCES anuncios(id) ON DELETE CASCADE,
    propietario_id INTEGER NOT NULL REFERENCES propietarios(id) ON DELETE CASCADE,
    fecha_lectura TIMESTAMP DEFAULT NOW(),
    UNIQUE(anuncio_id, propietario_id)
);

-- ===== APF3 =====
CREATE TABLE areas_comunes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL UNIQUE,
    descripcion TEXT,
    aforo INTEGER NOT NULL CHECK (aforo > 0),
    tarifa NUMERIC(10,2) NOT NULL DEFAULT 0 CHECK (tarifa >= 0),
    garantia NUMERIC(10,2) NOT NULL DEFAULT 0 CHECK (garantia >= 0),
    uso_exclusivo BOOLEAN NOT NULL DEFAULT TRUE,
    hora_apertura TIME NOT NULL,
    hora_cierre TIME NOT NULL,
    anticipacion_min_horas INTEGER NOT NULL DEFAULT 24,
    duracion_max_horas INTEGER NOT NULL DEFAULT 4,
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE reservas (
    id SERIAL PRIMARY KEY,
    area_id INTEGER NOT NULL REFERENCES areas_comunes(id) ON DELETE CASCADE,
    propietario_id INTEGER NOT NULL REFERENCES propietarios(id) ON DELETE CASCADE,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    asistentes INTEGER NOT NULL CHECK (asistentes > 0),
    cargo NUMERIC(10,2) NOT NULL DEFAULT 0,
    estado VARCHAR(20) NOT NULL DEFAULT 'confirmada'
        CHECK (estado IN ('pendiente_garantia', 'confirmada', 'cancelada', 'expirada')),
    garantia NUMERIC(10,2) NOT NULL DEFAULT 0,
    garantia_estado VARCHAR(20) NOT NULL DEFAULT 'no_aplica'
        CHECK (garantia_estado IN ('no_aplica', 'pendiente', 'pagada', 'devuelta',
                                   'devuelta_parcial', 'retenida', 'no_pagada')),
    garantia_retenida NUMERIC(10,2) NOT NULL DEFAULT 0,
    garantia_motivo VARCHAR(300),
    garantia_resuelta_en TIMESTAMPTZ,
    recibo_id INTEGER REFERENCES recibos(id) ON DELETE SET NULL,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (hora_fin > hora_inicio)
);
CREATE INDEX idx_reservas_area_fecha ON reservas(area_id, fecha);

CREATE TABLE reserva_invitados (
    id SERIAL PRIMARY KEY,
    reserva_id INTEGER NOT NULL REFERENCES reservas(id) ON DELETE CASCADE,
    nombres VARCHAR(60) NOT NULL,
    apellidos VARCHAR(60) NOT NULL,
    tipo_documento VARCHAR(3) NOT NULL CHECK (tipo_documento IN ('DNI', 'CE')),
    numero_documento VARCHAR(12) NOT NULL,
    UNIQUE (reserva_id, tipo_documento, numero_documento)
);

CREATE TABLE transacciones_pago (
    id SERIAL PRIMARY KEY,
    recibo_id INTEGER REFERENCES recibos(id) ON DELETE SET NULL,
    reserva_id INTEGER REFERENCES reservas(id) ON DELETE SET NULL,
    propietario_id INTEGER REFERENCES propietarios(id) ON DELETE SET NULL,
    concepto VARCHAR(20) NOT NULL DEFAULT 'recibo'
        CHECK (concepto IN ('recibo', 'garantia', 'devolucion')),
    transaccion_origen_id INTEGER REFERENCES transacciones_pago(id),
    proveedor VARCHAR(20) NOT NULL CHECK (proveedor IN ('yape', 'culqi', 'mercadopago')),
    monto NUMERIC(10,2) NOT NULL CHECK (monto > 0),
    moneda VARCHAR(3) NOT NULL DEFAULT 'PEN',
    estado VARCHAR(20) NOT NULL CHECK (estado IN ('aprobado', 'rechazado')),
    codigo_operacion VARCHAR(40) NOT NULL UNIQUE,
    idempotency_key VARCHAR(80) UNIQUE,
    medio_detalle VARCHAR(60),
    mensaje VARCHAR(200),
    respuesta_pasarela JSONB,
    modo VARCHAR(12) NOT NULL DEFAULT 'sandbox',
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE documentos (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    categoria VARCHAR(20) NOT NULL
        CHECK (categoria IN ('reglamento', 'acta', 'manual', 'presupuesto', 'otro')),
    descripcion VARCHAR(300),
    nombre_archivo VARCHAR(200) NOT NULL,
    tamano_bytes INTEGER NOT NULL,
    paginas INTEGER NOT NULL,
    contenido BYTEA NOT NULL,
    publico BOOLEAN NOT NULL DEFAULT TRUE,
    tiene_texto BOOLEAN NOT NULL DEFAULT TRUE,
    subido_por VARCHAR(50),
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE documento_fragmentos (
    id SERIAL PRIMARY KEY,
    documento_id INTEGER NOT NULL REFERENCES documentos(id) ON DELETE CASCADE,
    pagina INTEGER NOT NULL,
    texto TEXT NOT NULL
);
CREATE INDEX idx_fragmentos_documento ON documento_fragmentos(documento_id);

CREATE TABLE consultas_asistente (
    id SERIAL PRIMARY KEY,
    propietario_id INTEGER REFERENCES propietarios(id) ON DELETE CASCADE,
    pregunta TEXT NOT NULL,
    respuesta TEXT NOT NULL,
    fuentes JSONB,
    modo VARCHAR(12) NOT NULL,          -- ia | respaldo | privacidad
    proveedor VARCHAR(30),
    latencia_ms INTEGER,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 6.2 Campos clave

| Campo | Tabla | Significado |
|---|---|---|
| `password_hash` | `usuarios` | Hash de la contraseña (`security.hash_password`), nunca texto plano |
| `monto_pagado` | `recibos` | Suma de pagos recibidos (parciales o total) |
| `pagado` | `recibos` | `TRUE` cuando `monto_pagado >= total` |
| `monto_reservas` | `recibos` | Suma de tarifas de reservas confirmadas del mes |
| `monto_administracion` | `configuracion` | Se copia al generar cada recibo |
| `fecha_caducidad` | `anuncios` | Nulo = sin caducidad; si ya pasó, el propietario no lo ve |
| `uso_exclusivo` | `areas_comunes` | `TRUE`: no admite cruces; `FALSE`: admite cruces hasta el aforo |
| `estado` / `garantia_estado` | `reservas` | Ciclo de vida de la reserva y de su garantía |
| `idempotency_key` | `transacciones_pago` | `UNIQUE`: un reintento no genera un segundo cobro |
| `transaccion_origen_id` | `transacciones_pago` | Enlaza una devolución con el cobro original |
| `contenido` | `documentos` | El PDF en `BYTEA` (máx. 5 MB) |

### 6.3 Concurrencia

Pagos y reservas se ejecutan en una sola transacción con `SELECT ... FOR UPDATE`:

- el pago bloquea el recibo o la reserva;
- la reserva bloquea el área.

Así, dos pagos simultáneos no aplican el mismo saldo dos veces y dos reservas simultáneas no ocupan el mismo horario.

---

## 7. Estructuras de datos (backend)

Todas están en `backend/structures.py`, implementadas desde cero.

### 7.1 Lista enlazada: `ListaPropietarios`

```python
class NodoPropietario: ...            # data, next
class ListaPropietarios:
    def insertar(self, data)          # al final, O(1) con puntero a la cola
    def eliminar_por_id(self, id_)    # recorre y desenlaza, O(n)
    def recorrer(self, callback)
    def to_list(self) -> list
```

Usada en `propietario_service.listar_propietarios()`.

### 7.2 BST: `ArbolPropietariosBST` y `ArbolRecibosBST`

```python
class ArbolPropietariosBST:
    def insertar(self, key, data)     # key = DNI como entero
    def buscar(self, key)             # O(log n) promedio
    def inorden(self) -> list

class ArbolRecibosBST:
    def insertar(self, key, value)    # key = (saldo, id)
    def recorrer(self, tipo="inorden")   # inorden / preorden / postorden
    def rango(self, min_key, max_key)    # O(log n + k)
```

- `propietario_service.buscar_propietarios()`: con un DNI de 8 dígitos usa `buscar()`; con otro texto, `inorden()` y un filtro lineal.
- `recibo_service.buscar_recibos_bst()`: `GET /api/recibos/estructura/bst`.

### 7.3 AVL: `ArbolRecibosAVL`

```python
class NodoAVL: ...                    # key, value, left, right, height
class ArbolRecibosAVL:
    def _height(self, node) / _balance(self, node)
    def _rotate_right(self, y) / _rotate_left(self, x)
    def insertar(self, key, value)    # rebalancea al insertar: O(log n) garantizado
    def recorrer(self, tipo="inorden")
    def rango(self, min_key, max_key)
```

Es una clase independiente con la **misma interfaz** que `ArbolRecibosBST`, de modo que `recibo_service` los usa indistintamente según el parámetro `estructura` (patrón Estrategia). Se usa en `GET /api/recibos/estructura/avl`: el recorrido inorden devuelve los recibos ordenados por saldo.

### 7.4 Cola de prioridad: `ColaPrioridadMorosos`

```python
class ColaPrioridadMorosos:           # max-heap sobre lista
    def enqueue(self, item)           # O(log n), heapify_up
    def dequeue(self)                 # O(log n), heapify_down
    def to_sorted_list(self, limit=None)   # O(n log n)
```

Prioridad: `(saldo, dias_pendiente)` descendente. Usada en `GET /api/recibos/morosos/prioridad` y en el Excel de morosidad.

### 7.5 Matriz dispersa: `MatrizRecibos`

```python
class MatrizRecibos:                  # dict[mes][propietario_id] = recibo
    def set_recibo(self, mes, propietario_id, recibo)   # O(1)
    def get_recibo(self, mes, propietario_id)           # O(1)
    def total_por_mes(self, mes)
    def total_por_propietario(self, propietario_id)
    def listar_por_propietario(self, propietario_id, filtro_fn=None)
```

Usada en `recibo_service.listar_recibos_admin()` y `listar_recibos_propietario()`.

### 7.6 Índice TF-IDF: `services/rag.py`

Recuperación de información para el asistente, sin librerías externas:

1. **Normalización:** minúsculas, sin tildes y sin signos.
2. **Tokenización:** quita stopwords en español y aplica un stemmer simple por sufijos.
3. **Sinónimos:** expande la pregunta (p. ej., `gym` → `gimnasio`).
4. **TF-IDF:** un vector por artículo del reglamento y por fragmento de PDF público.
5. **Similitud coseno** entre la pregunta y cada vector, y se devuelven los *k* mejores.

El índice se reconstruye solo cuando cambia algún documento.

---

## 8. Seguridad

### 8.1 JWT

```python
# auth_service.generar_token()
now = dt.datetime.now(dt.timezone.utc)      # nunca utcnow(): ver nota
payload = {"sub": str(user["id"]), "usuario": ..., "tipo": ...,
           "iss": config.jwt_issuer(),
           "iat": int(now.timestamp()),
           "exp": int((now + timedelta(seconds=config.jwt_exp_seconds())).timestamp())}
# + "propietario_id" si es propietario

# middleware.get_payload()
payload = pyjwt.decode(token, config.jwt_secret(), algorithms=["HS256"], issuer=config.jwt_issuer())
# ExpiredSignatureError → 401 "Token expirado" · InvalidTokenError → 401 "Token inválido"

# middleware.require_roles(payload, "Administrador") → 403 si el rol no coincide
```

> `datetime.utcnow()` crea un datetime sin zona; `.timestamp()` lo interpreta en la hora local del servidor y corre `iat` y `exp`. Los tests de integración detectaron el error y se corrigió con `datetime.now(timezone.utc)`.

### 8.2 Logging de seguridad estructurado

```python
# utils/logger.py: python-json-logger (>= 3: pythonjsonlogger.json)
def get_logger(name):
    logger = logging.getLogger(name)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(jsonlogger.JsonFormatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
    ...
```

- **Eventos:**
  - `missing_token`;
  - `expired_token`;
  - `invalid_token`;
  - `forbidden_role`;
  - `rate_limited`;
  - `health_db_down`.
- **Campos:** `event`, `request_id`, `ip`, `path`, `method`, `user`, `rol_actual`, `rol_requerido`.
- **Access log:** `app.py` escribe una línea JSON por request con `X-Request-Id`.
- **Consultas lentas:** `db.py` registra las que superan `SLOW_QUERY_MS`.

### 8.3 Sin revelación de información

- **Login:** cualquier fallo responde `"Usuario o contraseña inválidos"`; el detalle solo va al log.
- **Recuperación:** responde el mismo mensaje exista o no el usuario.
- **Errores no controlados:** un handler global responde 500 genérico con `request_id`.

### 8.4 Fuerza bruta y contraseñas

```python
# routes/auth_routes.py
limitador_login     = LimitadorIntentos(maximo=5, ventana_seg=15 * 60)
limitador_recuperar = LimitadorIntentos(maximo=5, ventana_seg=60 * 60)
# clave = IP + usuario · al bloquear: 429 + Retry-After + log rate_limited
```

`validar_contrasena()` exige:

- 8 o más caracteres;
- letras y números;
- que no sea el DNI;
- que no repita la actual.

### 8.5 CORS y cabeceras HTTP

```python
CORS(app, resources={r"/api/*": {"origins": CORS_ORIGINS,
     "allow_headers": ["Content-Type", "Authorization", "Idempotency-Key"]}})

X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: no-referrer
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'none'; frame-ancestors 'none'
Permissions-Policy: camera=(), microphone=(), geolocation=()
Cache-Control: no-store   (respuestas de la API)
```

> Si el preflight `OPTIONS` falla, por un 404 o porque Render responde 502/503 sin cabeceras CORS durante un deploy o un *cold start*, el navegador lo muestra como "error de CORS". Antes de tocar `CORS_ORIGINS`, conviene revisar que el backend esté *Live*.

### 8.6 Entrada de datos

- `json_body()` en `middleware.py` normaliza el cuerpo: una lista donde se espera texto o `NaN` en un monto responde 400, nunca 500.
- `utils/validacion.py` valida nombre, apellido, usuario, torre, departamento, teléfono, correo e invitados.
- PDF: se valida la extensión, la firma `%PDF-` y el tamaño; los PDF cifrados se rechazan.

### 8.7 Asistente IA

- El contexto se arma solo con el `propietario_id` del JWT.
- No se envían DNI, correo, teléfono ni invitados.
- `pregunta_sobre_otro()` bloquea preguntas sobre otros vecinos (modo `privacidad`).
- El system prompt ordena ignorar instrucciones incrustadas en la pregunta o en los documentos.
- Límite de 8 consultas por minuto y preguntas de hasta 500 caracteres.

---

## 9. Responsive design

### 9.1 Breakpoints

```css
@media (max-width: 992px) {          /* Tablet: sidebar colapsa, hamburguesa visible */
    .sidebar { position: fixed; transform: translateX(-100%); }
    .sidebar.menu-open { transform: translateX(0); }
    .menu-toggle { display: inline-flex; }
}
@media (max-width: 760px) / (max-width: 700px) / (max-width: 640px) {
    /* calendario de reservas, checkout y chat en una columna */
}
@media (max-width: 576px) {          /* Móvil: grids a 1 columna */
    .stats-grid, .form-row, .recibos-actions-row { grid-template-columns: 1fr; }
}
@media (prefers-reduced-motion: reduce) { /* sin animaciones */ }
```

### 9.2 Menú hamburguesa

```javascript
function toggleSidebarMenu() {
    document.querySelector('.sidebar').classList.toggle('menu-open');
}
// Se cierra al elegir una sección en móvil y al ensanchar la ventana a más de 992px
```

---

## 10. Animaciones CSS

| Keyframe | Archivo | Uso |
|---|---|---|
| `fadeIn` | `styles.css` | Entrada de secciones (`.panel-section.active`) |
| `fadeUp` / `slideIn` | `styles.css` | Entrada de tarjetas y elementos de lista |
| `floatLogo` | `styles.css` | Logo flotante del login |
| `fadeInOverlay` / `slideUpModal` | `styles.css` | Apertura de modales |
| `toastIn` | `styles.css` | Entrada de toasts |
| `girar` | `innovacion.css` | Spinner de "procesando pago" |
| `rebote` | `innovacion.css` | Puntos de "escribiendo..." del asistente |
| `derivaFondo` | `moderno.css` | Fondo animado (se desactiva con `prefers-reduced-motion`) |
| `desplegar` | `moderno.css` | Menús y paneles desplegables |

```css
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes toastIn {
    from { opacity: 0; transform: translateX(30px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes rebote {
    0%, 80%, 100% { opacity: 0.3; transform: translateY(0); }
    40%           { opacity: 1;   transform: translateY(-4px); }
}
```

---

## 11. Exportación Excel (CU15)

### Backend: `reporte_service.exportar_morosidad_excel()`

```python
wb = openpyxl.Workbook()
ws = wb.active
ws.merge_cells("A1:H1")
ws["A1"] = "REPORTE DE MOROSIDAD"
# cabeceras con fondo azul y fuente blanca; filas con color alternado
for col in ws.columns:
    try:
        letter = col[0].column_letter   # MergedCell no tiene este atributo
    except AttributeError:
        continue
    ws.column_dimensions[letter].width = min(max_len + 4, 40)

buf = io.BytesIO()                       # en memoria, nunca en disco
wb.save(buf)
buf.seek(0)
return buf.read()
```

Los datos salen de `ColaPrioridadMorosos`, así que el Excel queda ordenado por prioridad.

### Frontend

```javascript
async function exportarMorosidadExcel() {
    const response = await fetch(url, { headers: { 'Authorization': `Bearer ${getAuthToken()}` } });
    if (!response.ok) { /* toast con el error */ return; }
    const blob = await response.blob();
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `morosidad_${mes || 'todos'}.xlsx`;
    link.click();
    URL.revokeObjectURL(link.href);
}
```

---

## 12. Componentes APF3: detalle técnico

### 12.1 Pasarela emulada

```
Navegador (pasarela.js)                     Backend
  tokeniza la tarjeta ─────────────┐
  POST /api/pagos                  │
  Idempotency-Key: <uuid>          ▼
                          pago_service.procesar_pago()
                            ├─ ¿idempotency_key ya existe? → devuelve la transacción previa
                            ├─ SELECT recibo/reserva FOR UPDATE
                            ├─ valida monto ≤ saldo (o = garantía)
                            ├─ obtener_pasarela(proveedor).cobrar()  ← Culqi | Yape | MP
                            ├─ si aprobado: actualiza recibo + FIFO a gastos
                            │               o confirma reserva + suma tarifa al recibo
                            ├─ INSERT transacciones_pago
                            └─ COMMIT (todo o nada)
```

### 12.2 Disponibilidad en el asistente

```
"¿Está libre la parrilla el 20 de noviembre a las 2pm?"
  extraer_fecha()  → 2026-11-20      (si la fecha ya pasó este año, usa el siguiente)
  extraer_hora()   → 14:00           (ignora duraciones como "3 horas")
  áreas mencionadas → Zona de parrillas
  reserva_service.disponibilidad(area_id, fecha) → bloques ocupados
  describir_disponibilidad() → "Zona de parrillas, viernes 20 de noviembre de 2026:
       reservas de 13:00 a 16:00. A las 14:00 está OCUPADA."
  → fuente [Fn] tipo "disponibilidad" en el CONTEXTO del LLM
```

---

## 13. Resumen de archivos

| Archivo | Descripción |
|---|---|
| `index.html` | Login en dos pasos y páginas informativas |
| `admin.html` | Panel administrador |
| `propietario.html` | Panel propietario |
| `recuperar.html` | Recuperación de contraseña |
| `css/styles.css` · `innovacion.css` · `moderno.css` | Estilos base, APF3 y capa visual |
| `js/config.js` | API, auth, escapeHtml, formato, toast, confirmModal, comprobante |
| `js/auth.js` | Login, guardias de rol, contraseñas, sidebar |
| `js/admin.js` · `admin-enlinea.js` | Panel admin y Pagos y Reservas |
| `js/propietario.js` | Panel propietario |
| `js/pasarela.js` · `reservas.js` · `invitados.js` | Pagos, reservas e invitados |
| `js/asistente.js` · `documentos.js` | Asistente IA y documentos |
| `backend/app.py` | Flask, CORS, cabeceras, access log, blueprints, migraciones base |
| `backend/migrations.py` | Migraciones APF3 y siembra de áreas |
| `backend/middleware.py` | JWT, roles, `json_body`, logging de seguridad |
| `backend/structures.py` | Lista, BST, AVL, Cola de prioridad, Matriz |
| `backend/dao/*.py` | SQL puro por entidad (10 archivos) |
| `backend/services/*.py` | Lógica de negocio (14 archivos) |
| `backend/routes/*.py` | Endpoints HTTP (12 blueprints) |
| `backend/utils/` | `logger`, `money`, `validacion`, `pdf_simple` |
| `backend/data/reglamento.json` | Reglamento indexado por el asistente |
| `backend/seed_demo.py` | Datos de demostración (no usar en producción) |
| `backend/tests/` | 225 tests (147 unitarias + 78 integración) |

---

**Versión:** 5.1 — Noviembre 2026
