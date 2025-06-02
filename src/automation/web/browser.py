# NOME_DO_ARQUIVO.py: browser.py
# Descrição: Módulo de automação web do Agente de Automação. Gerencia a interação com navegadores web de forma automatizada.
# Responsabilidades: Inicializar e controlar instâncias de navegadores (Chromium, Firefox, Webkit) usando Playwright, navegar para URLs, preencher formulários, clicar em elementos, extrair dados e gerenciar o ciclo de vida do navegador.
# Dependências: logging, pathlib, typing, playwright, src.config.
# Padrões aplicados: Programação Orientada a Objetos, Async/Await para operações assíncronas, Gerenciador de Contexto Assíncrono (`__aenter__`, `__aexit__`), Tratamento de exceções.
# Autor: Autor Original Desconhecido
# Última modificação: 2024-07-26

"""
Módulo de automação web do Agente de Automação.
Gerencia a interação com navegadores web de forma automatizada.
"""

# RACIOCÍNIO: Playwright foi escolhido por sua API moderna, suporte a múltiplos navegadores (Chromium, Firefox, WebKit),
# capacidade de automação robusta (incluindo espera automática, interceptação de rede) e bom suporte a operações assíncronas.
# Alternativas como Selenium são mais antigas e podem ter APIs menos consistentes ou mais complexas para certas tarefas.

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

# ESTRATÉGIA: Definir uma exceção personalizada para erros específicos de automação web.
# Isso permite um tratamento de erro mais granular e específico do domínio da automação web.
class WebAutomationError(Exception):
    """Exceção para erros de automação web."""
    pass

# ESTRATÉGIA: Encapsular a lógica de gerenciamento do navegador em uma classe.
# Isso promove a reutilização, organização e facilita o gerenciamento do ciclo de vida do navegador.
class BrowserManager:
    """Gerenciador de navegador para automação web."""
    
    def __init__(
        self,
        headless: Optional[bool] = None, # RACIOCÍNIO: Modo headless é essencial para execução em servidores ou em background. None permite que seja definido por settings.
        browser_type: str = "chromium",  # DECISÃO: Chromium como padrão por ser amplamente utilizado e ter bom suporte. Playwright também suporta 'firefox' e 'webkit'.
        viewport: Optional[Dict[str, int]] = None, # RACIOCÍNIO: Definir o viewport garante consistência no layout da página, útil para testes visuais e seletores.
        user_agent: Optional[str] = None, # RACIOCÍNIO: Mudar o user agent pode ser necessário para simular diferentes dispositivos ou evitar detecção de bot.
        downloads_path: Optional[Union[str, Path]] = None, # RACIOCÍNIO: Especificar um diretório de downloads é importante para automações que baixam arquivos.
    ):
        """Inicializa o gerenciador de navegador.
        
        Args:
            headless: Se True, executa em modo headless. (Controla a visibilidade da UI do navegador)
            browser_type: Tipo de navegador ('chromium', 'firefox', 'webkit').
            viewport: Dimensões da janela do navegador. Ex: {"width": 1280, "height": 800}.
            user_agent: User agent personalizado.
            downloads_path: Diretório para salvar arquivos baixados.
        """
        # LÓGICA: Priorizar o valor passado no construtor. Se None, usar o valor das configurações globais (`settings`).
        self.headless = headless if headless is not None else settings.HEADLESS
        # DECISÃO: Converter `browser_type` para minúsculas para consistência interna.
        self.browser_type = browser_type.lower()
        # LÓGICA: Similar ao headless, usar viewport das settings se não especificado.
        self.viewport = viewport or {"width": settings.WINDOW_WIDTH, "height": settings.WINDOW_HEIGHT}
        self.user_agent = user_agent # Se None, Playwright usará o user agent padrão do navegador.
        # LÓGICA: Se `downloads_path` não for fornecido, criar uma pasta "downloads" no diretório de trabalho atual.
        # ESTRATÉGIA: Usar `pathlib.Path` para manipulação de caminhos de forma robusta e multiplataforma.
        self.downloads_path = Path(downloads_path) if downloads_path else Path.cwd() / "downloads"
        
        # RACIOCÍNIO: É crucial que o diretório de downloads exista antes de o navegador tentar usá-lo.
        # LÓGICA: `mkdir(parents=True, exist_ok=True)` cria o diretório e quaisquer pais necessários,
        # e não levanta erro se o diretório já existir.
        self.downloads_path.mkdir(parents=True, exist_ok=True)
        
        # Atributos de instância para Playwright, Browser, Context e Page.
        # RACIOCÍNIO: Serão inicializados no método `start()`. Declarar aqui com `Optional` e valor inicial None
        # ajuda no type hinting e clareza sobre o estado da instância.
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None # A instância do navegador (ex: Chromium).
        self.context: Optional[BrowserContext] = None # Um contexto de navegação isolado (similar a um perfil de navegador).
        self.page: Optional[Page] = None # Uma aba (página) dentro do contexto.
    
    async def start(self) -> None:
        """Inicializa o Playwright, lança o navegador, cria um contexto e uma página."""
        try:
            # RACIOCÍNIO: `async_playwright().start()` inicializa o Playwright.
            # É necessário chamá-lo antes de qualquer operação do Playwright.
            self.playwright = await async_playwright().start()
            
            # LÓGICA: Selecionar dinamicamente o método de lançamento do navegador (chromium, firefox, webkit)
            # com base em `self.browser_type`. `getattr` permite isso de forma elegante.
            browser_launcher: Optional[BrowserType] = getattr(self.playwright, self.browser_type, None)
            if not browser_launcher:
                # VALIDAÇÃO: Garantir que o tipo de navegador é suportado.
                raise WebAutomationError(f"Navegador não suportado: {self.browser_type}")
            
            # RACIOCÍNIO: Lançar o navegador com configurações específicas.
            # `args` são passados para o executável do navegador.
            launch_args = [
                # ESTRATÉGIA: Tentar evitar detecção de automação.
                # `--disable-blink-features=AutomationControlled` remove alguns indicadores de que o navegador está sendo controlado por software.
                "--disable-blink-features=AutomationControlled",
                # ESTRATÉGIA: `--disable-infobars` remove barras de informação como "O Chrome está sendo controlado por software automatizado".
                "--disable-infobars",
                # DECISÃO: `--start-maximized` inicia o navegador maximizado para consistência,
                # embora o `viewport` seja a forma mais precisa de controlar o tamanho da área de renderização.
                "--start-maximized",
            ]
            self.browser = await browser_launcher.launch(
                headless=self.headless,
                args=launch_args,
            )
            
            # RACIOCÍNIO: Um contexto de navegador isola sessões de navegação (cookies, localStorage, etc.).
            # É uma boa prática usar um novo contexto para cada sessão de automação independente.
            # DECISÃO: Configurar viewport, user_agent e caminho de downloads no nível do contexto.
            # `accept_downloads=True` é crucial para permitir que o navegador baixe arquivos.
            self.context = await self.browser.new_context(
                viewport=self.viewport,
                user_agent=self.user_agent,
                accept_downloads=True,
                downloads_path=str(self.downloads_path.absolute()), # Playwright espera uma string para o caminho.
            )
            
            # ESTRATÉGIA: Script de inicialização para modificar o ambiente JavaScript da página antes de qualquer script da página rodar.
            # RACIOCÍNIO: Para evitar a detecção por alguns sites de que a automação está em controle,
            # é útil sobrescrever a propriedade `navigator.webdriver`.
            # LÓGICA: Definir `navigator.webdriver` como `undefined` é uma tática comum.
            await self.context.add_init_script(
                """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                """
            )
            
            # RACIOCÍNIO: Uma página (aba) é necessária para interagir com conteúdo web.
            self.page = await self.context.new_page()
            
            logger.info(f"Navegador {self.browser_type} inicializado com sucesso")
            
        except Exception as e:
            # ESTRATÉGIA: Em caso de falha na inicialização, registrar o erro,
            # tentar fechar quaisquer recursos que possam ter sido parcialmente abertos,
            # e levantar a exceção personalizada `WebAutomationError`.
            logger.error(f"Falha ao inicializar o navegador: {str(e)}")
            await self.close() # Tenta limpar o que foi aberto.
            raise WebAutomationError(f"Falha ao inicializar o navegador: {str(e)}")
    
    async def navigate(self, url: str, wait_until: str = "load") -> None:
        """Navega para uma URL específica.
        
        Args:
            url: A URL para a qual navegar.
            wait_until: Estratégia de espera para a navegação.
                        # RACIOCÍNIO: Diferentes estratégias de `wait_until` são úteis para diferentes cenários:
                        # 'load': Espera pelo evento 'load' da página. (Padrão do Playwright para page.goto)
                        # 'domcontentloaded': Espera pelo evento 'DOMContentLoaded'. Mais rápido, mas pode não ter todos os recursos (imagens, CSS) carregados.
                        # 'networkidle': Espera até que não haja mais atividade de rede por um certo período. Útil para SPAs (Single Page Applications).
                        # DECISÃO: 'load' como padrão é um bom equilíbrio, mas permitir a sobrescrita é importante.
        """
        # VALIDAÇÃO: Garantir que a página foi inicializada.
        if not self.page:
            raise WebAutomationError("Página não inicializada. Chame start() primeiro.")
        
        try:
            logger.info(f"Navegando para: {url}")
            await self.page.goto(url, wait_until=wait_until)
            logger.info(f"Página carregada: {self.page.title()}") # Logar o título pode ser útil para verificação.
        except Exception as e:
            logger.error(f"Erro ao navegar para {url}: {str(e)}")
            raise WebAutomationError(f"Falha ao navegar para {url}: {str(e)}")
    
    async def fill_form(self, selector: str, data: Dict[str, str]) -> None:
        """Preenche campos de um formulário com base em um seletor de formulário e um dicionário de dados.
        
        Args:
            selector: Seletor CSS do elemento do formulário (ou um container comum dos campos).
                      # ESTRATÉGIA: Assumir que os campos dentro do formulário podem ser selecionados
                      # usando o atributo `name`.
            data: Dicionário onde as chaves são os atributos `name` dos campos
                  e os valores são os dados a serem preenchidos.
        """
        if not self.page:
            raise WebAutomationError("Página não inicializada. Chame start() primeiro.")
        
        try:
            # LÓGICA: Iterar sobre o dicionário de dados. Para cada par (campo, valor),
            # construir um seletor CSS mais específico para o campo (ex: `form_selector [name='field_name']`)
            # e preenchê-lo com o valor.
            for field_name, value_to_fill in data.items():
                # DECISÃO: Construir o seletor do campo combinando o seletor do formulário com o atributo `name` do campo.
                # Isso é uma convenção comum, mas pode precisar de ajuste para formulários estruturados de forma diferente.
                field_selector = f"{selector} [name='{field_name}']"
                # RACIOCÍNIO: `page.fill` limpa o campo e digita o novo valor. É geralmente o método preferido para preencher inputs.
                await self.page.fill(field_selector, str(value_to_fill)) # Converter valor para string para garantir compatibilidade.
                logger.debug(f"Campo preenchido: {field_name} = {value_to_fill}")
        except Exception as e:
            logger.error(f"Erro ao preencher formulário ({selector}): {str(e)}")
            raise WebAutomationError(f"Falha ao preencher formulário ({selector}): {str(e)}")
    
    async def click(self, selector: str, wait_for_navigation: bool = False) -> None:
        """Clica em um elemento da página.
        
        Args:
            selector: Seletor CSS do elemento a ser clicado.
            wait_for_navigation: Booleano indicando se o clique deve disparar uma navegação.
                                 # RACIOCÍNIO: Alguns cliques resultam em navegação para uma nova página ou recarregamento.
                                 # Playwright precisa ser informado para esperar por essa navegação para evitar race conditions.
        """
        if not self.page:
            raise WebAutomationError("Página não inicializada. Chame start() primeiro.")
        
        try:
            # LÓGICA: Se `wait_for_navigation` for True, usar `page.expect_navigation()`
            # como um gerenciador de contexto em torno da ação de clique.
            # Isso garante que o Playwright aguardará a conclusão da navegação antes de prosseguir.
            if wait_for_navigation:
                # `page.expect_navigation()` é um gerenciador de contexto assíncrono.
                async with self.page.expect_navigation():
                    await self.page.click(selector)
            else:
                # Se não houver navegação esperada, um clique simples é suficiente.
                await self.page.click(selector)
            logger.debug(f"Clicado no elemento: {selector}")
        except Exception as e:
            logger.error(f"Erro ao clicar no elemento {selector}: {str(e)}")
            raise WebAutomationError(f"Falha ao clicar no elemento {selector}: {str(e)}")
    
    async def extract_data(self, selectors: Dict[str, str]) -> Dict[str, Any]:
        """Extrai dados de múltiplos elementos na página com base em um dicionário de seletores.
        
        Args:
            selectors: Dicionário onde as chaves são nomes descritivos para os dados
                       e os valores são os seletores CSS para os elementos correspondentes.
            
        Returns:
            Dicionário com os dados extraídos. Se um seletor não for encontrado ou
            ocorrer um erro na extração, o valor para essa chave será None.
        """
        if not self.page:
            raise WebAutomationError("Página não inicializada. Chame start() primeiro.")
        
        extracted_data: Dict[str, Any] = {}
        
        # LÓGICA: Iterar sobre o dicionário de seletores. Para cada um, tentar encontrar o elemento.
        for field_name, css_selector in selectors.items():
            try:
                # RACIOCÍNIO: `page.query_selector` é usado para verificar a existência do elemento.
                # Se o elemento existir, tentar extrair seu conteúdo.
                element = await self.page.query_selector(css_selector)
                if element:
                    # ESTRATÉGIA: Tentar obter o conteúdo de texto do elemento.
                    # Se não houver texto, tentar obter o atributo 'value' (comum para inputs).
                    # `strip()` é usado para limpar espaços em branco.
                    text_content = await element.text_content()
                    # Se text_content for None ou string vazia, tentar o atributo 'value'.
                    if text_content and text_content.strip():
                        extracted_data[field_name] = text_content.strip()
                    else:
                        value_attribute = await element.get_attribute("value")
                        if value_attribute and value_attribute.strip():
                            extracted_data[field_name] = value_attribute.strip()
                        else:
                            # Se ambos forem vazios, pode-se decidir retornar o texto vazio ou None.
                            # Aqui, se o texto é vazio mas o elemento existe, retorna o texto vazio.
                            # Se o `value_attribute` também for vazio, retorna string vazia.
                            extracted_data[field_name] = text_content.strip() if text_content else (value_attribute.strip() if value_attribute else "")
                else:
                    # CENÁRIO: Se o seletor não encontrar nenhum elemento.
                    logger.warning(f"Seletor não encontrado para o campo '{field_name}': {css_selector}")
                    extracted_data[field_name] = None
            except Exception as e:
                # CENÁRIO: Outros erros durante a tentativa de extração.
                logger.warning(f"Erro ao extrair dados para o campo '{field_name}' (seletor: {css_selector}): {str(e)}")
                extracted_data[field_name] = None
        
        return extracted_data
    
    async def close(self) -> None:
        """Fecha a página, o contexto, o navegador e para o Playwright."""
        # RACIOCÍNIO: É importante fechar os recursos na ordem correta para evitar erros ou recursos pendentes.
        # Página -> Contexto -> Navegador -> Playwright.
        try:
            # LÓGICA: Verificar se cada objeto existe antes de tentar fechá-lo,
            # para evitar erros se `close()` for chamado múltiplas vezes ou se `start()` falhou parcialmente.
            if self.page: # Embora Playwright geralmente feche páginas com o contexto, é bom ser explícito.
                await self.page.close()
                self.page = None
            if self.context:
                await self.context.close()
                self.context = None
            if self.browser:
                await self.browser.close()
                self.browser = None
            if self.playwright:
                # RACIOCÍNIO: `playwright.stop()` desliga o processo do Playwright.
                await self.playwright.stop()
                self.playwright = None
                
            logger.info("Navegador fechado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao fechar o navegador: {str(e)}")
            # DECISÃO: Levantar WebAutomationError mesmo durante o fechamento,
            # pois pode indicar problemas que precisam ser investigados.
            raise WebAutomationError(f"Falha ao fechar o navegador: {str(e)}")
    
    # --- Métodos de Gerenciamento de Contexto Assíncrono ---
    # RACIOCÍNIO: Implementar `__aenter__` e `__aexit__` permite que a classe `BrowserManager`
    # seja usada com a sintaxe `async with`, garantindo que os recursos do navegador
    # sejam corretamente inicializados (`start()`) e limpos (`close()`) automaticamente.
    async def __aenter__(self):
        """Permite usar BrowserManager com 'async with'. Chama start()."""
        # LÓGICA: `__aenter__` é chamado no início do bloco `async with`.
        # Deve inicializar os recursos e retornar o objeto a ser usado dentro do bloco (geralmente `self`).
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Garante que o navegador seja fechado ao sair do contexto 'async with'. Chama close()."""
        # LÓGICA: `__aexit__` é chamado ao final do bloco `async with`,
        # independentemente de exceções terem ocorrido dentro do bloco.
        # `exc_type`, `exc_val`, `exc_tb` contêm informações da exceção, se houver.
        await self.close()

# ESTRATÉGIA: Fornecer uma função de conveniência para simplificar a criação e inicialização
# de uma instância do BrowserManager para casos de uso comuns.
async def create_browser(
    headless: Optional[bool] = None, # Permite sobrescrever o padrão de headless.
    browser_type: str = "chromium",  # Permite escolher o navegador.
    **kwargs # Permite passar quaisquer outros argumentos para o construtor do BrowserManager.
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

# Resumo Técnico Final
# Pontos fortes da implementação:
# - Utilização da biblioteca Playwright, que é moderna e poderosa para automação web.
# - Suporte para múltiplos navegadores (Chromium, Firefox, Webkit).
# - Implementação assíncrona (async/await) para melhor desempenho em operações I/O bound.
# - Configurações flexíveis para headless mode, viewport, user-agent e downloads.
# - Tentativa de evitar detecção de automação (removendo `navigator.webdriver`).
# - Boa estruturação com a classe `BrowserManager`.
# - Logging detalhado das operações.
# Maturidade técnica demonstrada:
# - Uso de gerenciador de contexto assíncrono (`__aenter__`, `__aexit__`).
# - Tratamento de exceções robusto para operações de automação.
# - Criação de diretório de downloads de forma programática.
# - Verificações de tipo (Type Hinting) utilizadas.
# Aderência às boas práticas:
# - Código bem comentado com docstrings.
# - Nomenclatura clara e consistente.
# - Modularidade através da classe `BrowserManager` e da função `create_browser`.
# - Uso de `pathlib` para manipulação de caminhos.
