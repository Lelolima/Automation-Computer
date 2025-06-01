"""
Testes unitários para o módulo de automação de desktop.

Este módulo contém testes para a classe DesktopController e suas funcionalidades.
"""

import os
import unittest
from unittest.mock import MagicMock, patch, ANY
import pytest
import pyautogui

# Importa a classe a ser testada
from src.automation.desktop.controller import DesktopController, MouseButton, KeyAction, WindowInfo


class TestDesktopController(unittest.TestCase):
    """Testes para a classe DesktopController."""

    def setUp(self):
        """Configura o ambiente de teste."""
        # Cria um mock para as dependências externas
        # Configura mock para pyautogui
        self.pyautogui_patcher = patch('src.automation.desktop.controller.pyautogui')
        self.mock_pyautogui = self.pyautogui_patcher.start()
        
        # Configura mock para pygetwindow (importado como gw)
        self.gw_patcher = patch('src.automation.desktop.controller.gw')
        self.mock_gw = self.gw_patcher.start()
        
        # Configura mock para pytesseract
        self.pytesseract_patcher = patch('src.automation.desktop.controller.pytesseract')
        self.mock_pytesseract = self.pytesseract_patcher.start()
        
        # Configura mocks para o módulo pygetwindow
        self.mock_window = MagicMock()
        self.mock_window.title = "Janela de Teste"
        self.mock_window.left = 100
        self.mock_window.top = 100
        self.mock_window.width = 800
        self.mock_window.height = 600
        self.mock_window.isActive = True
        
        # Configura os retornos dos métodos do pygetwindow
        self.mock_gw.getActiveWindow.return_value = self.mock_window
        self.mock_gw.getWindowsWithTitle.return_value = [self.mock_window]
        self.mock_gw.getAllTitles.return_value = ["Janela de Teste", "Outra Janela"]
        
        # Inicializa o controlador para os testes
        self.controller = DesktopController()
    
    def tearDown(self):
        """Limpa o ambiente de teste."""
        self.pyautogui_patcher.stop()
        self.gw_patcher.stop()
        self.pytesseract_patcher.stop()
    
    def test_initialization(self):
        """Testa a inicialização do controlador."""
        self.assertIsNotNone(self.controller)
        # Verifica se as configurações do PyAutoGUI foram aplicadas
        self.assertTrue(pyautogui.FAILSAFE)
        self.assertEqual(pyautogui.PAUSE, 0.1)
    
    def test_move_mouse(self):
        """Testa o movimento do mouse."""
        x, y = 100, 200
        self.controller.move_mouse(x, y)
        self.mock_pyautogui.moveTo.assert_called_once_with(
            x, y, 
            duration=ANY,  # Não nos importamos com o valor exato
            tween=self.mock_pyautogui.easeInOutQuad
        )
    
    def test_click(self):
        """Testa o clique do mouse."""
        # Testa clique simples
        x, y = 150, 250
        self.controller.click(x, y)
        self.mock_pyautogui.click.assert_called_once_with(
            x=x, y=y, 
            button=MouseButton.LEFT.value,
            clicks=1,
            interval=0.1
        )
        
        # Testa clique com botão direito
        self.mock_pyautogui.reset_mock()
        self.controller.click(x, y, button=MouseButton.RIGHT, clicks=2)
        self.mock_pyautogui.click.assert_called_once_with(
            x=x, y=y,
            button=MouseButton.RIGHT.value,
            clicks=2,
            interval=0.1
        )
    
    def test_scroll(self):
        """Testa a rolagem da roda do mouse."""
        # Rola para cima
        self.controller.scroll(5)
        self.mock_pyautogui.scroll.assert_called_once_with(5)
        
        # Rola para baixo
        self.mock_pyautogui.reset_mock()
        self.controller.scroll(-3)
        self.mock_pyautogui.scroll.assert_called_once_with(-3)
    
    def test_type_text(self):
        """Testa a digitação de texto."""
        text = "Olá, mundo!"
        self.controller.type_text(text)
        self.mock_pyautogui.write.assert_called_once_with(text, interval=0.1)
    
    def test_press_key(self):
        """Testa o pressionamento de teclas."""
        # Configura os mocks para os métodos de teclado
        self.mock_pyautogui.hotkey.return_value = None
        self.mock_pyautogui.keyDown.return_value = None
        self.mock_pyautogui.keyUp.return_value = None
        
        # Testa tecla única com ação padrão (PRESS)
        self.controller.press_key("enter")
        self.mock_pyautogui.hotkey.assert_called_once_with("enter")
        
        # Testa combinação de teclas
        self.mock_pyautogui.reset_mock()
        self.controller.press_key(["ctrl", "s"])
        self.mock_pyautogui.hotkey.assert_called_once_with("ctrl", "s")
        
        # Testa ação KEY_DOWN
        self.mock_pyautogui.reset_mock()
        self.controller.press_key("shift", action=KeyAction.DOWN)
        self.mock_pyautogui.keyDown.assert_called_once_with("shift")
        
        # Testa ação KEY_UP
        self.mock_pyautogui.reset_mock()
        self.controller.press_key("shift", action=KeyAction.UP)
        self.mock_pyautogui.keyUp.assert_called_once_with("shift")
    
    def test_get_active_window(self):
        """Testa a obtenção da janela ativa."""
        window = self.controller.get_active_window()
        self.assertIsNotNone(window)
        self.assertEqual(window.title, "Janela de Teste")
        self.assertEqual(window.left, 100)
        self.assertEqual(window.top, 100)
        self.assertEqual(window.width, 800)
        self.assertEqual(window.height, 600)
        self.assertTrue(window.is_active)
    
    def test_get_windows(self):
        """Testa a listagem de janelas."""
        # Configura o mock para retornar uma lista de janelas
        mock_window2 = MagicMock()
        mock_window2.title = "Outra Janela"
        mock_window2.left = 200
        mock_window2.top = 200
        mock_window2.width = 400
        mock_window2.height = 300
        mock_window2.isActive = False
        
        self.mock_gw.getAllWindows.return_value = [self.mock_window, mock_window2]
        self.mock_gw.getWindowsWithTitle.return_value = [mock_window2]
        
        # Testa listagem de todas as janelas
        windows = self.controller.get_windows()
        self.assertEqual(len(windows), 2)
        self.assertEqual(windows[0].title, "Janela de Teste")
    
    def test_activate_window(self):
        """Testa a ativação de uma janela."""
        # Configura o mock para retornar uma janela ao buscar pelo título
        self.mock_window.activate.return_value = True
        
        # Testa ativação bem-sucedida
        result = self.controller.activate_window("Janela de Teste")
        self.assertTrue(result)
        self.mock_window.activate.assert_called_once()
        
        # Testa restauração de janela minimizada
        self.mock_window.reset_mock()
        self.mock_window.isMinimized = True
        result = self.controller.activate_window("Janela de Teste")
        self.assertTrue(result)
        self.mock_window.restore.assert_called_once()
        self.mock_window.activate.assert_called_once()
        
        # Testa com janela não encontrada
        self.mock_gw.getWindowsWithTitle.return_value = []
        result = self.controller.activate_window("Janela Inexistente")
        self.assertFalse(result)
    
    @patch('src.automation.desktop.controller.ImageGrab')
    @patch('src.automation.desktop.controller.os')
    def test_capture_screen(self, mock_os, mock_image_grab):
        """Testa a captura de tela."""
        # Configura o mock para ImageGrab.grab()
        mock_screenshot = MagicMock()
        mock_image_grab.grab.return_value = mock_screenshot
        
        # Configura o mock para os.path
        mock_os.path.dirname.return_value = "screenshots"
        mock_os.makedirs.return_value = None
        
        # Testa captura de tela inteira com salvamento
        save_path = "screenshots/test.png"
        result = self.controller.capture_screen(save_path=save_path)
        
        # Verifica se a imagem foi salva
        mock_screenshot.save.assert_called_once_with(save_path)
        mock_os.makedirs.assert_called_once_with("screenshots", exist_ok=True)
        
        # Testa captura de região
        mock_screenshot.save.reset_mock()
        mock_os.makedirs.reset_mock()
        
        region = (10, 10, 110, 110)  # left, top, right, bottom
        result = self.controller.capture_screen(region=region, save_path=save_path)
        
        # Verifica se a região correta foi usada
        mock_image_grab.grab.assert_called_with(bbox=region)
        mock_screenshot.save.assert_called_once_with(save_path)
        
        # Testa captura sem salvar
        mock_image_grab.grab.reset_mock()
        mock_screenshot.save.reset_mock()
        
        result = self.controller.capture_screen()
        mock_image_grab.grab.assert_called_once_with(bbox=None)
        mock_screenshot.save.assert_not_called()
        self.assertEqual(result, mock_screenshot)
    
    @patch('src.automation.desktop.controller.ImageGrab')
    def test_extract_text_from_screen(self, mock_image_grab):
        """Testa a extração de texto da tela."""
        # Configura o mock para o OCR
        self.mock_pytesseract.image_to_string.return_value = "Texto extraído"
        
        # Testa extração de texto
        text = self.controller.extract_text_from_screen()
        self.assertEqual(text, "Texto extraído")
        
        # Verifica se o OCR foi chamado com a imagem correta
        self.mock_pytesseract.image_to_string.assert_called_once()


if __name__ == '__main__':
    unittest.main()
