"""Local-only Ollama client. Prompts are sent only to the loopback interface."""
from __future__ import annotations

import requests

BASE_URL = "http://127.0.0.1:11434"
CONNECT_TIMEOUT = 3
GENERATE_TIMEOUT = 120
MAX_RESPONSE_BYTES = 1_000_000


class OllamaError(RuntimeError):
    pass


def _request(method: str, path: str, **kwargs):
    url = f"{BASE_URL}{path}"
    try:
        with requests.Session() as session:
            session.trust_env = False
            response = session.request(
                method, url, timeout=(CONNECT_TIMEOUT, GENERATE_TIMEOUT),
                allow_redirects=False, **kwargs
            )
            response.raise_for_status()
            if len(response.content) > MAX_RESPONSE_BYTES:
                raise OllamaError("Risposta Ollama oltre il limite consentito")
            return response.json()
    except requests.RequestException as exc:
        raise OllamaError(
            "Ollama non raggiungibile su 127.0.0.1:11434. "
            "Verificare che Ollama sia installato e in esecuzione."
        ) from exc
    except ValueError as exc:
        raise OllamaError("Ollama ha restituito una risposta JSON non valida") from exc


def list_models() -> list[str]:
    payload = _request("GET", "/api/tags")
    models = payload.get("models", [])
    return sorted(
        str(item.get("name", "")) for item in models
        if isinstance(item, dict) and item.get("name")
    )


def generate_response(model: str, prompt: str) -> str:
    model = model.strip()
    prompt = prompt.strip()
    if not model or len(model) > 128:
        raise ValueError("Selezionare un modello Ollama valido")
    if not prompt or len(prompt) > 20_000:
        raise ValueError("Il prompt deve contenere da 1 a 20.000 caratteri")
    payload = _request(
        "POST", "/api/generate",
        json={"model": model, "prompt": prompt, "stream": False,
              "options": {"temperature": 0.2}},
    )
    response = payload.get("response")
    if not isinstance(response, str):
        raise OllamaError("La risposta del modello non contiene testo")
    return response
