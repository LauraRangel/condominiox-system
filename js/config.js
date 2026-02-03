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
    const date = new Date(dateString);
    return date.toLocaleDateString('es-PE', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Formatear moneda
function formatCurrency(amount) {
    return `S/ ${parseFloat(amount).toFixed(2)}`;
}
