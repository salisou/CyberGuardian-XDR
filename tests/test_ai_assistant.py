import pytest

from modules.ai_assistant import ollama_client


def test_list_models(monkeypatch):
    monkeypatch.setattr(ollama_client, "_request", lambda *args, **kwargs: {
        "models": [{"name": "llama3.2"}, {"name": "qwen2.5"}]
    })
    assert ollama_client.list_models() == ["llama3.2", "qwen2.5"]


def test_generate_response(monkeypatch):
    monkeypatch.setattr(ollama_client, "_request", lambda *args, **kwargs: {"response": "Analisi completata"})
    assert ollama_client.generate_response("llama3.2", "Analizza questo alert") == "Analisi completata"


@pytest.mark.parametrize("model,prompt", [("", "test"), ("model", ""), ("model", "x" * 20001)])
def test_generate_rejects_invalid_input(model, prompt):
    with pytest.raises(ValueError):
        ollama_client.generate_response(model, prompt)
