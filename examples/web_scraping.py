"""
Automation-Computer - Exemplo de Web Scraping
Este script demonstra como usar o WebAutomation para extrair dados.

Criado por Wellington de Lima Catarina
"""

import asyncio
from src.automation.web_automation import WebAutomation


async def main():
    """Exemplo de automação web com scraping."""
    print("=" * 60)
    print("  AUTOMATION-COMPUTER - Exemplo de Web Scraping")
    print("=" * 60)

    async with WebAutomation(headless=True) as browser:
        # Navegar para Wikipedia
        print("\n1. Navegando para Wikipedia...")
        await browser.navigate("https://pt.wikipedia.org/wiki/Python")

        # Tirar screenshot
        print("2. Tirando screenshot...")
        await browser.screenshot("screenshot_wiki.png")

        # Extrair título
        print("3. Extraindo título da página...")
        title = await browser.get_text("h1#firstHeading")
        print(f"   Título: {title}")

        # Extrair primeiro parágrafo
        print("4. Extraindo primeiro parágrafo...")
        intro = await browser.get_text("#mw-content-text p")
        print(f"   Introdução: {intro[:200]}...")

        # Extrair links da tabela de conteúdos
        print("5. Extraindo links da tabela de conteúdos...")
        links = await browser.extract_all("#toc a")
        print(f"   Encontrados {len(links)} links")
        for i, link in enumerate(links[:5]):
            print(f"   - {link.get('value', 'N/A')[:50]}")

        # Executar JavaScript
        print("6. Executando JavaScript...")
        word_count = await browser.evaluate("""
            document.body.innerText.split(/\s+/).length
        """)
        print(f"   Contagem aproximada de palavras: {word_count}")

    print("\nExemplo concluído!")
    print("Screenshot salva: screenshot_wiki.png")


if __name__ == "__main__":
    asyncio.run(main())