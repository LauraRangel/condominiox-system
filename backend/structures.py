class NodoPropietario:
    def __init__(self, data):
        self.data = data
        self.next = None


class ListaPropietarios:
    def __init__(self):
        self.head = None
        self.tail = None
        self.length = 0

    def insertar(self, data):
        nodo = NodoPropietario(data)
        if not self.head:
            self.head = nodo
            self.tail = nodo
        else:
            self.tail.next = nodo
            self.tail = nodo
        self.length += 1

    def eliminar_por_id(self, id_):
        if not self.head:
            return False

        if self.head.data.get("id") == id_:
            self.head = self.head.next
            if not self.head:
                self.tail = None
            self.length -= 1
            return True

        prev = self.head
        curr = self.head.next
        while curr:
            if curr.data.get("id") == id_:
                prev.next = curr.next
                if curr == self.tail:
                    self.tail = prev
                self.length -= 1
                return True
            prev = curr
            curr = curr.next
        return False

    def recorrer(self, callback):
        curr = self.head
        while curr:
            callback(curr.data)
            curr = curr.next

    def to_list(self):
        data = []
        self.recorrer(lambda item: data.append(item))
        return data


class MatrizRecibos:
    def __init__(self):
        self.meses = {}

    def _asegurar_mes(self, mes):
        if mes not in self.meses:
            self.meses[mes] = {}
        return self.meses[mes]

    def set_recibo(self, mes, propietario_id, recibo):
        fila = self._asegurar_mes(mes)
        fila[propietario_id] = recibo

    def get_recibo(self, mes, propietario_id):
        fila = self.meses.get(mes)
        if not fila:
            return None
        return fila.get(propietario_id)

    def total_por_mes(self, mes):
        fila = self.meses.get(mes)
        if not fila:
            return 0
        total = 0
        for recibo in fila.values():
            total += (
                recibo["monto_administracion"]
                + recibo["monto_agua"]
                + recibo["monto_luz"]
                + recibo["monto_mantenimiento"]
            )
        return total

    def total_por_propietario(self, propietario_id):
        total = 0
        for fila in self.meses.values():
            recibo = fila.get(propietario_id)
            if recibo:
                total += (
                    recibo["monto_administracion"]
                    + recibo["monto_agua"]
                    + recibo["monto_luz"]
                    + recibo["monto_mantenimiento"]
                )
        return total

    def listar_por_propietario(self, propietario_id, filtro_fn=None):
        result = []
        for fila in self.meses.values():
            for recibo in fila.values():
                if recibo.get("propietario_id") == propietario_id:
                    if not filtro_fn or filtro_fn(recibo):
                        result.append(recibo)
        return result


class NodoGasto:
    def __init__(self, data):
        self.data = data
        self.next = None


class ListaGastos:
    def __init__(self):
        self.head = None
        self.tail = None
        self.length = 0

    def agregar(self, data):
        nodo = NodoGasto(data)
        if not self.head:
            self.head = nodo
            self.tail = nodo
        else:
            self.tail.next = nodo
            self.tail = nodo
        self.length += 1

    def filtrar_por_tipo(self, tipo):
        result = []
        curr = self.head
        while curr:
            if curr.data.get("tipo") == tipo:
                result.append(curr.data)
            curr = curr.next
        return result

    def totalizar(self):
        total = 0
        curr = self.head
        while curr:
            total += float(curr.data.get("monto", 0))
            curr = curr.next
        return total

    def to_list(self):
        result = []
        curr = self.head
        while curr:
            result.append(curr.data)
            curr = curr.next
        return result
