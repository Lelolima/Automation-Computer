"""
Configuração do pytest para os testes.

Este arquivo contém configurações e fixtures que podem ser usadas em todos os testes.
"""

import os
import sys
from pathlib import Path
from typing import Generator

import pytest

# Adiciona o diretório raiz ao path do Python para que os módulos possam ser importados
sys.path.insert(0, str(Path(__file__).parent.absolute()))

# Configuração de logging para os testes
@pytest.fixture(autouse=True)
def setup_logging():
    """Configura o logging para os testes."""
    import logging
    logging.basicConfig(level=logging.DEBUG)

# Fixture para o controlador de desktop mockado
@pytest.fixture
def mock_desktop_controller():
    """Retorna uma instância de DesktopController com mocks para dependências externas."""
    with patch('src.automation.desktop.controller.pyautogui'), \
         patch('src.automation.desktop.controller.pg'), \
         patch('src.automation.desktop.controller.pytesseract'):
        from src.automation.desktop.controller import DesktopController
        return DesktopController()

# Configuração para testes de integração
def pytest_configure(config):
    """Configurações globais do pytest."""
    # Marca para testes de integração (que exigem interação com o sistema)
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test (deselect with '-m not integration')"
    )

# Desativa a cobertura para arquivos de teste
collect_ignore = ["test_*.py"]
