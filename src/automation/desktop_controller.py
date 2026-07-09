"""
Automation-Computer - Módulo de Automação Desktop
Controle de mouse, teclado e janelas Windows usando pywinauto + pynput

Criado por Wellington de Lima Catarina
"""

from typing import Optional, List
import time
import logging

from pywinauto import Application, findwindows
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController

logger = logging.getLogger(__name__)


class DesktopController:
    """Controlador de automação desktop para Windows."""

    def __init__(self, app_path: Optional[str] = None):
        """
        Inicializa o controlador desktop.

        Args:
            app_path: Caminho para aplicação a ser automatizada (opcional)
        """
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        self.app = None
        self.app_path = app_path
        logger.info("DesktopController inicializado")

    def start_app(self, app_path: str) -> None:
        """
        Inicia uma aplicação.

        Args:
            app_path: Caminho ou comando da aplicação
        """
        try:
            self.app = Application().start(app_path)
            self.app_path = app_path
            logger.info(f"Aplicação iniciada: {app_path}")
        except Exception as e:
            logger.error(f"Erro ao iniciar aplicação: {e}")
            raise

    def connect_app(self, window_title: str) -> None:
        """
        Conecta a uma aplicação já em execução.

        Args:
            window_title: Título da janela para conectar
        """
        try:
            self.app = Application().connect(title=window_title)
            logger.info(f"Conectado à aplicação: {window_title}")
        except Exception as e:
            logger.error(f"Erro ao conectar aplicação: {e}")
            raise

    def click(self, x: int, y: int, button: str = "left", clicks: int = 1) -> None:
        """
        Clica em uma posição específica da tela.

        Args:
            x: Coordenada X
            y: Coordenada Y
            button: 'left', 'right' ou 'middle'
            clicks: Número de cliques
        """
        try:
            self.mouse.position = (x, y)
            button_map = {
                "left": Button.left,
                "right": Button.right,
                "middle": Button.middle
            }
            for _ in range(clicks):
                self.mouse.click(button_map.get(button, Button.left))
                time.sleep(0.1)
            logger.debug(f"Click {button} em ({x}, {y})")
        except Exception as e:
            logger.error(f"Erro ao clicar: {e}")
            raise

    def click_window_element(self, element_id: str, window_title: Optional[str] = None) -> None:
        """
        Clica em um elemento de janela específico.

        Args:
            element_id: ID ou título do elemento
            window_title: Título da janela (usa app atual se None)
        """
        try:
            if window_title:
                self.connect_app(window_title)

            if self.app:
                window = self.app.top_window()
                element = window.child_window(title=element_id)
                if element.exists():
                    element.click_input()
                    logger.info(f"Clicado elemento: {element_id}")
                else:
                    logger.warning(f"Elemento não encontrado: {element_id}")
        except Exception as e:
            logger.error(f"Erro ao clicar elemento: {e}")
            raise

    def type_text(self, text: str, delay: float = 0.05) -> None:
        """
        Digita um texto.

        Args:
            text: Texto para digitar
            delay: Delay entre teclas (segundos)
        """
        try:
            for char in text:
                self.keyboard.press(char)
                self.keyboard.release(char)
                time.sleep(delay)
            logger.debug(f"Texto digitado: {text[:20]}...")
        except Exception as e:
            logger.error(f"Erro ao digitar: {e}")
            raise

    def press_key(self, key: str) -> None:
        """
        Pressiona uma tecla específica.

        Args:
            key: Nome da tecla (ex: 'enter', 'tab', 'ctrl_c')
        """
        try:
            key_map = {
                'enter': Key.enter,
                'tab': Key.tab,
                'esc': Key.esc,
                'space': Key.space,
                'backspace': Key.backspace,
                'delete': Key.delete,
            }

            if key in key_map:
                self.keyboard.press(key_map[key])
                self.keyboard.release(key_map[key])
            elif key == 'ctrl_c':
                self._press_hotkey(Key.ctrl, 'c')
            elif key == 'ctrl_v':
                self._press_hotkey(Key.ctrl, 'v')
            elif key == 'ctrl_a':
                self._press_hotkey(Key.ctrl, 'a')
            else:
                self.keyboard.press(key)
                self.keyboard.release(key)

            logger.debug(f"Tecla pressionada: {key}")
        except Exception as e:
            logger.error(f"Erro ao pressionar tecla: {e}")
            raise

    def move_to(self, x: int, y: int) -> None:
        """
        Move o mouse para uma posição.

        Args:
            x: Coordenada X
            y: Coordenada Y
        """
        try:
            self.mouse.position = (x, y)
            logger.debug(f"Mouse movido para ({x}, {y})")
        except Exception as e:
            logger.error(f"Erro ao mover mouse: {e}")
            raise

    def scroll(self, x: int, y: int, dx: int = 0, dy: int = 0) -> None:
        """
        Scroll na posição especificada.

        Args:
            x: Coordenada X
            y: Coordenada Y
            dx: Scroll horizontal
            dy: Scroll vertical
        """
        try:
            self.mouse.position = (x, y)
            self.mouse.scroll(dx, dy)
            logger.debug(f"Scroll em ({x}, {y}): dx={dx}, dy={dy}")
        except Exception as e:
            logger.error(f"Erro ao scrollar: {e}")
            raise

    def get_window_handle(self, title: str) -> Optional[str]:
        """
        Obtém o handle de uma janela pelo título.

        Args:
            title: Título da janela

        Returns:
            Handle da janela ou None se não encontrada
        """
        try:
            windows = findwindows.find_windows(title=title)
            if windows:
                handle = str(windows[0])
                logger.info(f"Window handle encontrado: {handle}")
                return handle
            logger.warning(f"Janela não encontrada: {title}")
            return None
        except Exception as e:
            logger.error(f"Erro ao encontrar janela: {e}")
            return None

    def minimize_window(self, window_title: str) -> None:
        """Minimiza uma janela."""
        try:
            self.connect_app(window_title)
            if self.app:
                window = self.app.top_window()
                window.minimize()
                logger.info(f"Janela minimizada: {window_title}")
        except Exception as e:
            logger.error(f"Erro ao minimizar: {e}")
            raise

    def maximize_window(self, window_title: str) -> None:
        """Maximiza uma janela."""
        try:
            self.connect_app(window_title)
            if self.app:
                window = self.app.top_window()
                window.maximize()
                logger.info(f"Janela maximizada: {window_title}")
        except Exception as e:
            logger.error(f"Erro ao maximizar: {e}")
            raise

    def close_window(self, window_title: str) -> None:
        """Fecha uma janela."""
        try:
            self.connect_app(window_title)
            if self.app:
                window = self.app.top_window()
                window.close()
                logger.info(f"Janela fechada: {window_title}")
        except Exception as e:
            logger.error(f"Erro ao fechar: {e}")
            raise

    def _press_hotkey(self, modifier, key: str) -> None:
        """
        Pressiona uma combinação de teclas (hotkey).

        Args:
            modifier: Tecla modificadora (ex: Key.ctrl)
            key: Tecla a ser pressionada com o modificador
        """
        self.keyboard.press(modifier)
        self.keyboard.press(key)
        self.keyboard.release(key)
        self.keyboard.release(modifier)