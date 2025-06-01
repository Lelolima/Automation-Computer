"""
Pacote de automação do Agente de Automação Integrada.

Este pacote contém módulos para automação web, desktop e outras tarefas de automação.
"""

__version__ = "0.1.0"

# Importações principais para facilitar o acesso aos módulos
from .web.browser import BrowserManager, WebAutomationError

__all__ = [
    'BrowserManager',
    'WebAutomationError',
]
