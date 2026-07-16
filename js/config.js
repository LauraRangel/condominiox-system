// URL base del backend
const API_URL = 'https://condominiox-system.onrender.com/api';
window.API_URL = API_URL;

// Configuración de almacenamiento local
const AUTH_TOKEN_KEY = 'auth_token';
const USER_DATA_KEY = 'user_data';

async function apiFetch(path, options = {}) {
    const url = `${API_URL}${path}`;
    const headers = new Headers(options.headers || {});
    const token = getAuthToken();
    if (token) {
        headers.set('Authorization', `Bearer ${token}`);
    }
    if (!headers.has('Content-Type') && options.body) {
        headers.set('Content-Type', 'application/json');
    }

    const response = await fetch(url, {
        ...options,
        headers
    });

    if (response.status === 401) {
        removeAuthToken();
        window.location.href = 'index.html';
        throw new Error('Sesión expirada');
    }

    const data = await response.json().catch(() => ({}));
    return { response, data };
}

// Helper para obtener el token
function getAuthToken() {
    return localStorage.getItem(AUTH_TOKEN_KEY);
}

// Helper para guardar el token
function setAuthToken(token) {
    localStorage.setItem(AUTH_TOKEN_KEY, token);
}

// Helper para eliminar el token
function removeAuthToken() {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(USER_DATA_KEY);
}

// Helper para obtener datos del usuario
function getUserData() {
    const data = localStorage.getItem(USER_DATA_KEY);
    return data ? JSON.parse(data) : null;
}

// Helper para guardar datos del usuario
function setUserData(data) {
    localStorage.setItem(USER_DATA_KEY, JSON.stringify(data));
}

// Verificar si el usuario está autenticado
function isAuthenticated() {
    return getAuthToken() !== null;
}

// Redirigir si no está autenticado
function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = 'index.html';
    }
}

// Formatear fecha
function formatDate(dateString) {
    if (!dateString) return '-';
    const safe = String(dateString).slice(0, 10);
    const parts = safe.split('-').map(Number);
    if (parts.length === 3 && parts.every(n => !Number.isNaN(n))) {
        const [year, month, day] = parts;
        const dd = String(day).padStart(2, '0');
        const mm = String(month).padStart(2, '0');
        return `${dd}/${mm}/${year}`;
    }
    const date = new Date(dateString);
    return date.toLocaleDateString('es-PE', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatMonthYear(dateString) {
    if (!dateString) return '-';
    const safe = String(dateString).slice(0, 10);
    const parts = safe.split('-').map(Number);
    if (parts.length === 3 && parts.every(n => !Number.isNaN(n))) {
        const [year, month] = parts;
        const meses = [
            'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
            'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
        ];
        const nombreMes = meses[month - 1] || '';
        return `${nombreMes} ${year}`.trim();
    }
    const date = new Date(dateString);
    return date.toLocaleDateString('es-PE', { month: 'long', year: 'numeric' });
}

// Formatear moneda
function formatCurrency(amount) {
    return `S/ ${parseFloat(amount).toFixed(2)}`;
}

// ========================================
// CONFIRM MODAL (compartido admin + propietario)
// ========================================
let confirmModalResolver = null;

function cerrarConfirmModal(accepted) {
    const modal = document.getElementById('confirmModal');
    if (modal) modal.classList.add('hidden');
    if (confirmModalResolver) {
        confirmModalResolver(accepted);
        confirmModalResolver = null;
    }
}

function confirmModal(message, title = 'Confirmar acción', tipo = 'danger') {
    const modal = document.getElementById('confirmModal');
    const titleEl = document.getElementById('confirmModalTitle');
    const messageEl = document.getElementById('confirmModalMessage');
    const iconEl = document.getElementById('confirmModalIcon');
    if (!modal || !titleEl || !messageEl) {
        return Promise.resolve(window.confirm(message));
    }

    const icons = { danger: '⚠️', warning: '⚠️', info: 'ℹ️' };
    const btnAccept = document.getElementById('confirmModalAccept');
    const btnCancel = document.getElementById('confirmModalCancel');

    titleEl.textContent = title;
    messageEl.textContent = message;
    if (iconEl) {
        iconEl.textContent = icons[tipo] || '⚠️';
        iconEl.className = `modal-icon ${tipo}`;
    }
    if (btnAccept) {
        btnAccept.className = tipo === 'danger' ? 'btn btn-danger' : 'btn btn-primary';
        btnAccept.onclick = () => cerrarConfirmModal(true);
    }
    if (btnCancel) {
        btnCancel.onclick = () => cerrarConfirmModal(false);
    }
    modal.onclick = (e) => { if (e.target === modal) cerrarConfirmModal(false); };
    modal.classList.remove('hidden');

    return new Promise((resolve) => {
        confirmModalResolver = resolve;
    });
}

// Toast notifications
function showToast(message, type = 'info', title = '') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
    const titles = { success: 'Éxito', error: 'Error', warning: 'Advertencia', info: 'Información' };

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.info}</span>
        <div class="toast-body">
            <p class="toast-title">${title || titles[type] || ''}</p>
            <p class="toast-message">${message}</p>
        </div>
        <button class="toast-close" onclick="this.closest('.toast').remove()">✕</button>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('hiding');
        setTimeout(() => toast.remove(), 320);
    }, 4000);
}

// ========================================
// COMPROBANTE DE RECIBO (CU16)
// ========================================
async function verComprobante(reciboId) {
    const { response, data } = await apiFetch(`/recibos/${reciboId}`);
    if (!response.ok) {
        showToast(data.error || 'No se pudo cargar el recibo', 'error');
        return;
    }

    const r = data;
    const total = (+r.monto_administracion) + (+r.monto_agua) + (+r.monto_luz) + (+r.monto_mantenimiento);
    const saldo = r.saldo !== undefined ? +r.saldo : (total - (+r.monto_pagado || 0));
    const pagado = r.pagado;
    const prop = r.propietario || {};
    const estadoClass = pagado ? 'pagado' : 'pendiente';
    const estadoLabel = pagado ? '✅ PAGADO' : '⏳ PENDIENTE';
    const fechaEmision = r.fecha_emision ? formatDate(r.fecha_emision) : '—';
    const fechaPago = r.fecha_pago ? formatDate(r.fecha_pago) : '—';

    document.getElementById('comprobanteBody').innerHTML = `
        <div class="comprobante">
            <div class="comprobante-header">
                <img src="img/logo.png" alt="Logo">
                <div>
                    <h2>CondominioX</h2>
                    <p>Comprobante de Recibo #${r.id}</p>
                </div>
            </div>

            <div class="comprobante-meta">
                <div class="comprobante-meta-item">
                    <span>Propietario</span>
                    <span>${prop.nombre || ''} ${prop.apellido || ''}</span>
                </div>
                <div class="comprobante-meta-item">
                    <span>DNI</span>
                    <span>${prop.dni || '—'}</span>
                </div>
                <div class="comprobante-meta-item">
                    <span>Departamento</span>
                    <span>${r.nro_departamento || '—'}</span>
                </div>
                <div class="comprobante-meta-item">
                    <span>Torre</span>
                    <span>${r.torre || '—'}</span>
                </div>
                <div class="comprobante-meta-item">
                    <span>Fecha de emisión</span>
                    <span>${fechaEmision}</span>
                </div>
                <div class="comprobante-meta-item">
                    <span>Fecha de pago</span>
                    <span>${fechaPago}</span>
                </div>
            </div>

            <span class="comprobante-estado ${estadoClass}">${estadoLabel}</span>

            <table class="comprobante-table">
                <thead>
                    <tr>
                        <th>Concepto</th>
                        <th style="text-align:right;">Monto</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td>Administración</td><td style="text-align:right;">${formatCurrency(r.monto_administracion)}</td></tr>
                    <tr><td>Agua</td><td style="text-align:right;">${formatCurrency(r.monto_agua)}</td></tr>
                    <tr><td>Luz</td><td style="text-align:right;">${formatCurrency(r.monto_luz)}</td></tr>
                    <tr><td>Mantenimiento</td><td style="text-align:right;">${formatCurrency(r.monto_mantenimiento)}</td></tr>
                    <tr>
                        <td>TOTAL</td>
                        <td style="text-align:right;">${formatCurrency(total)}</td>
                    </tr>
                </tbody>
            </table>

            <table class="comprobante-table">
                <thead>
                    <tr><th>Monto pagado</th><th style="text-align:right;">Saldo pendiente</th></tr>
                </thead>
                <tbody>
                    <tr>
                        <td>${formatCurrency(r.monto_pagado || 0)}</td>
                        <td style="text-align:right;">${formatCurrency(saldo)}</td>
                    </tr>
                </tbody>
            </table>

            <p class="comprobante-footer">
                Generado el ${new Date().toLocaleDateString('es-PE')} · CondominioX Sistema de Gestión
            </p>
        </div>
    `;

    document.getElementById('modalComprobante').classList.remove('hidden');
    document.body.classList.add('printing-comprobante');
}

function cerrarComprobante() {
    document.getElementById('modalComprobante').classList.add('hidden');
    document.body.classList.remove('printing-comprobante');
}

function imprimirComprobante() {
    window.print();
}
