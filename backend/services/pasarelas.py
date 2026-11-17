"""Pasarela de pagos emulada (componente innovador 2).

Cada proveedor se implementa como un adaptador con la misma interfaz `cobrar()`
(patrón Strategy / Adapter). Las respuestas imitan la forma de las APIs reales:

  * Culqi  -> objeto "charge" (montos en céntimos, outcome.type = venta_exitosa)
  * Yape   -> cargo con celular + código de aprobación (OTP) generado en la app Yape
  * Mercado Pago -> objeto "payment" (status approved / rejected, status_detail)

En modo sandbox no se mueve dinero real. Pasar a producción implica reemplazar
`_enviar()` de cada adaptador por la llamada HTTP real con las credenciales del
comercio (variables de entorno), sin cambiar la lógica de negocio de pago_service.

Datos de prueba (documentados también en el frontend):
  * Tarjeta aprobada: 4111 1111 1111 1111   | rechazada: 4000 0000 0000 0002
  * Yape: cualquier celular 9XXXXXXXX y OTP de 6 dígitos | OTP 000000 = rechazado
  * Mercado Pago: cualquier correo | correo que contenga "rechazo" = rechazado
"""

import datetime as dt
import re
import secrets
from decimal import Decimal

MODO = "sandbox"


def _ahora_iso():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def _codigo(prefijo: str, n=16) -> str:
    return f"{prefijo}{secrets.token_hex(n // 2).upper()}"


def _resultado(aprobado, codigo, mensaje, medio_detalle, raw):
    return {
        "aprobado": aprobado,
        "codigo_operacion": codigo,
        "mensaje": mensaje,
        "medio_detalle": medio_detalle,
        "respuesta": raw,
    }


class PasarelaBase:
    proveedor = ""

    def validar(self, datos: dict) -> str | None:
        raise NotImplementedError

    def cobrar(self, monto: Decimal, datos: dict, referencia: str) -> dict:
        raise NotImplementedError

    def reembolsar(self, codigo_cargo: str, monto: Decimal, motivo: str) -> dict:
        """Devolución total o parcial de un cargo aprobado (objeto "refund" estilo Culqi)."""
        codigo = _codigo("ref_test_", 16)
        raw = {
            "object": "refund",
            "id": codigo,
            "charge_id": codigo_cargo,
            "creation_date": _ahora_iso(),
            "amount": int(monto * 100),
            "reason": "solicitud_comprador",
            "description": motivo,
        }
        return _resultado(True, codigo, "Devolución procesada", None, raw)


class CulqiSandbox(PasarelaBase):
    """Cobro con tarjeta. El frontend tokeniza la tarjeta (como Culqi.js), así que
    el backend nunca recibe el número de tarjeta: solo un token tkn_test_..."""

    proveedor = "culqi"
    _TOKEN_RE = re.compile(r"^tkn_test_(visa|mastercard|amex)_(\d{4})_[a-z0-9]{12}$")

    def validar(self, datos):
        if not self._TOKEN_RE.match(str(datos.get("token_id") or "")):
            return "Token de tarjeta inválido o vencido"
        return None

    def cobrar(self, monto, datos, referencia):
        marca, last4 = self._TOKEN_RE.match(datos["token_id"]).groups()
        aprobado = last4 != "0002"
        codigo = _codigo("chr_test_", 16)
        raw = {
            "object": "charge",
            "id": codigo,
            "creation_date": _ahora_iso(),
            "amount": int(monto * 100),
            "currency_code": "PEN",
            "description": referencia,
            "source": {"object": "token", "id": datos["token_id"],
                       "iin": {"card_brand": marca.capitalize()}, "card_number": f"****{last4}"},
            "outcome": (
                {"type": "venta_exitosa", "code": "AUT0000",
                 "merchant_message": "La operación de venta ha sido autorizada exitosamente",
                 "user_message": "Su compra ha sido exitosa."}
                if aprobado else
                {"type": "tarjeta_rechazada", "code": "card_declined",
                 "merchant_message": "La tarjeta fue rechazada por el banco emisor",
                 "user_message": "Su tarjeta ha sido rechazada. Intente con otra tarjeta."}
            ),
            "reference_code": secrets.token_hex(5).upper() if aprobado else None,
        }
        return _resultado(aprobado, codigo, raw["outcome"]["user_message"],
                          f"{marca.capitalize()} ****{last4}", raw)


class YapeSandbox(PasarelaBase):
    proveedor = "yape"

    def validar(self, datos):
        if not re.fullmatch(r"9\d{8}", str(datos.get("celular") or "")):
            return "Ingrese un celular válido de 9 dígitos que empiece con 9"
        if not re.fullmatch(r"\d{6}", str(datos.get("otp") or "")):
            return "El código de aprobación de Yape tiene 6 dígitos"
        return None

    def cobrar(self, monto, datos, referencia):
        aprobado = datos["otp"] != "000000"
        celular = datos["celular"]
        codigo = _codigo("ype_test_", 16)
        raw = {
            "object": "charge",
            "id": codigo,
            "creation_date": _ahora_iso(),
            "amount": int(monto * 100),
            "currency_code": "PEN",
            "description": referencia,
            "source": {"type": "yape", "phone_number": f"{celular[:1]}*****{celular[-3:]}"},
            "outcome": (
                {"type": "venta_exitosa", "user_message": "Pago con Yape aprobado."}
                if aprobado else
                {"type": "codigo_invalido", "user_message": "El código de aprobación de Yape es inválido o venció."}
            ),
        }
        return _resultado(aprobado, codigo, raw["outcome"]["user_message"],
                          f"Yape {celular[:1]}*****{celular[-3:]}", raw)


class MercadoPagoSandbox(PasarelaBase):
    proveedor = "mercadopago"

    def validar(self, datos):
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", str(datos.get("email") or "")):
            return "Ingrese el correo de su cuenta de Mercado Pago"
        return None

    def cobrar(self, monto, datos, referencia):
        aprobado = "rechazo" not in datos["email"].lower()
        correo = datos["email"]
        oculto = correo[:2] + "***" + correo[correo.index("@"):]
        pago_id = secrets.randbelow(9 * 10**9) + 10**9
        codigo = f"mp_test_{pago_id}"
        raw = {
            "id": pago_id,
            "date_created": _ahora_iso(),
            "status": "approved" if aprobado else "rejected",
            "status_detail": "accredited" if aprobado else "cc_rejected_other_reason",
            "transaction_amount": float(monto),
            "currency_id": "PEN",
            "description": referencia,
            "payment_method_id": "account_money",
            "payer": {"email": oculto},
            "live_mode": False,
        }
        mensaje = "Pago acreditado en Mercado Pago." if aprobado else "Mercado Pago rechazó el pago."
        return _resultado(aprobado, codigo, mensaje, f"Mercado Pago {oculto}", raw)


def _reembolso_mp(self, codigo_cargo, monto, motivo):
    """Mercado Pago responde la devolución con un objeto refund propio."""
    ref_id = secrets.randbelow(9 * 10**9) + 10**9
    raw = {
        "id": ref_id,
        "payment_id": codigo_cargo.replace("mp_test_", ""),
        "amount": float(monto),
        "status": "approved",
        "date_created": _ahora_iso(),
        "reason": motivo,
    }
    return _resultado(True, f"mp_ref_test_{ref_id}", "Devolución acreditada en Mercado Pago", None, raw)


MercadoPagoSandbox.reembolsar = _reembolso_mp

PASARELAS = {p.proveedor: p() for p in (CulqiSandbox, YapeSandbox, MercadoPagoSandbox)}


def obtener_pasarela(proveedor: str) -> PasarelaBase | None:
    return PASARELAS.get((proveedor or "").lower())
