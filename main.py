#!/usr/bin/env python3
"""
Agente Autônomo de Automação Integrada - Elite Version
-------------------------------------
Sistema avançado de automação web e desktop com suporte a LLM, CLI robusta e arquitetura enterprise.

Features:
    - Automação Web assíncrona com Playwright
    - Automação Desktop com controle preciso
    - Segurança enterprise (JWT, AES-256, bcrypt)
    - Integração com LLMs (OpenAI, Anthropic, Google)
    - CLI completa com Typer
    - Logging estruturado com Loguru
    - Monitoramento de saúde do sistema
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.spinner import Spinner

# Adiciona o diretório raiz ao path do Python
sys.path.append(str(Path(__file__).parent.absolute()))

from src.config import settings
from src.security.auth import create_access_token, verify_password, get_user
from src.security.encryption import EncryptionManager
from src.automation.web.browser import BrowserManager, WebAutomationError
from src.automation.desktop.controller import DesktopController, DesktopAutomationError

# Configuração da aplicação Typer
app = typer.Typer(
    name="automation-agent",
    help="🤖 Agente Autônomo de Automação Integrada - Sistema enterprise para automação web e desktop",
    add_completion=True,
    pretty_exceptions_enable=True,
    pretty_exceptions_show_locals=False,
)

console = Console()

# Configuração avançada de logging com Loguru
logger.remove()  # Remove handler padrão

# Handler para console com formatação rica
logger.add(
    sink=sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL,
    colorize=True,
    backtrace=True,
    diagnose=True,
)

# Handler para arquivo com rotação
logger.add(
    "logs/automation.log",
    rotation="50 MB",
    retention="90 days",
    compression="zip",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {process.name} | {thread.name} | {level} | {name}:{function}:{line} | {extra} | {message}",
    enqueue=True,
    serialize=False,
    backtrace=True,
    diagnose=True,
)


class HealthStatus:
    """Status de saúde dos componentes do sistema."""
    
    def __init__(self):
        self.components = {
            "config": {"status": "unknown", "message": ""},
            "security": {"status": "unknown", "message": ""},
            "web_automation": {"status": "unknown", "message": ""},
            "desktop_automation": {"status": "unknown", "message": ""},
            "llm": {"status": "unknown", "message": ""},
        }
    
    def update(self, component: str, status: str, message: str = ""):
        """Atualiza o status de um componente."""
        if component in self.components:
            self.components[component] = {"status": status, "message": message}
    
    def is_healthy(self) -> bool:
        """Verifica se todos os componentes estão saudáveis."""
        return all(comp["status"] == "healthy" for comp in self.components.values())
    
    def render_table(self) -> Table:
        """Renderiza tabela de status."""
        table = Table(title="🏥 Saúde do Sistema", show_header=True, header_style="bold magenta")
        table.add_column("Componente", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Detalhes", style="yellow")
        
        status_icons = {
            "healthy": "✅",
            "degraded": "⚠️",
            "unhealthy": "❌",
            "unknown": "❓",
        }
        
        for component, info in self.components.items():
            icon = status_icons.get(info["status"], "❓")
            table.add_row(
                component.replace("_", " ").title(),
                f"{icon} {info['status'].upper()}",
                info["message"] or "-",
            )
        
        return table


class AutomationAgent:
    """
    Classe principal do agente de automação - Versão Enterprise.
    
    Features:
        - Gerenciamento de ciclo de vida de componentes
        - Health check em tempo real
        - Execução assíncrona otimizada
        - Tratamento de erros robusto
        - Métricas de desempenho
    """
    
    def __init__(self, task_id: Optional[str] = None):
        """
        Inicializa o agente de automação.
        
        Args:
            task_id: Identificador único para rastreamento da tarefa
        """
        self.task_id = task_id or f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.started_at: Optional[datetime] = None
        self.health_status = HealthStatus()
        
        # Componentes lazy-loaded
        self._encryption_manager: Optional[EncryptionManager] = None
        self._browser_manager: Optional[BrowserManager] = None
        self._desktop_controller: Optional[DesktopController] = None
        
        # Métricas
        self.metrics = {
            "tasks_executed": 0,
            "tasks_failed": 0,
            "avg_execution_time": 0.0,
            "total_execution_time": 0.0,
        }
        
        logger.info(f"Agente de automação inicializado [Task ID: {self.task_id}]")
    
    @property
    def encryption_manager(self) -> EncryptionManager:
        """Lazy loading do gerenciador de criptografia."""
        if self._encryption_manager is None:
            try:
                self._encryption_manager = EncryptionManager()
                self.health_status.update("security", "healthy", "Criptografia AES-256 ativa")
            except Exception as e:
                self.health_status.update("security", "unhealthy", str(e))
                raise
        return self._encryption_manager
    
    @property
    def browser_manager(self) -> BrowserManager:
        """Lazy loading do gerenciador de navegador."""
        if self._browser_manager is None:
            try:
                self._browser_manager = BrowserManager()
                self.health_status.update("web_automation", "healthy", "Playwright pronto")
            except Exception as e:
                self.health_status.update("web_automation", "unhealthy", str(e))
                raise
        return self._browser_manager
    
    @property
    def desktop_controller(self) -> DesktopController:
        """Lazy loading do controlador de desktop."""
        if self._desktop_controller is None:
            try:
                self._desktop_controller = DesktopController()
                self.health_status.update("desktop_automation", "healthy", "PyAutoGUI pronto")
            except Exception as e:
                self.health_status.update("desktop_automation", "unhealthy", str(e))
                raise
        return self._desktop_controller
    
    async def health_check(self) -> bool:
        """
        Verifica a saúde de todos os componentes do sistema.
        
        Returns:
            bool: True se todos os componentes estiverem saudáveis
        """
        logger.info("Iniciando health check do sistema...")
        
        # Check config
        try:
            _ = settings.SECRET_KEY
            _ = settings.ENCRYPTION_KEY
            self.health_status.update("config", "healthy", "Configurações válidas")
        except Exception as e:
            self.health_status.update("config", "unhealthy", f"Config inválida: {e}")
        
        # Check security
        try:
            _ = self.encryption_manager
            self.health_status.update("security", "healthy", "Criptografia operacional")
        except Exception as e:
            self.health_status.update("security", "unhealthy", str(e))
        
        # Check LLM
        if settings.OPENAI_API_KEY or settings.ANTHROPIC_API_KEY or settings.GOOGLE_API_KEY:
            self.health_status.update("llm", "healthy", f"Provedor: {settings.LLM_PROVIDER}")
        else:
            self.health_status.update("llm", "degraded", "Nenhuma API key configurada")
        
        is_healthy = self.health_status.is_healthy()
        status = "✅ Saudável" if is_healthy else "⚠️ Problemas detectados"
        logger.info(f"Health check concluído: {status}")
        
        return is_healthy
    
    async def initialize_components(self):
        """Inicializa todos os componentes do agente."""
        logger.info("Inicializando componentes do agente...")
        
        try:
            # Validação de configurações
            _ = settings.SECRET_KEY
            _ = settings.ENCRYPTION_KEY
            _ = settings.DATABASE_URL
            self.health_status.update("config", "healthy", "Todas as configs válidas")
            
            # Inicializar componentes (lazy loading já trata health status)
            _ = self.encryption_manager
            _ = self.desktop_controller
            
            logger.info("Componentes inicializados com sucesso")
            
        except Exception as e:
            logger.error(f"Falha na inicialização: {e}")
            raise
    
    async def run_task(self, task_type: str, **kwargs) -> dict:
        """
        Executa uma tarefa de automação específica.
        
        Args:
            task_type: Tipo de tarefa ("web", "desktop", "hybrid")
            **kwargs: Parâmetros específicos da tarefa
            
        Returns:
            dict: Resultado da execução
        """
        start_time = datetime.now()
        self.started_at = start_time
        
        result = {
            "task_id": self.task_id,
            "task_type": task_type,
            "status": "pending",
            "started_at": start_time.isoformat(),
            "completed_at": None,
            "duration_seconds": 0.0,
            "data": {},
            "error": None,
        }
        
        try:
            logger.info(f"Executando tarefa {task_type} [ID: {self.task_id}]")
            
            if task_type == "web":
                result["data"] = await self._execute_web_task(**kwargs)
            elif task_type == "desktop":
                result["data"] = await self._execute_desktop_task(**kwargs)
            elif task_type == "hybrid":
                result["data"] = await self._execute_hybrid_task(**kwargs)
            else:
                raise ValueError(f"Tipo de tarefa desconhecido: {task_type}")
            
            result["status"] = "success"
            self.metrics["tasks_executed"] += 1
            
        except Exception as e:
            logger.error(f"Tarefa falhou: {e}", exc_info=True)
            result["status"] = "failed"
            result["error"] = str(e)
            self.metrics["tasks_failed"] += 1
            raise
        
        finally:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            result["completed_at"] = end_time.isoformat()
            result["duration_seconds"] = duration
            
            # Atualizar métricas
            total_tasks = self.metrics["tasks_executed"] + self.metrics["tasks_failed"]
            self.metrics["total_execution_time"] += duration
            self.metrics["avg_execution_time"] = (
                self.metrics["total_execution_time"] / total_tasks if total_tasks > 0 else 0
            )
        
        return result
    
    async def _execute_web_task(self, url: str, actions: Optional[list] = None, **kwargs) -> dict:
        """Executa tarefa de automação web."""
        logger.info(f"Web automation: {url}")
        
        browser = self.browser_manager
        await browser.start()
        
        try:
            await browser.navigate(url)
            
            # Executar ações se fornecidas
            if actions:
                for action in actions:
                    action_type = action.get("type")
                    if action_type == "fill":
                        await browser.fill_form(
                            action.get("selector", "form"),
                            action.get("data", {})
                        )
                    elif action_type == "click":
                        await browser.click(
                            action.get("selector"),
                            wait_for_navigation=action.get("wait_nav", False)
                        )
                    elif action_type == "extract":
                        data = await browser.extract_data(action.get("selectors", {}))
                        kwargs.setdefault("extracted_data", {}).update(data)
            
            # Extrair dados adicionais se solicitado
            if kwargs.get("extract"):
                data = await browser.extract_data(kwargs["extract"])
                kwargs.setdefault("extracted_data", {}).update(data)
            
            return {
                "url": url,
                "title": browser.page.title() if browser.page else "",
                "extracted_data": kwargs.get("extracted_data", {}),
            }
            
        finally:
            await browser.close()
    
    async def _execute_desktop_task(self, actions: list, **kwargs) -> dict:
        """Executa tarefa de automação desktop."""
        logger.info(f"Desktop automation: {len(actions)} ações")
        
        controller = self.desktop_controller
        results = []
        
        for action in actions:
            action_type = action.get("type")
            
            if action_type == "move_mouse":
                controller.move_mouse(action["x"], action["y"], action.get("duration", 0.5))
                results.append({"action": "move_mouse", "success": True})
                
            elif action_type == "click":
                button = MouseButton(action.get("button", "left"))
                controller.click(
                    action.get("x"),
                    action.get("y"),
                    button=button,
                    clicks=action.get("clicks", 1)
                )
                results.append({"action": "click", "success": True})
                
            elif action_type == "type_text":
                controller.type_text(action["text"], action.get("interval", 0.1))
                results.append({"action": "type_text", "success": True})
                
            elif action_type == "press_key":
                controller.press_key(
                    action["keys"],
                    action=KeyAction(action.get("key_action", "PRESS")),
                    presses=action.get("presses", 1)
                )
                results.append({"action": "press_key", "success": True})
                
            elif action_type == "capture_screen":
                screenshot = controller.capture_screen(
                    region=action.get("region"),
                    save_path=action.get("save_path")
                )
                results.append({"action": "capture_screen", "success": True, "image": screenshot})
        
        return {"actions_executed": len(results), "results": results}
    
    async def _execute_hybrid_task(self, web_config: dict, desktop_config: dict, **kwargs) -> dict:
        """Executa tarefa híbrida (web + desktop)."""
        logger.info("Executando tarefa híbrida")
        
        web_result = await self._execute_web_task(**web_config)
        desktop_result = await self._execute_desktop_task(**desktop_config)
        
        return {
            "web": web_result,
            "desktop": desktop_result,
        }
    
    async def shutdown(self):
        """Finaliza todos os componentes gracefulmente."""
        logger.info("Finalizando agente...")
        
        if self._browser_manager:
            await self._browser_manager.close()
        
        self._encryption_manager = None
        self._browser_manager = None
        self._desktop_controller = None
        
        logger.info("Agente finalizado")
    
    def get_metrics(self) -> dict:
        """Retorna métricas de execução."""
        return self.metrics.copy()


# ============================================================================
# CLI COMMANDS
# ============================================================================

@app.command()
def version():
    """Exibe a versão do agente."""
    console.print(Panel(
        "[bold green]🤖 Automation Agent[/bold green]\n\n"
        f"Versão: [cyan]0.2.0 (Elite)[/cyan]\n"
        f"Python: [cyan]{sys.version.split()[0]}[/cyan]\n"
        f"Ambiente: [cyan]{settings.ENVIRONMENT}[/cyan]",
        title="Informações do Sistema",
        border_style="blue",
    ))


@app.command()
def health():
    """Verifica a saúde do sistema."""
    console.print("[bold blue]Verificando saúde do sistema...[/bold blue]\n")
    
    agent = AutomationAgent()
    
    with Live(agent.health_status.render_table(), refresh_per_second=4) as live:
        # Simula check dos componentes
        import time
        
        time.sleep(0.5)
        agent.health_status.update("config", "healthy" if settings.SECRET_KEY else "unhealthy", "Validando...")
        live.update(agent.health_status.render_table())
        
        time.sleep(0.5)
        try:
            _ = agent.encryption_manager
        except:
            pass
        live.update(agent.health_status.render_table())
        
        time.sleep(0.5)
        try:
            _ = agent.desktop_controller
        except:
            pass
        live.update(agent.health_status.render_table())
        
        time.sleep(0.5)
        if settings.OPENAI_API_KEY or settings.ANTHROPIC_API_KEY:
            agent.health_status.update("llm", "healthy", f"Provedor: {settings.LLM_PROVIDER}")
        else:
            agent.health_status.update("llm", "degraded", "API keys ausentes")
        live.update(agent.health_status.render_table())
    
    if agent.health_status.is_healthy():
        console.print("\n[bold green]✅ Sistema saudável![/bold green]")
    else:
        console.print("\n[bold yellow]⚠️ Problemas detectados. Verifique os logs.[/bold yellow]")


@app.command()
async def run(
    task_type: str = typer.Argument(
        "web",
        help="Tipo de tarefa: web, desktop, ou hybrid",
        case_sensitive=False,
    ),
    url: Optional[str] = typer.Option(
        None,
        "--url", "-u",
        help="URL para automação web",
    ),
    actions_file: Optional[Path] = typer.Option(
        None,
        "--actions", "-a",
        help="Arquivo JSON com ações a executar",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    headless: bool = typer.Option(
        False,
        "--headless", "-h",
        help="Executar em modo headless",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Modo verbose",
    ),
):
    """
    Executa uma tarefa de automação.
    
    Exemplos:
    
    🔹 Automação Web:
        automation-agent run web -u https://exemplo.com
    
    🔹 Com arquivo de ações:
        automation-agent run web -a actions.json
    
    🔹 Modo Headless:
        automation-agent run web -u https://exemplo.com --headless
    """
    console.print(f"[bold blue]Iniciando tarefa {task_type}...[/bold blue]\n")
    
    # Override settings se necessário
    if headless:
        settings.HEADLESS = True
    
    agent = AutomationAgent()
    
    try:
        await agent.initialize_components()
        
        # Carregar ações do arquivo se fornecido
        actions = None
        if actions_file:
            import json
            with open(actions_file, "r") as f:
                actions = json.load(f)
        
        # Preparar parâmetros
        kwargs = {}
        if url:
            kwargs["url"] = url
        if actions:
            kwargs["actions"] = actions
        
        # Mostrar spinner durante execução
        with console.status("[bold green]Executando...", spinner="dots"):
            result = await agent.run_task(task_type, **kwargs)
        
        # Exibir resultado
        console.print("\n[bold green]✅ Tarefa concluída![/bold green]\n")
        
        result_table = Table(title="Resultado da Execução")
        result_table.add_column("Campo", style="cyan")
        result_table.add_column("Valor", style="green")
        
        result_table.add_row("Task ID", result["task_id"])
        result_table.add_row("Status", result["status"])
        result_table.add_row("Duração", f"{result['duration_seconds']:.2f}s")
        result_table.add_row("Início", result["started_at"])
        result_table.add_row("Término", result["completed_at"])
        
        console.print(result_table)
        
        if result.get("data"):
            console.print("\n[bold]Dados:[/bold]")
            console.print_json(data=result["data"], indent=2)
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Erro: {e}[/bold red]")
        if verbose:
            console.print_exception()
        raise typer.Exit(1)
    
    finally:
        await agent.shutdown()


@app.command()
async def interactive():
    """Inicia modo interativo (REPL)."""
    from rich.prompt import Prompt
    
    console.print(Panel(
        "[bold green]🤖 Automation Agent - Modo Interativo[/bold green]\n\n"
        "Digite comandos para controlar o agente.\n"
        "Comandos disponíveis: [cyan]help, web, desktop, encrypt, decrypt, exit[/cyan]",
        title="Bem-vindo",
        border_style="green",
    ))
    
    agent = AutomationAgent()
    await agent.initialize_components()
    
    while True:
        try:
            command = Prompt.ask("\n[bold cyan]agent>[/bold cyan]")
            
            if command.lower() in ["exit", "quit", "q"]:
                console.print("[yellow]Finalizando...[/yellow]")
                break
            
            elif command.lower() == "help":
                console.print("""
[bold]Comandos disponíveis:[/bold]
  [cyan]web <url>[/cyan]     - Navegar para URL
  [cyan]desktop[/cyan]       - Comando desktop
  [cyan]encrypt <text>[/cyan] - Criptografar texto
  [cyan]decrypt <text>[/cyan] - Descriptografar texto
  [cyan]health[/cyan]        - Health check
  [cyan]metrics[/cyan]       - Mostrar métricas
  [cyan]exit[/cyan]          - Sair
                """)
            
            elif command.lower() == "health":
                is_healthy = await agent.health_check()
                console.print(agent.health_status.render_table())
            
            elif command.lower() == "metrics":
                metrics = agent.get_metrics()
                console.print_json(data=metrics, indent=2)
            
            elif command.startswith("encrypt "):
                text = command[8:]
                encrypted = agent.encryption_manager.encrypt(text)
                console.print(f"[green]Criptografado:[/green] {encrypted}")
            
            elif command.startswith("decrypt "):
                text = command[8:]
                try:
                    decrypted = agent.encryption_manager.decrypt(text)
                    console.print(f"[green]Descriptografado:[/green] {decrypted}")
                except Exception as e:
                    console.print(f"[red]Erro:[/red] {e}")
            
            else:
                console.print(f"[yellow]Comando desconhecido: {command}[/yellow]")
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrompido pelo usuário[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Erro: {e}[/red]")
    
    await agent.shutdown()


@app.command()
def encrypt(text: str):
    """Criptografa um texto usando AES-256."""
    try:
        manager = EncryptionManager()
        encrypted = manager.encrypt(text)
        console.print(Panel(
            f"[green]{encrypted}[/green]",
            title="🔐 Texto Criptografado",
            border_style="green",
        ))
    except Exception as e:
        console.print(f"[red]Erro: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def decrypt(encrypted_text: str):
    """Descriptografa um texto usando AES-256."""
    try:
        manager = EncryptionManager()
        decrypted = manager.decrypt(encrypted_text)
        console.print(Panel(
            f"[green]{decrypted}[/green]",
            title="🔓 Texto Descriptografado",
            border_style="green",
        ))
    except Exception as e:
        console.print(f"[red]Erro: {e}[/red]")
        raise typer.Exit(1)


# Importações necessárias para tarefas desktop
from src.automation.desktop.controller import MouseButton, KeyAction


def main():
    """Ponto de entrada principal."""
    app()


if __name__ == "__main__":
    app()
