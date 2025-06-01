"""
Módulo de automação web do Agente de Automação.
Gerencia a interação com navegadores web de forma automatizada.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from playwright.async_api import (
    Browser,
    BrowserContext,
    BrowserType,
    Page,
    Playwright,
    async_playwright,
)

from src.config import settings

logger = logging.getLogger(__name__)


class WebAutomationError(Exception):
    """Exceção para erros de automação web."""
    pass


class BrowserManager:
    """Gerenciador de navegador para automação web."""
    
    def __init__(
        self,
        headless: Optional[bool] = None,
        browser_type: str = "chromium",
        viewport: Optional[Dict[str, int]] = None,
        user_agent: Optional[str] = None,
        downloads_path: Optional[Union[str, Path]] = None,
    ):
        """Inicializa o gerenciador de navegador.
        
        Args:
            headless: Se True, executa em modo headless.
            browser_type: Tipo de navegador ('chromium', 'firefox', 'webkit').
            viewport: Dimensões da janela do navegador. Ex: {"width": 1280, "height": 800}
            user_agent: User agent personalizado.
            downloads_path: Diretório para downloads.
        """
        self.headless = headless if headless is not None else settings.HEADLESS
        self.browser_type = browser_type.lower()
        self.viewport = viewport or {"width": settings.WINDOW_WIDTH, "height": settings.WINDOW_HEIGHT}
        self.user_agent = user_agent
        self.downloads_path = Path(downloads_path) if downloads_path else Path.cwd() / "downloads"
        
        # Garante que o diretório de downloads existe
        self.downloads_path.mkdir(parents=True, exist_ok=True)
        
        # Atributos de instância
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    async def start(self) -> None:
        """Inicializa o navegador e configura o ambiente."""
        try:
            self.playwright = await async_playwright().start()
            
            # Seleciona o tipo de navegador
            browser_launcher = getattr(self.playwright, self.browser_type, None)
            if not browser_launcher:
                raise WebAutomationError(f"Navegador não suportado: {self.browser_type}")
            
            # Lança o navegador
            self.browser = await browser_launcher.launch(
                headless=self.headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-infobars",
                    "--start-maximized",
                ],
            )
            
            # Cria um novo contexto
            self.context = await self.browser.new_context(
                viewport=self.viewport,
                user_agent=self.user_agent,
                accept_downloads=True,
                downloads_path=str(self.downloads_path.absolute()),
            )
            
            # Adiciona injeção para evitar detecção de automação
            await self.context.add_init_script(
                """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                """
            )
            
            # Cria uma nova página
            self.page = await self.context.new_page()
            
            logger.info(f"Navegador {self.browser_type} inicializado com sucesso")
            
        except Exception as e:
            logger.error(f"Falha ao inicializar o navegador: {str(e)}")
            await self.close()
            raise WebAutomationError(f"Falha ao inicializar o navegador: {str(e)}")
    
    async def navigate(self, url: str, wait_until: str = "load") -> None:
        """Navega para uma URL.
        
        Args:
            url: URL para navegar.
            wait_until: Quando considerar a navegação concluída.
                      Pode ser 'load', 'domcontentloaded', 'networkidle'.
        """
        if not self.page:
            raise WebAutomationError("Página não inicializada. Chame start() primeiro.")
        
        try:
            logger.info(f"Navegando para: {url}")
            await self.page.goto(url, wait_until=wait_until)
            logger.info(f"Página carregada: {self.page.title()}")
        except Exception as e:
            logger.error(f"Erro ao navegar para {url}: {str(e)}")
            raise WebAutomationError(f"Falha ao navegar para {url}: {str(e)}")
    
    async def fill_form(self, selector: str, data: Dict[str, str]) -> None:
        """Preenche um formulário.
        
        Args:
            selector: Seletor CSS do formulário.
            data: Dicionário com os campos e valores a preencher.
        """
        if not self.page:
            raise WebAutomationError("Página não inicializada. Chame start() primeiro.")
        
        try:
            for field, value in data.items():
                field_selector = f"{selector} [name='{field}']"
                await self.page.fill(field_selector, str(value))
                logger.debug(f"Campo preenchido: {field} = {value}")
        except Exception as e:
            logger.error(f"Erro ao preencher formulário: {str(e)}")
            raise WebAutomationError(f"Falha ao preencher formulário: {str(e)}")
    
    async def click(self, selector: str, wait_for_navigation: bool = False) -> None:
        """Clica em um elemento.
        
        Args:
            selector: Seletor CSS do elemento.
            wait_for_navigation: Se True, aguarda a navegação após o clique.
        """
        if not self.page:
            raise WebAutomationError("Página não inicializada. Chame start() primeiro.")
        
        try:
            if wait_for_navigation:
                async with self.page.expect_navigation():
                    await self.page.click(selector)
            else:
                await self.page.click(selector)
            logger.debug(f"Clicado no elemento: {selector}")
        except Exception as e:
            logger.error(f"Erro ao clicar no elemento {selector}: {str(e)}")
            raise WebAutomationError(f"Falha ao clicar no elemento {selector}: {str(e)}")
    
    async def extract_data(self, selectors: Dict[str, str]) -> Dict[str, Any]:
        """Extrai dados da página usando seletores CSS.
        
        Args:
            selectors: Dicionário com nomes de campos e seletores CSS.
            
        Returns:
            Dicionário com os dados extraídos.
        """
        if not self.page:
            raise WebAutomationError("Página não inicializada. Chame start() primeiro.")
        
        result = {}
        
        for field, selector in selectors.items():
            try:
                if await self.page.query_selector(selector):
                    # Tenta extrair texto, valor ou atributo
                    text = await self.page.text_content(selector)
                    value = await self.page.get_attribute(selector, "value")
                    
                    result[field] = text.strip() if text else (value.strip() if value else "")
                else:
                    result[field] = None
            except Exception as e:
                logger.warning(f"Erro ao extrair dados do seletor {selector}: {str(e)}")
                result[field] = None
        
        return result
    
    async def close(self) -> None:
        """Fecha o navegador e libera recursos."""
        try:
            if self.context:
                await self.context.close()
                self.context = None
            
            if self.browser:
                await self.browser.close()
                self.browser = None
            
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
                
            logger.info("Navegador fechado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao fechar o navegador: {str(e)}")
            raise WebAutomationError(f"Falha ao fechar o navegador: {str(e)}")
    
    async def __aenter__(self):
        """Suporte ao gerenciador de contexto assíncrono."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Garante que o navegador seja fechado ao sair do contexto."""
        await self.close()


# Função de conveniência para criar uma instância do gerenciador de navegador
async def create_browser(
    headless: Optional[bool] = None,
    browser_type: str = "chromium",
    **kwargs
) -> BrowserManager:
    """Cria e inicializa uma instância do gerenciador de navegador.
    
    Args:
        headless: Se True, executa em modo headless.
        browser_type: Tipo de navegador ('chromium', 'firefox', 'webkit').
        **kwargs: Argumentos adicionais para o BrowserManager.
        
    Returns:
        Instância inicializada do BrowserManager.
    """
    browser = BrowserManager(headless=headless, browser_type=browser_type, **kwargs)
    await browser.start()
    return browser
