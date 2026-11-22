"""
Automation-Computer - CLI Interface
Interface de linha de comando usando Typer + Rich

Criado por Wellington de Lima Catarina
"""

import importlib

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

load_dotenv()  # carrega .env (python-dotenv já era dependência, mas nunca era usado)

app = typer.Typer(help="Automation-Computer - RPA com IA")
console = Console()

MODULOS = {
    "Desktop Controller": "src.automation.desktop_controller",
    "Web Automation": "src.automation.web_automation",
    "Security": "src.security.encryption",
    "LLM Orchestrator": "src.ai.llm_orchestrator",
    "CLI": "src.ui.cli",
}


def _status_modulo(modulo: str) -> str:
    """Importa o módulo de verdade e informa se está utilizável."""
    try:
        importlib.import_module(modulo)
        return "✅ Disponível"
    except Exception as exc:  # dependência ausente ou SO não suportado
        return f"❌ Indisponível ({type(exc).__name__}: {exc})"


@app.command()
def hello(name: str = typer.Argument("Mundo", help="Nome para saudar")):
    """Comando de exemplo."""
    console.print(Panel(f"Olá, [bold green]{name}[/bold green]!"))
    console.print("\n[yellow]Bem-vindo ao Automation-Computer![/yellow]")


@app.command()
def desktop():
    """Inicia modo de automação desktop."""
    console.print(Panel("[bold blue]Modo Desktop[/bold blue]"))
    console.print("Em desenvolvimento: controle de mouse/teclado via pywinauto")


@app.command()
def web(url: str = typer.Argument(..., help="URL para automatizar")):
    """Inicia automação web."""
    console.print(Panel("[bold blue]Automação Web[/bold blue]"))
    console.print(f"URL: {url}")
    console.print("Em desenvolvimento: navegação com Playwright")


@app.command()
def status():
    """Mostra status do sistema."""
    table = Table(title="Status do Automation-Computer")
    table.add_column("Módulo", style="cyan")
    table.add_column("Status", style="green")

    # Antes os status eram fixos ("✅ Disponível") mesmo sem as dependências.
    for nome, modulo in MODULOS.items():
        table.add_row(nome, _status_modulo(modulo))
    table.add_row("Dashboard", "🔜 Em breve")

    console.print(table)


@app.command()
def version():
    """Mostra versão."""
    console.print("[bold]Automation-Computer[/bold] v0.1.0")
    console.print("Por: Wellington de Lima Catarina")


def main():
    """Ponto de entrada principal."""
    app()


if __name__ == "__main__":
    app()
