# Documentación Técnica - Sistema CondominioX

## 0. Arquitectura General (Resumen)

- **Frontend:** HTML, CSS, JavaScript (panel admin y propietario).
- **Backend:** Flask + PostgreSQL (API REST).
- **Hosting:** Frontend en GitHub Pages, backend en Render.

### Variables de entorno (backend)
- `DATABASE_URL`: cadena de conexión a PostgreSQL.
- `JWT_SECRET`: clave para firmar tokens JWT.
- Opcional: `JWT_ISSUER`, `JWT_EXPIRES_SECONDS`.

### Endpoints principales (API)
- `POST /api/login`
- `GET /api/propietarios` | `POST /api/propietarios` | `DELETE /api/propietarios/:id`
- `GET /api/gastos` | `POST /api/gastos` | `DELETE /api/gastos/:id`
- `POST /api/recibos/generar`
- `POST /api/recibos/recalcular`
- `GET /api/recibos?estado=pendientes|pagados&mes=YYYY-MM`
- `GET /api/recibos/propietario/:id`
- `POST /api/recibos/:id/pagar` (pagos parciales)
- `DELETE /api/recibos/:id`
- `GET /api/configuracion` | `PUT /api/configuracion`

---

## 1. HTML: Estructura Básica y Elementos

### Checklist de Requisitos (Dónde se ve en el proyecto)

- **Estructura básica HTML + meta tags:** `index.html`, `admin.html`, `propietario.html`, `recuperar.html` (etiquetas `<html>`, `<head>`, `<meta charset>`, `<meta viewport>`).
- **Etiquetas de texto:** `index.html` y `admin.html` (`<h1>`, `<h2>`, `<p>`, `<span>`, `<small>`).
- **Enlaces:** `index.html` (link a `recuperar.html`).
- **Encabezado/menú/cuerpo:** `admin.html` y `propietario.html` (`<aside class="sidebar">`, `<main class="panel-content">`).
- **Formularios:** `index.html` (login), `admin.html` (propietarios/gastos/config), `propietario.html` (cambiar contraseña).
- **Tablas:** `admin.html` (propietarios/gastos/recibos/resumen), `propietario.html` (recibos).
- **Multimedia (imágenes):** `img/logo.png` usado en `index.html`, `admin.html`, `propietario.html`.

### 1.1 Estructura del Documento HTML

```html
<!DOCTYPE html>           <!-- Declaración del tipo de documento HTML5 -->
<html lang="es">          <!-- Elemento raíz con idioma español -->
<head>                    <!-- Cabecera con metadatos -->
    ...
</head>
<body>                    <!-- Cuerpo del documento -->
    ...
</body>
</html>
```

### 1.2 Meta Tags Básicos

Los meta tags proporcionan información sobre el documento:

```html
<meta charset="UTF-8">
```
- **charset="UTF-8"**: Define la codificación de caracteres. UTF-8 soporta caracteres especiales como ñ, tildes y símbolos.

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```
- **viewport**: Controla cómo se muestra la página en dispositivos móviles.
- **width=device-width**: El ancho se ajusta al dispositivo.
- **initial-scale=1.0**: Escala inicial del zoom (100%).

```html
<meta name="description" content="CondominioX - Sistema de Gestión...">
```
- **description**: Descripción del sitio para motores de búsqueda (SEO).

### 1.3 Etiquetas de Texto

| Etiqueta | Uso en el Proyecto | Descripción |
|----------|-------------------|-------------|
| `<h1>` | `<h1>CONDOMINIOX</h1>` | Título principal (solo 1 por página) |
| `<h2>` | `<h2>Dashboard</h2>` | Títulos de secciones |
| `<h3>` | `<h3>Nuevo Propietario</h3>` | Subtítulos de formularios |
| `<h4>` | `<h4>Seguridad</h4>` | Títulos menores |
| `<p>` | `<p>Resumen general</p>` | Párrafos de texto |
| `<span>` | `<span class="stat-value">0</span>` | Texto en línea |
| `<small>` | `<small>Mínimo 6 caracteres</small>` | Texto pequeño/ayuda |
| `<strong>` | `<strong>${formatCurrency(total)}</strong>` | Texto en negrita |

### 1.4 Enlaces

```html
<a href="recuperar.html">¿Olvidó su contraseña?</a>
```
- **href**: Dirección de destino del enlace.
- Enlace relativo (mismo directorio).

```html
<link rel="stylesheet" href="css/styles.css">
```
- Enlaza la hoja de estilos CSS externa.

### 1.5 Saltos de Línea y Estructura

El proyecto usa contenedores semánticos en lugar de `<br>`:

```html
<div class="form-group">      <!-- Agrupa elementos de formulario -->
    <label>...</label>
    <input>...</input>
</div>

<section id="dashboard-section">  <!-- Sección semántica -->
    ...
</section>

<aside class="sidebar">       <!-- Barra lateral -->
    ...
</aside>

<main class="panel-content">  <!-- Contenido principal -->
    ...
</main>

<nav class="sidebar-nav">     <!-- Navegación -->
    ...
</nav>
```

---

## 2. CSS: Sintaxis, Selectores y Atributos

### 2.1 Variables CSS (Custom Properties)

Las variables permiten reutilizar valores en todo el CSS:

```css
:root {
    --primary-dark: #1e3a3a;      /* Verde oscuro */
    --primary: #2d4a4a;            /* Verde principal */
    --accent-gold: #c9a227;        /* Dorado */
    --white: #ffffff;              /* Blanco */
    --off-white: #f8f9fa;          /* Gris claro */
    --shadow: 0 4px 20px rgba(0, 0, 0, 0.1);  /* Sombra */
    --radius: 12px;                /* Radio de bordes */
    --transition: all 0.3s ease;   /* Transición suave */
}
```

### Checklist de CSS

- **Selectores y valores:** `css/styles.css` (clases, IDs, pseudo-clases).
- **Tipografía / colores / íconos:** `css/styles.css` + `img/logo.png`.
- **Transiciones:** botones y navegación (`.btn:hover`, `.nav-item:hover`).
- **Animaciones (keyframes):** `css/styles.css` (`@keyframes floatLogo`, `fadeUp`, `slideIn`).
- **Flexbox:** `.sidebar`, `.action-buttons`, `.nav-item`.
- **Grid:** `.stats-grid`, `.form-row`.
- **Responsive:** `@media (max-width: 992px)` y `@media (max-width: 576px)` en `css/styles.css`.

---

## 3. Base de Datos (PostgreSQL)

### Tablas principales
- `usuarios`: credenciales y roles (Administrador/Propietario).
- `propietarios`: datos personales y vínculo `usuario_id`.
- `gastos`: mantenimiento, luz y agua (con fecha manual).
- `recibos`: montos por tipo, `monto_pagado`, estado y fechas.
- `configuracion`: monto de administración configurable.

### Campos relevantes
- `recibos.monto_pagado`: permite pagos parciales.
- `recibos.pagado`: se actualiza cuando `monto_pagado >= total`.
- `configuracion.monto_administracion`: valor editable desde el panel admin.

---

## 4. Estructuras de Datos (Backend)

### Lista enlazada de propietarios (`ListaPropietarios`)
- Implementación en `backend/structures.py`.
- Se usa en `GET /api/propietarios` para recorrer e insertar propietarios.
- Operaciones: insertar, eliminar por id, recorrer, to_list.

### Matriz de recibos por mes (`MatrizRecibos`)
- Implementación en `backend/structures.py`.
- Representación: `meses[YYYY-MM][propietario_id] = recibo`.
- Se usa en:
  - `GET /api/recibos` (admin) para organizar y resumir por mes.
  - `GET /api/recibos/propietario/:id` para listar por propietario.
- Operaciones: set_recibo, get_recibo, total_por_mes, listar_por_propietario.


**Uso de variables:**
```css
.sidebar {
    background: var(--primary-dark);  /* Usa la variable */
}
```

### 2.2 Tipos de Selectores

| Tipo | Ejemplo | Descripción |
|------|---------|-------------|
| **Universal** | `*` | Selecciona todos los elementos |
| **Elemento** | `body`, `h1`, `table` | Selecciona por etiqueta |
| **Clase** | `.sidebar`, `.btn-primary` | Selecciona por clase (.) |
| **ID** | `#loginForm`, `#userName` | Selecciona por ID (#) |
| **Descendiente** | `.sidebar-nav .nav-item` | Elemento dentro de otro |
| **Pseudo-clase** | `.btn:hover`, `input:focus` | Estado del elemento |
| **Atributo** | `[data-tab="inicio"]` | Por atributo |

### 2.3 Reset CSS

Elimina estilos predeterminados del navegador:

```css
* {
    margin: 0;           /* Sin márgenes */
    padding: 0;          /* Sin relleno */
    box-sizing: border-box;  /* El padding se incluye en el ancho */
}
```

### 2.4 Propiedades CSS Principales

#### Layout con Flexbox:
```css
.app-container {
    display: flex;           /* Activa Flexbox */
    min-height: 100vh;       /* Mínimo altura de pantalla */
}

.sidebar {
    display: flex;
    flex-direction: column;  /* Elementos en columna */
    gap: 8px;               /* Espacio entre elementos */
}

.nav-item {
    display: flex;
    align-items: center;     /* Centra verticalmente */
    justify-content: center; /* Centra horizontalmente */
}
```

#### Layout con Grid:
```css
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 20px;
}

.form-row {
    display: grid;
    grid-template-columns: repeat(2, 1fr);  /* 2 columnas iguales */
    gap: 20px;
}
```

#### Estilos de Caja:
```css
.stat-card {
    background: var(--white);
    border-radius: var(--radius);    /* Bordes redondeados */
    padding: 25px;                    /* Relleno interno */
    box-shadow: var(--shadow);        /* Sombra */
}
```

#### Gradientes:
```css
.sidebar {
    background: linear-gradient(180deg, var(--primary-dark) 0%, var(--primary) 100%);
}

.btn-primary {
    background: linear-gradient(135deg, var(--accent-gold), var(--accent-gold-dark));
}
```

#### Transiciones:
```css
.nav-item {
    transition: var(--transition);  /* all 0.3s ease */
}

.nav-item:hover {
    background: rgba(255, 255, 255, 0.1);
    transform: translateY(-2px);
}
```

---

## 3. Estructura del Layout

### 3.1 Encabezado con Menú (Sidebar)

```html
<aside class="sidebar">
    <!-- Header del sidebar -->
    <div class="sidebar-header">
        <img src="img/logo.png" alt="Logo" class="logo-img">
        <h1>CONDOMINIOX</h1>
        <p class="tagline">Gestión Inteligente</p>
    </div>

    <!-- Navegación/Menú -->
    <nav class="sidebar-nav">
        <button class="nav-item active" onclick="showTab('inicio')">
            <span class="nav-icon">🏠</span>
            <span>Inicio</span>
        </button>
        <!-- Más botones... -->
    </nav>

    <!-- Footer del sidebar -->
    <div class="sidebar-footer">
        <p>&copy; 2025 CondominioX</p>
    </div>
</aside>
```

**CSS del Sidebar:**
```css
.sidebar {
    width: 280px;
    background: linear-gradient(180deg, var(--primary-dark), var(--primary));
    padding: 30px 20px;
    display: flex;
    flex-direction: column;
    position: fixed;
    height: 100vh;
    left: 0;
    top: 0;
}
```

### 3.2 Cuerpo (Contenido Principal)

```html
<main class="main-content">
    <div class="tab-content active">
        <div class="content-header">
            <h2>Bienvenido</h2>
            <p>Seleccione su tipo de acceso</p>
        </div>
        <!-- Contenido... -->
    </div>
</main>
```

**CSS:**
```css
.main-content {
    flex: 1;
    margin-left: 280px;    /* Espacio para el sidebar */
    padding: 40px;
    background: var(--off-white);
    min-height: 100vh;
}
```

### 3.3 Pie de Página

```html
<div class="sidebar-footer">
    <p>&copy; 2025 CondominioX</p>
</div>
```

---

## 4. Formularios

### 4.1 Estructura Básica del Formulario

```html
<form id="loginForm" class="form-login">
    <!-- Campo oculto -->
    <input type="hidden" id="tipoUsuario" name="tipoUsuario" value="">

    <!-- Grupo de campo -->
    <div class="form-group">
        <label for="usuario">Usuario</label>
        <div class="input-wrapper">
            <span class="input-icon">👤</span>
            <input
                type="text"
                id="usuario"
                name="usuario"
                placeholder="Ingrese su usuario"
                required
                autocomplete="username"
            >
        </div>
    </div>

    <!-- Mensaje de error/éxito -->
    <div id="mensaje" class="mensaje"></div>

    <!-- Botón de envío -->
    <button type="submit" class="btn btn-primary">
        <span>Iniciar Sesión</span>
        <span class="btn-arrow">→</span>
    </button>
</form>
```

### 4.2 Tipos de Elementos de Formulario

| Elemento | Código | Uso |
|----------|--------|-----|
| **Text** | `<input type="text">` | Nombre, usuario, DNI |
| **Password** | `<input type="password">` | Contraseñas |
| **Email** | `<input type="email">` | Correo electrónico |
| **Tel** | `<input type="tel">` | Teléfono |
| **Number** | `<input type="number" step="0.01">` | Montos |
| **Date** | `<input type="date">` | Fechas |
| **Month** | `<input type="month">` | Mes y año |
| **Select** | `<select><option>...</option></select>` | Listas desplegables |
| **Textarea** | `<textarea rows="3">` | Texto largo |
| **Hidden** | `<input type="hidden">` | Datos ocultos |

### 4.3 Atributos de Validación

```html
<input type="text" id="propDNI" required maxlength="8">
<input type="password" id="propContrasena" required minlength="6">
<input type="number" id="gastoMonto" step="0.01" min="0" required>
```

| Atributo | Descripción |
|----------|-------------|
| `required` | Campo obligatorio |
| `maxlength="8"` | Máximo 8 caracteres |
| `minlength="6"` | Mínimo 6 caracteres |
| `min="0"` | Valor mínimo |
| `step="0.01"` | Incremento decimal |
| `placeholder` | Texto de ayuda |

### 4.4 CSS de Formularios

```css
/* Grupo de campos */
.form-group {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

/* Etiquetas */
.form-group label {
    font-weight: 600;
    color: var(--text-dark);
}

/* Inputs */
.form-group input,
.form-group select,
.form-group textarea {
    width: 100%;
    padding: 12px 15px;
    border: 2px solid var(--light-gray);
    border-radius: var(--radius);
    font-size: 1rem;
    transition: var(--transition);
}

/* Focus (cuando está seleccionado) */
.form-group input:focus {
    outline: none;
    border-color: var(--accent-gold);
    box-shadow: 0 0 0 4px rgba(201, 162, 39, 0.15);
}

/* Filas de 2 columnas */
.form-row {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
}
```

---

## 5. Multimedia: Imágenes

### 5.1 Etiqueta de Imagen

```html
<img src="img/logo.png" alt="CondominioX Logo" class="logo-img">
```

| Atributo | Descripción |
|----------|-------------|
| `src` | Ruta de la imagen |
| `alt` | Texto alternativo (accesibilidad y SEO) |
| `class` | Clase CSS para estilos |

### 5.2 CSS de Imágenes

```css
.sidebar-header .logo-img {
    width: 120px;
    height: 120px;
    object-fit: contain;    /* Mantiene proporción */
    margin-bottom: 15px;
    filter: drop-shadow(0 5px 15px rgba(0, 0, 0, 0.3));
}

.about-logo img {
    width: 150px;
    height: 150px;
    object-fit: contain;
}
```

---

## 6. Tablas

### 6.1 Estructura de Tabla

```html
<div class="data-table-container">
    <table class="data-table">
        <!-- Encabezado -->
        <thead>
            <tr>
                <th>ID</th>
                <th>Nombre Completo</th>
                <th>DNI</th>
                <th>Depto.</th>
                <th>Torre</th>
                <th>Teléfono</th>
                <th>Acciones</th>
            </tr>
        </thead>
        <!-- Cuerpo -->
        <tbody id="tablaPropietarios">
            <tr>
                <td colspan="7" class="empty-state">No hay propietarios</td>
            </tr>
        </tbody>
    </table>
</div>
```

### 6.2 Elementos de Tabla

| Elemento | Descripción |
|----------|-------------|
| `<table>` | Contenedor de la tabla |
| `<thead>` | Encabezado de la tabla |
| `<tbody>` | Cuerpo de la tabla |
| `<tr>` | Fila (table row) |
| `<th>` | Celda de encabezado |
| `<td>` | Celda de datos |
| `colspan="7"` | Celda que ocupa 7 columnas |

### 6.3 CSS de Tablas

```css
/* Contenedor */
.data-table-container {
    background: var(--white);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow);
    overflow: hidden;
}

/* Tabla */
.data-table {
    width: 100%;
    border-collapse: collapse;   /* Sin espacio entre celdas */
}

/* Celdas */
.data-table th,
.data-table td {
    padding: 15px;
    text-align: left;
    border-bottom: 1px solid var(--light-gray);
}

/* Encabezados */
.data-table th {
    background: var(--primary);
    color: var(--white);
    font-weight: 600;
}

/* Hover en filas */
.data-table tbody tr:hover {
    background: var(--off-white);
}

/* Estado vacío */
.data-table .empty-state {
    text-align: center;
    color: var(--text-muted);
    padding: 40px;
}
```

---

## 7. JavaScript: Funciones Principales

### 7.1 config.js - Configuración

```javascript
// Constantes para localStorage
const AUTH_TOKEN_KEY = 'auth_token';
const USER_DATA_KEY = 'user_data';

// Funciones de autenticación
function getAuthToken() {
    return localStorage.getItem(AUTH_TOKEN_KEY);
}

function setAuthToken(token) {
    localStorage.setItem(AUTH_TOKEN_KEY, token);
}

function removeAuthToken() {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(USER_DATA_KEY);
}

// Funciones de formato
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-PE', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatCurrency(amount) {
    return `S/ ${parseFloat(amount).toFixed(2)}`;
}
```

### 7.2 auth.js - Autenticación

```javascript
// Usuarios de demo
const USUARIOS_DEMO = {
    'admin': { id: 1, usuario: 'admin', contrasena: '123456', tipo: 'Administrador' },
    'propietario': { id: 2, usuario: 'propietario', contrasena: '123456', tipo: 'Propietario' }
};

// Manejo del formulario de login
document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();  // Evita recargar la página

    // Obtener valores
    const usuario = document.getElementById('usuario').value;
    const contrasena = document.getElementById('contrasena').value;

    // Validar credenciales
    const userDemo = USUARIOS_DEMO[usuario];
    if (userDemo && userDemo.contrasena === contrasena) {
        // Login exitoso
        setAuthToken('demo_token_' + Date.now());
        setUserData({ id: userDemo.id, usuario: userDemo.usuario, tipo: userDemo.tipo });

        // Redirigir según tipo
        if (userDemo.tipo === 'Administrador') {
            window.location.href = 'admin.html';
        } else {
            window.location.href = 'propietario.html';
        }
    }
});

// Cerrar sesión
function cerrarSesion() {
    if (confirm('¿Está seguro que desea cerrar sesión?')) {
        removeAuthToken();
        window.location.href = 'index.html';
    }
}
```

### 7.3 admin.js - Panel Administrador

```javascript
// Datos de ejemplo
let propietarios = [
    { id: 1, nombre: 'Juan Carlos', apellido: 'Pérez García', dni: '12345678', ... }
];

// Cargar dashboard
function cargarDashboard() {
    document.getElementById('totalPropietarios').textContent = propietarios.length;
    // ...
}

// Listar propietarios en tabla
function listarPropietarios() {
    const tbody = document.getElementById('tablaPropietarios');
    tbody.innerHTML = '';

    propietarios.forEach(prop => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${prop.id}</td>
            <td>${prop.nombre} ${prop.apellido}</td>
            <td>${prop.dni}</td>
            ...
        `;
        tbody.appendChild(tr);
    });
}

// Manejar formulario
document.getElementById('formPropietario').addEventListener('submit', function(e) {
    e.preventDefault();

    // Crear nuevo propietario
    const nuevoPropietario = {
        id: obtenerSiguienteId(propietarios),
        nombre: document.getElementById('propNombre').value.trim(),
        // ...
    };

    // Agregar a la lista
    propietarios.push(nuevoPropietario);
    listarPropietarios();
    cargarDashboard();
});

// Inicialización
window.addEventListener('DOMContentLoaded', function() {
    cargarDashboard();
    listarPropietarios();
    listarGastos();
});
```

---

## 8. Responsive Design

### 8.1 Media Queries

```css
/* Tablet (< 992px) */
@media (max-width: 992px) {
    .sidebar {
        width: 100%;
        height: auto;
        position: relative;
    }

    .main-content {
        margin-left: 0;
    }

    .app-container {
        flex-direction: column;
    }
}

/* Móvil (< 576px) */
@media (max-width: 576px) {
    .stats-grid {
        grid-template-columns: 1fr;
    }

    .form-row {
        grid-template-columns: 1fr;
    }

    .action-buttons {
        flex-direction: column;
    }
}
```

---

## 9. Listas HTML

### 9.1 Listas No Ordenadas

Usadas para mostrar funcionalidades en las tarjetas de información:

```html
<ul class="feature-list">
    <li><span class="check">✓</span> Gestión de Propietarios</li>
    <li><span class="check">✓</span> Generar Recibos</li>
    <li><span class="check">✓</span> Registrar Gastos</li>
    <li><span class="check">✓</span> Reportes y Estadísticas</li>
</ul>
```

| Elemento | Descripción |
|----------|-------------|
| `<ul>` | Lista no ordenada (unordered list) |
| `<li>` | Elemento de lista (list item) |

### 9.2 CSS de Listas

```css
.feature-list {
    list-style: none;    /* Quita los puntos por defecto */
    padding: 25px;
}

.feature-list li {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 0;
    border-bottom: 1px solid var(--light-gray);
}

.feature-list .check {
    color: #16a34a;      /* Verde para el check */
    font-weight: bold;
}
```

---

## 10. Botones

### 10.1 Tipos de Botones

```html
<!-- Botón de envío de formulario -->
<button type="submit" class="btn btn-primary">Guardar</button>

<!-- Botón normal -->
<button type="button" class="btn btn-secondary" onclick="cerrarFormulario()">Cancelar</button>

<!-- Botón de navegación -->
<button class="nav-item active" onclick="mostrarSeccion('dashboard')">
    <span class="nav-icon">📊</span>
    <span>Dashboard</span>
</button>

<!-- Botón de acción -->
<button class="btn btn-danger btn-sm" onclick="eliminarPropietario(1)">Eliminar</button>
```

### 10.2 CSS de Botones

```css
/* Botón base */
.btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    padding: 18px 30px;
    border: none;
    border-radius: var(--radius);
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: var(--transition);
}

/* Botón primario (dorado) */
.btn-primary {
    background: linear-gradient(135deg, var(--accent-gold), var(--accent-gold-dark));
    color: var(--white);
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(201, 162, 39, 0.35);
}

/* Botón secundario (gris) */
.btn-secondary {
    background: var(--light-gray);
    color: var(--text-dark);
}

/* Botón de éxito (verde) */
.btn-success {
    background: linear-gradient(135deg, #22c55e, #16a34a);
    color: var(--white);
}

/* Botón de peligro (rojo) */
.btn-danger {
    background: linear-gradient(135deg, #ef4444, #dc2626);
    color: var(--white);
}

/* Botón pequeño */
.btn-sm {
    padding: 0.4rem 0.8rem;
    font-size: 0.85rem;
}
```

---

## 11. Animaciones CSS

### 11.1 Keyframes

```css
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Uso de la animación */
.tab-content.active {
    animation: fadeIn 0.3s ease;
}

.panel-section.active {
    animation: fadeIn 0.3s ease;
}
```

### 11.2 Transiciones

```css
/* Transición suave en hover */
.user-type-btn {
    transition: var(--transition);  /* all 0.3s ease */
}

.user-type-btn:hover {
    border-color: var(--accent-gold);
    transform: translateY(-3px);
    box-shadow: var(--shadow-lg);
}

/* Flecha animada en botón */
.btn-arrow {
    transition: transform 0.3s ease;
}

.btn-primary:hover .btn-arrow {
    transform: translateX(5px);
}
```

---

## 12. Etiqueta Script

### 12.1 Scripts Externos

```html
<!-- Al final del body, antes de cerrar -->
<script src="js/config.js"></script>
<script src="js/auth.js"></script>
<script src="js/admin.js"></script>
```

- Se colocan al final del `<body>` para que el HTML cargue primero
- El orden importa: config.js primero porque define funciones usadas por los demás

### 12.2 Scripts Internos

```html
<script>
    // Función para cambiar de pestaña
    function showTab(tabName) {
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });
        document.getElementById('tab-' + tabName).classList.add('active');
    }
</script>
```

---

## 13. Eventos JavaScript

### 13.1 Eventos en HTML (onclick)

```html
<button onclick="mostrarSeccion('dashboard', this)">Dashboard</button>
<button onclick="eliminarPropietario(${prop.id})">Eliminar</button>
<button onclick="cerrarSesion()">Cerrar Sesión</button>
```

### 13.2 Eventos con addEventListener

```javascript
// Evento submit del formulario
document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();  // Evita que la página se recargue
    // Lógica del login...
});

// Evento DOMContentLoaded (cuando el HTML está listo)
window.addEventListener('DOMContentLoaded', function() {
    cargarDashboard();
    listarPropietarios();
});

// Evento click en navegación
document.querySelectorAll('.nav-item').forEach(btn => {
    btn.addEventListener('click', function() {
        // Lógica de navegación...
    });
});
```

---

## 14. Manipulación del DOM

### 14.1 Selección de Elementos

```javascript
// Por ID
document.getElementById('tablaPropietarios')

// Por clase (devuelve NodeList)
document.querySelectorAll('.nav-item')

// Por selector CSS
document.querySelector('.nav-item[data-tab="inicio"]')
```

### 14.2 Modificación de Contenido

```javascript
// Cambiar texto
document.getElementById('totalPropietarios').textContent = propietarios.length;

// Cambiar HTML interno
tbody.innerHTML = '<tr><td>...</td></tr>';

// Crear elementos
const tr = document.createElement('tr');
tr.innerHTML = `<td>${prop.nombre}</td>`;
tbody.appendChild(tr);
```

### 14.3 Manipulación de Clases

```javascript
// Agregar clase
elemento.classList.add('active');

// Quitar clase
elemento.classList.remove('active');

// Alternar clase
elemento.classList.toggle('hidden');

// Verificar si tiene clase
if (elemento.classList.contains('active')) { ... }
```

---

## Resumen de Archivos

| Archivo | Descripción |
|---------|-------------|
| `index.html` | Página de login con selección de usuario |
| `admin.html` | Panel del administrador |
| `propietario.html` | Panel del propietario |
| `recuperar.html` | Recuperación de contraseña |
| `css/styles.css` | Todos los estilos del sistema |
| `js/config.js` | Configuración y funciones auxiliares |
| `js/auth.js` | Autenticación y funciones UI |
| `js/admin.js` | Lógica del panel administrador |
| `js/propietario.js` | Lógica del panel propietario |
| `img/logo.png` | Logo del sistema |
