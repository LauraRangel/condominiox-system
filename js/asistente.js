// ========================================
// ASISTENTE VIRTUAL CON IA (componente innovador 3)
// ========================================

let _chatIniciado = false;

const _ICONO_FUENTE = { reglamento: '📘', recibo: '🧾', pago: '💳', reserva: '📅', gastos: '📊', documento: '📄', areas: '📍' };

function _escChat(texto) {
    return String(texto ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

function iniciarAsistente() {
    if (_chatIniciado) return;
    _chatIniciado = true;
    const nombre = (typeof perfil !== 'undefined' && perfil?.nombre) ? `, ${perfil.nombre}` : '';
    _agregarMensaje('bot', `¡Hola${_escChat(nombre)}! Puedo responder dudas sobre el reglamento del edificio y sobre tu cuenta: recibos, pagos, reservas y gastos comunes. ¿En qué te ayudo?`);
    document.getElementById('chatPregunta').focus();
}

function _agregarMensaje(tipo, html, extra = '') {
    const cont = document.getElementById('chatMensajes');
    const div = document.createElement('div');
    div.className = `chat-msg ${tipo}`;
    div.innerHTML = `<div class="burbuja">${html}${extra}</div>`;
    cont.appendChild(div);
    cont.scrollTop = cont.scrollHeight;
    return div;
}

function _formatearRespuesta(texto, fuentes) {
    const ids = new Map(fuentes.map((f, i) => [f.id, i + 1]));
    let html = _escChat(texto)
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');
    html = html.replace(/\[(F\d+)\]/g, (m, id) => ids.has(id) ? `<sup class="cita">${ids.get(id)}</sup>` : '');
    return html;
}

function _chipFuente(f, i) {
    const art = f.tipo === 'reglamento' ? (/Art\. (\d+)/.exec(f.etiqueta) || [])[1] : null;
    const ref = f.tipo === 'documento' ? f.documento_id : art;
    const contenido = `<b>${i + 1}</b> ${_ICONO_FUENTE[f.tipo] || '📄'} ${_escChat(f.etiqueta)}`;
    return ref && typeof abrirFuente === 'function'
        ? `<button type="button" class="fuente-chip enlace" title="Abrir fuente" onclick="abrirFuente('${f.tipo}', ${Number(ref)})">${contenido}</button>`
        : `<span class="fuente-chip">${contenido}</span>`;
}

function preguntaSugerida(btn) {
    document.getElementById('chatPregunta').value = btn.textContent;
    enviarPregunta();
}

async function enviarPregunta(event) {
    if (event) event.preventDefault();
    const input = document.getElementById('chatPregunta');
    const btn = document.getElementById('btnEnviarPregunta');
    const pregunta = input.value.trim();
    if (!pregunta || btn.disabled) return;

    _agregarMensaje('user', _escChat(pregunta));
    input.value = '';
    btn.disabled = true;
    const escribiendo = _agregarMensaje('bot', '<span class="typing"><i></i><i></i><i></i></span>');

    let res;
    try {
        res = await apiFetch('/asistente/consulta', { method: 'POST', body: JSON.stringify({ pregunta }) });
    } catch (e) {
        res = { response: { ok: false }, data: { error: 'No se pudo conectar con el servidor' } };
    }
    escribiendo.remove();
    btn.disabled = false;
    input.focus();

    const { response, data } = res;
    if (!response.ok) {
        _agregarMensaje('bot error', _escChat(data.error || 'No pude responder en este momento.'));
        return;
    }

    const fuentes = data.fuentes || [];
    const listaFuentes = fuentes.length
        ? `<div class="chat-fuentes"><span>Fuentes:</span>${fuentes.map((f, i) =>
            _chipFuente(f, i)).join('')}</div>`
        : '';
    const modo = data.modo === 'ia'
        ? `<div class="chat-meta">IA · ${_escChat(data.proveedor)} · ${data.latencia_ms} ms</div>`
        : data.modo === 'privacidad'
            ? '<div class="chat-meta privacidad">🔒 Protección de datos personales</div>'
            : `<div class="chat-meta respaldo">Modo respaldo (sin IA) · ${data.latencia_ms} ms</div>`;
    _agregarMensaje('bot', _formatearRespuesta(data.respuesta, fuentes), listaFuentes + modo);
}
