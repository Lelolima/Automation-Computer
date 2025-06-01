"""
Módulo de automação de desktop do Agente de Automação Integrada.

Este módulo fornece funcionalidades para automação de aplicativos desktop,
controle de mouse e teclado, e interação com janelas do Windows.
"""

from .controller import (
    DesktopAutomationError,
    DesktopController,
    WindowInfo,
    MouseButton,
    KeyAction,
)

__all__ = [
    'DesktopAutomationError',
    'DesktopController',
    'WindowInfo',
    'MouseButton',
    'KeyAction',
]
