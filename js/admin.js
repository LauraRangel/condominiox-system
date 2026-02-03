let propietarios = [];
let gastos = [];
let recibos = [];

function obtenerSiguienteId(items, campo = 'id') {
    if (!items || items.length === 0) return 1;
    return Math.max(...items.map(item => item[campo])) + 1;
}

// ========================================
// DASHBOARD
// ========================================

function actualizarDashboard() {
    document.getElementById('totalPropietarios').textContent = propietarios.length;

    const recibosPendientes = recibos.filter(r => !r.pagado);
    document.getElementById('recibosPendientes').textContent = recibosPendientes.length;

    const totalGastos = gastos.reduce((sum, g) => sum + parseFloat(g.monto), 0);
    document.getElementById('gastosDelMes').textContent = formatCurrency(totalGastos);

    const recibosPagados = recibos.filter(r => r.pagado);
    document.getElementById('recibosPagados').textContent = recibosPagados.length;
}

async function cargarDashboard() {
    await Promise.all([cargarPropietarios(), cargarGastos(), cargarRecibos()]);
    actualizarDashboard();
}

// ========================================
// GESTIÓN DE PROPIETARIOS
// ========================================

async function cargarPropietarios() {
    const { response, data } = await apiFetch('/propietarios');
    if (!response.ok) {
        console.error(data);
        return;
    }
    propietarios = data.items || [];
    listarPropietarios();
}

function listarPropietarios() {
    const tbody = document.getElementById('tablaPropietarios');

    if (propietarios.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="empty-state">No hay propietarios registrados</td></tr>';
        return;
    }

    tbody.innerHTML = '';
    propietarios.forEach(prop => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${prop.id}</td>
            <td>${prop.nombre} ${prop.apellido}</td>
            <td>${prop.dni}</td>
            <td>${prop.nro_departamento}</td>
            <td>${prop.torre}</td>
            <td>${prop.telefono || '-'}</td>
            <td>
                <button class="btn btn-danger btn-sm" onclick="eliminarPropietario(${prop.id})">Eliminar</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

if (document.getElementById('formPropietario')) {
    const dniInput = document.getElementById('propDNI');
    const passwordInput = document.getElementById('propContrasena');
    if (dniInput && passwordInput) {
        dniInput.addEventListener('input', function() {
            passwordInput.value = dniInput.value.trim();
        });
        passwordInput.setAttribute('readonly', 'readonly');
    }

    document.getElementById('formPropietario').addEventListener('submit', async function(e) {
        e.preventDefault();

        const nuevoPropietario = {
            usuario: document.getElementById('propUsuario').value.trim(),
            nombre: document.getElementById('propNombre').value.trim(),
            apellido: document.getElementById('propApellido').value.trim(),
            dni: document.getElementById('propDNI').value.trim(),
            correo: document.getElementById('propCorreo').value.trim(),
            telefono: document.getElementById('propTelefono').value.trim(),
            nro_departamento: document.getElementById('propDepartamento').value.trim(),
            torre: document.getElementById('propTorre').value
        };

        if (!/^\d{8}$/.test(nuevoPropietario.dni)) {
            mostrarMensaje('mensajePropietario', 'El DNI debe tener 8 dígitos numéricos', 'error');
            return;
        }

        const { response, data } = await apiFetch('/propietarios', {
            method: 'POST',
            body: JSON.stringify(nuevoPropietario)
        });

        if (!response.ok) {
            mostrarMensaje('mensajePropietario', data.error || 'Error al registrar', 'error');
            return;
        }

        mostrarMensaje('mensajePropietario', 'Propietario registrado exitosamente', 'success');
        document.getElementById('formPropietario').reset();
        await cargarPropietarios();
        actualizarDashboard();

        setTimeout(() => {
            cerrarFormulario('agregarPropietario');
        }, 2000);
    });
}

async function eliminarPropietario(id) {
    if (!confirm('¿Está seguro de eliminar este propietario?')) {
        return;
    }

    const { response, data } = await apiFetch(`/propietarios/${id}`, {
        method: 'DELETE'
    });

    if (!response.ok) {
        alert(data.error || 'No se pudo eliminar');
        return;
    }

    alert('Propietario eliminado exitosamente');
    await cargarPropietarios();
    actualizarDashboard();
}

// ========================================
// GESTIÓN DE GASTOS
// ========================================

async function cargarGastos() {
    const { response, data } = await apiFetch('/gastos');
    if (!response.ok) {
        console.error(data);
        return;
    }
    gastos = data.items || [];
    listarGastos();
}

if (document.getElementById('formGasto')) {
    document.getElementById('formGasto').addEventListener('submit', async function(e) {
        e.preventDefault();

        const nuevoGasto = {
            proveedor: document.getElementById('gastoProveedor').value.trim(),
            concepto: document.getElementById('gastoConcepto').value.trim(),
            monto: parseFloat(document.getElementById('gastoMonto').value),
            tipo: 'mantenimiento',
            fecha_registro: document.getElementById('gastoFecha').value
        };

        const { response, data } = await apiFetch('/gastos', {
            method: 'POST',
            body: JSON.stringify(nuevoGasto)
        });

        if (!response.ok) {
            mostrarMensaje('mensajeGasto', data.error || 'Error al registrar', 'error');
            return;
        }

        mostrarMensaje('mensajeGasto', 'Gasto registrado exitosamente', 'success');
        document.getElementById('formGasto').reset();
        await cargarGastos();
        actualizarDashboard();

        setTimeout(() => {
            cerrarFormulario('agregarGasto');
        }, 2000);
    });
}

if (document.getElementById('formGastoLuz')) {
    document.getElementById('formGastoLuz').addEventListener('submit', async function(e) {
        e.preventDefault();

        const mes = document.getElementById('gastoLuzMes').value;

        const nuevoGasto = {
            proveedor: 'Luz del Sur',
            concepto: `Gasto de luz común - ${mes}`,
            monto: parseFloat(document.getElementById('gastoLuzMonto').value),
            tipo: 'luz',
            fecha_registro: document.getElementById('gastoLuzFecha').value
        };

        const { response, data } = await apiFetch('/gastos', {
            method: 'POST',
            body: JSON.stringify(nuevoGasto)
        });

        if (!response.ok) {
            mostrarMensaje('mensajeGastoLuz', data.error || 'Error al registrar', 'error');
            return;
        }

        mostrarMensaje('mensajeGastoLuz', 'Gasto de luz registrado', 'success');
        document.getElementById('formGastoLuz').reset();
        await cargarGastos();
        actualizarDashboard();

        setTimeout(() => {
            cerrarFormulario('agregarGastoLuz');
        }, 2000);
    });
}

function listarGastos() {
    const tbody = document.getElementById('tablaGastos');

    if (gastos.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="empty-state">No hay gastos registrados</td></tr>';
        return;
    }

    tbody.innerHTML = '';
    gastos.forEach(gasto => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${gasto.id}</td>
            <td>${gasto.proveedor}</td>
            <td>${gasto.concepto}</td>
            <td><span style="background: var(--accent-gold); color: white; padding: 0.2rem 0.5rem; border-radius: 3px;">${gasto.tipo}</span></td>
            <td>${formatCurrency(gasto.monto)}</td>
            <td>${formatDate(gasto.fecha_registro)}</td>
        `;
        tbody.appendChild(tr);
    });
}

// ========================================
// GESTIÓN DE RECIBOS
// ========================================

async function generarRecibos() {
    if (!confirm('¿Generar recibos del mes actual para todos los propietarios?')) {
        return;
    }

    const { response, data } = await apiFetch('/recibos/generar', {
        method: 'POST',
        body: JSON.stringify({})
    });

    if (!response.ok) {
        alert(data.error || 'No se pudieron generar los recibos');
        return;
    }

    alert(`Se generaron ${data.generados} recibos exitosamente`);
    await cargarRecibos('pendientes');
    await cargarRecibos('pagados');
    actualizarDashboard();
}

async function cargarRecibos(estado = '') {
    const query = estado ? `?estado=${estado}` : '';
    const { response, data } = await apiFetch(`/recibos${query}`);
    if (!response.ok) {
        console.error(data);
        return;
    }
    if (!estado) {
        recibos = data.items || [];
    }
    if (estado) {
        listarRecibos(estado, data.items || []);
    }
}

function listarRecibos(tipo = 'pendientes', items = []) {
    const tbody = document.getElementById('tablaRecibos');
    const filtrados = items;

    if (filtrados.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="empty-state">No hay recibos ${tipo}</td></tr>`;
        return;
    }

    tbody.innerHTML = '';
    filtrados.forEach(recibo => {
        const total = recibo.monto_administracion + recibo.monto_agua + recibo.monto_luz + recibo.monto_mantenimiento;
        const estado = recibo.pagado
            ? '<span style="color: green;">✅ Pagado</span>'
            : '<span style="color: orange;">⏳ Pendiente</span>';

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${recibo.id}</td>
            <td>${recibo.propietario.nombre} ${recibo.propietario.apellido}</td>
            <td>${recibo.nro_departamento} - ${recibo.torre}</td>
            <td>${formatCurrency(total)}</td>
            <td>${estado}</td>
            <td>${formatDate(recibo.fecha_emision)}</td>
            <td>${formatDate(recibo.fecha_pago)}</td>
        `;
        tbody.appendChild(tr);
    });
}

// ========================================
// CAMBIAR CONTRASEÑA
// ========================================

if (document.getElementById('formCambiarContrasena')) {
    document.getElementById('formCambiarContrasena').addEventListener('submit', function(e) {
        e.preventDefault();

        const nuevaContrasena = document.getElementById('nuevaContrasena').value;
        const confirmarContrasena = document.getElementById('confirmarContrasena').value;

        if (nuevaContrasena !== confirmarContrasena) {
            mostrarMensaje('mensajePerfil', 'Las contraseñas no coinciden', 'error');
            return;
        }

        mostrarMensaje('mensajePerfil', 'Contraseña cambiada exitosamente', 'success');
        document.getElementById('formCambiarContrasena').reset();
    });
}

// ========================================
// INICIALIZACIÓN
// ========================================

window.addEventListener('DOMContentLoaded', function() {
    cargarDashboard();
    cargarRecibos('pendientes');
});
