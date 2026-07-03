from structures import (
    ArbolPropietariosBST,
    ArbolRecibosAVL,
    ArbolRecibosBST,
    ColaPrioridadMorosos,
    ListaPropietarios,
    MatrizRecibos,
)


class TestListaPropietarios:
    def test_insertar_y_to_list_preserva_orden(self):
        lista = ListaPropietarios()
        lista.insertar({"id": 1})
        lista.insertar({"id": 2})
        lista.insertar({"id": 3})
        assert [d["id"] for d in lista.to_list()] == [1, 2, 3]
        assert lista.length == 3

    def test_eliminar_head(self):
        lista = ListaPropietarios()
        lista.insertar({"id": 1})
        lista.insertar({"id": 2})
        assert lista.eliminar_por_id(1) is True
        assert [d["id"] for d in lista.to_list()] == [2]
        assert lista.length == 1

    def test_eliminar_medio(self):
        lista = ListaPropietarios()
        for i in (1, 2, 3):
            lista.insertar({"id": i})
        assert lista.eliminar_por_id(2) is True
        assert [d["id"] for d in lista.to_list()] == [1, 3]

    def test_eliminar_tail_actualiza_tail(self):
        lista = ListaPropietarios()
        for i in (1, 2, 3):
            lista.insertar({"id": i})
        assert lista.eliminar_por_id(3) is True
        assert [d["id"] for d in lista.to_list()] == [1, 2]
        # insertar de nuevo debe engancharse al nuevo tail (id=2), no al viejo
        lista.insertar({"id": 4})
        assert [d["id"] for d in lista.to_list()] == [1, 2, 4]

    def test_eliminar_id_inexistente(self):
        lista = ListaPropietarios()
        lista.insertar({"id": 1})
        assert lista.eliminar_por_id(999) is False
        assert lista.length == 1

    def test_eliminar_en_lista_vacia(self):
        lista = ListaPropietarios()
        assert lista.eliminar_por_id(1) is False

    def test_eliminar_unico_elemento_deja_lista_vacia(self):
        lista = ListaPropietarios()
        lista.insertar({"id": 1})
        assert lista.eliminar_por_id(1) is True
        assert lista.head is None
        assert lista.tail is None
        assert lista.length == 0


class TestArbolPropietariosBST:
    def test_buscar_en_arbol_vacio(self):
        arbol = ArbolPropietariosBST()
        assert arbol.buscar(1) is None

    def test_insertar_y_buscar_hit(self):
        arbol = ArbolPropietariosBST()
        arbol.insertar(5, {"nombre": "Ana"})
        arbol.insertar(3, {"nombre": "Beto"})
        arbol.insertar(8, {"nombre": "Caro"})
        assert arbol.buscar(3) == {"nombre": "Beto"}
        assert arbol.size == 3

    def test_buscar_miss(self):
        arbol = ArbolPropietariosBST()
        arbol.insertar(5, {"nombre": "Ana"})
        assert arbol.buscar(999) is None

    def test_inorden_orden_ascendente(self):
        arbol = ArbolPropietariosBST()
        for key in (5, 3, 8, 1, 4, 7, 9):
            arbol.insertar(key, key)
        assert arbol.inorden() == [1, 3, 4, 5, 7, 8, 9]

    def test_keys_duplicadas_no_se_pierden(self):
        arbol = ArbolPropietariosBST()
        arbol.insertar(5, "primero")
        arbol.insertar(5, "segundo")
        assert arbol.size == 2
        assert arbol.inorden() == ["primero", "segundo"]


class TestMatrizRecibos:
    def _recibo(self, propietario_id, admin=100, agua=20, luz=30, mant=10):
        return {
            "propietario_id": propietario_id,
            "monto_administracion": admin,
            "monto_agua": agua,
            "monto_luz": luz,
            "monto_mantenimiento": mant,
        }

    def test_set_y_get_recibo(self):
        matriz = MatrizRecibos()
        recibo = self._recibo(1)
        matriz.set_recibo("2026-06", 1, recibo)
        assert matriz.get_recibo("2026-06", 1) == recibo

    def test_get_recibo_mes_inexistente(self):
        matriz = MatrizRecibos()
        assert matriz.get_recibo("2026-06", 1) is None

    def test_get_recibo_propietario_inexistente(self):
        matriz = MatrizRecibos()
        matriz.set_recibo("2026-06", 1, self._recibo(1))
        assert matriz.get_recibo("2026-06", 999) is None

    def test_total_por_mes_suma_los_cuatro_montos(self):
        matriz = MatrizRecibos()
        matriz.set_recibo("2026-06", 1, self._recibo(1, 100, 20, 30, 10))
        matriz.set_recibo("2026-06", 2, self._recibo(2, 50, 5, 5, 5))
        assert matriz.total_por_mes("2026-06") == 225

    def test_total_por_mes_vacio(self):
        matriz = MatrizRecibos()
        assert matriz.total_por_mes("2026-06") == 0

    def test_total_por_propietario_varios_meses(self):
        matriz = MatrizRecibos()
        matriz.set_recibo("2026-05", 1, self._recibo(1, 100, 20, 30, 10))
        matriz.set_recibo("2026-06", 1, self._recibo(1, 100, 20, 30, 10))
        assert matriz.total_por_propietario(1) == 320

    def test_listar_por_propietario_sin_filtro(self):
        matriz = MatrizRecibos()
        matriz.set_recibo("2026-05", 1, self._recibo(1))
        matriz.set_recibo("2026-06", 1, self._recibo(1))
        matriz.set_recibo("2026-06", 2, self._recibo(2))
        resultado = matriz.listar_por_propietario(1)
        assert len(resultado) == 2

    def test_listar_por_propietario_con_filtro(self):
        matriz = MatrizRecibos()
        matriz.set_recibo("2026-05", 1, {**self._recibo(1), "pagado": True})
        matriz.set_recibo("2026-06", 1, {**self._recibo(1), "pagado": False})
        resultado = matriz.listar_por_propietario(1, filtro_fn=lambda r: r["pagado"])
        assert len(resultado) == 1
        assert resultado[0]["pagado"] is True


class TestArbolRecibosBST:
    def _arbol_conocido(self):
        arbol = ArbolRecibosBST()
        for key in (5, 3, 8, 1, 4, 7, 9):
            arbol.insertar(key, key)
        return arbol

    def test_recorrer_inorden(self):
        arbol = self._arbol_conocido()
        assert arbol.recorrer("inorden") == [1, 3, 4, 5, 7, 8, 9]

    def test_recorrer_preorden(self):
        arbol = self._arbol_conocido()
        assert arbol.recorrer("preorden") == [5, 3, 1, 4, 8, 7, 9]

    def test_recorrer_postorden(self):
        arbol = self._arbol_conocido()
        assert arbol.recorrer("postorden") == [1, 4, 3, 7, 9, 8, 5]

    def test_recorrer_arbol_vacio(self):
        arbol = ArbolRecibosBST()
        assert arbol.recorrer("inorden") == []

    def test_rango_vacio(self):
        arbol = self._arbol_conocido()
        assert arbol.rango(100, 200) == []

    def test_rango_cubre_todo(self):
        arbol = self._arbol_conocido()
        assert arbol.rango(0, 100) == [1, 3, 4, 5, 7, 8, 9]

    def test_rango_parcial(self):
        arbol = self._arbol_conocido()
        assert arbol.rango(4, 8) == [4, 5, 7, 8]

    def test_rango_limites_inclusivos(self):
        arbol = self._arbol_conocido()
        assert arbol.rango(1, 1) == [1]
        assert arbol.rango(9, 9) == [9]


class TestArbolRecibosAVL:
    def _altura(self, node):
        if node is None:
            return 0
        return 1 + max(self._altura(node.left), self._altura(node.right))

    def test_insercion_ascendente_mantiene_balanceo(self):
        arbol = ArbolRecibosAVL()
        for key in range(1, 8):  # 1..7, secuencia degenerada para BST clásico
            arbol.insertar(key, key)
        altura = self._altura(arbol.root)
        # con balanceo AVL, 7 nodos deben caber en altura 3 (log2(7)+1 ≈ 3.8 -> 3)
        assert altura == 3
        assert arbol.recorrer("inorden") == [1, 2, 3, 4, 5, 6, 7]

    def test_rotacion_simple_derecha_ll(self):
        arbol = ArbolRecibosAVL()
        for key in (3, 2, 1):  # fuerza rotación LL
            arbol.insertar(key, key)
        assert arbol.root.key == 2
        assert arbol.recorrer("inorden") == [1, 2, 3]

    def test_rotacion_simple_izquierda_rr(self):
        arbol = ArbolRecibosAVL()
        for key in (1, 2, 3):  # fuerza rotación RR
            arbol.insertar(key, key)
        assert arbol.root.key == 2
        assert arbol.recorrer("inorden") == [1, 2, 3]

    def test_rotacion_doble_izquierda_derecha_lr(self):
        arbol = ArbolRecibosAVL()
        for key in (3, 1, 2):  # fuerza rotación LR
            arbol.insertar(key, key)
        assert arbol.root.key == 2
        assert arbol.recorrer("inorden") == [1, 2, 3]

    def test_rotacion_doble_derecha_izquierda_rl(self):
        arbol = ArbolRecibosAVL()
        for key in (1, 3, 2):  # fuerza rotación RL
            arbol.insertar(key, key)
        assert arbol.root.key == 2
        assert arbol.recorrer("inorden") == [1, 2, 3]

    def test_rango_heredado_funciona_igual_que_bst(self):
        arbol = ArbolRecibosAVL()
        for key in (5, 3, 8, 1, 4, 7, 9):
            arbol.insertar(key, key)
        assert arbol.rango(4, 8) == [4, 5, 7, 8]

    def test_recorrer_preorden(self):
        arbol = ArbolRecibosAVL()
        for key in (5, 3, 8, 1, 4, 7, 9):
            arbol.insertar(key, key)
        assert arbol.recorrer("preorden") == [5, 3, 1, 4, 8, 7, 9]

    def test_recorrer_postorden(self):
        arbol = ArbolRecibosAVL()
        for key in (5, 3, 8, 1, 4, 7, 9):
            arbol.insertar(key, key)
        assert arbol.recorrer("postorden") == [1, 4, 3, 7, 9, 8, 5]


class TestColaPrioridadMorosos:
    def _item(self, saldo, dias, nombre):
        return {"saldo": saldo, "dias_pendiente": dias, "nombre": nombre}

    def test_dequeue_heap_vacio(self):
        cola = ColaPrioridadMorosos()
        assert cola.dequeue() is None

    def test_dequeue_un_solo_elemento(self):
        cola = ColaPrioridadMorosos()
        cola.enqueue(self._item(100, 5, "A"))
        assert cola.dequeue()["nombre"] == "A"
        assert cola.dequeue() is None

    def test_prioridad_por_mayor_saldo(self):
        cola = ColaPrioridadMorosos()
        cola.enqueue(self._item(50, 10, "bajo"))
        cola.enqueue(self._item(200, 1, "alto"))
        assert cola.dequeue()["nombre"] == "alto"
        assert cola.dequeue()["nombre"] == "bajo"

    def test_empate_en_saldo_desempata_por_dias(self):
        cola = ColaPrioridadMorosos()
        cola.enqueue(self._item(100, 5, "menos_dias"))
        cola.enqueue(self._item(100, 20, "mas_dias"))
        assert cola.dequeue()["nombre"] == "mas_dias"
        assert cola.dequeue()["nombre"] == "menos_dias"

    def test_to_sorted_list_respeta_orden_completo(self):
        cola = ColaPrioridadMorosos()
        datos = [
            self._item(100, 5, "c"),
            self._item(300, 2, "a"),
            self._item(200, 1, "b"),
        ]
        for d in datos:
            cola.enqueue(d)
        resultado = cola.to_sorted_list()
        assert [d["nombre"] for d in resultado] == ["a", "b", "c"]

    def test_to_sorted_list_respeta_limit(self):
        cola = ColaPrioridadMorosos()
        for saldo, nombre in [(100, "c"), (300, "a"), (200, "b")]:
            cola.enqueue(self._item(saldo, 1, nombre))
        resultado = cola.to_sorted_list(limit=2)
        assert [d["nombre"] for d in resultado] == ["a", "b"]

    def test_to_sorted_list_no_muta_el_heap_original(self):
        cola = ColaPrioridadMorosos()
        for saldo, nombre in [(100, "c"), (300, "a"), (200, "b")]:
            cola.enqueue(self._item(saldo, 1, nombre))
        tamano_antes = len(cola.heap)
        cola.to_sorted_list()
        assert len(cola.heap) == tamano_antes
        # debe poder volver a hacer dequeue con normalidad tras el backup/restore
        assert cola.dequeue()["nombre"] == "a"

    def test_heapify_down_con_hijo_derecho_mayor(self):
        # heap de 5+ elementos donde el reemplazo de la raíz debe hundirse
        # comparando también contra el hijo derecho (no solo el izquierdo)
        cola = ColaPrioridadMorosos()
        for saldo, nombre in [
            (500, "raiz"),
            (100, "izq"),
            (400, "der"),
            (50, "izq-izq"),
            (300, "der-izq"),
        ]:
            cola.enqueue(self._item(saldo, 1, nombre))
        resultado = cola.to_sorted_list()
        assert [d["nombre"] for d in resultado] == [
            "raiz",
            "der",
            "der-izq",
            "izq",
            "izq-izq",
        ]
