"""
Exemplo de uso do módulo de automação de desktop.

Este script demonstra como usar a classe DesktopController para automatizar
tarefas comuns em aplicativos desktop, como navegação, preenchimento de formulários
e interação com janelas.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from time import sleep

# Adiciona o diretório raiz ao path do Python
sys.path.append(str(Path(__file__).parent.parent.absolute()))

from src.automation.desktop import DesktopController, MouseButton, KeyAction

# Configuração básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('desktop_automation.log')
    ]
)

logger = logging.getLogger(__name__)

# Funções de exemplo

def example_mouse_control(desktop: DesktopController):
    """Demonstra o controle do mouse."""
    logger.info("=== Exemplo: Controle do Mouse ===")
    
    # Move o mouse para uma posição específica
    desktop.move_mouse(100, 100)
    logger.info("Mouse movido para (100, 100)")
    sleep(1)
    
    # Clique simples
    desktop.click(200, 200)
    logger.info("Clique simples em (200, 200)")
    sleep(1)
    
    # Clique com o botão direito
    desktop.click(300, 200, button=MouseButton.RIGHT)
    logger.info("Clique com botão direito em (300, 200)")
    sleep(1)
    
    # Duplo clique
    desktop.click(400, 200, clicks=2, interval=0.2)
    logger.info("Duplo clique em (400, 200)")
    sleep(1)
    
    # Roda do mouse
    desktop.scroll(5)  # Rola para cima
    logger.info("Rolagem para cima")
    sleep(1)
    
    desktop.scroll(-5)  # Rola para baixo
    logger.info("Rolagem para baixo")
    sleep(1)


def example_keyboard_control(desktop: DesktopController):
    """Demonstra o controle do teclado."""
    logger.info("\n=== Exemplo: Controle do Teclado ===")
    
    # Digita um texto
    desktop.type_text("Olá, mundo!")
    logger.info("Texto digitado: 'Olá, mundo!'")
    sleep(1)
    
    # Pressiona a tecla Enter
    desktop.press_key("enter")
    logger.info("Tecla Enter pressionada")
    sleep(1)
    
    # Combinação de teclas (Ctrl+A para selecionar tudo)
    desktop.press_key(["ctrl", "a"])
    logger.info("Ctrl+A pressionado")
    sleep(1)
    
    # Pressiona a tecla Delete
    desktop.press_key("delete")
    logger.info("Tecla Delete pressionada")
    sleep(1)

def example_window_management(desktop: DesktopController):
    """Demonstra o gerenciamento de janelas."""
    logger.info("\n=== Exemplo: Gerenciamento de Janelas ===")
    
    # Obtém a janela ativa
    active_window = desktop.get_active_window()
    if active_window:
        logger.info(f"Janela ativa: {active_window.title}")
        logger.info(f"Posição: ({active_window.left}, {active_window.top})")
        logger.info(f"Tamanho: {active_window.width}x{active_window.height}")
    
    # Lista todas as janelas abertas
    windows = desktop.get_windows()
    logger.info(f"\nTotal de janelas abertas: {len(windows)}")
    
    # Exibe os títulos das primeiras 5 janelas
    for i, window in enumerate(windows[:5], 1):
        status = "[ATIVA]" if window.is_active else ""
        logger.info(f"{i}. {window.title} {status}")
    
    # Tenta ativar o Bloco de Notas (se estiver aberto)
    logger.info("\nTentando ativar o Bloco de Notas...")
    if desktop.activate_window("Bloco de Notas"):
        logger.info("Bloco de Notas ativado com sucesso!")
    else:
        logger.info("Bloco de Notas não encontrado.")

def example_screen_capture(desktop: DesktopController):
    """Demonstra a captura de tela e OCR."""
    logger.info("\n=== Exemplo: Captura de Tela e OCR ===")
    
    # Cria um diretório para as capturas de tela, se não existir
    screenshots_dir = Path("screenshots")
    screenshots_dir.mkdir(exist_ok=True)
    
    # Captura a tela inteira
    screenshot_path = screenshots_dir / "tela_inteira.png"
    desktop.capture_screen(save_path=screenshot_path)
    logger.info(f"Captura de tela salva em: {screenshot_path}")
    
    # Captura uma região específica (canto superior esquerdo)
    region = (0, 0, 400, 300)
    region_path = screenshots_dir / "regiao_especifica.png"
    desktop.capture_screen(region=region, save_path=region_path)
    logger.info(f"Captura de região salva em: {region_path}")
    
    # Tenta extrair texto da região capturada
    try:
        text = desktop.extract_text_from_screen(region=region)
        if text:
            logger.info("\nTexto extraído da região:")
            logger.info(text)
        else:
            logger.info("Nenhum texto encontrado na região.")
    except Exception as e:
        logger.warning(f"Não foi possível extrair texto: {e}")

def main():
    """Função principal que executa os exemplos."""
    logger.info("Iniciando exemplos de automação de desktop...")
    
    try:
        # Inicializa o controlador de desktop
        with DesktopController() as desktop:
            logger.info("Controlador de desktop inicializado com sucesso!")
            
            # Executa os exemplos
            example_mouse_control(desktop)
            example_keyboard_control(desktop)
            example_window_management(desktop)
            example_screen_capture(desktop)
            
            logger.info("\nExemplos concluídos com sucesso!")
    
    except Exception as e:
        logger.error(f"Erro durante a execução: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    # Adiciona uma pequena pausa para dar tempo de mudar para a janela desejada
    input("Pressione Enter para começar (mude para a janela onde deseja testar em 5 segundos)...")
    print("Iniciando em 5 segundos...")
    sleep(5)
    
    # Executa a função principal
    sys.exit(main())
