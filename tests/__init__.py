"""
Testes __init__ para configuração do pytest
"""

import sys
from pathlib import Path

# Adicionar src ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))