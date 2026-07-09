"""
Testes para DesktopController
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestDesktopController:
    """Testes para DesktopController."""

    def test_init(self):
        """Testa inicialização."""
        with patch('src.automation.desktop_controller.MouseController') as mock_mouse, \
             patch('src.automation.desktop_controller.KeyboardController') as mock_keyboard:

            from src.automation.desktop_controller import DesktopController

            controller = DesktopController()

            assert controller.app is None
            assert controller.app_path is None
            mock_mouse.assert_called_once()
            mock_keyboard.assert_called_once()

    def test_type_text(self):
        """Testa digitação de texto."""
        with patch('src.automation.desktop_controller.MouseController'), \
             patch('src.automation.desktop_controller.KeyboardController') as mock_kb_cls:

            from src.automation.desktop_controller import DesktopController

            mock_kb = MagicMock()
            mock_kb_cls.return_value = mock_kb

            controller = DesktopController()
            controller.type_text("test")

            assert mock_kb.press.call_count >= 4
            assert mock_kb.release.call_count >= 4

    def test_press_key_enter(self):
        """Testa pressionar Enter."""
        with patch('src.automation.desktop_controller.MouseController'), \
             patch('src.automation.desktop_controller.KeyboardController') as mock_kb_cls, \
             patch('src.automation.desktop_controller.Key') as mock_key:

            from src.automation.desktop_controller import DesktopController

            mock_kb = MagicMock()
            mock_kb_cls.return_value = mock_kb
            mock_key.enter = MagicMock()

            controller = DesktopController()
            controller.press_key("enter")

            mock_kb.press.assert_called()
            mock_kb.release.assert_called()