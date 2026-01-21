// Configuración de almacenamiento local
const AUTH_TOKEN_KEY = 'auth_token';
const USER_DATA_KEY = 'user_data';

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
