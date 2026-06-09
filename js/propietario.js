let perfil = null;
let recibosPendientes = [];
let recibosPagados = [];
let editandoContacto = false;

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
    const correoInput = document.getElementById('infoCorreoInput');
    const telefonoInput = document.getElementById('infoTelefonoInput');
    if (correoInput) correoInput.value = perfil.correo || '';
    if (telefonoInput) telefonoInput.value = perfil.telefono || '';

    await cargarEstadisticas();
}

function activarEdicionContacto(activo) {
    editandoContacto = activo;
    const correoValor = document.getElementById('infoCorreo');
    const telefonoValor = document.getElementById('infoTelefono');
    const correoInput = document.getElementById('infoCorreoInput');
    const telefonoInput = document.getElementById('infoTelefonoInput');
    const acciones = document.getElementById('accionesEditarContacto');
    const btnEditar = document.getElementById('btnEditarContacto');

    if (!correoValor || !telefonoValor || !correoInput || !telefonoInput || !acciones || !btnEditar) {
        return;
    }

    correoValor.classList.toggle('hidden', activo);
    telefonoValor.classList.toggle('hidden', activo);
    correoInput.classList.toggle('hidden', !activo);
    telefonoInput.classList.toggle('hidden', !activo);
    correoInput.disabled = !activo;
    telefonoInput.disabled = !activo;
    acciones.classList.toggle('hidden', !activo);
    btnEditar.classList.toggle('hidden', activo);

    if (activo) {
        correoInput.value = perfil?.correo || '';
        telefonoInput.value = perfil?.telefono || '';
        correoInput.focus();
    }
}

async function guardarContacto() {
    const correoInput = document.getElementById('infoCorreoInput');
    const telefonoInput = document.getElementById('infoTelefonoInput');
    if (!correoInput || !telefonoInput) return;

    const correo = correoInput.value.trim();
    const telefono = telefonoInput.value.trim();
    const { response, data } = await apiFetch('/mi-perfil', {
        method: 'PUT',
        body: JSON.stringify({ correo, telefono })
    });
    if (!response.ok) {
        mostrarMensaje('mensajeContacto', data.error || 'No se pudo actualizar', 'error');
        return;
    }

    activarEdicionContacto(false);
    await cargarInformacionPersonal();
    mostrarMensaje('mensajeContacto', 'Guardado exitosamente', 'success');
}

function cancelarEdicionContacto() {
    activarEdicionContacto(false);
}

async function cargarEstadisticas() {
    await Promise.all([cargarRecibosPendientes(), cargarRecibosPagados()]);

    document.getElementById('totalPendientes').textContent = recibosPendientes.length;

    const totalPendiente = recibosPendientes.reduce((sum, r) => {
        const total = toNumber(r.monto_administracion)
            + toNumber(r.monto_agua)
            + toNumber(r.monto_luz)
            + toNumber(r.monto_mantenimiento);
        const pagado = toNumber(r.monto_pagado);
        return sum + (total - pagado);
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
        tbody.innerHTML = '<tr><td colspan="10" class="empty-state">No tiene recibos pendientes</td></tr>';
        return;
    }

    tbody.innerHTML = '';
    recibosPendientes.forEach(recibo => {
        const total = toNumber(recibo.monto_administracion)
            + toNumber(recibo.monto_agua)
            + toNumber(recibo.monto_luz)
            + toNumber(recibo.monto_mantenimiento);
        const pagado = toNumber(recibo.monto_pagado);
        const saldo = recibo.saldo !== undefined ? toNumber(recibo.saldo) : (total - pagado);

        const mesAnio = formatMonthYear(recibo.fecha_emision);

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${recibo.id}</td>
            <td>${mesAnio}</td>
            <td>${formatCurrency(recibo.monto_administracion)}</td>
            <td>${formatCurrency(recibo.monto_agua)}</td>
            <td>${formatCurrency(recibo.monto_luz)}</td>
            <td>${formatCurrency(recibo.monto_mantenimiento)}</td>
            <td><strong>${formatCurrency(total)}</strong></td>
            <td>${formatCurrency(pagado)}</td>
            <td>${formatCurrency(saldo)}</td>
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
        tbody.innerHTML = '<tr><td colspan="10" class="empty-state">No tiene recibos pagados aún</td></tr>';
        return;
    }

    tbody.innerHTML = '';
    recibosPagados.forEach(recibo => {
        const total = toNumber(recibo.monto_administracion)
            + toNumber(recibo.monto_agua)
            + toNumber(recibo.monto_luz)
            + toNumber(recibo.monto_mantenimiento);
        const pagado = toNumber(recibo.monto_pagado);
        const saldo = recibo.saldo !== undefined ? toNumber(recibo.saldo) : (total - pagado);

        const mesAnio = formatMonthYear(recibo.fecha_emision);

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${recibo.id}</td>
            <td>${mesAnio}</td>
            <td><strong>${formatCurrency(total)}</strong></td>
            <td>${formatCurrency(pagado)}</td>
            <td>${formatCurrency(saldo)}</td>
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
    document.getElementById('formCambiarContrasena').addEventListener('submit', async function(e) {
        e.preventDefault();

        const actualContrasena = document.getElementById('actualContrasena').value;
        const nuevaContrasena = document.getElementById('nuevaContrasena').value;
        const confirmarContrasena = document.getElementById('confirmarContrasena').value;

        if (nuevaContrasena !== confirmarContrasena) {
            mostrarMensaje('mensajePerfil', 'Las contraseñas no coinciden', 'error');
            return;
        }

        const { response, data } = await apiFetch('/mi-contrasena', {
            method: 'PUT',
            body: JSON.stringify({
                actual_contrasena: actualContrasena,
                nueva_contrasena: nuevaContrasena
            })
        });
        if (!response.ok) {
            mostrarMensaje('mensajePerfil', data.error || 'No se pudo cambiar la contraseña', 'error');
            return;
        }

        mostrarMensaje('mensajePerfil', 'Contraseña cambiada exitosamente', 'success');
        document.getElementById('formCambiarContrasena').reset();
    });
}

if (document.getElementById('btnEditarContacto')) {
    document.getElementById('btnEditarContacto').addEventListener('click', () => activarEdicionContacto(true));
}
if (document.getElementById('btnGuardarContacto')) {
    document.getElementById('btnGuardarContacto').addEventListener('click', guardarContacto);
}
if (document.getElementById('btnCancelarContacto')) {
    document.getElementById('btnCancelarContacto').addEventListener('click', cancelarEdicionContacto);
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
        case 'comunicados':
            cargarComunicados();
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

// ========================================
// CU12 — FILTRO HISTORIAL DE PAGOS
// ========================================

async function filtrarPagadosPorMes() {
    const mes = (document.getElementById('filtroMesPagados')?.value || '').trim();
    if (!mes) {
        renderTablaRecibosPagados(recibosPagados);
        return;
    }
    const filtrados = recibosPagados.filter(r => (r.fecha_emision || '').slice(0, 7) === mes);
    renderTablaRecibosPagados(filtrados);
}

function limpiarFiltroPagados() {
    const inp = document.getElementById('filtroMesPagados');
    if (inp) inp.value = '';
    renderTablaRecibosPagados(recibosPagados);
}

function renderTablaRecibosPagados(items) {
    const tbody = document.getElementById('tablaRecibosPagados');
    if (!tbody) return;
    if (!items.length) {
        tbody.innerHTML = `<tr><td colspan="10" class="empty-state">No hay recibos pagados</td></tr>`;
        return;
    }
    tbody.innerHTML = items.map(r => `
        <tr>
            <td>${r.id}</td>
            <td>${(r.fecha_emision || '').slice(0, 7)}</td>
            <td>S/ ${(+r.total).toFixed(2)}</td>
            <td>S/ ${(+(r.monto_pagado || 0)).toFixed(2)}</td>
            <td>S/ ${(+(r.saldo || 0)).toFixed(2)}</td>
            <td>${r.fecha_pago || '-'}</td>
            <td>S/ ${(+(r.monto_administracion || 0)).toFixed(2)}</td>
            <td>S/ ${(+(r.monto_agua || 0)).toFixed(2)}</td>
            <td>S/ ${(+(r.monto_luz || 0)).toFixed(2)}</td>
            <td>S/ ${(+(r.monto_mantenimiento || 0)).toFixed(2)}</td>
        </tr>
    `).join('');
}

// ========================================
// CU13 — COMUNICADOS (propietario)
// ========================================

let _todosComunicados = [];

const TIPO_LABEL = { informativo: 'Informativo', pago: 'Pago', mantenimiento: 'Mantenimiento' };
const TIPO_COLOR = { informativo: '#dbeafe:#1e40af', pago: '#fef3c7:#92400e', mantenimiento: '#dcfce7:#166534' };

async function cargarComunicados() {
    const contenedor = document.getElementById('contenedorComunicados');
    if (!contenedor) return;
    contenedor.innerHTML = '<p class="empty-state">Cargando...</p>';

    const propietarioId = JSON.parse(localStorage.getItem('user') || '{}').propietario_id;
    if (!propietarioId) return;

    const { response, data } = await apiFetch('/comunicados');
    if (!response.ok) {
        contenedor.innerHTML = '<p class="empty-state">Error al cargar comunicados</p>';
        return;
    }
    _todosComunicados = data.items || [];
    _actualizarBadgeComunicados(_todosComunicados);
    filtrarComunicados();
}

function _actualizarBadgeComunicados(items) {
    const badge = document.getElementById('badgeComunicados');
    if (!badge) return;
    const noLeidos = items.filter(c => !c.leido).length;
    if (noLeidos > 0) {
        badge.textContent = noLeidos;
        badge.classList.remove('hidden');
    } else {
        badge.classList.add('hidden');
    }
}

function filtrarComunicados() {
    const tipo = document.getElementById('filtroTipoComunicado')?.value || '';
    const estado = document.getElementById('filtroEstadoComunicado')?.value || '';

    let filtrados = _todosComunicados;
    if (tipo) filtrados = filtrados.filter(c => c.tipo === tipo);
    if (estado === 'sin_leer') filtrados = filtrados.filter(c => !c.leido);
    if (estado === 'leido') filtrados = filtrados.filter(c => c.leido);

    _renderComunicados(filtrados);
}

function limpiarFiltroComunicados() {
    const tipoEl = document.getElementById('filtroTipoComunicado');
    const estadoEl = document.getElementById('filtroEstadoComunicado');
    if (tipoEl) tipoEl.value = '';
    if (estadoEl) estadoEl.value = '';
    _renderComunicados(_todosComunicados);
}

function _renderComunicados(items) {
    const contenedor = document.getElementById('contenedorComunicados');
    if (!contenedor) return;
    if (!items.length) {
        contenedor.innerHTML = '<p class="empty-state">No hay comunicados disponibles</p>';
        return;
    }
    contenedor.innerHTML = items.map(c => {
        const [bg, color] = (TIPO_COLOR[c.tipo] || '#f3f4f6:#374151').split(':');
        const leido = c.leido;
        return `
        <div style="border:1px solid ${leido ? '#e5e7eb' : '#3b82f6'};border-left:4px solid ${leido ? '#d1d5db' : '#2563eb'};border-radius:8px;padding:1rem;margin-bottom:0.75rem;background:${leido ? '#fff' : '#eff6ff'};">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:0.5rem;">
                <div>
                    <span style="background:${bg};color:${color};padding:2px 8px;border-radius:12px;font-size:0.8rem;">${TIPO_LABEL[c.tipo] || c.tipo}</span>
                    ${!leido ? '<span style="background:#dc2626;color:white;padding:2px 8px;border-radius:12px;font-size:0.8rem;margin-left:4px;">Nuevo</span>' : ''}
                    <h4 style="margin:0.5rem 0 0.25rem 0;">${c.titulo}</h4>
                </div>
                <div style="text-align:right;">
                    <small style="color:#6b7280;">Publicado: ${c.fecha_publicacion || ''}</small>
                    ${c.fecha_caducidad ? `<br><small style="color:#dc2626;">Caduca: ${c.fecha_caducidad}</small>` : ''}
                    ${!leido ? `<br><button class="btn btn-secondary btn-sm" style="margin-top:4px;" onclick="marcarLeido(${c.id})">Marcar leído</button>` : '<br><small style="color:#16a34a;">✓ Leído</small>'}
                </div>
            </div>
            <p style="margin:0.5rem 0 0 0;color:#374151;">${c.contenido}</p>
        </div>
        `;
    }).join('');
}

async function marcarLeido(anuncioId) {
    const { response } = await apiFetch(`/comunicados/${anuncioId}/leer`, { method: 'POST' });
    if (response.ok) {
        const item = _todosComunicados.find(c => c.id === anuncioId);
        if (item) item.leido = true;
        _actualizarBadgeComunicados(_todosComunicados);
        filtrarComunicados();
    }
}
