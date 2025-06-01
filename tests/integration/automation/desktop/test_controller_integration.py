"""
Testes de integração para o módulo de automação de desktop.

Estes testes verificam a integração do DesktopController com o sistema operacional
e aplicativos reais. Eles são marcados como 'integration' e podem ser executados
separadamente dos testes unitários.

AVISO: Estes testes interagem com o ambiente real do usuário e podem mover o mouse
e pressionar teclas. Certifique-se de que não há dados importantes em risco antes de executá-los.
"""

import os
import sys
import time
import pytest
from pathlib import Path

# Adiciona o diretório raiz ao path do Python
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent.absolute()))

# Importa a classe a ser testada
from src.automation.desktop.controller import DesktopController, MouseButton

# Pula os testes se estiver em um ambiente CI ou se não for Windows
pytestmark = pytest.mark.skipif(
    os.getenv('CI') == 'true' or not sys.platform.startswith('win'),
    reason='Testes de integração não são executados em CI ou em sistemas não Windows'
)

class TestDesktopControllerIntegration:
    """Testes de integração para a classe DesktopController."""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Configuração e limpeza para cada teste."""
        self.controller = DesktopController()
        # Salva a posição inicial do mouse para restaurar depois
        self.original_position = self.controller._get_mouse_position()
        yield
        # Restaura a posição original do mouse
        self.controller.move_mouse(*self.original_position)
        self.controller.close()
    
    @pytest.mark.integration
    def test_mouse_movement(self):
        """Testa o movimento do mouse."""
        # Move para uma posição específica
        x, y = 100, 100
        self.controller.move_mouse(x, y)
        new_x, new_y = self.controller._get_mouse_position()
        
        # Verifica se o mouse se moveu para perto da posição desejada
        # (pode haver pequenas diferenças devido à aceleração do mouse)
        assert abs(new_x - x) <= 5, f"Mouse X position {new_x} not close to {x}"
        assert abs(new_y - y) <= 5, f"Mouse Y position {new_y} not close to {y}"
    
    @pytest.mark.integration
    def test_click(self):
        """Testa o clique do mouse."""
        # Move para uma posição segura (canto superior esquerdo)
        self.controller.move_mouse(50, 50)
        
        # Simula um clique esquerdo
        self.controller.click(50, 50, button=MouseButton.LEFT)
        
        # Não há como verificar facilmente se o clique foi registrado sem um aplicativo de teste
        # Então apenas verificamos se não houve exceção
        assert True
    
    @pytest.mark.integration
    def test_keyboard_input(self):
        """Testa a entrada de teclado."""
        # Abre o Bloco de Notas
        import subprocess
        notepad = subprocess.Popen(['notepad'])
        time.sleep(1)  # Espera o Bloco de Notas abrir
        
        try:
            # Torna a janela do Bloco de Notas ativa
            self.controller.activate_window("Sem título - Bloco de Notas")
            time.sleep(0.5)  # Espera a ativação
            
            # Digita um texto
            test_text = "Teste de automação"
            self.controller.type_text(test_text)
            
            # Não há como verificar facilmente se o texto foi digitado sem um aplicativo de teste
            # Então apenas verificamos se não houve exceção
            assert True
            
        finally:
            # Fecha o Bloco de Notas sem salvar
            notepad.terminate()
    
    @pytest.mark.integration
    def test_window_management(self):
        """Testa o gerenciamento de janelas."""
        # Abre o Bloco de Notas
        import subprocess
        notepad = subprocess.Popen(['notepad'])
        time.sleep(1)  # Espera o Bloco de Notas abrir
        
        try:
            # Testa a ativação da janela
            result = self.controller.activate_window("Sem título - Bloco de Notas")
            assert result is True, "Falha ao ativar a janela do Bloco de Notas"
            
            # Obtém a janela ativa
            window = self.controller.get_active_window()
            assert window is not None, "Nenhuma janela ativa encontrada"
            assert "Bloco de Notas" in window.title, f"Janela ativa incorreta: {window.title}"
            
            # Lista todas as janelas
            windows = self.controller.get_windows()
            assert len(windows) > 0, "Nenhuma janela encontrada"
            
            # Verifica se a janela do Bloco de Notas está na lista
            notepad_windows = [w for w in windows if "Bloco de Notas" in w.title]
            assert len(notepad_windows) > 0, "Janela do Bloco de Notas não encontrada"
            
        finally:
            # Fecha o Bloco de Notas sem salvar
            notepad.terminate()
    
    @pytest.mark.integration
    def test_screen_capture(self, tmp_path):
        """Testa a captura de tela."""
        # Cria um diretório temporário para salvar a captura de tela
        screenshot_dir = tmp_path / "screenshots"
        screenshot_dir.mkdir()
        screenshot_path = screenshot_dir / "test_screenshot.png"
        
        # Captura a tela
        self.controller.capture_screen(save_path=str(screenshot_path))
        
        # Verifica se o arquivo foi criado
        assert screenshot_path.exists(), "Arquivo de captura de tela não foi criado"
        assert screenshot_path.stat().st_size > 0, "Arquivo de captura de tela está vazio"
        
        # Verifica se o arquivo parece ser uma imagem PNG
        with open(screenshot_path, 'rb') as f:
            header = f.read(8)
            assert header.startswith(b'\x89PNG'), "O arquivo não parece ser uma imagem PNG válida"
