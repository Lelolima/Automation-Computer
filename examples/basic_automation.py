"""
Automation-Computer - Exemplo de Automação Básica
Este script demonstra como usar o DesktopController para automação simples.

Criado por Wellington de Lima Catarina
"""

import time
from src.automation.desktop_controller import DesktopController


def main():
    """Exemplo de automação desktop."""
    print("=" * 60)
    print("  AUTOMATION-COMPUTER - Exemplo de Automação Desktop")
    print("=" * 60)

    # Inicializar controlador
    desktop = DesktopController()

    print("\n1. Abrindo Bloco de Notas...")
    desktop.start_app("notepad.exe")
    time.sleep(2)

    print("2. Digitando texto...")
    desktop.type_text("Olá, Automation-Computer!")
    desktop.press_key("enter")
    desktop.type_text("Este é um teste de automação desktop.")
    desktop.press_key("enter")
    desktop.type_text("Data: " + time.strftime("%d/%m/%Y %H:%M:%S"))

    print("3. Selecionando texto (Ctrl+A)...")
    time.sleep(1)
    desktop.press_key("ctrl_a")

    print("\nTeste concluído!")
    print("\nObservação: O Bloco de Notas permanece aberto para revisão.")


if __name__ == "__main__":
    main()