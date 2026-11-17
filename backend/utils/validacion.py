"""Validaciones de entrada compartidas (defensa en profundidad contra datos maliciosos)."""

import re
import threading
import time
from collections import defaultdict, deque

_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' .-]{2,100}$")
_TELEFONO = re.compile(r"^\+?[0-9 ]{6,15}$")
_DEPTO = re.compile(r"^[A-Za-z0-9-]{1,10}$")
_TORRE = re.compile(r"^[A-Za-z0-9]{1,5}$")
_USUARIO = re.compile(r"^[A-Za-z0-9._-]{3,50}$")


def validar_propietario(body: dict) -> str | None:
    if not _USUARIO.match(str(body.get("usuario") or "").strip()):
        return "El usuario solo puede tener letras, números, punto, guion y guion bajo (3 a 50)"
    for campo, etiqueta in (("nombre", "El nombre"), ("apellido", "El apellido")):
        if not _NOMBRE.match(str(body.get(campo) or "").strip()):
            return f"{etiqueta} solo puede tener letras y espacios"
    if not _DEPTO.match(str(body.get("nro_departamento") or "").strip()):
        return "Número de departamento inválido"
    if not _TORRE.match(str(body.get("torre") or "").strip()):
        return "Torre inválida"
    return validar_telefono(body.get("telefono"))


def validar_telefono(telefono) -> str | None:
    t = str(telefono or "").strip()
    if t and not _TELEFONO.match(t):
        return "El teléfono solo puede tener números (6 a 15 dígitos)"
    return None


def validar_contrasena(nueva: str) -> str | None:
    if len(nueva) < 8 or not re.search(r"[A-Za-z]", nueva) or not re.search(r"\d", nueva):
        return "La contraseña debe tener al menos 8 caracteres, con letras y números"
    return None


class LimitadorIntentos:
    """Bloquea una clave (IP + usuario) tras demasiados fallos en una ventana de tiempo.

    Vive en memoria del proceso: suficiente para una instancia de Render. Con varias
    instancias habría que moverlo a Redis.
    """

    def __init__(self, maximo: int, ventana_seg: int):
        self.maximo = maximo
        self.ventana = ventana_seg
        self._fallos = defaultdict(deque)
        self._lock = threading.Lock()

    def _limpiar(self, cola, ahora):
        while cola and ahora - cola[0] > self.ventana:
            cola.popleft()

    def bloqueado(self, clave) -> int:
        """Devuelve los segundos que faltan de bloqueo (0 si puede intentar)."""
        ahora = time.monotonic()
        with self._lock:
            cola = self._fallos[clave]
            self._limpiar(cola, ahora)
            if len(cola) >= self.maximo:
                return int(self.ventana - (ahora - cola[0])) + 1
        return 0

    def registrar_fallo(self, clave):
        with self._lock:
            self._fallos[clave].append(time.monotonic())

    def reiniciar(self, clave=None):
        with self._lock:
            if clave is None:
                self._fallos.clear()
            else:
                self._fallos.pop(clave, None)
