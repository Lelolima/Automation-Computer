"""
Automation-Computer - Módulo de IA
Orquestração de LLMs, visão computacional e motor de decisão

Criado por Wellington de Lima Catarina
"""

import logging
from typing import Optional, Dict, Any, List
import os
import json

logger = logging.getLogger(__name__)

# Modelos configurados (podem ser sobrescritos via env)
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

# Lazy imports para evitar erros se pacotes não instalados


class LLMOrchestrator:
    """
    Orquestrador de LLMs com suporte a múltiplos providers
    e fallback automático.
    """

    def __init__(
        self,
        primary_provider: str = "anthropic",
        fallback_providers: Optional[List[str]] = None,
        local_model: Optional[str] = None
    ):
        """
        Inicializa o orquestrador.

        Args:
            primary_provider: Provider primário ('anthropic', 'openai', 'ollama')
            fallback_providers: Lista de providers em ordem de fallback
            local_model: Modelo local para fallback offline (usa OLLAMA_MODEL env se None)
        """
        self.primary_provider = primary_provider
        self.fallback_providers = fallback_providers or ["ollama"]
        self.local_model = local_model or OLLAMA_MODEL
        self.current_provider = None
        self._client = None
        logger.info(f"LLMOrchestrator inicializado: primary={primary_provider}")

    def _get_anthropic_client(self):
        """Obtém cliente Anthropic/Claude."""
        try:
            from anthropic import Anthropic
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY não definida")
            return Anthropic(api_key=api_key)
        except ImportError:
            logger.error("anthropic não instalado")
            raise
        except Exception as e:
            logger.error(f"Erro Anthropic: {e}")
            raise

    def _get_openai_client(self):
        """Obtém cliente OpenAI."""
        try:
            from openai import OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY não definida")
            return OpenAI(api_key=api_key)
        except ImportError:
            logger.error("openai não instalado")
            raise
        except Exception as e:
            logger.error(f"Erro OpenAI: {e}")
            raise

    def _get_ollama_client(self):
        """Obtém cliente Ollama (local)."""
        try:
            import ollama
            # Testa conexão
            ollama.list()
            return ollama
        except ImportError:
            logger.error("ollama não instalado")
            raise
        except Exception as e:
            logger.error(f"Erro Ollama: {e}")
            raise

    def _get_client(self, provider: str):
        """Obtém cliente para um provider específico."""
        if provider == "anthropic":
            return self._get_anthropic_client()
        elif provider == "openai":
            return self._get_openai_client()
        elif provider == "ollama":
            return self._get_ollama_client()
        else:
            raise ValueError(f"Provider desconhecido: {provider}")

    async def generate_plan(
        self,
        task: str,
        context: Optional[str] = None,
        max_steps: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Gera um plano de execução para uma tarefa.

        Args:
            task: Descrição da tarefa em linguagem natural
            context: Contexto adicional
            max_steps: Número máximo de passos

        Returns:
            Lista de passos do plano
        """
        providers_to_try = [self.primary_provider] + self.fallback_providers

        for provider in providers_to_try:
            try:
                logger.info(f"Tentando gerar plano com {provider}")
                plan = await self._generate_plan_with_provider(provider, task, context, max_steps)
                self.current_provider = provider
                logger.info(f"Plano gerado com {provider}")
                return plan
            except Exception as e:
                logger.warning(f"Falha com {provider}: {e}")
                continue

        raise RuntimeError("Todos os providers falharam ao gerar plano")

    async def _generate_plan_with_provider(
        self,
        provider: str,
        task: str,
        context: Optional[str],
        max_steps: int
    ) -> List[Dict[str, Any]]:
        """Gera plano usando um provider específico."""
        prompt = f"""
Tarefa: {task}
{f'Contexto: {context}' if context else ''}

Gere um plano de execução com máximo de {max_steps} passos.
Formato JSON: {{"steps": [{{"action": "...", "description": "..."}}]}}
"""

        if provider == "anthropic":
            client = self._get_client(provider)
            response = client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )
            # Parse da resposta (simplificado)
            return self._parse_plan_response(response.content)

        elif provider == "openai":
            client = self._get_client(provider)
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            return self._parse_plan_response(response.choices[0].message.content)

        elif provider == "ollama":
            client = self._get_client(provider)
            response = client.chat(
                model=self.local_model,
                messages=[{"role": "user", "content": prompt}]
            )
            return self._parse_plan_response(response['message']['content'])

        return []

    def _parse_plan_response(self, content: str) -> List[Dict[str, Any]]:
        """Parse da resposta de plano (simplificado)."""
        try:
            # Tenta extrair JSON da resposta
            if "{" in content:
                start = content.index("{")
                end = content.rindex("}") + 1
                data = json.loads(content[start:end])
                return data.get("steps", [])
        except Exception as e:
            logger.error(f"Erro ao parsear plano: {e}")

        # Fallback: cria passo único
        return [{"action": "execute", "description": content[:500]}]

    async def chat(
        self,
        message: str,
        system: Optional[str] = None,
        conversation: Optional[List[Dict]] = None
    ) -> str:
        """
        Chat genérico com LLM.

        Args:
            message: Mensagem do usuário
            system: Instrução de sistema
            conversation: Histórico de conversa

        Returns:
            Resposta do LLM
        """
        providers_to_try = [self.primary_provider] + self.fallback_providers

        for provider in providers_to_try:
            try:
                return await self._chat_with_provider(provider, message, system, conversation)
            except Exception as e:
                logger.warning(f"Falha com {provider}: {e}")
                continue

        raise RuntimeError("Todos os providers falharam")

    async def _chat_with_provider(
        self,
        provider: str,
        message: str,
        system: Optional[str],
        conversation: Optional[List[Dict]]
    ) -> str:
        """Chat usando provider específico."""
        messages = []

        if system:
            if provider == "anthropic":
                # Anthropic usa system separado
                pass
            else:
                messages.append({"role": "system", "content": system})

        if conversation:
            messages.extend(conversation)

        messages.append({"role": "user", "content": message})

        if provider == "anthropic":
            client = self._get_client(provider)
            kwargs = {}
            if system:
                kwargs["system"] = system
            response = client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=4096,
                messages=messages,
                **kwargs
            )
            return response.content[0].text

        elif provider == "openai":
            client = self._get_client(provider)
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages
            )
            return response.choices[0].message.content

        elif provider == "ollama":
            client = self._get_client(provider)
            response = client.chat(
                model=self.local_model,
                messages=messages
            )
            return response['message']['content']

        return ""