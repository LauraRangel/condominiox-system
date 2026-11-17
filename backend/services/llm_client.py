"""Cliente LLM intercambiable (Groq o Gemini) usando solo la librería estándar.

Variables de entorno:
  LLM_PROVIDER  groq (por defecto) | gemini | none
  GROQ_API_KEY / GEMINI_API_KEY
  LLM_MODEL     opcional (groq: llama-3.3-70b-versatile, gemini: gemini-2.5-flash)
  LLM_TIMEOUT   segundos (por defecto 12)
"""

import json
import os
import urllib.error
import urllib.request

_DEFAULT_MODELS = {"groq": "llama-3.3-70b-versatile", "gemini": "gemini-2.5-flash"}


class LLMNoDisponible(Exception):
    pass


def proveedor_configurado() -> str | None:
    prov = (os.getenv("LLM_PROVIDER") or "groq").strip().lower()
    if prov == "groq" and os.getenv("GROQ_API_KEY"):
        return "groq"
    if prov == "gemini" and os.getenv("GEMINI_API_KEY"):
        return "gemini"
    return None


def _post_json(url, payload, headers):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "CondominioX/5.1", **headers},
        method="POST",
    )
    timeout = float(os.getenv("LLM_TIMEOUT", "12"))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise LLMNoDisponible(f"HTTP {e.code}") from e
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        raise LLMNoDisponible(str(e)) from e


def completar(system: str, user: str) -> tuple[str, str]:
    """Devuelve (texto, 'proveedor/modelo'). Lanza LLMNoDisponible si no hay proveedor o falla."""
    prov = proveedor_configurado()
    if not prov:
        raise LLMNoDisponible("Sin proveedor LLM configurado")
    modelo = os.getenv("LLM_MODEL") or _DEFAULT_MODELS[prov]

    if prov == "groq":
        data = _post_json(
            "https://api.groq.com/openai/v1/chat/completions",
            {
                "model": modelo,
                "temperature": 0.2,
                "max_tokens": 450,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            },
            {"Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}"},
        )
        try:
            texto = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            raise LLMNoDisponible("Respuesta inesperada de Groq") from e
    else:
        data = _post_json(
            f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent",
            {
                "systemInstruction": {"parts": [{"text": system}]},
                "contents": [{"role": "user", "parts": [{"text": user}]}],
                "generationConfig": {"temperature": 0.2, "maxOutputTokens": 450},
            },
            {"x-goog-api-key": os.getenv("GEMINI_API_KEY")},
        )
        try:
            texto = "".join(p.get("text", "") for p in data["candidates"][0]["content"]["parts"])
        except (KeyError, IndexError) as e:
            raise LLMNoDisponible("Respuesta inesperada de Gemini") from e

    return texto.strip(), f"{prov}/{modelo}"
