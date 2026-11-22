"""Testes do LLMOrchestrator com clientes falsos (nenhuma chamada real/paga de API)."""

import json
from types import SimpleNamespace

import pytest

from src.ai.llm_orchestrator import LLMOrchestrator

PLANO = {"steps": [{"action": "open", "description": "abrir navegador"}]}


class FakeAnthropic:
    """Imita o formato real: `content` é uma lista de blocos com `.text`."""

    def __init__(self, text):
        self.messages = SimpleNamespace(
            create=lambda **kw: SimpleNamespace(content=[SimpleNamespace(type="text", text=text)])
        )


@pytest.mark.asyncio
async def test_generate_plan_anthropic_parseia_blocos(monkeypatch):
    orq = LLMOrchestrator(primary_provider="anthropic", fallback_providers=[])
    monkeypatch.setattr(orq, "_get_client", lambda p: FakeAnthropic(json.dumps(PLANO)))
    plano = await orq.generate_plan("abrir navegador")
    assert plano == PLANO["steps"]


@pytest.mark.asyncio
async def test_fallback_para_proximo_provider(monkeypatch):
    orq = LLMOrchestrator(primary_provider="anthropic", fallback_providers=["openai"])

    def get_client(provider):
        if provider == "anthropic":
            raise ValueError("ANTHROPIC_API_KEY não definida")
        msg = SimpleNamespace(content="Resposta: " + json.dumps(PLANO))
        return SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(
                    create=lambda **kw: SimpleNamespace(choices=[SimpleNamespace(message=msg)])
                )
            )
        )

    monkeypatch.setattr(orq, "_get_client", get_client)
    assert await orq.generate_plan("x") == PLANO["steps"]
    assert orq.current_provider == "openai"


def test_parse_texto_sem_json_vira_passo_unico():
    orq = LLMOrchestrator()
    assert orq._parse_plan_response("faça X") == [{"action": "execute", "description": "faça X"}]


@pytest.mark.asyncio
async def test_todos_providers_falham(monkeypatch):
    orq = LLMOrchestrator(primary_provider="anthropic", fallback_providers=["ollama"])

    def boom(provider):
        raise RuntimeError("indisponível")

    monkeypatch.setattr(orq, "_get_client", boom)
    with pytest.raises(RuntimeError):
        await orq.generate_plan("x")
