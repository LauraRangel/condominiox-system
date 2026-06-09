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
