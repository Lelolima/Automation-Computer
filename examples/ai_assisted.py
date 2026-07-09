"""
Automation-Computer - Exemplo de IA Assistida
Este script demonstra como usar o LLMOrchestrator para gerar planos.

Criado por Wellington de Lima Catarina
"""

import asyncio
from src.ai.llm_orchestrator import LLMOrchestrator


async def main():
    """Exemplo de geração de plano com IA."""
    print("=" * 60)
    print("  AUTOMATION-COMPUTER - Exemplo de IA Assistida")
    print("=" * 60)

    # Inicializar orquestrador
    llm = LLMOrchestrator(
        primary_provider="ollama",  # Fallback local primeiro
        fallback_providers=["ollama"]
    )

    # Tarefa em linguagem natural
    tarefa = """
    Abra o navegador, acesse o site example.com,
    extraia o título da página e salve em um arquivo de texto.
    """

    print(f"\nTarefa: {tarefa.strip()}")
    print("\nGerando plano de execução...")

    try:
        plano = await llm.generate_plan(tarefa, max_steps=5)

        print("\n Plano Gerado:")
        print("-" * 40)
        for i, passo in enumerate(plano, 1):
            acao = passo.get("action", "desconhecido")
            descricao = passo.get("description", "sem descrição")
            print(f"  {i}. {acao}: {descricao}")
        print("-" * 40)

        # Exemplo de chat
        print("\n Perguntando ao LLM...")
        resposta = await llm.chat(
            "Qual a melhor forma de fazer web scraping em Python?"
        )
        print(f"\n Resposta do LLM:\n {resposta[:300]}...")

    except Exception as e:
        print(f"Erro (esperado se Ollama não estiver instalado): {e}")
        print("\nDica: Instale o Ollama em https://ollama.ai")

    print("\nExemplo concluído!")


if __name__ == "__main__":
    asyncio.run(main())