// ========================================
// Lista de invitados de una reserva (vista compartida propietario / administrador)
// ========================================

function _escInv(t) {
    return String(t ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

async function verInvitados(reservaId) {
    const { response, data } = await apiFetch(`/reservas/${reservaId}/invitados`);
    if (!response.ok) {
        showToast(data.error || 'No se pudo cargar la lista', 'error');
        return;
    }
    let modal = document.getElementById('modalInvitados');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'modalInvitados';
        modal.className = 'modal-overlay hidden';
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-modal', 'true');
        modal.addEventListener('click', () => modal.classList.add('hidden'));
        document.body.appendChild(modal);
    }
    const filas = data.items.length
        ? data.items.map((i, n) => `<tr><td>${n + 1}</td><td>${_escInv(i.apellidos)}, ${_escInv(i.nombres)}</td><td>${i.tipo_documento}</td><td>${_escInv(i.numero_documento)}</td></tr>`).join('')
        : '<tr><td colspan="4" class="empty-state">No registró invitados</td></tr>';
    modal.innerHTML = `
        <div class="modal-card inv-modal" onclick="event.stopPropagation()">
            <div class="modal-header">
                <h3><span class="modal-icon success">👥</span><span>Invitados · ${_escInv(data.area)}</span></h3>
                <button type="button" class="btn-close" onclick="document.getElementById('modalInvitados').classList.add('hidden')" aria-label="Cerrar">×</button>
            </div>
            <div class="modal-body">
                <p class="inv-sub">${formatDate(data.fecha)}, ${data.hora_inicio} a ${data.hora_fin} · Titular: <b>${_escInv(data.titular)}</b></p>
                <div class="data-table-container">
                    <table class="data-table">
                        <thead><tr><th>#</th><th>Apellidos y nombres</th><th>Doc.</th><th>Número</th></tr></thead>
                        <tbody>${filas}</tbody>
                    </table>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" onclick="imprimirInvitados()">Imprimir para portería</button>
                <button type="button" class="btn btn-primary" onclick="document.getElementById('modalInvitados').classList.add('hidden')">Cerrar</button>
            </div>
        </div>`;
    modal.classList.remove('hidden');
}

function imprimirInvitados() {
    document.body.classList.add('imprimiendo-invitados');
    window.print();
    setTimeout(() => document.body.classList.remove('imprimiendo-invitados'), 300);
}
