"""
Módulo de exemplos para demonstração das funcionalidades do sistema de automação.

Este pacote contém exemplos práticos de como utilizar os diferentes módulos do sistema,
incluindo automação web, automação desktop, integração com LLM e funcionalidades de segurança.
"""

from pathlib import Path

# Caminho para o diretório de exemplos
EXAMPLES_DIR = Path(__file__).parent.absolute()

# Lista de exemplos disponíveis
AVAILABLE_EXAMPLES = [
    'web_automation_example.py',
    'desktop_automation_example.py',
    'llm_integration_example.py',
    'security_example.py'
]

def get_example_path(example_name: str) -> Path:
    """
    Retorna o caminho completo para um arquivo de exemplo.
    
    Args:
        example_name: Nome do arquivo de exemplo (com ou sem a extensão .py)
        
    Returns:
        Path: Caminho completo para o arquivo de exemplo
        
    Raises:
        FileNotFoundError: Se o exemplo não for encontrado
    """
    if not example_name.endswith('.py'):
        example_name += '.py'
    
    example_path = EXAMPLES_DIR / example_name
    
    if not example_path.exists():
        available = '\n  - '.join(AVAILABLE_EXAMPLES)
        raise FileNotFoundError(
            f"Exemplo '{example_name}' não encontrado.\n"
            f"Exemplos disponíveis:\n  - {available}"
        )
    
    return example_path
