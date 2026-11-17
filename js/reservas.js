// ========================================
// RESERVA DE ÁREAS COMUNES (componente innovador 1)
// ========================================

let _areas = [];


function _esc(texto) {
    return String(texto ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

async function cargarReservas() {
    const [areasRes] = await Promise.all([apiFetch('/areas-comunes'), cargarMisReservas()]);
    if (!areasRes.response.ok) return;
    _areas = areasRes.data.items || [];

    document.getElementById('areasGrid').innerHTML = _areas.map((a, i) => `
        <article class="amenidad-card" onclick="abrirReserva(${a.id})" tabindex="0"
                 onkeydown="if(event.key==='Enter')abrirReserva(${a.id})">
            <img class="amenidad-img" src="${imagenArea(a.nombre)}" alt="" loading="lazy">
            <span class="amenidad-num">#${String(i + 1).padStart(2, '0')}</span>
            <h4>${_esc(a.nombre)}</h4>
            <p>${_esc(a.descripcion || '')}</p>
            <div class="amenidad-datos">
                <span>Aforo ${a.aforo}</span>
                <span>${a.hora_apertura} - ${a.hora_cierre}</span>
                <span>${a.uso_exclusivo ? 'Exclusivo' : 'Compartido'}</span>
                <span>${a.anticipacion_min_horas} h antes</span>
                <span>Máx. ${a.duracion_max_horas} h</span>
            </div>
            <div class="amenidad-precio">
                <strong>${a.tarifa > 0 ? formatCurrency(a.tarifa) : 'Sin costo'}</strong>
                ${a.garantia > 0 ? `<small>+ garantía ${formatCurrency(a.garantia)} retornable</small>` : '<small>sin garantía</small>'}
            </div>
            <span class="amenidad-cta">Reservar →</span>
        </article>`).join('');
}

// ---------- Panel de reserva por área ----------

const _DIAS_VISIBLES = 14;
let _res = { area: null, fecha: null, ocupados: [], inicio: null, fin: null, personas: 1, invitados: [] };

function _isoLocal(d) {
    return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
}
const _aMin = t => parseInt(t.slice(0, 2), 10) * 60 + parseInt(t.slice(3, 5), 10);
const _aHora = m => `${String(Math.floor(m / 60)).padStart(2, '0')}:${String(m % 60).padStart(2, '0')}`;

function abrirReserva(id) {
    const area = _areas.find(a => a.id === id);
    if (!area) return;
    _res = { area, fecha: null, ocupados: [], inicio: null, fin: null, personas: 1, invitados: [] };
    _pintarInvitados();
    document.getElementById('resImg').src = imagenArea(area.nombre);
    document.getElementById('resTitulo').textContent = area.nombre;
    document.getElementById('resSub').textContent =
        `${area.hora_apertura} a ${area.hora_cierre} · aforo ${area.aforo} · ${area.uso_exclusivo ? 'uso exclusivo' : 'uso compartido'} · máx. ${area.duracion_max_horas} h`;
    document.getElementById('reglasIncumplidas').classList.add('hidden');

    const hoy = new Date();
    const dias = [];
    for (let i = 0; i < _DIAS_VISIBLES; i++) {
        const d = new Date(hoy.getFullYear(), hoy.getMonth(), hoy.getDate() + i);
        dias.push(d);
    }
    document.getElementById('resDias').innerHTML = dias.map(d => {
        const iso = _isoLocal(d);
        const semana = d.toLocaleDateString('es-PE', { weekday: 'short' }).replace('.', '');
        const mes = d.toLocaleDateString('es-PE', { month: 'short' }).replace('.', '');
        return `<button type="button" class="res-dia" data-fecha="${iso}" onclick="elegirDia('${iso}')">
                    <small>${semana}</small><b>${d.getDate()}</b><small>${mes}</small></button>`;
    }).join('');

    document.getElementById('modalReserva').classList.remove('hidden');
    // primer día en que la anticipación mínima permite reservar algo
    const primero = dias.find(d => {
        const cierre = new Date(d); cierre.setHours(0, _aMin(area.hora_cierre) - 60, 0, 0);
        return cierre.getTime() - Date.now() >= area.anticipacion_min_horas * 3600000;
    }) || dias[0];
    elegirDia(_isoLocal(primero));
}

function cerrarModalReserva() {
    document.getElementById('modalReserva').classList.add('hidden');
}

async function elegirDia(fecha) {
    _res.fecha = fecha;
    _res.inicio = _res.fin = null;
    document.querySelectorAll('.res-dia').forEach(b => b.classList.toggle('activo', b.dataset.fecha === fecha));
    const cont = document.getElementById('resSlots');
    cont.innerHTML = '<p class="res-cargando">Consultando disponibilidad...</p>';
    const { response, data } = await apiFetch(`/areas-comunes/${_res.area.id}/disponibilidad?fecha=${fecha}`);
    if (_res.fecha !== fecha) return; // el usuario ya cambió de día
    _res.ocupados = response.ok ? data.ocupados : [];
    _pintarSlots();
}

// Estado de cada bloque de 1 hora
function _slots() {
    const a = _res.area;
    const ini = _aMin(a.hora_apertura);
    const fin = _aMin(a.hora_cierre);
    const limite = Date.now() + a.anticipacion_min_horas * 3600000;
    const mias = _misReservas.filter(r => r.area_id === a.id && r.fecha === _res.fecha
        && ['confirmada', 'pendiente_garantia'].includes(r.estado));
    const lista = [];
    for (let m = ini; m + 60 <= fin; m += 60) {
        const inicio = new Date(`${_res.fecha}T${_aHora(m)}:00`);
        const cruzan = _res.ocupados.filter(o => _aMin(o.hora_inicio) < m + 60 && _aMin(o.hora_fin) > m);
        const personas = cruzan.reduce((s, o) => s + (o.personas || 0), 0);
        const mia = mias.some(r => _aMin(r.hora_inicio) < m + 60 && _aMin(r.hora_fin) > m);
        let estado = 'libre';
        if (inicio.getTime() < limite) estado = 'bloqueado';
        else if (mia) estado = 'mia';
        else if (a.uso_exclusivo && cruzan.length) estado = 'ocupado';
        else if (!a.uso_exclusivo && personas >= a.aforo) estado = 'ocupado';
        else if (!a.uso_exclusivo && personas > 0) estado = 'parcial';
        lista.push({ m, estado, libres: a.aforo - personas });
    }
    return lista;
}

function _pintarSlots() {
    const lista = _slots();
    const cont = document.getElementById('resSlots');
    if (!lista.length) { cont.innerHTML = '<p class="res-cargando">Sin horarios para este día</p>'; return; }
    const sel = m => _res.inicio !== null && m >= _res.inicio && m < _res.fin;
    cont.innerHTML = lista.map(s => {
        const reservable = s.estado === 'libre' || s.estado === 'parcial';
        const detalle = !_res.area.uso_exclusivo && reservable ? `<small>${s.libres} cupo${s.libres === 1 ? '' : 's'}</small>`
            : s.estado === 'ocupado' ? '<small>Reservado</small>'
            : s.estado === 'mia' ? '<small>Tuya</small>'
            : s.estado === 'bloqueado' ? '<small>—</small>' : '<small>Libre</small>';
        return `<button type="button" class="res-slot ${s.estado} ${sel(s.m) ? 'sel' : ''}" ${reservable ? '' : 'disabled'}
                    onclick="tocarSlot(${s.m})"><b>${_aHora(s.m)}</b>${detalle}</button>`;
    }).join('');
    const libres = lista.filter(s => s.estado === 'libre' || s.estado === 'parcial').length;
    document.getElementById('resAyudaHorario').textContent = libres
        ? 'Toca la hora de inicio y luego la de fin para extender'
        : 'No quedan horarios disponibles este día';
    _actualizarResumen();
}

function tocarSlot(m) {
    const a = _res.area;
    const lista = _slots();
    const cupoMin = (desde, hasta) => Math.min(...lista.filter(s => s.m >= desde && s.m < hasta).map(s => s.libres));
    const libreEntre = (desde, hasta) => lista.filter(s => s.m >= desde && s.m < hasta)
        .every(s => s.estado === 'libre' || s.estado === 'parcial');

    if (_res.inicio !== null && m >= _res.inicio && m < _res.fin && _res.fin - _res.inicio === 60) {
        _res.inicio = _res.fin = null;                       // tocar el único bloque elegido lo quita
    } else if (_res.inicio !== null && m >= _res.fin && m + 60 - _res.inicio <= a.duracion_max_horas * 60
               && libreEntre(_res.inicio, m + 60)) {
        _res.fin = m + 60;                                   // extiende hasta la hora tocada
    } else if (_res.inicio !== null && m > _res.inicio && m < _res.fin) {
        _res.fin = m + 60;                                   // acorta
    } else {
        _res.inicio = m; _res.fin = m + 60;                  // nuevo inicio
    }
    if (!a.uso_exclusivo && _res.inicio !== null) {
        _res.personas = Math.min(_res.personas, cupoMin(_res.inicio, _res.fin));
    }
    _pintarSlots();
}

function _maxPersonas() {
    const a = _res.area;
    if (!a.uso_exclusivo && _res.inicio !== null) {
        return Math.min(..._slots().filter(s => s.m >= _res.inicio && s.m < _res.fin).map(s => s.libres));
    }
    return a.aforo;
}

function cambiarPersonas(delta) {
    const minimo = 1 + _res.invitados.length;   // tú + tus invitados registrados
    if (delta < 0 && _res.personas <= minimo && _res.invitados.length) {
        showToast('Quita un invitado de la lista para reducir el número de personas', 'warning');
        return;
    }
    _res.personas = Math.max(minimo, Math.min(_maxPersonas(), _res.personas + delta));
    _actualizarResumen();
}

// ---------- Lista de invitados ----------

function _invitadoVacio() {
    return { nombres: '', apellidos: '', tipo_documento: 'DNI', numero_documento: '' };
}

function agregarInvitado(datos) {
    if (1 + _res.invitados.length >= _maxPersonas()) {
        showToast(`El aforo disponible es de ${_maxPersonas()} persona(s) contándote a ti`, 'warning');
        return false;
    }
    _res.invitados.push(datos || _invitadoVacio());
    _res.personas = Math.max(_res.personas, 1 + _res.invitados.length);
    _pintarInvitados();
    _actualizarResumen();
    if (!datos) {
        const filas = document.querySelectorAll('.inv-fila');
        filas[filas.length - 1]?.querySelector('input')?.focus();
    }
    return true;
}

function quitarInvitado(i) {
    _res.invitados.splice(i, 1);
    _pintarInvitados();
    _actualizarResumen();
}

function editarInvitado(i, campo, valor) {
    _res.invitados[i][campo] = valor;
    if (campo === 'tipo_documento') {
        const input = document.querySelector(`.inv-fila[data-i="${i}"] .inv-doc`);
        if (input) {
            input.maxLength = valor === 'DNI' ? 8 : 12;
            input.placeholder = valor === 'DNI' ? '8 dígitos' : '9 a 12 caracteres';
        }
    }
    document.querySelector(`.inv-fila[data-i="${i}"]`)?.classList.remove('invalida');
}

function _pintarInvitados() {
    const cont = document.getElementById('resInvitados');
    if (!cont) return;
    cont.innerHTML = _res.invitados.map((v, i) => `
        <div class="inv-fila" data-i="${i}">
            <span class="inv-num">${i + 1}</span>
            <input type="text" placeholder="Nombres" maxlength="60" value="${_esc(v.nombres)}" oninput="editarInvitado(${i}, 'nombres', this.value)">
            <input type="text" placeholder="Apellidos" maxlength="60" value="${_esc(v.apellidos)}" oninput="editarInvitado(${i}, 'apellidos', this.value)">
            <select onchange="editarInvitado(${i}, 'tipo_documento', this.value)">
                <option value="DNI" ${v.tipo_documento === 'DNI' ? 'selected' : ''}>DNI</option>
                <option value="CE" ${v.tipo_documento === 'CE' ? 'selected' : ''}>CE</option>
            </select>
            <input type="text" class="inv-doc" placeholder="${v.tipo_documento === 'DNI' ? '8 dígitos' : '9 a 12 caracteres'}"
                   maxlength="${v.tipo_documento === 'DNI' ? 8 : 12}" value="${_esc(v.numero_documento)}"
                   oninput="editarInvitado(${i}, 'numero_documento', this.value.toUpperCase().replace(/[^A-Z0-9]/g, ''))">
            <button type="button" class="inv-quitar" onclick="quitarInvitado(${i})" aria-label="Quitar invitado">×</button>
        </div>`).join('');
}

function _validarInvitadosCliente() {
    const nombreOk = t => /^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' .-]{2,60}$/.test(t.trim());
    let ok = true;
    _res.invitados.forEach((v, i) => {
        const docOk = v.tipo_documento === 'DNI' ? /^\d{8}$/.test(v.numero_documento) : /^[A-Z0-9]{9,12}$/.test(v.numero_documento);
        const valido = nombreOk(v.nombres) && nombreOk(v.apellidos) && docOk;
        document.querySelector(`.inv-fila[data-i="${i}"]`)?.classList.toggle('invalida', !valido);
        if (!valido) ok = false;
    });
    return ok;
}

function importarInvitados(input) {
    const archivo = input.files && input.files[0];
    input.value = '';
    if (!archivo) return;
    const lector = new FileReader();
    lector.onload = () => {
        const lineas = String(lector.result).split(/\r?\n/).map(l => l.trim()).filter(Boolean);
        let agregados = 0, omitidos = 0;
        for (const linea of lineas) {
            const c = linea.split(/[;,\t]/).map(x => x.trim().replace(/^"|"$/g, ''));
            if (/nombre/i.test(c[0])) continue;                    // encabezado
            let [nombres, apellidos, tipo, numero] = c;
            if (c.length === 3) { numero = tipo; tipo = 'DNI'; }    // nombres, apellidos, número
            tipo = (tipo || 'DNI').toUpperCase().includes('CE') ? 'CE' : 'DNI';
            if (!nombres || !apellidos || !numero) { omitidos++; continue; }
            const ok = agregarInvitado({ nombres, apellidos, tipo_documento: tipo,
                                         numero_documento: numero.toUpperCase().replace(/[^A-Z0-9]/g, '') });
            if (!ok) { omitidos += 1; break; }
            agregados++;
        }
        _validarInvitadosCliente();
        showToast(`${agregados} invitado(s) importado(s)${omitidos ? `, ${omitidos} omitido(s)` : ''}`, agregados ? 'success' : 'warning');
    };
    lector.readAsText(archivo, 'UTF-8');
}

function _actualizarResumen() {
    const a = _res.area;
    document.getElementById('resPersonas').textContent = _res.personas;
    document.getElementById('resPersonasAyuda').textContent =
        `personas en total, contándote a ti · máximo ${_maxPersonas()}${a.uso_exclusivo ? '' : ' (cupos libres)'}`;
    const contador = document.getElementById('resInvContador');
    if (contador) contador.textContent = `${_res.invitados.length} de ${Math.max(_res.personas - 1, 0)}`;
    const btn = document.getElementById('btnReservar');
    const resumen = document.getElementById('resResumen');
    if (_res.inicio === null) {
        resumen.innerHTML = '';
        btn.disabled = true;
        btn.textContent = 'Elige un horario';
        return;
    }
    const horas = (_res.fin - _res.inicio) / 60;
    const fecha = new Date(`${_res.fecha}T12:00:00`).toLocaleDateString('es-PE', { weekday: 'long', day: 'numeric', month: 'long' });
    resumen.innerHTML = `
        <div><span>Cuándo</span><b>${fecha}, ${_aHora(_res.inicio)} a ${_aHora(_res.fin)} (${horas} h)</b></div>
        <div><span>Tarifa</span><b>${a.tarifa > 0 ? `${formatCurrency(a.tarifa)} <small>va a tu recibo del mes</small>` : 'Sin costo'}</b></div>
        ${a.garantia > 0 ? `<div><span>Garantía</span><b>${formatCurrency(a.garantia)} <small>se paga ahora y se devuelve después del uso</small></b></div>` : ''}`;
    btn.disabled = false;
    btn.textContent = a.garantia > 0 ? 'Reservar y pagar garantía' : 'Confirmar reserva';
}

async function crearReserva() {
    const btn = document.getElementById('btnReservar');
    const errores = document.getElementById('reglasIncumplidas');
    if (_res.inicio === null || btn.disabled) return;
    errores.classList.add('hidden');
    if (!_validarInvitadosCliente()) {
        errores.innerHTML = '<strong>Revisa la lista de invitados:</strong> nombres y apellidos con letras, DNI de 8 dígitos o CE de 9 a 12 caracteres.';
        errores.classList.remove('hidden');
        return;
    }
    btn.disabled = true;
    const body = {
        area_id: _res.area.id,
        fecha: _res.fecha,
        hora_inicio: _aHora(_res.inicio),
        hora_fin: _aHora(_res.fin),
        asistentes: _res.personas,
        invitados: _res.invitados
    };
    const { response, data } = await apiFetch('/reservas', { method: 'POST', body: JSON.stringify(body) });
    btn.disabled = false;
    if (!response.ok) {
        const reglas = data.reglas_incumplidas || [data.error || 'No se pudo reservar'];
        errores.innerHTML = `<strong>No se pudo confirmar la reserva:</strong><ul>${reglas.map(r => `<li>${_esc(r)}</li>`).join('')}</ul>`;
        errores.classList.remove('hidden');
        elegirDia(_res.fecha);   // refresca por si alguien tomó el horario
        return;
    }
    cerrarModalReserva();
    await Promise.all([cargarMisReservas(), cargarEstadisticas()]);
    if (data.estado === 'pendiente_garantia') {
        showToast(data.mensaje, 'info', 'Falta pagar la garantía');
        pagarGarantia(data.id, data.garantia, data.area);
    } else {
        showToast(data.mensaje || 'Reserva confirmada', 'success', 'Reserva confirmada');
    }
}

// Compatibilidad: otras partes llaman a estas funciones tras pagar o cancelar
function cargarDisponibilidad() {
    const modal = document.getElementById('modalReserva');
    if (_res.area && _res.fecha && modal && !modal.classList.contains('hidden')) elegirDia(_res.fecha);
}
function seleccionarArea(id) { abrirReserva(id); }

const _ESTADO_RESERVA = {
    confirmada: 'Confirmada', pendiente_garantia: 'Falta garantía', cancelada: 'Cancelada', expirada: 'Vencida'
};

function _celdaGarantia(r) {
    if (!r.garantia) return '—';
    const monto = formatCurrency(r.garantia);
    switch (r.garantia_estado) {
        case 'pendiente': return `${monto}<br><small class="txt-alerta">Pendiente de pago</small>`;
        case 'pagada': return `${monto}<br><small class="txt-info">En custodia</small>`;
        case 'devuelta': return `${monto}<br><small class="txt-ok">Devuelta</small>`;
        case 'devuelta_parcial': return `${monto}<br><small class="txt-alerta">Retenido ${formatCurrency(r.garantia_retenida)}: ${_esc(r.garantia_motivo)}</small>`;
        case 'retenida': return `${monto}<br><small class="txt-error">Retenida: ${_esc(r.garantia_motivo)}</small>`;
        default: return `${monto}<br><small>No pagada</small>`;
    }
}

let _misReservas = [];

function pagarGarantiaDeReserva(id) {
    const r = _misReservas.find(x => x.id === id);
    if (r) pagarGarantia(r.id, r.garantia, r.area);
}

async function cargarMisReservas() {
    const tbody = document.getElementById('tablaMisReservas');
    const { response, data } = await apiFetch('/reservas/mias');
    if (!response.ok) return;
    const items = data.items || [];
    _misReservas = items;
    if (!items.length) {
        tbody.innerHTML = '<tr><td colspan="7" class="empty-state">Aún no tienes reservas</td></tr>';
        return;
    }
    tbody.innerHTML = items.map(r => {
        const activa = r.estado === 'confirmada' || r.estado === 'pendiente_garantia';
        const pagar = r.estado === 'pendiente_garantia'
            ? `<button class="btn btn-success btn-sm" onclick="pagarGarantiaDeReserva(${r.id})">Pagar garantía</button>` : '';
        return `
        <tr class="${activa ? '' : 'fila-cancelada'}">
            <td>${_esc(r.area)}${r.invitados ? `<br><a href="#" class="link-inv" onclick="verInvitados(${r.id});return false;">👥 ${r.invitados} invitado${r.invitados === 1 ? '' : 's'}</a>` : ''}</td>
            <td>${formatDate(r.fecha)}</td>
            <td>${r.hora_inicio} - ${r.hora_fin}</td>
            <td>${r.cargo > 0 ? formatCurrency(r.cargo) : '—'}</td>
            <td>${_celdaGarantia(r)}</td>
            <td><span class="estado-chip ${r.estado}">${_ESTADO_RESERVA[r.estado] || r.estado}</span></td>
            <td><div class="acciones-group">${pagar}${activa ? `<button class="btn btn-secondary btn-sm" onclick="cancelarReserva(${r.id})">Cancelar</button>` : ''}</div></td>
        </tr>`;
    }).join('');
}

async function cancelarReserva(id) {
    const ok = await confirmModal('Se cancelará la reserva: la tarifa se descuenta del recibo y, si pagaste garantía, se devuelve completa.', 'Cancelar reserva');
    if (!ok) return;
    const { response, data } = await apiFetch(`/reservas/${id}`, { method: 'DELETE' });
    if (!response.ok) {
        showToast(data.error || 'No se pudo cancelar', 'error');
        return;
    }
    showToast(data.garantia_devuelta ? `Garantía devuelta: ${formatCurrency(data.garantia_devuelta)} (${data.codigo_devolucion})` : 'Reserva cancelada', 'success', 'Reserva cancelada');
    await Promise.all([cargarMisReservas(), cargarDisponibilidad(), cargarEstadisticas()]);
}
