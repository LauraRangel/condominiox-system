// Datos de ejemplo (se pueden agregar más durante la sesión)
const propietariosDemo = [
    {
        id: 1,
        nombre: 'Juan Carlos',
        apellido: 'Pérez García',
        dni: '12345678',
        correo: 'juan.perez@email.com',
        telefono: '987654321',
        nro_departamento: '101',
        torre: 'A'
    },
    {
        id: 2,
        nombre: 'María Elena',
        apellido: 'López Rodríguez',
        dni: '87654321',
        correo: 'maria.lopez@email.com',
        telefono: '912345678',
        nro_departamento: '202',
        torre: 'B'
    },
    {
        id: 3,
        nombre: 'Carlos Alberto',
        apellido: 'Ramírez Torres',
        dni: '45678912',
        correo: 'carlos.ramirez@email.com',
        telefono: '956789123',
        nro_departamento: '303',
        torre: 'A'
    }
];

const propietariosList = new window.Estructuras.ListaPropietarios();
propietariosDemo.forEach(prop => propietariosList.insertar(prop));

const gastosDemo = [
    {
        id: 1,
        proveedor: 'Mantenimiento General',
        concepto: 'Limpieza de áreas comunes',
        monto: 500.00,
        tipo: 'mantenimiento',
        fecha_registro: '2025-01-15'
    },
    {
        id: 2,
        proveedor: 'Luz del Sur',
        concepto: 'Gasto de luz común - Enero 2025',
        monto: 350.00,
        tipo: 'luz',
        fecha_registro: '2025-01-10'
    }
];

const gastosList = new window.Estructuras.ListaGastos();
gastosDemo.forEach(gasto => gastosList.agregar(gasto));

const recibosDemo = [
    {
        id_recibo: 1,
        propietario_id: 1,
        propietario: { nombre: 'Juan Carlos', apellido: 'Pérez García' },
        nro_departamento: '101',
        torre: 'A',
        monto_administracion: 50.00,
        monto_agua: 30.00,
        monto_luz: 85.00,
        monto_mantenimiento: 127.50,
        fecha_emision: '2025-01-01',
        fecha_pago: null,
        pagado: false
    },
    {
        id_recibo: 2,
        propietario_id: 2,
        propietario: { nombre: 'María Elena', apellido: 'López Rodríguez' },
        nro_departamento: '202',
        torre: 'B',
        monto_administracion: 50.00,
        monto_agua: 30.00,
        monto_luz: 85.00,
        monto_mantenimiento: 127.50,
        fecha_emision: '2025-01-01',
        fecha_pago: '2025-01-05',
        pagado: true
    }
];

const recibos = recibosDemo.slice();
const matrizRecibos = new window.Estructuras.MatrizRecibos();
recibos.forEach(recibo => {
    const mes = recibo.fecha_emision.slice(0, 7);
    matrizRecibos.setRecibo(mes, recibo.propietario_id, recibo);
});

// Obtener siguiente ID
function obtenerSiguienteId(lista, campo = 'id') {
    const items = Array.isArray(lista)
        ? lista
        : (lista && typeof lista.toArray === 'function' ? lista.toArray() : []);
    if (items.length === 0) return 1;
    return Math.max(...items.map(item => item[campo])) + 1;
}

// ========================================
// DASHBOARD
// ========================================

function cargarDashboard() {
    document.getElementById('totalPropietarios').textContent = propietariosList.length;

    const recibosPendientes = recibos.filter(r => !r.pagado);
    document.getElementById('recibosPendientes').textContent = recibosPendientes.length;

    const totalGastos = gastosList.totalizar();
    document.getElementById('gastosDelMes').textContent = formatCurrency(totalGastos);

    const recibosPagados = recibos.filter(r => r.pagado);
    document.getElementById('recibosPagados').textContent = recibosPagados.length;

    const mesActual = new Date().toISOString().slice(0, 7);
    const totalRecibosMes = matrizRecibos.totalPorMes(mesActual);
    const recibosPagadosElement = document.getElementById('recibosPagados');
    if (recibosPagadosElement) {
        recibosPagadosElement.title = `Total emitido ${mesActual}: ${formatCurrency(totalRecibosMes)}`;
    }
}

// ========================================
// GESTIÓN DE PROPIETARIOS
// ========================================

function listarPropietarios() {
    const tbody = document.getElementById('tablaPropietarios');

    const propietarios = propietariosList.toArray();
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

// Manejar formulario de agregar propietario
if (document.getElementById('formPropietario')) {
    document.getElementById('formPropietario').addEventListener('submit', function(e) {
        e.preventDefault();

        const nuevoPropietario = {
            id: obtenerSiguienteId(propietariosList),
            nombre: document.getElementById('propNombre').value.trim(),
            apellido: document.getElementById('propApellido').value.trim(),
            dni: document.getElementById('propDNI').value.trim(),
            correo: document.getElementById('propCorreo').value.trim(),
            telefono: document.getElementById('propTelefono').value.trim(),
            nro_departamento: document.getElementById('propDepartamento').value.trim(),
            torre: document.getElementById('propTorre').value
        };

        // Validar DNI (8 dígitos)
        if (!/^\d{8}$/.test(nuevoPropietario.dni)) {
            mostrarMensaje('mensajePropietario', 'El DNI debe tener 8 dígitos numéricos', 'error');
            return;
        }

        // Validar DNI único
        const propietarios = propietariosList.toArray();
        if (propietarios.some(p => p.dni === nuevoPropietario.dni)) {
            mostrarMensaje('mensajePropietario', 'Ya existe un propietario con ese DNI', 'error');
            return;
        }

        // Agregar nuevo propietario
        propietariosList.insertar(nuevoPropietario);

        mostrarMensaje('mensajePropietario', 'Propietario registrado exitosamente', 'success');
        document.getElementById('formPropietario').reset();
        listarPropietarios();
        cargarDashboard();

        setTimeout(() => {
            cerrarFormulario('agregarPropietario');
        }, 2000);
    });
}

// Eliminar propietario
function eliminarPropietario(id) {
    if (!confirm('¿Está seguro de eliminar este propietario?')) {
        return;
    }

    const eliminado = propietariosList.eliminarPorId(id);
    if (eliminado) {
        alert('Propietario eliminado exitosamente');
        listarPropietarios();
        cargarDashboard();
    } else {
        alert('No se encontró el propietario');
    }
}

// ========================================
// GESTIÓN DE GASTOS
// ========================================

// Manejar formulario de gasto de mantenimiento
if (document.getElementById('formGasto')) {
    document.getElementById('formGasto').addEventListener('submit', function(e) {
        e.preventDefault();

        const nuevoGasto = {
            id: obtenerSiguienteId(gastosList),
            proveedor: document.getElementById('gastoProveedor').value.trim(),
            concepto: document.getElementById('gastoConcepto').value.trim(),
            monto: parseFloat(document.getElementById('gastoMonto').value),
            tipo: 'mantenimiento',
            fecha_registro: document.getElementById('gastoFecha').value
        };

        gastosList.agregar(nuevoGasto);

        mostrarMensaje('mensajeGasto', 'Gasto registrado exitosamente', 'success');
        document.getElementById('formGasto').reset();
        listarGastos();
        cargarDashboard();

        setTimeout(() => {
            cerrarFormulario('agregarGasto');
        }, 2000);
    });
}

// Manejar formulario de gasto de luz
if (document.getElementById('formGastoLuz')) {
    document.getElementById('formGastoLuz').addEventListener('submit', function(e) {
        e.preventDefault();

        const mes = document.getElementById('gastoLuzMes').value;

        const nuevoGasto = {
            id: obtenerSiguienteId(gastosList),
            proveedor: 'Luz del Sur',
            concepto: `Gasto de luz común - ${mes}`,
            monto: parseFloat(document.getElementById('gastoLuzMonto').value),
            tipo: 'luz',
            fecha_registro: document.getElementById('gastoLuzFecha').value
        };

        gastosList.agregar(nuevoGasto);

        mostrarMensaje('mensajeGastoLuz', 'Gasto de luz registrado', 'success');
        document.getElementById('formGastoLuz').reset();
        listarGastos();
        cargarDashboard();

        setTimeout(() => {
            cerrarFormulario('agregarGastoLuz');
        }, 2000);
    });
}

// Listar gastos
function listarGastos() {
    const tbody = document.getElementById('tablaGastos');
    const gastos = gastosList.toArray();

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

function generarRecibos() {
    const propietarios = propietariosList.toArray();
    if (propietarios.length === 0) {
        alert('No hay propietarios registrados para generar recibos');
        return;
    }

    if (!confirm('¿Generar recibos del mes actual para todos los propietarios?')) {
        return;
    }

    const fechaActual = new Date();
    const mesActual = fechaActual.toISOString().slice(0, 7);

    // Calcular montos
    const totalGastos = gastosList.totalizar();
    const gastoPorPropietario = totalGastos / propietarios.length;

    const montoAdministracion = 50.00;
    const montoAgua = 30.00;
    const montoLuz = gastoPorPropietario * 0.4;
    const montoMantenimiento = gastoPorPropietario * 0.6;

    let recibosGenerados = 0;

    propietarios.forEach(prop => {
        // Verificar si ya tiene recibo este mes
        const yaExiste = recibos.some(r =>
            r.propietario_id === prop.id &&
            r.fecha_emision.startsWith(mesActual)
        );

        if (!yaExiste) {
            const nuevoRecibo = {
                id_recibo: obtenerSiguienteId(recibos, 'id_recibo'),
                propietario_id: prop.id,
                propietario: {
                    nombre: prop.nombre,
                    apellido: prop.apellido
                },
                nro_departamento: prop.nro_departamento,
                torre: prop.torre,
                monto_administracion: montoAdministracion,
                monto_agua: montoAgua,
                monto_luz: parseFloat(montoLuz.toFixed(2)),
                monto_mantenimiento: parseFloat(montoMantenimiento.toFixed(2)),
                fecha_emision: fechaActual.toISOString().slice(0, 10),
                fecha_pago: null,
                pagado: false
            };

            recibos.push(nuevoRecibo);
            matrizRecibos.setRecibo(mesActual, prop.id, nuevoRecibo);
            recibosGenerados++;
        }
    });

    if (recibosGenerados > 0) {
        alert(`Se generaron ${recibosGenerados} recibos exitosamente`);
    } else {
        alert('Los recibos de este mes ya fueron generados');
    }

    listarRecibos('pendientes');
    cargarDashboard();
}

function listarRecibos(tipo = 'pendientes') {
    const tbody = document.getElementById('tablaRecibos');

    const filtrados = tipo === 'pendientes'
        ? recibos.filter(r => !r.pagado)
        : recibos.filter(r => r.pagado);

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
            <td>${recibo.id_recibo}</td>
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
    listarPropietarios();
    listarGastos();
});
