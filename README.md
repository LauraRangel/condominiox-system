# CondominioX - Sistema de Gestión de Condominio

**Universidad Tecnológica del Perú**

**Estudiante:** Laura Isabel Rangel Teran

---

Sistema web para la gestión de condominios con frontend en HTML/CSS/JS y backend en Flask + PostgreSQL.

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
├── backend/
│   ├── app.py              # API Flask
│   ├── db.py               # Conexión a PostgreSQL
│   ├── security.py         # Hashing y verificación de contraseña
│   ├── structures.py       # Estructuras de datos (listas/matriz)
│   ├── requirements.txt    # Dependencias backend
│   └── schema.sql          # Esquema de base de datos
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

### Abrir el Sistema

**Opción A: Frontend directo**
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

### Backend local (opcional)
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="postgres://usuario:password@host:puerto/db"
export JWT_SECRET="una_clave_segura"
python app.py
```

### Backend en Render
- Configura `DATABASE_URL` y `JWT_SECRET` en el servicio.
- Start Command: `gunicorn app:app` (si el root es `backend/`).

### Flujo de Login

1. Selecciona el tipo de usuario (Administrador o Propietario)
2. Ingresa usuario y contraseña
3. Serás redirigido al panel correspondiente

## Funcionalidades

### Panel Administrador

| Sección | Funcionalidades |
|---------|-----------------|
| **Dashboard** | Estadísticas generales (propietarios, recibos, gastos) |
| **Propietarios** | Agregar, listar y eliminar propietarios (crea usuario con contraseña = DNI) |
| **Gastos** | Registrar gastos de mantenimiento, luz y agua (con fecha manual) |
| **Recibos** | Generar, recalcular por mes, ver pendientes/pagados y eliminar |
| **Mi Perfil** | Cambiar contraseña |

### Panel Propietario

| Sección | Funcionalidades |
|---------|-----------------|
| **Mi Información** | Ver datos personales y resumen de cuenta |
| **Recibos Pendientes** | Ver recibos pendientes con saldo |
| **Recibos Pagados** | Historial de pagos realizados con monto pagado |
| **Mi Perfil** | Cambiar contraseña |

## Datos
- Los datos reales se guardan en PostgreSQL.
- El login utiliza usuarios reales registrados en la base de datos.

## Tecnologías

- **HTML5** - Estructura
- **CSS3** - Estilos con variables CSS, Flexbox, Grid
- **JavaScript ES6+** - Lógica de la aplicación
- **Flask** - API backend
- **PostgreSQL** - Base de datos

## Responsive Design

| Dispositivo | Breakpoint | Características |
|-------------|------------|-----------------|
| Desktop | > 992px | Sidebar visible, layout completo |
| Tablet | 576px - 992px | Sidebar oculto, contenido adaptado |
| Móvil | < 576px | Layout vertical |

---

**Versión:** 2.0
**Fecha:** Febrero 2026
