"""
Automation-Computer - CLI Interface
Interface de linha de comando usando Typer + Rich

Criado por Wellington de Lima Catarina
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

app = typer.Typer(help="Automation-Computer - RPA com IA")
console = Console()


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
    console.print(Panel(f"[bold blue]Automação Web[/bold blue]"))
    console.print(f"URL: {url}")
    console.print("Em desenvolvimento: navegação com Playwright")


@app.command()
def status():
    """Mostra status do sistema."""
    table = Table(title="Status do Automation-Computer")
    table.add_column("Módulo", style="cyan")
    table.add_column("Status", style="green")

    table.add_row("Desktop Controller", "✅ Disponível")
    table.add_row("Web Automation", "✅ Disponível")
    table.add_row("Security", "✅ Disponível")
    table.add_row("LLM Orchestrator", "✅ Disponível")
    table.add_row("CLI", "✅ Disponível")
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