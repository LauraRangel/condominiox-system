// ========================================
// PASARELA DE PAGOS EMULADA (componente innovador 2)
// ========================================
// CulqiSandbox imita a Culqi.js: tokeniza la tarjeta EN EL NAVEGADOR, así el número de
// tarjeta nunca viaja a nuestro backend; solo se envía un token tkn_test_...

const CulqiSandbox = {
    luhn(numero) {
        let suma = 0;
        let doble = false;
        for (let i = numero.length - 1; i >= 0; i--) {
            let d = parseInt(numero[i], 10);
            if (doble) { d *= 2; if (d > 9) d -= 9; }
            suma += d;
            doble = !doble;
        }
        return suma % 10 === 0;
    },
    marca(numero) {
        if (/^4/.test(numero)) return 'visa';
        if (/^(5[1-5]|2[2-7])/.test(numero)) return 'mastercard';
        if (/^3[47]/.test(numero)) return 'amex';
        return null;
    },
    crearToken({ numero, exp, cvv, email }) {
        const n = (numero || '').replace(/\D/g, '');
        if (n.length < 13 || !this.luhn(n)) return { error: 'Número de tarjeta inválido' };
        const marca = this.marca(n);
        if (!marca) return { error: 'Solo se aceptan Visa, Mastercard o American Express' };
        const m = /^(\d{2})\/(\d{2})$/.exec((exp || '').trim());
        if (!m || +m[1] < 1 || +m[1] > 12) return { error: 'Fecha de vencimiento inválida (MM/AA)' };
        const vence = new Date(2000 + +m[2], +m[1], 1);
        if (vence <= new Date()) return { error: 'La tarjeta está vencida' };
        if (!/^\d{3,4}$/.test(cvv || '')) return { error: 'CVV inválido' };
        if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email || '')) return { error: 'Ingrese un correo válido' };
        const azar = Array.from(crypto.getRandomValues(new Uint8Array(12)))
            .map(b => 'abcdefghijklmnopqrstuvwxyz0123456789'[b % 36]).join('');
        return { id: `tkn_test_${marca}_${n.slice(-4)}_${azar}`, marca, last4: n.slice(-4) };
    }
};

let _pago = { concepto: 'recibo', reciboId: null, reservaId: null, saldo: 0, medio: null, enviando: false };

function _pasoPago(paso) {
    ['pasoMedio', 'pasoProcesando', 'pasoResultado'].forEach(id =>
        document.getElementById(id).classList.toggle('hidden', id !== paso));
    document.getElementById('pagoFooter').classList.toggle('hidden', paso !== 'pasoMedio');
}

function _errorPago(msg) {
    const el = document.getElementById('modalPagoError');
    el.textContent = msg || '';
    el.style.display = msg ? 'block' : 'none';
}

function pagarRecibo(idRecibo, saldo) {
    _pago = { concepto: 'recibo', reciboId: idRecibo, reservaId: null, saldo: +saldo, medio: null, enviando: false };
    _abrirModalPago(`Pagar recibo #${idRecibo}`, `Saldo pendiente: ${formatCurrency(saldo)}`, saldo, true);
}

// La garantía se paga completa (no admite pagos parciales) y confirma la reserva
function pagarGarantia(reservaId, monto, area) {
    _pago = { concepto: 'garantia', reciboId: null, reservaId, saldo: +monto, medio: null, enviando: false };
    _abrirModalPago(`Garantía · ${area}`,
        `Garantía retornable de ${formatCurrency(monto)}. Al pagarla se confirma tu reserva; la administración la devuelve después del uso.`,
        monto, false);
}

function _abrirModalPago(titulo, texto, monto, editable) {
    document.getElementById('modalPagoTitulo').textContent = titulo;
    document.getElementById('modalPagoSaldo').textContent = texto;
    const input = document.getElementById('modalPagoMonto');
    input.value = (+monto).toFixed(2);
    input.max = monto;
    input.readOnly = !editable;
    document.getElementById('btnMontoTotal').classList.toggle('hidden', !editable);
    document.querySelectorAll('.medio-btn').forEach(b => b.classList.remove('selected'));
    ['formYape', 'formCulqi', 'formMp'].forEach(id => document.getElementById(id).classList.add('hidden'));
    ['yapeCelular', 'yapeOtp', 'tarjetaNumero', 'tarjetaExp', 'tarjetaCvv', 'mpEmail'].forEach(id =>
        document.getElementById(id).value = '');
    document.getElementById('tarjetaEmail').value = (typeof perfil !== 'undefined' && perfil?.correo) || '';
    _errorPago('');
    _pasoPago('pasoMedio');
    document.getElementById('modalPago').classList.remove('hidden');
}

function usarMontoTotal() {
    document.getElementById('modalPagoMonto').value = _pago.saldo.toFixed(2);
    _errorPago('');
}

function cerrarModalPago() {
    if (_pago.enviando) return;
    document.getElementById('modalPago').classList.add('hidden');
}

function elegirMedio(medio) {
    _pago.medio = medio;
    document.querySelectorAll('.medio-btn').forEach(b => b.classList.toggle('selected', b.dataset.medio === medio));
    document.getElementById('formYape').classList.toggle('hidden', medio !== 'yape');
    document.getElementById('formCulqi').classList.toggle('hidden', medio !== 'culqi');
    document.getElementById('formMp').classList.toggle('hidden', medio !== 'mercadopago');
    _errorPago('');
}

const _NOMBRE_MEDIO = { yape: 'Yape', culqi: 'Culqi', mercadopago: 'Mercado Pago' };

function _esperar(ms) { return new Promise(r => setTimeout(r, ms)); }

async function confirmarPago() {
    if (_pago.enviando) return;
    const monto = parseFloat(document.getElementById('modalPagoMonto').value);
    if (Number.isNaN(monto) || monto <= 0) return _errorPago('Ingrese un monto válido mayor a cero.');
    if (monto > _pago.saldo + 0.001) return _errorPago(`El monto no puede exceder el saldo (${formatCurrency(_pago.saldo)}).`);
    if (!_pago.medio) return _errorPago('Elija un medio de pago.');

    let datos = {};
    if (_pago.medio === 'yape') {
        datos = {
            celular: document.getElementById('yapeCelular').value.trim(),
            otp: document.getElementById('yapeOtp').value.trim()
        };
        if (!/^9\d{8}$/.test(datos.celular)) return _errorPago('Ingrese un celular de 9 dígitos que empiece con 9.');
        if (!/^\d{6}$/.test(datos.otp)) return _errorPago('El código de aprobación tiene 6 dígitos.');
    } else if (_pago.medio === 'culqi') {
        const token = CulqiSandbox.crearToken({
            numero: document.getElementById('tarjetaNumero').value,
            exp: document.getElementById('tarjetaExp').value,
            cvv: document.getElementById('tarjetaCvv').value,
            email: document.getElementById('tarjetaEmail').value.trim()
        });
        if (token.error) return _errorPago(token.error);
        datos = { token_id: token.id };   // solo viaja el token, nunca la tarjeta
    } else {
        datos = { email: document.getElementById('mpEmail').value.trim() };
        if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(datos.email)) return _errorPago('Ingrese el correo de su cuenta.');
    }

    _pago.enviando = true;
    _errorPago('');
    _pasoPago('pasoProcesando');
    const texto = document.getElementById('textoProcesando');
    texto.textContent = `Conectando con ${_NOMBRE_MEDIO[_pago.medio]}...`;

    const idempotencyKey = (crypto.randomUUID && crypto.randomUUID()) || `${Date.now()}-${Math.random()}`;
    const peticion = apiFetch('/pagos', {
        method: 'POST',
        headers: { 'Idempotency-Key': idempotencyKey },
        body: JSON.stringify(_pago.concepto === 'garantia'
            ? { concepto: 'garantia', reserva_id: _pago.reservaId, proveedor: _pago.medio, datos }
            : { concepto: 'recibo', recibo_id: _pago.reciboId, monto, proveedor: _pago.medio, datos })
    });
    await _esperar(700);
    texto.textContent = 'Autorizando el pago...';
    let resultado;
    try {
        [resultado] = await Promise.all([peticion, _esperar(700)]);
    } catch (e) {
        resultado = { response: { ok: false, status: 0 }, data: { error: 'No se pudo conectar con el servidor' } };
    }
    _pago.enviando = false;
    _mostrarResultadoPago(resultado.response, resultado.data);
}

function _mostrarResultadoPago(response, data) {
    const cont = document.getElementById('pasoResultado');
    const tx = data.transaccion;
    if (response.ok && tx) {
        const saldo = data.recibo ? +data.recibo.saldo : null;
        const esGarantia = tx.concepto === 'garantia';
        const filaDestino = esGarantia
            ? `<dt>Reserva</dt><dd>#${tx.reserva_id} · <b>confirmada</b>${data.mensaje_cargo ? `<br><small>${data.mensaje_cargo}</small>` : ''}</dd>`
            : `<dt>Recibo</dt><dd>#${tx.recibo_id}${saldo !== null ? (saldo > 0 ? ` · saldo restante ${formatCurrency(saldo)}` : ' · <b>pagado completo</b>') : ''}</dd>`;
        cont.innerHTML = `
            <div class="pago-resultado ok">
                <div class="resultado-icono">✓</div>
                <h3>${esGarantia ? 'Garantía pagada' : 'Pago aprobado'}</h3>
                <p class="resultado-monto">${formatCurrency(tx.monto)}</p>
                <dl class="resultado-detalle">
                    <dt>Código de operación</dt><dd><code>${tx.codigo_operacion}</code></dd>
                    <dt>Medio</dt><dd>${tx.medio_detalle || _NOMBRE_MEDIO[tx.proveedor]}</dd>
                    ${filaDestino}
                    <dt>Fecha</dt><dd>${new Date(tx.fecha).toLocaleString('es-PE')}</dd>
                </dl>
                <div class="resultado-acciones">
                    ${esGarantia ? '' : `<button class="btn btn-secondary" onclick="verComprobante(${tx.recibo_id})">${window.iconoSvg ? iconoSvg('recibo') : '🧾'} Ver comprobante</button>`}
                    <button class="btn btn-primary" onclick="cerrarModalPago()">Listo</button>
                </div>
            </div>`;
        showToast(`${esGarantia ? 'Garantía pagada' : 'Pago aprobado'} · ${tx.codigo_operacion}`, 'success');
        cargarEstadisticas();
        if (esGarantia && typeof cargarMisReservas === 'function') {
            cargarMisReservas();
            cargarDisponibilidad();
        }
    } else {
        const msg = data.error || 'No se pudo procesar el pago';
        cont.innerHTML = `
            <div class="pago-resultado error">
                <div class="resultado-icono">✕</div>
                <h3>Pago no realizado</h3>
                <p>${msg}</p>
                ${tx ? `<p class="resultado-codigo">Referencia: <code>${tx.codigo_operacion}</code></p>` : ''}
                <div class="resultado-acciones">
                    <button class="btn btn-secondary" onclick="cerrarModalPago()">Cerrar</button>
                    <button class="btn btn-primary" onclick="_pasoPago('pasoMedio')">Intentar de nuevo</button>
                </div>
            </div>`;
    }
    _pasoPago('pasoResultado');
}
