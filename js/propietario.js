// Datos estáticos de ejemplo
const PROPIETARIO_DEMO = {
    nombre: 'Juan Carlos',
    apellido: 'Pérez García',
    dni: '12345678',
    correo: 'juan.perez@email.com',
    telefono: '987654321',
    nro_departamento: '101',
    torre: 'A'
};

const RECIBOS_PENDIENTES_DEMO = [
    {
        id_recibo: 1,
        monto_administracion: 50.00,
        monto_agua: 30.00,
        monto_luz: 85.00,
        monto_mantenimiento: 127.50,
        fecha_emision: '2025-01-01'
    }
];

const RECIBOS_PAGADOS_DEMO = [
    {
        id_recibo: 2,
        monto_administracion: 50.00,
        monto_agua: 28.00,
        monto_luz: 75.00,
        monto_mantenimiento: 120.00,
        fecha_emision: '2024-12-01',
        fecha_pago: '2024-12-15'
    }
];

// ========================================
// CARGAR INFORMACIÓN PERSONAL
// ========================================

function cargarInformacionPersonal() {
    document.getElementById('infoNombre').textContent = `${PROPIETARIO_DEMO.nombre} ${PROPIETARIO_DEMO.apellido}`;
    document.getElementById('infoDepartamentoTorre').textContent = `Depto. ${PROPIETARIO_DEMO.nro_departamento} - Torre ${PROPIETARIO_DEMO.torre}`;
    document.getElementById('infoDNI').textContent = PROPIETARIO_DEMO.dni;
    document.getElementById('infoCorreo').textContent = PROPIETARIO_DEMO.correo || '-';
    document.getElementById('infoTelefono').textContent = PROPIETARIO_DEMO.telefono || '-';

    cargarEstadisticas();
}

function cargarEstadisticas() {
    document.getElementById('totalPendientes').textContent = RECIBOS_PENDIENTES_DEMO.length;

    const totalPendiente = RECIBOS_PENDIENTES_DEMO.reduce((sum, r) => {
        return sum + r.monto_administracion + r.monto_agua + r.monto_luz + r.monto_mantenimiento;
    }, 0);
    document.getElementById('montoPendiente').textContent = formatCurrency(totalPendiente);

    document.getElementById('totalPagados').textContent = RECIBOS_PAGADOS_DEMO.length;
}

// ========================================
// RECIBOS PENDIENTES
// ========================================

function cargarRecibosPendientes() {
    const tbody = document.getElementById('tablaRecibosPendientes');

    if (RECIBOS_PENDIENTES_DEMO.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="empty-state">No tiene recibos pendientes</td></tr>';
        return;
    }

    tbody.innerHTML = '';
    RECIBOS_PENDIENTES_DEMO.forEach(recibo => {
        const total = recibo.monto_administracion + recibo.monto_agua +
                      recibo.monto_luz + recibo.monto_mantenimiento;

        const fecha = new Date(recibo.fecha_emision);
        const mesAnio = fecha.toLocaleDateString('es-PE', { month: 'long', year: 'numeric' });

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${recibo.id_recibo}</td>
            <td>${mesAnio}</td>
            <td>${formatCurrency(recibo.monto_administracion)}</td>
            <td>${formatCurrency(recibo.monto_agua)}</td>
            <td>${formatCurrency(recibo.monto_luz)}</td>
            <td>${formatCurrency(recibo.monto_mantenimiento)}</td>
            <td><strong>${formatCurrency(total)}</strong></td>
            <td>
                <button class="btn btn-success" onclick="pagarRecibo(${recibo.id_recibo})"
                        style="padding: 0.4rem 0.8rem;">
                    Pagar
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function pagarRecibo(idRecibo) {
    alert('Función disponible cuando se conecte la base de datos.\n\nEste botón procesará el pago del recibo #' + idRecibo);
}

// ========================================
// RECIBOS PAGADOS
// ========================================

function cargarRecibosPagados() {
    const tbody = document.getElementById('tablaRecibosPagados');

    if (RECIBOS_PAGADOS_DEMO.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="empty-state">No tiene recibos pagados aún</td></tr>';
        return;
    }

    tbody.innerHTML = '';
    RECIBOS_PAGADOS_DEMO.forEach(recibo => {
        const total = recibo.monto_administracion + recibo.monto_agua +
                      recibo.monto_luz + recibo.monto_mantenimiento;

        const fecha = new Date(recibo.fecha_emision);
        const mesAnio = fecha.toLocaleDateString('es-PE', { month: 'long', year: 'numeric' });

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${recibo.id_recibo}</td>
            <td>${mesAnio}</td>
            <td><strong>${formatCurrency(total)}</strong></td>
            <td>${formatDate(recibo.fecha_pago)}</td>
            <td>${formatCurrency(recibo.monto_administracion)}</td>
            <td>${formatCurrency(recibo.monto_agua)}</td>
            <td>${formatCurrency(recibo.monto_luz)}</td>
            <td>${formatCurrency(recibo.monto_mantenimiento)}</td>
        `;
        tbody.appendChild(tr);
    });
}

// ========================================
// CAMBIAR CONTRASEÑA
// ========================================

if (document.getElementById('formCambiarContrasena')) {
    document.getElementById('formCambiarContrasena').addEventListener('submit', function(e) {
        e.preventDefault();

        const nuevaContrasena = document.getElementById('nuevaContrasena').value;
        const confirmarContrasena = document.getElementById('confirmarContrasena').value;

        if (nuevaContrasena !== confirmarContrasena) {
            mostrarMensaje('mensajePerfil', 'Las contraseñas no coinciden', 'error');
            return;
        }

        mostrarMensaje('mensajePerfil', 'Contraseña cambiada exitosamente (demo)', 'success');
        document.getElementById('formCambiarContrasena').reset();
    });
}

// ========================================
// CARGA DE DATOS POR SECCIÓN
// ========================================

function cargarDatosSeccion(seccionId) {
    switch(seccionId) {
        case 'informacion':
            cargarInformacionPersonal();
            break;
        case 'pendientes':
            cargarRecibosPendientes();
            break;
        case 'pagados':
            cargarRecibosPagados();
            break;
    }
}

// Interceptar clicks en la navegación para cargar datos
document.querySelectorAll('.sidebar-nav .nav-item').forEach(btn => {
    btn.addEventListener('click', function() {
        const seccion = this.getAttribute('data-section');
        if (seccion) {
            cargarDatosSeccion(seccion);
        }
    });
});

// ========================================
// INICIALIZACIÓN
// ========================================

window.addEventListener('DOMContentLoaded', function() {
    cargarInformacionPersonal();
});
