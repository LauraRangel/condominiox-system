let perfil = null;
let recibosPendientes = [];
let recibosPagados = [];

function toNumber(value) {
    if (typeof value === 'number') return value;
    const parsed = parseFloat(value);
    return Number.isNaN(parsed) ? 0 : parsed;
}

function getPropietarioId() {
    const user = getUserData();
    return user && user.propietario_id ? user.propietario_id : null;
}

// ========================================
// CARGAR INFORMACIÓN PERSONAL
// ========================================

async function cargarInformacionPersonal() {
    const { response, data } = await apiFetch('/mi-perfil');
    if (!response.ok) {
        console.error(data);
        return;
    }

    perfil = data.perfil || {};

    document.getElementById('infoNombre').textContent = `${perfil.nombre || ''} ${perfil.apellido || ''}`.trim();
    document.getElementById('infoDepartamentoTorre').textContent = `Depto. ${perfil.nro_departamento || '-'} - Torre ${perfil.torre || '-'}`;
    document.getElementById('infoDNI').textContent = perfil.dni || '-';
    document.getElementById('infoCorreo').textContent = perfil.correo || '-';
    document.getElementById('infoTelefono').textContent = perfil.telefono || '-';

    await cargarEstadisticas();
}

async function cargarEstadisticas() {
    await Promise.all([cargarRecibosPendientes(), cargarRecibosPagados()]);

    document.getElementById('totalPendientes').textContent = recibosPendientes.length;

    const totalPendiente = recibosPendientes.reduce((sum, r) => {
        return sum
            + toNumber(r.monto_administracion)
            + toNumber(r.monto_agua)
            + toNumber(r.monto_luz)
            + toNumber(r.monto_mantenimiento);
    }, 0);
    document.getElementById('montoPendiente').textContent = formatCurrency(totalPendiente);

    document.getElementById('totalPagados').textContent = recibosPagados.length;
}

// ========================================
// RECIBOS PENDIENTES
// ========================================

async function cargarRecibosPendientes() {
    const propietarioId = getPropietarioId();
    if (!propietarioId) return;

    const { response, data } = await apiFetch(`/recibos/propietario/${propietarioId}?estado=pendientes`);
    if (!response.ok) {
        console.error(data);
        return;
    }

    recibosPendientes = data.items || [];
    const tbody = document.getElementById('tablaRecibosPendientes');

    if (recibosPendientes.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="empty-state">No tiene recibos pendientes</td></tr>';
        return;
    }

    tbody.innerHTML = '';
    recibosPendientes.forEach(recibo => {
        const total = toNumber(recibo.monto_administracion)
            + toNumber(recibo.monto_agua)
            + toNumber(recibo.monto_luz)
            + toNumber(recibo.monto_mantenimiento);

        const fecha = new Date(recibo.fecha_emision);
        const mesAnio = fecha.toLocaleDateString('es-PE', { month: 'long', year: 'numeric' });

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${recibo.id}</td>
            <td>${mesAnio}</td>
            <td>${formatCurrency(recibo.monto_administracion)}</td>
            <td>${formatCurrency(recibo.monto_agua)}</td>
            <td>${formatCurrency(recibo.monto_luz)}</td>
            <td>${formatCurrency(recibo.monto_mantenimiento)}</td>
            <td><strong>${formatCurrency(total)}</strong></td>
            <td>
                <button class="btn btn-success" onclick="pagarRecibo(${recibo.id})"
                        style="padding: 0.4rem 0.8rem;">
                    Pagar
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

async function pagarRecibo(idRecibo) {
    const montoStr = prompt('Ingrese el monto a pagar');
    if (!montoStr) {
        return;
    }
    const monto = parseFloat(montoStr);
    if (Number.isNaN(monto) || monto <= 0) {
        alert('Monto inválido');
        return;
    }

    const { response, data } = await apiFetch(`/recibos/${idRecibo}/pagar`, {
        method: 'POST',
        body: JSON.stringify({ monto })
    });

    if (!response.ok) {
        alert(data.error || 'No se pudo procesar el pago');
        return;
    }

    await cargarEstadisticas();
}

// ========================================
// RECIBOS PAGADOS
// ========================================

async function cargarRecibosPagados() {
    const propietarioId = getPropietarioId();
    if (!propietarioId) return;

    const { response, data } = await apiFetch(`/recibos/propietario/${propietarioId}?estado=pagados`);
    if (!response.ok) {
        console.error(data);
        return;
    }

    recibosPagados = data.items || [];
    const tbody = document.getElementById('tablaRecibosPagados');

    if (recibosPagados.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="empty-state">No tiene recibos pagados aún</td></tr>';
        return;
    }

    tbody.innerHTML = '';
    recibosPagados.forEach(recibo => {
        const total = toNumber(recibo.monto_administracion)
            + toNumber(recibo.monto_agua)
            + toNumber(recibo.monto_luz)
            + toNumber(recibo.monto_mantenimiento);

        const fecha = new Date(recibo.fecha_emision);
        const mesAnio = fecha.toLocaleDateString('es-PE', { month: 'long', year: 'numeric' });

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${recibo.id}</td>
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

        mostrarMensaje('mensajePerfil', 'Contraseña cambiada exitosamente', 'success');
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
