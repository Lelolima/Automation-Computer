"""
Módulo de controle de desktop do Agente de Automação Integrada.

Fornece funcionalidades para automação de aplicativos desktop, incluindo:
- Controle de mouse e teclado
- Gerenciamento de janelas
- Captura de tela
- Reconhecimento de imagens na tela
"""

import logging
import os
import time
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional, Tuple, Union

import pyautogui
import pygetwindow as gw
import pytesseract
from PIL import Image, ImageGrab

from src.config import settings

# Configuração de logging
logger = logging.getLogger(__name__)

# Configura o PyAutoGUI
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1


class DesktopAutomationError(Exception):
    """Exceção para erros de automação de desktop."""
    pass


class MouseButton(Enum):
    """Enumeração para botões do mouse."""
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"


class KeyAction(Enum):
    """Enumeração para ações de teclas."""
    PRESS = auto()
    DOWN = auto()
    UP = auto()


@dataclass
class WindowInfo:
    """Classe para armazenar informações sobre uma janela."""
    title: str
    left: int
    top: int
    width: int
    height: int
    is_active: bool = False
    is_maximized: bool = False
    is_minimized: bool = False
    process_id: Optional[int] = None
    process_name: Optional[str] = None
    
    @property
    def right(self) -> int:
        """Retorna a coordenada x da borda direita da janela."""
        return self.left + self.width
    
    @property
    def bottom(self) -> int:
        """Retorna a coordenada y da borda inferior da janela."""
        return self.top + self.height
    
    @property
    def center(self) -> Tuple[int, int]:
        """Retorna as coordenadas do centro da janela."""
        return (self.left + self.width // 2, self.top + self.height // 2)
    
    def contains_point(self, x: int, y: int) -> bool:
        """Verifica se um ponto (x, y) está dentro da janela."""
        return (self.left <= x <= self.right and 
                self.top <= y <= self.bottom)


class DesktopController:
    """Classe para controle de automação de desktop."""
    
    def __init__(self, fail_safe: bool = True, pause: float = 0.1):
        """Inicializa o controlador de desktop.
        
        Args:
            fail_safe: Se True, permite interromper o movimento do mouse para um canto da tela.
            pause: Tempo de pausa entre ações do PyAutoGUI.
        """
        pyautogui.FAILSAFE = fail_safe
        pyautogui.PAUSE = pause
        
        # Configura o caminho para o Tesseract OCR, se disponível
        try:
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        except Exception as e:
            logger.warning(f"Tesseract OCR não encontrado: {e}")
    
    # Métodos de controle de mouse
    def move_mouse(self, x: int, y: int, duration: float = 0.5) -> None:
        """Move o mouse para as coordenadas (x, y).
        
        Args:
            x: Coordenada x.
            y: Coordenada y.
            duration: Duração da animação do movimento em segundos.
        """
        try:
            pyautogui.moveTo(x, y, duration=duration, tween=pyautogui.easeInOutQuad)
            logger.debug(f"Mouse movido para ({x}, {y})")
        except Exception as e:
            raise DesktopAutomationError(f"Falha ao mover o mouse: {e}")
    
    def click(
        self, 
        x: Optional[int] = None, 
        y: Optional[int] = None, 
        button: MouseButton = MouseButton.LEFT,
        clicks: int = 1,
        interval: float = 0.1
    ) -> None:
        """Realiza um clique do mouse.
        
        Args:
            x: Coordenada x. Se None, usa a posição atual do mouse.
            y: Coordenada y. Se None, usa a posição atual do mouse.
            button: Botão do mouse a ser clicado.
            clicks: Número de cliques.
            interval: Intervalo entre cliques em segundos.
        """
        try:
            if x is not None and y is not None:
                self.move_mouse(x, y)
            
            pyautogui.click(
                x=x, 
                y=y, 
                button=button.value,
                clicks=clicks,
                interval=interval
            )
            logger.debug(f"Clicado no botão {button.value} em ({x or 'current'}, {y or 'current'})")
        except Exception as e:
            raise DesktopAutomationError(f"Falha ao clicar: {e}")
    
    def scroll(self, clicks: int, x: Optional[int] = None, y: Optional[int] = None) -> None:
        """Rola a roda do mouse.
        
        Args:
            clicks: Número de cliques para rolar. Positivo para cima, negativo para baixo.
            x: Coordenada x. Se None, usa a posição atual do mouse.
            y: Coordenada y. Se None, usa a posição atual do mouse.
        """
        try:
            if x is not None and y is not None:
                self.move_mouse(x, y)
            
            pyautogui.scroll(clicks)
            logger.debug(f"Rolado {clicks} cliques")
        except Exception as e:
            raise DesktopAutomationError(f"Falha ao rolar: {e}")
    
    # Métodos de controle de teclado
    def type_text(self, text: str, interval: float = 0.1) -> None:
        """Digita um texto.
        
        Args:
            text: Texto a ser digitado.
            interval: Intervalo entre as teclas em segundos.
        """
        try:
            pyautogui.write(text, interval=interval)
            logger.debug(f"Texto digitado: '{text}'")
        except Exception as e:
            raise DesktopAutomationError(f"Falha ao digitar texto: {e}")
    
    def press_key(
        self, 
        keys: Union[str, List[str]], 
        action: KeyAction = KeyAction.PRESS,
        presses: int = 1,
        interval: float = 0.1
    ) -> None:
        """Pressiona uma tecla ou combinação de teclas.
        
        Args:
            keys: Tecla ou lista de teclas a serem pressionadas.
            action: Ação a ser realizada (pressionar, segurar ou soltar).
            presses: Número de vezes que a tecla será pressionada.
            interval: Intervalo entre as pressões em segundos.
        """
        try:
            if isinstance(keys, str):
                keys = [keys]
            
            if action == KeyAction.PRESS:
                pyautogui.hotkey(*keys)
                logger.debug(f"Teclas pressionadas: {'+'.join(keys)}")
            elif action == KeyAction.DOWN:
                for key in keys:
                    pyautogui.keyDown(key)
                logger.debug(f"Teclas pressionadas (segurando): {'+'.join(keys)}")
            elif action == KeyAction.UP:
                for key in reversed(keys):
                    pyautogui.keyUp(key)
                logger.debug(f"Teclas liberadas: {'+'.join(keys)}")
        except Exception as e:
            raise DesktopAutomationError(f"Falha ao pressionar teclas: {e}")
    
    # Métodos de gerenciamento de janelas
    def get_active_window(self) -> Optional[WindowInfo]:
        """Obtém informações sobre a janela ativa.
        
        Returns:
            Informações sobre a janela ativa ou None se não houver janela ativa.
        """
        try:
            window = gw.getActiveWindow()
            if window:
                return self._convert_to_window_info(window, is_active=True)
            return None
        except Exception as e:
            raise DesktopAutomationError(f"Falha ao obter janela ativa: {e}")
    
    def get_windows(self, title: Optional[str] = None) -> List[WindowInfo]:
        """Obtém uma lista de janelas abertas.
        
        Args:
            title: Título da janela para filtrar (opcional).
            
        Returns:
            Lista de janelas que correspondem ao filtro.
        """
        try:
            windows = gw.getWindowsWithTitle(title) if title else gw.getAllWindows()
            active_window = gw.getActiveWindow()
            
            result = []
            for window in windows:
                if window and window.title:  # Filtra janelas inválidas
                    is_active = (window == active_window)
                    result.append(self._convert_to_window_info(window, is_active))
            
            return result
        except Exception as e:
            raise DesktopAutomationError(f"Falha ao obter janelas: {e}")
    
    def activate_window(self, title: str) -> bool:
        """Ativa uma janela pelo título.
        
        Args:
            title: Título da janela a ser ativada.
            
        Returns:
            True se a janela foi ativada com sucesso, False caso contrário.
        """
        try:
            windows = gw.getWindowsWithTitle(title)
            if windows:
                window = windows[0]
                if window.isMinimized:
                    window.restore()
                window.activate()
                logger.debug(f"Janela ativada: {title}")
                return True
            return False
        except Exception as e:
            raise DesktopAutomationError(f"Falha ao ativar janela '{title}': {e}")
    
    # Métodos de captura de tela e OCR
    def capture_screen(
        self, 
        region: Optional[Tuple[int, int, int, int]] = None, 
        save_path: Optional[Union[str, Path]] = None
    ) -> Image.Image:
        """Captura a tela ou uma região da tela.
        
        Args:
            region: Região a ser capturada (left, top, width, height). Se None, captura a tela inteira.
            save_path: Caminho para salvar a captura de tela (opcional).
            
        Returns:
            Imagem capturada como um objeto PIL.Image.
        """
        try:
            # Always pass bbox to maintain consistent behavior in tests
            screenshot = ImageGrab.grab(bbox=region) if region is not None else ImageGrab.grab(bbox=None)
            
            if save_path:
                # Ensure the directory exists
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                screenshot.save(save_path)
                logger.debug(f"Captura de tela salva em: {save_path}")
            
            return screenshot
        except Exception as e:
            raise DesktopAutomationError(f"Falha ao capturar tela: {e}")
    
    def find_image_on_screen(
        self, 
        image_path: Union[str, Path], 
        confidence: float = 0.8,
        grayscale: bool = True,
        region: Optional[Tuple[int, int, int, int]] = None
    ) -> Optional[Tuple[int, int]]:
        """Localiza uma imagem na tela.
        
        Args:
            image_path: Caminho para a imagem a ser localizada.
            confidence: Nível de confiança para a correspondência (0 a 1).
            grayscale: Se True, converte a imagem para tons de cinza antes da busca.
            region: Região da tela para buscar (left, top, width, height).
            
        Returns:
            Coordenadas (x, y) do centro da imagem encontrada ou None se não encontrada.
        """
        try:
            location = pyautogui.locateOnScreen(
                str(image_path),
                confidence=confidence,
                grayscale=grayscale,
                region=region
            )
            
            if location:
                center = pyautogui.center(location)
                logger.debug(f"Imagem encontrada em: {center}")
                return (center.x, center.y)
            
            logger.debug("Imagem não encontrada na tela")
            return None
        except Exception as e:
            raise DesktopAutomationError(f"Falha ao localizar imagem: {e}")
    
    def extract_text_from_screen(
        self, 
        region: Optional[Tuple[int, int, int, int]] = None,
        lang: str = 'por+eng',
        config: str = '--psm 6'
    ) -> str:
        """Extrai texto da tela usando OCR.
        
        Args:
            region: Região da tela para extrair texto (left, top, width, height).
            lang: Idiomas para reconhecimento (padrão: português + inglês).
            config: Configuração do Tesseract OCR.
            
        Returns:
            Texto extraído da imagem.
        """
        try:
            # Captura a região da tela
            screenshot = self.capture_screen(region=region)
            
            # Usa o Tesseract OCR para extrair o texto
            text = pytesseract.image_to_string(screenshot, lang=lang, config=config)
            
            logger.debug(f"Texto extraído: {text[:100]}...")
            return text.strip()
        except Exception as e:
            raise DesktopAutomationError(f"Falha ao extrair texto da tela: {e}")
    
    # Métodos auxiliares
    @staticmethod
    def _convert_to_window_info(window: Any, is_active: bool = False) -> WindowInfo:
        """Converte uma janela do PyGetWindow para WindowInfo."""
        return WindowInfo(
            title=window.title,
            left=window.left,
            top=window.top,
            width=window.width,
            height=window.height,
            is_active=is_active,
            is_maximized=window.isMaximized,
            is_minimized=window.isMinimized,
        )
    
    # Métodos de contexto
    def __enter__(self):
        """Suporte ao gerenciador de contexto."""
        return self
    
    def _get_mouse_position(self) -> Tuple[int, int]:
        """Obtém a posição atual do mouse.
        
        Returns:
            Tupla com as coordenadas (x, y) atuais do mouse.
        """
        try:
            return pyautogui.position()
        except Exception as e:
            raise DesktopAutomationError(f"Falha ao obter posição do mouse: {e}")
    
    def close(self):
        """Libera recursos utilizados pelo controlador."""
        # Atualmente não há recursos para liberar, mas este método é mantido para compatibilidade
        # com o gerenciador de contexto e testes.
        pass
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Garante que os recursos sejam liberados ao sair do contexto."""
        self.close()
