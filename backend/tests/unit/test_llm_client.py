import io
import json

import pytest

from services import llm_client


class _Resp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_sin_api_key_no_hay_proveedor(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(llm_client.LLMNoDisponible):
        llm_client.completar("s", "u")


def test_groq_formato_openai(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test")
    enviado = {}

    def falso_urlopen(req, timeout):
        enviado["url"] = req.full_url
        enviado["body"] = json.loads(req.data)
        enviado["auth"] = req.get_header("Authorization")
        return _Resp(json.dumps({"choices": [{"message": {"content": " Hola [F1] "}}]}).encode())

    monkeypatch.setattr(llm_client.urllib.request, "urlopen", falso_urlopen)
    texto, prov = llm_client.completar("sistema", "pregunta")
    assert texto == "Hola [F1]"
    assert prov == "groq/llama-3.3-70b-versatile"
    assert enviado["url"].endswith("/openai/v1/chat/completions")
    assert enviado["auth"] == "Bearer gsk_test"
    assert enviado["body"]["messages"][0] == {"role": "system", "content": "sistema"}


def test_gemini(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "AIza_test")

    def falso_urlopen(req, timeout):
        return _Resp(json.dumps({"candidates": [{"content": {"parts": [{"text": "Ok"}]}}]}).encode())

    monkeypatch.setattr(llm_client.urllib.request, "urlopen", falso_urlopen)
    assert llm_client.completar("s", "u")[0] == "Ok"
