# CondominioX - Sistema de Gestión de Condominio

**Universidad Tecnológica del Perú**

**Estudiante:** Laura Isabel Rangel Teran

---

Sistema web para la gestión de condominios desarrollado con HTML, CSS y JavaScript.

## Estructura del Proyecto

```
sistema-condominio/
├── index.html              # Página de login
├── admin.html              # Panel administrador
├── propietario.html        # Panel propietario
├── recuperar.html          # Recuperar contraseña
├── css/
│   └── styles.css          # Estilos globales
├── js/
│   ├── config.js           # Configuración y helpers
│   ├── auth.js             # Autenticación y navegación
│   ├── admin.js            # Funciones panel admin
│   └── propietario.js      # Funciones panel propietario
├── img/
│   └── logo.png            # Logo del sistema
└── README.md
```

## Diseño

El sistema cuenta con:

- **Sidebar lateral** con navegación y logo
- **Sistema de pestañas** (Inicio, Información, Acerca de)
- **Login en dos pasos**: selección de rol + credenciales
- **Paneles de administración** con estadísticas en cards
- **Tablas de datos** estilizadas
- **Formularios** para agregar registros
- **Diseño responsive**

### Paleta de Colores

```css
--primary-dark: #1e3a3a     /* Verde oscuro */
--primary: #2d4a4a          /* Verde principal */
--accent-gold: #c9a227      /* Dorado */
--white: #ffffff            /* Blanco */
--off-white: #f8f9fa        /* Gris claro */
```

## Inicio Rápido

### Credenciales de prueba

| Rol | Usuario | Contraseña |
|-----|---------|------------|
| Administrador | `admin` | `123456` |
| Propietario | `propietario` | `123456` |

### Abrir el Sistema

**Opción A: Directamente**
- Abre `index.html` en tu navegador

**Opción B: Con servidor local (Python)**
```bash
cd sistema-condominio
python -m http.server 8080
```
Luego abre: `http://localhost:8080`

**Opción C: Con VS Code**
- Instala la extensión "Live Server"
- Clic derecho en `index.html` → "Open with Live Server"

### Flujo de Login

1. Selecciona el tipo de usuario (Administrador o Propietario)
2. Ingresa usuario y contraseña
3. Serás redirigido al panel correspondiente

## Funcionalidades

### Panel Administrador

| Sección | Funcionalidades |
|---------|-----------------|
| **Dashboard** | Estadísticas generales (propietarios, recibos, gastos) |
| **Propietarios** | Agregar, listar y eliminar propietarios |
| **Gastos** | Registrar gastos de mantenimiento y luz |
| **Recibos** | Generar recibos mensuales, ver pendientes y pagados |
| **Mi Perfil** | Cambiar contraseña |

### Panel Propietario

| Sección | Funcionalidades |
|---------|-----------------|
| **Mi Información** | Ver datos personales y resumen de cuenta |
| **Recibos Pendientes** | Ver recibos pendientes |
| **Recibos Pagados** | Historial de pagos realizados |
| **Mi Perfil** | Cambiar contraseña |

## Datos de Ejemplo

El sistema incluye datos de ejemplo precargados:

- **3 Propietarios** registrados
- **2 Gastos** (mantenimiento y luz)
- **2 Recibos** (1 pendiente, 1 pagado)

Los datos se pueden modificar durante la sesión. Al recargar la página, se restauran los datos de ejemplo.

## Tecnologías

- **HTML5** - Estructura
- **CSS3** - Estilos con variables CSS, Flexbox, Grid
- **JavaScript ES6+** - Lógica de la aplicación

## Responsive Design

| Dispositivo | Breakpoint | Características |
|-------------|------------|-----------------|
| Desktop | > 992px | Sidebar visible, layout completo |
| Tablet | 576px - 992px | Sidebar oculto, contenido adaptado |
| Móvil | < 576px | Layout vertical |

---

**Versión:** 1.0
**Fecha:** Enero 2026
