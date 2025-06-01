"""
Exemplo de uso do Agente de Automação Web.

Este script demonstra como usar a classe BrowserManager para automatizar tarefas web,
como navegar para um site, preencher um formulário e extrair dados.
"""

import asyncio
import json
import logging
from pathlib import Path

# Adiciona o diretório raiz ao path do Python
import sys
sys.path.append(str(Path(__file__).parent.parent.absolute()))

from src.automation.web.browser import BrowserManager

# Configuração básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('web_automation.log')
    ]
)

logger = logging.getLogger(__name__)

async def example_automation():
    """Exemplo de automação web."""
    # Configuração do navegador
    browser_config = {
        'headless': False,  # Altere para True para execução em modo headless
        'browser_type': 'chromium',  # Pode ser 'chromium', 'firefox' ou 'webkit'
        'viewport': {'width': 1280, 'height': 800},
        'downloads_path': 'downloads'
    }
    
    # Cria uma instância do gerenciador de navegador
    async with BrowserManager(**browser_config) as browser:
        try:
            # Exemplo 1: Navegação simples
            logger.info("Exemplo 1: Navegação simples")
            await browser.navigate("https://www.python.org")
            
            # Aguarda um momento para visualização
            await asyncio.sleep(2)
            
            # Exemplo 2: Extração de dados
            logger.info("Exemplo 2: Extração de dados")
            selectors = {
                'titulo': 'h1',
                'descricao': 'div.medium-widget p',
                'menu_itens': '#top ul.menu li a',
            }
            
            dados = await browser.extract_data(selectors)
            logger.info(f"Dados extraídos: {json.dumps(dados, indent=2, ensure_ascii=False)}")
            
            # Exemplo 3: Preenchimento de formulário (exemplo com Google)
            logger.info("Exemplo 3: Preenchimento de formulário")
            await browser.navigate("https://www.google.com")
            
            # Aceita cookies se necessário
            try:
                await browser.click("button:has-text('Aceito')")
            except:
                logger.debug("Nenhum aviso de cookies encontrado")
            
            # Preenche o campo de busca
            search_box = 'input[name="q"]'
            await browser.page.fill(search_box, "Automação Web com Python")
            
            # Submete o formulário pressionando Enter
            await browser.page.press(search_box, 'Enter')
            
            # Aguarda os resultados
            await browser.page.wait_for_selector('#search')
            
            # Extrai os títulos dos resultados
            results = await browser.page.query_selector_all('h3')
            logger.info("\nResultados da busca:")
            for i, result in enumerate(results[:5], 1):
                title = await result.text_content()
                logger.info(f"{i}. {title}")
            
            # Aguarda um momento para visualização
            await asyncio.sleep(3)
            
            logger.info("Exemplo concluído com sucesso!")
            
        except Exception as e:
            logger.error(f"Erro durante a execução: {str(e)}", exc_info=True)
            raise

if __name__ == "__main__":
    asyncio.run(example_automation())
