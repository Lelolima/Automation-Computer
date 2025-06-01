"""
Módulo de automação web do Agente de Automação Integrada.

Este módulo fornece funcionalidades para automação de navegadores web,
incluindo navegação, preenchimento de formulários e extração de dados.
"""

from .browser import BrowserManager, WebAutomationError

__all__ = [
    'BrowserManager',
    'WebAutomationError',
]
