"""
Configuração do pytest para carregar variáveis de ambiente de teste.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env.test
env_path = Path(__file__).parent / ".env.test"
load_dotenv(dotenv_path=env_path)

# Configura o ambiente para teste
os.environ["ENVIRONMENT"] = "test"
os.environ["PYTHONPATH"] = str(Path(__file__).parent.absolute())
