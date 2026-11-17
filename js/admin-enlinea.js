// ========================================
// ADMIN: PAGOS EN LÍNEA, ÁREAS COMUNES Y RESERVAS (APF3)
// ========================================

function _escA(texto) {
    return String(texto ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

const _MEDIO_ADMIN = { yape: 'Yape', culqi: 'Tarjeta (Culqi)', mercadopago: 'Mercado Pago' };

let _txAdmin = [];

async function cargarPanelEnLinea() {
    const [pagos, reservas] = await Promise.all([
        apiFetch('/pagos'), apiFetch('/reservas'), cargarAreasAdmin()
    ]);
    _txAdmin = pagos.response.ok ? (pagos.data.items || []) : [];
    _reservasAdmin = reservas.response.ok ? (reservas.data.items || []) : [];
    _llenarOpcionesFiltro();
    aplicarFiltrosEnLinea();
}

// ---------- Filtros (fecha, área, persona, depto., concepto/estado) ----------

const _normA = t => String(t ?? '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().trim();

function _llenarOpcionesFiltro() {
    const select = document.getElementById('fArea');
    if (!select) return;
    const actual = select.value;
    const nombres = [...new Set([...(_areasAdmin || []).map(a => a.nombre), ..._reservasAdmin.map(r => r.area)])].filter(Boolean);
    select.innerHTML = '<option value="">Todas las áreas</option>' + nombres.map(n => `<option>${_escA(n)}</option>`).join('');
    select.value = nombres.includes(actual) ? actual : '';
}

function _leerFiltros() {
    const v = id => (document.getElementById(id)?.value || '').trim();
    return {
        desde: v('fDesde'), hasta: v('fHasta'), area: v('fArea'),
        persona: _normA(v('fPersona')), depto: _normA(v('fDepto')).replace(/\s+/g, ''),
        concepto: v('fConcepto'), estadoPago: v('fEstadoPago'), estadoReserva: v('fEstadoReserva')
    };
}

function _coincideComun(f, fechaIso, area, persona, depto, torre) {
    const dia = (fechaIso || '').slice(0, 10);
    if (f.desde && dia < f.desde) return false;
    if (f.hasta && dia > f.hasta) return false;
    if (f.area && area !== f.area) return false;
    if (f.persona && !_normA(persona).includes(f.persona)) return false;
    if (f.depto) {
        const d = _normA(`${depto || ''}${torre || ''}`).replace(/[\s-]+/g, '');
        if (!d.includes(f.depto.replace(/-/g, ''))) return false;
    }
    return true;
}

function _diaLocal(iso) {
    // la fecha de la transacción viene con zona horaria: se compara en hora local
    const d = new Date(iso);
    return Number.isNaN(d.getTime()) ? '' : new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
}

function aplicarFiltrosEnLinea() {
    const f = _leerFiltros();
    const tx = _txAdmin.filter(t =>
        _coincideComun(f, _diaLocal(t.fecha), t.area || null, t.propietario, t.nro_departamento, t.torre)
        && (!f.concepto || t.concepto === f.concepto)
        && (!f.estadoPago || (f.estadoPago === 'devuelto' ? t.concepto === 'devolucion'
                                                         : t.estado === f.estadoPago && t.concepto !== 'devolucion')));
    const res = _reservasAdmin.filter(r =>
        _coincideComun(f, r.fecha, r.area, r.propietario, r.nro_departamento, r.torre)
        && (!f.estadoReserva || (f.estadoReserva === 'garantia_custodia'
                                 ? r.garantia_estado === 'pagada' : r.estado === f.estadoReserva)));

    _pintarTransacciones(tx);
    _pintarReservasAdmin(res);
    _pintarKpis(tx, res);

    const activos = Object.values(f).filter(Boolean).length;
    document.getElementById('fResumen').textContent = activos
        ? `Mostrando ${tx.length} de ${_txAdmin.length} transacciones y ${res.length} de ${_reservasAdmin.length} reservas`
        : `${_txAdmin.length} transacciones · ${_reservasAdmin.length} reservas`;
    document.getElementById('btnLimpiarFiltros').classList.toggle('hidden', !activos);
}

function limpiarFiltrosEnLinea() {
    ['fDesde', 'fHasta', 'fArea', 'fPersona', 'fDepto', 'fConcepto', 'fEstadoPago', 'fEstadoReserva'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });
    aplicarFiltrosEnLinea();
}

function filtroRapido(dias) {
    const hoy = new Date();
    const iso = d => new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
    if (dias === 'mes') {
        document.getElementById('fDesde').value = iso(new Date(hoy.getFullYear(), hoy.getMonth(), 1));
        document.getElementById('fHasta').value = iso(new Date(hoy.getFullYear(), hoy.getMonth() + 1, 0));
    } else {
        document.getElementById('fDesde').value = iso(new Date(hoy.getFullYear(), hoy.getMonth(), hoy.getDate() - dias));
        document.getElementById('fHasta').value = iso(hoy);
    }
    aplicarFiltrosEnLinea();
}

function _pintarKpis(tx, res) {
    const aprobadas = tx.filter(t => t.estado === 'aprobado' && t.concepto !== 'devolucion');
    document.getElementById('kpiAprobadas').textContent = aprobadas.length;
    document.getElementById('kpiRechazadas').textContent = tx.filter(t => t.estado === 'rechazado').length;
    document.getElementById('kpiConciliado').textContent =
        formatCurrency(aprobadas.filter(t => t.concepto === 'recibo').reduce((s, t) => s + t.monto, 0));
    document.getElementById('kpiReservas').textContent = res.filter(r => r.estado === 'confirmada').length;
    document.getElementById('kpiCustodia').textContent =
        formatCurrency(res.filter(r => r.garantia_estado === 'pagada').reduce((s, r) => s + r.garantia, 0));
}

function _pintarTransacciones(items) {
    document.getElementById('tablaTransacciones').innerHTML = items.length ? items.map(t => `
        <tr>
            <td>${new Date(t.fecha).toLocaleString('es-PE')}</td>
            <td>${_escA(t.propietario || '-')}</td>
            <td>${_escA(t.nro_departamento || '-')} - ${_escA(t.torre || '')}</td>
            <td>${_conceptoTx(t)}</td>
            <td>${_escA(t.medio_detalle || _MEDIO_ADMIN[t.proveedor])}</td>
            <td class="${t.concepto === 'devolucion' ? 'txt-error' : ''}">${t.concepto === 'devolucion' ? '- ' : ''}${formatCurrency(t.monto)}</td>
            <td><span class="estado-chip ${t.estado}">${t.concepto === 'devolucion' ? 'Devuelto' : (t.estado === 'aprobado' ? 'Aprobado' : 'Rechazado')}</span></td>
            <td><code>${_escA(t.codigo_operacion)}</code></td>
        </tr>`).join('') : '<tr><td colspan="8" class="empty-state">Sin transacciones con estos filtros</td></tr>';
}

function _pintarReservasAdmin(items) {
    document.getElementById('tablaReservasAdmin').innerHTML = items.length ? items.map(r => `
        <tr class="${['cancelada', 'expirada'].includes(r.estado) ? 'fila-cancelada' : ''}">
            <td>${formatDate(r.fecha)}</td>
            <td>${r.hora_inicio} - ${r.hora_fin}</td>
            <td>${_escA(r.area)}</td>
            <td>${_escA(r.propietario)}</td>
            <td>${_escA(r.nro_departamento)} - ${_escA(r.torre)}</td>
            <td>${r.asistentes}${r.invitados ? `<br><a href="#" class="link-inv" onclick="verInvitados(${r.id});return false;">Ver lista (${r.invitados})</a>` : ''}</td>
            <td>${r.cargo > 0 ? formatCurrency(r.cargo) : '—'}<br><small>${r.estado === 'confirmada' ? (r.recibo_id ? 'Recibo #' + r.recibo_id : 'Próximo recibo') : ''}</small></td>
            <td>${_garantiaAdmin(r)}</td>
            <td><span class="estado-chip ${r.estado}">${_ESTADO_RES_ADMIN[r.estado] || r.estado}</span></td>
            <td><div class="acciones-group">
                ${r.garantia_estado === 'pagada' ? `<button class="btn btn-primary btn-sm" onclick="abrirModalGarantia(${r.id})">Devolver garantía</button>` : ''}
                ${['confirmada', 'pendiente_garantia'].includes(r.estado) ? `<button class="btn btn-secondary btn-sm" onclick="cancelarReservaAdmin(${r.id})">Cancelar</button>` : ''}
            </div></td>
        </tr>`).join('') : '<tr><td colspan="10" class="empty-state">Sin reservas con estos filtros</td></tr>';
}

const _ESTADO_RES_ADMIN = { confirmada: 'Confirmada', pendiente_garantia: 'Falta garantía', cancelada: 'Cancelada', expirada: 'Vencida' };
let _reservasAdmin = [];
let _reservaGarantia = null;

function _conceptoTx(t) {
    if (t.concepto === 'garantia') return `Garantía · ${_escA(t.area || 'reserva #' + t.reserva_id)}`;
    if (t.concepto === 'devolucion') return `Devolución de garantía · ${_escA(t.area || 'reserva #' + t.reserva_id)}`;
    return t.recibo_id
        ? `<a href="#" onclick="verComprobante(${t.recibo_id});return false;">Recibo #${t.recibo_id}</a> ${t.mes_recibo ? `(${t.mes_recibo})` : ''}`
        : 'Recibo';
}

function _garantiaAdmin(r) {
    if (!r.garantia) return '—';
    const m = formatCurrency(r.garantia);
    const estados = {
        pendiente: '<small class="txt-alerta">Pendiente de pago</small>',
        pagada: '<small class="txt-info">En custodia</small>',
        devuelta: '<small class="txt-ok">Devuelta</small>',
        devuelta_parcial: `<small class="txt-alerta">Retenido ${formatCurrency(r.garantia_retenida)}: ${_escA(r.garantia_motivo)}</small>`,
        retenida: `<small class="txt-error">Retenida: ${_escA(r.garantia_motivo)}</small>`,
        no_pagada: '<small>No pagada</small>'
    };
    return `${m}<br>${estados[r.garantia_estado] || ''}`;
}

function abrirModalGarantia(id) {
    const r = _reservasAdmin.find(x => x.id === id);
    if (!r) return;
    _reservaGarantia = r;
    document.getElementById('modalGarantiaTitulo').textContent = `Garantía · ${r.area}`;
    document.getElementById('garantiaResumen').innerHTML =
        `${_escA(r.propietario)} (Depto. ${_escA(r.nro_departamento)} - ${_escA(r.torre)}) · reserva del ${formatDate(r.fecha)}, ${r.hora_inicio} a ${r.hora_fin}.<br>Garantía pagada: <b>${formatCurrency(r.garantia)}</b>. Se devuelve por el mismo medio con que se pagó.`;
    document.getElementById('garantiaRetener').value = '0';
    document.getElementById('garantiaRetener').max = r.garantia;
    document.getElementById('garantiaMotivo').value = '';
    document.getElementById('garantiaError').style.display = 'none';
    actualizarDevolucion();
    document.getElementById('modalGarantia').classList.remove('hidden');
}

function actualizarDevolucion() {
    if (!_reservaGarantia) return;
    const retener = Math.min(Math.max(parseFloat(document.getElementById('garantiaRetener').value) || 0, 0), _reservaGarantia.garantia);
    document.getElementById('garantiaADevolver').textContent = formatCurrency(_reservaGarantia.garantia - retener);
}

function cerrarModalGarantia() {
    document.getElementById('modalGarantia').classList.add('hidden');
    _reservaGarantia = null;
}

async function resolverGarantia(event) {
    event.preventDefault();
    const btn = document.getElementById('btnResolverGarantia');
    const errorEl = document.getElementById('garantiaError');
    const body = {
        retener: parseFloat(document.getElementById('garantiaRetener').value) || 0,
        motivo: document.getElementById('garantiaMotivo').value.trim()
    };
    btn.disabled = true;
    const { response, data } = await apiFetch(`/reservas/${_reservaGarantia.id}/garantia/resolucion`, {
        method: 'POST', body: JSON.stringify(body)
    });
    btn.disabled = false;
    if (!response.ok) {
        errorEl.textContent = data.error || 'No se pudo procesar';
        errorEl.style.display = 'block';
        return;
    }
    cerrarModalGarantia();
    const msg = data.devuelto > 0
        ? `Se devolvieron ${formatCurrency(data.devuelto)}${data.retenido > 0 ? ` y se retuvieron ${formatCurrency(data.retenido)}` : ''} · ${data.transaccion.codigo_operacion}`
        : `Se retuvo la garantía completa (${formatCurrency(data.retenido)})`;
    showToast(msg, 'success', 'Garantía resuelta');
    cargarPanelEnLinea();
}

async function cancelarReservaAdmin(id) {
    const ok = await confirmModal('Se cancelará la reserva: la tarifa se descuenta del recibo y la garantía pagada se devuelve completa.', 'Cancelar reserva');
    if (!ok) return;
    const { response, data } = await apiFetch(`/reservas/${id}`, { method: 'DELETE' });
    if (!response.ok) {
        showToast(data.error || 'No se pudo cancelar', 'error');
        return;
    }
    showToast(data.garantia_devuelta ? `Garantía devuelta: ${formatCurrency(data.garantia_devuelta)}` : 'Reserva cancelada', 'success', 'Reserva cancelada');
    cargarPanelEnLinea();
}

// ---------- Configuración de áreas comunes ----------

let _areasAdmin = [];
let _areaEditando = null;

async function cargarAreasAdmin() {
    const { response, data } = await apiFetch('/areas-comunes?todas=1');
    const tbody = document.getElementById('tablaAreasAdmin');
    if (!response.ok) {
        tbody.innerHTML = '<tr><td colspan="10" class="empty-state">No se pudieron cargar las áreas</td></tr>';
        return;
    }
    _areasAdmin = data.items || [];
    tbody.innerHTML = _areasAdmin.map(a => `
        <tr class="${a.activo ? '' : 'fila-cancelada'}">
            <td><div class="area-celda"><img src="${typeof imagenArea === 'function' ? imagenArea(a.nombre) : 'img/logo.png'}" alt=""><div><strong>${_escA(a.nombre)}</strong><br><small>${_escA(a.descripcion || '')}</small></div></div></td>
            <td>${a.tarifa > 0 ? formatCurrency(a.tarifa) : 'Sin costo'}</td>
            <td>${a.garantia > 0 ? formatCurrency(a.garantia) : '—'}</td>
            <td>${a.uso_exclusivo ? 'Exclusivo' : 'Compartido'}</td>
            <td>${a.aforo} personas</td>
            <td>${a.hora_apertura} - ${a.hora_cierre}</td>
            <td>${a.anticipacion_min_horas} h</td>
            <td>${a.duracion_max_horas} h</td>
            <td><span class="estado-chip ${a.activo ? 'confirmada' : 'cancelada'}">${a.activo ? 'Activa' : 'Inactiva'}</span></td>
            <td><button class="btn btn-secondary btn-sm" onclick="abrirModalArea(${a.id})">${window.iconoSvg ? iconoSvg('lapiz') : '✏️'} Editar</button></td>
        </tr>`).join('') || '<tr><td colspan="10" class="empty-state">Sin áreas</td></tr>';
}

function abrirModalArea(id) {
    const a = _areasAdmin.find(x => x.id === id);
    if (!a) return;
    _areaEditando = id;
    document.getElementById('modalAreaTitulo').textContent = `Editar ${a.nombre}`;
    document.getElementById('areaNombre').value = a.nombre;
    document.getElementById('areaDescripcion').value = a.descripcion || '';
    document.getElementById('areaTarifa').value = (+a.tarifa).toFixed(2);
    document.getElementById('areaGarantia').value = (+a.garantia).toFixed(2);
    document.getElementById('areaExclusivo').checked = !!a.uso_exclusivo;
    document.getElementById('areaAforo').value = a.aforo;
    document.getElementById('areaDuracion').value = a.duracion_max_horas;
    document.getElementById('areaApertura').value = a.hora_apertura;
    document.getElementById('areaCierre').value = a.hora_cierre;
    document.getElementById('areaAnticipacion').value = a.anticipacion_min_horas;
    document.getElementById('areaActivo').checked = !!a.activo;
    document.getElementById('areaError').style.display = 'none';
    document.getElementById('modalArea').classList.remove('hidden');
}

function cerrarModalArea() {
    document.getElementById('modalArea').classList.add('hidden');
    _areaEditando = null;
}

async function guardarArea(event) {
    event.preventDefault();
    const btn = document.getElementById('btnGuardarArea');
    const errorEl = document.getElementById('areaError');
    const body = {
        nombre: document.getElementById('areaNombre').value.trim(),
        descripcion: document.getElementById('areaDescripcion').value.trim(),
        tarifa: document.getElementById('areaTarifa').value,
        garantia: document.getElementById('areaGarantia').value,
        uso_exclusivo: document.getElementById('areaExclusivo').checked,
        aforo: document.getElementById('areaAforo').value,
        duracion_max_horas: document.getElementById('areaDuracion').value,
        hora_apertura: document.getElementById('areaApertura').value,
        hora_cierre: document.getElementById('areaCierre').value,
        anticipacion_min_horas: document.getElementById('areaAnticipacion').value,
        activo: document.getElementById('areaActivo').checked
    };
    btn.disabled = true;
    const { response, data } = await apiFetch(`/areas-comunes/${_areaEditando}`, { method: 'PUT', body: JSON.stringify(body) });
    btn.disabled = false;
    if (!response.ok) {
        errorEl.innerHTML = (data.errores || [data.error || 'No se pudo guardar']).map(_escA).join('<br>');
        errorEl.style.display = 'block';
        return;
    }
    cerrarModalArea();
    const aviso = data.reservas_futuras
        ? ` Las ${data.reservas_futuras} reserva(s) ya confirmada(s) mantienen su cargo.`
        : '';
    showToast(`Cambios guardados.${aviso}`, 'success', data.nombre);
    cargarAreasAdmin();
}
