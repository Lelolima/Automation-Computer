"""
Automation-Computer - Módulo de Automação Web
Automação web de alta performance usando Playwright

Criado por Wellington de Lima Catarina
"""

from typing import Optional, Dict, Any, List
import logging

from playwright.async_api import async_playwright, Page, Browser, BrowserContext

logger = logging.getLogger(__name__)


class WebAutomation:
    """Automação web assíncrona usando Playwright."""

    def __init__(
        self,
        headless: bool = True,
        browser_type: str = "chromium",
        slow_mo: int = 0
    ):
        """
        Inicializa a automação web.

        Args:
            headless: Executar em modo headless
            browser_type: 'chromium', 'firefox' ou 'webkit'
            slow_mo: Atraso em ms para debugging
        """
        self.headless = headless
        self.browser_type = browser_type
        self.slow_mo = slow_mo
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        logger.info(f"WebAutomation inicializado (headless={headless}, browser={browser_type})")

    async def __aenter__(self):
        """Context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.close()

    async def start(self) -> None:
        """Inicia o browser."""
        try:
            self.playwright = await async_playwright().start()

            browser_launcher = getattr(self.playwright, self.browser_type)
            self.browser = await browser_launcher.launch(
                headless=self.headless,
                slow_mo=self.slow_mo
            )

            self.context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )

            self.page = await self.context.new_page()
            logger.info("Browser iniciado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao iniciar browser: {e}")
            raise

    async def close(self) -> None:
        """Fecha o browser e limpa recursos."""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("Browser fechado")
        except Exception as e:
            logger.error(f"Erro ao fechar browser: {e}")

    async def navigate(self, url: str, wait_until: str = "domcontentloaded") -> None:
        """
        Navega para uma URL.

        Args:
            url: URL para navegar
            wait_until: 'load', 'domcontentloaded', 'networkidle', 'commit'
        """
        try:
            await self.page.goto(url, wait_until=wait_until)
            logger.info(f"Navegado para: {url}")
        except Exception as e:
            logger.error(f"Erro ao navegar: {e}")
            raise

    async def click(self, selector: str, timeout: int = 30000) -> None:
        """
        Clica em um elemento.

        Args:
            selector: CSS selector ou XPath
            timeout: Timeout em ms
        """
        try:
            await self.page.click(selector, timeout=timeout)
            logger.debug(f"Click em: {selector}")
        except Exception as e:
            logger.error(f"Erro ao clicar: {e}")
            raise

    async def fill(self, selector: str, value: str) -> None:
        """
        Preenche um campo de input.

        Args:
            selector: CSS selector ou XPath
            value: Valor para preencher
        """
        try:
            await self.page.fill(selector, value)
            logger.debug(f"Preenchido {selector} com valor")
        except Exception as e:
            logger.error(f"Erro ao preencher: {e}")
            raise

    async def type_text(self, selector: str, text: str, delay: int = 50) -> None:
        """
        Digita texto caractere por caractere (útil para CAPTCHAs).

        Args:
            selector: CSS selector
            text: Texto para digitar
            delay: Delay entre caracteres em ms
        """
        try:
            await self.page.type(selector, text, delay=delay)
            logger.debug(f"Texto digitado em {selector}")
        except Exception as e:
            logger.error(f"Erro ao digitar: {e}")
            raise

    async def get_text(self, selector: str) -> str:
        """
        Obtém o texto de um elemento.

        Args:
            selector: CSS selector

        Returns:
            Texto do elemento
        """
        try:
            return await self.page.text_content(selector)
        except Exception as e:
            logger.error(f"Erro ao obter texto: {e}")
            raise

    async def get_html(self) -> str:
        """Obtém o HTML completo da página."""
        try:
            return await self.page.content()
        except Exception as e:
            logger.error(f"Erro ao obter HTML: {e}")
            raise

    async def extract_data(self, selector: str, attribute: Optional[str] = None) -> str:
        """
        Extrai dados de um elemento.

        Args:
            selector: CSS selector
            attribute: Atributo para extrair (None = texto)

        Returns:
            Dado extraído ou string vazia se elemento não encontrado
        """
        try:
            element = await self.page.query_selector(selector)
            if element is None:
                logger.warning(f"Elemento não encontrado: {selector}")
                return ""
            if attribute:
                return await element.get_attribute(attribute)
            return await element.text_content()
        except Exception as e:
            logger.error(f"Erro ao extrair dados: {e}")
            raise

    async def extract_all(self, selector: str, attribute: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Extrai dados de múltiplos elementos.

        Args:
            selector: CSS selector
            attribute: Atributo para extrair

        Returns:
            Lista de dados
        """
        try:
            elements = await self.page.query_selector_all(selector)
            results = []

            for elem in elements:
                if attribute:
                    value = await elem.get_attribute(attribute)
                else:
                    value = await elem.text_content()
                results.append({"value": value})

            logger.info(f"Extraídos {len(results)} elementos")
            return results
        except Exception as e:
            logger.error(f"Erro ao extrair múltiplos: {e}")
            raise

    async def screenshot(self, path: str, full_page: bool = False) -> None:
        """
        Tira um screenshot.

        Args:
            path: Caminho para salvar
            full_page: Screenshot de toda a página
        """
        try:
            await self.page.screenshot(path=path, full_page=full_page)
            logger.info(f"Screenshot salvo em: {path}")
        except Exception as e:
            logger.error(f"Erro ao tirar screenshot: {e}")
            raise

    async def wait_for_selector(self, selector: str, timeout: int = 30000, state: str = "visible") -> None:
        """
        Aguarda por um selector.

        Args:
            selector: CSS selector
            timeout: Timeout em ms
            state: 'visible', 'hidden', 'attached', 'detached'
        """
        try:
            await self.page.wait_for_selector(selector, timeout=timeout, state=state)
            logger.debug(f"Selector aguardado: {selector}")
        except Exception as e:
            logger.error(f"Erro ao aguardar selector: {e}")
            raise

    async def wait_for_navigation(self, timeout: int = 30000) -> None:
        """Aguarda navegação."""
        try:
            await self.page.wait_for_load_state(timeout=timeout)
        except Exception as e:
            logger.error(f"Erro ao aguardar navegação: {e}")
            raise

    async def evaluate(self, script: str) -> Any:
        """
        Executa JavaScript na página.

        Args:
            script: Código JavaScript

        Returns:
            Resultado da avaliação
        """
        try:
            result = await self.page.evaluate(script)
            logger.debug(f"JavaScript executado: {script[:50]}...")
            return result
        except Exception as e:
            logger.error(f"Erro ao avaliar JS: {e}")
            raise

    async def set_cookies(self, cookies: List[Dict]) -> None:
        """Define cookies."""
        try:
            await self.context.add_cookies(cookies)
            logger.info(f"{len(cookies)} cookies definidos")
        except Exception as e:
            logger.error(f"Erro ao definir cookies: {e}")
            raise

    async def get_cookies(self) -> List[Dict]:
        """Obtém cookies da página atual."""
        try:
            return await self.context.cookies()
        except Exception as e:
            logger.error(f"Erro ao obter cookies: {e}")
            raise

    async def press_key(self, key: str) -> None:
        """Pressiona uma tecla."""
        try:
            await self.page.keyboard.press(key)
            logger.debug(f"Tecla pressionada: {key}")
        except Exception as e:
            logger.error(f"Erro ao pressionar tecla: {e}")
            raise