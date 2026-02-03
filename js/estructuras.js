// ================================
// ESTRUCTURAS DE DATOS DEL PROYECTO
// ================================

// -------------------------------
// Lista enlazada para Propietarios
// -------------------------------

class NodoPropietario {
    constructor(data) {
        this.data = data;
        this.next = null;
    }
}

class ListaPropietarios {
    constructor() {
        this.head = null;
        this.tail = null;
        this.length = 0;
    }

    insertar(data) {
        const nodo = new NodoPropietario(data);
        if (!this.head) {
            this.head = nodo;
            this.tail = nodo;
        } else {
            this.tail.next = nodo;
            this.tail = nodo;
        }
        this.length += 1;
    }

    eliminarPorId(id) {
        if (!this.head) return false;

        if (this.head.data.id === id) {
            this.head = this.head.next;
            if (!this.head) this.tail = null;
            this.length -= 1;
            return true;
        }

        let prev = this.head;
        let curr = this.head.next;
        while (curr) {
            if (curr.data.id === id) {
                prev.next = curr.next;
                if (curr === this.tail) this.tail = prev;
                this.length -= 1;
                return true;
            }
            prev = curr;
            curr = curr.next;
        }
        return false;
    }

    recorrer(callback) {
        let curr = this.head;
        while (curr) {
            callback(curr.data);
            curr = curr.next;
        }
    }

    toArray() {
        const arr = [];
        this.recorrer(item => arr.push(item));
        return arr;
    }
}

// -------------------------------
// Matriz para Recibos (mes x propietario)
// -------------------------------

class MatrizRecibos {
    constructor() {
        this.meses = new Map(); // key: "YYYY-MM"
    }

    _asegurarMes(mes) {
        if (!this.meses.has(mes)) {
            this.meses.set(mes, new Map()); // key: propietarioId -> recibo
        }
        return this.meses.get(mes);
    }

    setRecibo(mes, propietarioId, recibo) {
        const fila = this._asegurarMes(mes);
        fila.set(propietarioId, recibo);
    }

    getRecibo(mes, propietarioId) {
        const fila = this.meses.get(mes);
        if (!fila) return null;
        return fila.get(propietarioId) || null;
    }

    totalPorMes(mes) {
        const fila = this.meses.get(mes);
        if (!fila) return 0;
        let total = 0;
        fila.forEach(recibo => {
            total += recibo.monto_administracion +
                     recibo.monto_agua +
                     recibo.monto_luz +
                     recibo.monto_mantenimiento;
        });
        return total;
    }

    totalPorPropietario(propietarioId) {
        let total = 0;
        this.meses.forEach(fila => {
            const recibo = fila.get(propietarioId);
            if (recibo) {
                total += recibo.monto_administracion +
                         recibo.monto_agua +
                         recibo.monto_luz +
                         recibo.monto_mantenimiento;
            }
        });
        return total;
    }

    listarPorPropietario(propietarioId, filtroFn = null) {
        const result = [];
        this.meses.forEach(fila => {
            fila.forEach(recibo => {
                if (recibo.propietario_id === propietarioId) {
                    if (!filtroFn || filtroFn(recibo)) {
                        result.push(recibo);
                    }
                }
            });
        });
        return result;
    }
}

// -------------------------------
// Lista enlazada para Gastos
// -------------------------------

class NodoGasto {
    constructor(data) {
        this.data = data;
        this.next = null;
    }
}

class ListaGastos {
    constructor() {
        this.head = null;
        this.tail = null;
        this.length = 0;
    }

    agregar(data) {
        const nodo = new NodoGasto(data);
        if (!this.head) {
            this.head = nodo;
            this.tail = nodo;
        } else {
            this.tail.next = nodo;
            this.tail = nodo;
        }
        this.length += 1;
    }

    filtrarPorTipo(tipo) {
        const result = [];
        let curr = this.head;
        while (curr) {
            if (curr.data.tipo === tipo) {
                result.push(curr.data);
            }
            curr = curr.next;
        }
        return result;
    }

    totalizar() {
        let total = 0;
        let curr = this.head;
        while (curr) {
            total += parseFloat(curr.data.monto);
            curr = curr.next;
        }
        return total;
    }

    toArray() {
        const arr = [];
        let curr = this.head;
        while (curr) {
            arr.push(curr.data);
            curr = curr.next;
        }
        return arr;
    }
}

// Exponer clases en el scope global
window.Estructuras = {
    ListaPropietarios,
    MatrizRecibos,
    ListaGastos
};
