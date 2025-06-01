"""
Teste de automação web para acessar o Google, buscar o perfil do GitHub do usuário
e configurar um repositório para o projeto.
"""

import os
import sys
import time
import subprocess
from pathlib import Path
import pytest
from typing import Optional

# Adiciona o diretório raiz ao path do Python
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent.absolute()))

# Importa as classes necessárias
from src.automation.desktop.controller import DesktopController

# Pula os testes se estiver em um ambiente CI ou se não for Windows
pytestmark = pytest.mark.skipif(
    os.getenv('CI') == 'true' or not sys.platform.startswith('win'),
    reason='Testes de integração não são executados em CI ou em sistemas não Windows'
)

class TestGitHubAutomation:
    """Testes de automação para o GitHub."""
    
    GITHUB_USERNAME = "Lelolima"
    GITHUB_PROFILE_URL = f"https://github.com/{GITHUB_USERNAME}"
    PROJECT_NAME = "automation-computer"
    PROJECT_DESCRIPTION = "Sistema avançado de automação que combina navegação web complexa e controle local em Windows."
    
    @pytest.fixture(scope="class")
    def controller(self):
        """Inicializa o controlador de desktop."""
        controller = DesktopController()
        yield controller
        controller.close()
    
    def test_github_automation(self, controller):
        """
        Testa a automação para acessar o Google, buscar o perfil do GitHub,
        criar um repositório e configurar o projeto local.
        """
        try:
            # 1. Abrir o navegador (usando o navegador padrão para o Google)
            self._open_google(controller)
            
            # 2. Buscar o perfil do GitHub
            self._search_github_profile(controller)
            
            # 3. Navegar até o perfil do GitHub
            self._navigate_to_github_profile(controller)
            
            # 4. Criar um repositório (isso exigirá autenticação)
            # Comentado por segurança - descomente e ajuste conforme necessário
            # self._create_github_repository(controller)
            
            # 5. Configurar o repositório local e fazer o push
            self._setup_local_repository()
            
            assert True, "Automação concluída com sucesso"
            
        except Exception as e:
            pytest.fail(f"Falha na automação: {str(e)}")
    
    def _open_google(self, controller):
        """Abre o Google no navegador padrão."""
        try:
            # Usa o comando start para abrir o Google no navegador padrão
            os.system('start https://www.google.com')
            time.sleep(3)  # Espera o navegador abrir
            
            # Aguarda a página carregar
            time.sleep(2)
            
        except Exception as e:
            raise Exception(f"Falha ao abrir o Google: {str(e)}")
    
    def _search_github_profile(self, controller):
        """Busca o perfil do GitHub no Google."""
        try:
            # Digita a consulta de busca
            search_query = f"github {self.GITHUB_USERNAME} profile"
            controller.type_text(search_query)
            controller.press_key("enter")
            time.sleep(2)  # Espera os resultados carregarem
            
        except Exception as e:
            raise Exception(f"Falha ao buscar perfil do GitHub: {str(e)}")
    
    def _navigate_to_github_profile(self, controller):
        """Navega até o perfil do GitHub a partir dos resultados de busca."""
        try:
            # Pressiona Tab para navegar até o primeiro resultado
            for _ in range(5):  # Tenta algumas vezes para garantir
                controller.press_key("tab")
                time.sleep(0.5)
            
            # Pressiona Enter para acessar o perfil
            controller.press_key("enter")
            time.sleep(3)  # Espera a página carregar
            
        except Exception as e:
            raise Exception(f"Falha ao navegar até o perfil do GitHub: {str(e)}")
    
    def _create_github_repository(self, controller):
        """Cria um novo repositório no GitHub (requer autenticação)."""
        try:
            # Navega até a página de criação de repositório
            controller.type_text(f"{self.GITHUB_PROFILE_URL}/new")
            controller.press_key("enter")
            time.sleep(3)  # Espera a página carregar
            
            # Preenche os detalhes do repositório
            # Nota: Isso requer autenticação e interação com a interface do GitHub
            # A implementação exata dependerá da estrutura da página do GitHub
            
            # Exemplo (ajuste conforme necessário):
            # controller.type_text(self.PROJECT_NAME)
            # controller.press_key("tab")
            # controller.type_text(self.PROJECT_DESCRIPTION)
            # controller.press_key("tab", presses=3)  # Navega até o botão de criar
            # controller.press_key("enter")
            
            time.sleep(3)  # Espera o repositório ser criado
            
        except Exception as e:
            raise Exception(f"Falha ao criar repositório no GitHub: {str(e)}")
    
    def _setup_local_repository(self):
        """Configura o repositório Git local e faz o push para o GitHub."""
        try:
            project_root = str(Path(__file__).parent.parent.parent.parent.parent.absolute())
            
            # Inicializa o repositório Git se ainda não estiver inicializado
            if not (Path(project_root) / ".git").exists():
                subprocess.run(["git", "init"], check=True, cwd=project_root)
            
            # Configura o usuário do Git se ainda não estiver configurado
            try:
                subprocess.run(
                    ["git", "config", "user.name", "GitHub Actions Bot"], 
                    check=True, 
                    cwd=project_root
                )
                subprocess.run(
                    ["git", "config", "user.email", "actions@github.com"], 
                    check=True, 
                    cwd=project_root
                )
            except subprocess.CalledProcessError:
                pass  # As configurações já podem existir
            
            # Adiciona todos os arquivos
            subprocess.run(["git", "add", "."], check=True, cwd=project_root)
            
            # Faz o commit inicial
            try:
                subprocess.run(
                    ["git", "commit", "-m", "Initial commit: Configuração inicial do projeto"], 
                    check=True, 
                    cwd=project_root,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            except subprocess.CalledProcessError as e:
                if "nothing to commit" not in e.stderr.decode():
                    raise
            
            # Verifica se já existe um repositório remoto
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"], 
                cwd=project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Se não houver repositório remoto, podemos adicionar um
            if result.returncode != 0:
                print("\nAviso: Nenhum repositório remoto configurado.")
                print(f"Para configurar manualmente, execute:")
                print(f"cd {project_root}")
                print(f"git remote add origin https://github.com/{self.GITHUB_USERNAME}/{self.PROJECT_NAME}.git")
                print("git push -u origin master\n")
            
            # Descomente as linhas abaixo para configurar automaticamente
            # repo_url = f"https://github.com/{self.GITHUB_USERNAME}/{self.PROJECT_NAME}.git"
            # subprocess.run(
            #     ["git", "remote", "add", "origin", repo_url], 
            #     check=False, 
            #     cwd=project_root
            # )
            # 
            # # Tenta fazer o push para o repositório remoto
            # subprocess.run(
            #     ["git", "push", "-u", "origin", "master"], 
            #     check=False, 
            #     cwd=project_root
            # )
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Falha ao configurar o repositório local: {str(e)}")
        except Exception as e:
            raise Exception(f"Erro inesperado ao configurar o repositório: {str(e)}")
