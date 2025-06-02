# NOME_DO_ARQUIVO.py: config.py
# Descrição: Módulo de configuração do Agente de Automação. Centraliza o gerenciamento de configurações do sistema utilizando Pydantic e arquivos .env.
# Responsabilidades: Definir e validar todas as configurações da aplicação, carregar variáveis de ambiente, e fornecer uma instância global de configurações (`settings`). Configurar o sistema de logging.
# Dependências: os, pathlib, typing, dotenv, pydantic, pydantic_settings.
# Padrões aplicados: Pydantic BaseSettings para gerenciamento de configurações, Carregamento de variáveis de ambiente de arquivo .env, Validadores Pydantic para campos específicos, Configuração centralizada de logging.
# Autor: Autor Original Desconhecido
# Última modificação: 2024-07-26

"""
Módulo de configuração do Agente de Automação.
Centraliza o gerenciamento de configurações do sistema.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

# RACIOCÍNIO: `python-dotenv` é usado para carregar variáveis de ambiente de um arquivo `.env`.
# Isso é útil para desenvolvimento local, permitindo definir configurações sem modificar
# o ambiente global do sistema ou hardcodar valores sensíveis. Em produção, as variáveis
# de ambiente são geralmente definidas diretamente no ambiente de hospedagem.
from dotenv import load_dotenv
# RACIOCÍNIO: Pydantic é usado para definir modelos de configurações com tipagem e validação.
# `Field` permite adicionar metadados e validações aos campos. `validator` para validadores customizados.
from pydantic import Field, validator
# `AnyHttpUrl` e `PostgresDsn` são tipos específicos do Pydantic para validar URLs e DSNs do Postgres.
from pydantic.networks import AnyHttpUrl, PostgresDsn # Embora não usados ativamente no código visível, são bons exemplos de tipos Pydantic.
# `BaseSettings` de `pydantic-settings` (anteriormente `pydantic.BaseSettings`) é a classe base
# para carregar configurações de variáveis de ambiente e arquivos .env automaticamente.
from pydantic_settings import BaseSettings

# ESTRATÉGIA: Carregar o arquivo .env no início do módulo.
# Isso garante que as variáveis de ambiente definidas no .env estejam disponíveis
# quando a instância de `Settings` for criada.
load_dotenv()

# CONFIGURAÇÃO: Define o diretório base do projeto.
# RACIOCÍNIO: `Path(__file__).parent` refere-se ao diretório do arquivo atual (`src/config.py`, então `src`).
# `.parent` novamente sobe para o diretório raiz do projeto. `.absolute()` obtém o caminho absoluto.
# `BASE_DIR` é útil para construir caminhos para outros arquivos e diretórios no projeto (ex: logs, templates).
BASE_DIR = Path(__file__).parent.parent.absolute()

# ESTRATÉGIA: Usar Pydantic `BaseSettings` para gerenciar todas as configurações da aplicação.
# Benefícios:
# - Validação de tipo: Garante que as configurações tenham os tipos esperados (ex: bool, int, str).
# - Valores padrão: Permite definir valores padrão se uma variável de ambiente não for encontrada.
# - Carregamento de .env: Automaticamente carrega variáveis de arquivos .env.
# - Sensibilidade a maiúsculas/minúsculas configurável.
# - Clareza: Todas as configurações são definidas explicitamente em uma classe.
class Settings(BaseSettings):
    """Configurações da aplicação. Carrega de variáveis de ambiente e arquivos .env."""

    # --- Configurações Básicas ---
    # CONFIGURAÇÃO: Modo Debug. Se True, pode habilitar logging mais verboso, mostrar erros detalhados, etc.
    # DECISÃO: Padrão `False` para segurança em produção. Carregado da var env `DEBUG`.
    DEBUG: bool = Field(default=False, env="DEBUG")
    # CONFIGURAÇÃO: Ambiente da aplicação (ex: "development", "staging", "production").
    # RACIOCÍNIO: Permite que a aplicação se comporte de maneira diferente com base no ambiente.
    # DECISÃO: Padrão "development". Carregado da var env `ENVIRONMENT`.
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    # CONFIGURAÇÃO: Chave secreta usada para operações criptográficas (ex: assinatura de JWTs, cookies seguros).
    # RACIOCÍNIO: Deve ser uma string longa, aleatória e mantida em segredo absoluto em produção.
    # DECISÃO: `...` (Ellipsis) indica que este campo é obrigatório e deve ser fornecido (via var env `SECRET_KEY`).
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    # CONFIGURAÇÃO: Chave usada para criptografia simétrica de dados sensíveis.
    # RACIOCÍNIO: Similar à SECRET_KEY, deve ser forte e secreta. Usada pelo `EncryptionManager`.
    # DECISÃO: Obrigatória, carregada da var env `ENCRYPTION_KEY`.
    ENCRYPTION_KEY: str = Field(..., env="ENCRYPTION_KEY")

    # --- Configurações de Log ---
    # CONFIGURAÇÃO: Nível de logging (ex: "DEBUG", "INFO", "WARNING", "ERROR").
    # DECISÃO: Padrão "INFO" é um bom equilíbrio para produção. Carregado da var env `LOG_LEVEL`.
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    # CONFIGURAÇÃO: Caminho para o arquivo de log.
    # DECISÃO: Padrão é um arquivo `automation.log` dentro de uma pasta `logs` no `BASE_DIR`.
    # O validador `validate_log_file` garante que o diretório `logs` seja criado.
    LOG_FILE: Path = Field(default=BASE_DIR / "logs" / "automation.log", env="LOG_FILE")

    # --- Configurações de API (se aplicável, para um servidor web em torno do agente) ---
    # CONFIGURAÇÃO: Prefixo base para todas as rotas da API.
    API_PREFIX: str = "/api/v1"
    # CONFIGURAÇÃO: Título da API (usado em documentação OpenAPI/Swagger).
    API_TITLE: str = "Automation Agent API"
    # CONFIGURAÇÃO: Descrição da API.
    API_DESCRIPTION: str = "API para o Agente de Automação Integrada"
    # CONFIGURAÇÃO: Versão da API.
    API_VERSION: str = "0.1.0"

    # --- Configurações de Segurança (relacionadas a tokens, etc.) ---
    # CONFIGURAÇÃO: Algoritmo usado para assinar JWTs.
    # DECISÃO: "HS256" (HMAC com SHA-256) é um algoritmo comum e seguro para JWTs simétricos.
    SECURITY_ALGORITHM: str = "HS256"
    # CONFIGURAÇÃO: Tempo de expiração para tokens de acesso em minutos.
    # DECISÃO: 7 dias (60 min * 24 horas * 7 dias) é um exemplo; pode ser mais curto (ex: 15-60 min) para maior segurança.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 dias
    # CONFIGURAÇÃO: Tempo de expiração para tokens de atualização em dias.
    # RACIOCÍNIO: Refresh tokens têm vida mais longa para permitir que usuários permaneçam logados por mais tempo sem reinserir credenciais.
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # --- Configurações de Banco de Dados ---
    # CONFIGURAÇÃO: URL de conexão com o banco de dados principal.
    # RACIOCÍNIO: Formato DSN (Data Source Name) que especifica o tipo de DB, usuário, senha, host, porta, nome do DB.
    # DECISÃO: Obrigatória, carregada da var env `DATABASE_URL`. O validador fornece um fallback para SQLite.
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    # CONFIGURAÇÃO: URL de conexão para o banco de dados de teste.
    # RACIOCÍNIO: Permite usar um banco de dados separado para testes automatizados, evitando interferência com dados de desenvolvimento/produção.
    # DECISÃO: Opcional. Se não definida, os testes podem usar o `DATABASE_URL` ou um SQLite em memória.
    TEST_DATABASE_URL: Optional[str] = Field(None, env="TEST_DATABASE_URL")
    # CONFIGURAÇÃO: URL de conexão com o Redis (se usado para cache, filas, etc.).
    # DECISÃO: Obrigatória, carregada da var env `REDIS_URL`.
    REDIS_URL: str = Field(..., env="REDIS_URL")

    # --- Configurações de LLM (Large Language Model) ---
    # CONFIGURAÇÃO: Chaves de API para diferentes provedores de LLM.
    # RACIOCÍNIO: Permite que a aplicação se integre com modelos de linguagem de diferentes empresas.
    # DECISÃO: Opcionais, pois nem todos os provedores podem ser usados.
    OPENAI_API_KEY: Optional[str] = Field(None, env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    GOOGLE_API_KEY: Optional[str] = Field(None, env="GOOGLE_API_KEY")
    # CONFIGURAÇÃO: Provedor de LLM padrão a ser usado.
    # DECISÃO: "openai" como padrão.
    LLM_PROVIDER: str = Field(default="openai", env="LLM_PROVIDER")
    # CONFIGURAÇÃO: Modelo específico do LLM a ser usado.
    # DECISÃO: "gpt-4" como padrão.
    LLM_MODEL: str = Field(default="gpt-4", env="LLM_MODEL")
    # CONFIGURAÇÃO: Temperatura para a geração do LLM (controla a aleatoriedade/criatividade).
    # DECISÃO: 0.7 é um valor comum para equilíbrio.
    LLM_TEMPERATURE: float = Field(default=0.7, env="LLM_TEMPERATURE")
    # CONFIGURAÇÃO: Número máximo de tokens a serem gerados pelo LLM em uma resposta.
    LLM_MAX_TOKENS: int = Field(default=2000, env="LLM_MAX_TOKENS")

    # --- Configurações de Navegador (para automação web) ---
    # CONFIGURAÇÃO: Navegador padrão para automação.
    # DECISÃO: "chrome" como padrão. Comentário indica outras opções.
    BROWSER: str = Field(default="chrome", env="BROWSER")  # chrome, firefox, edge
    # CONFIGURAÇÃO: Se o navegador deve rodar em modo headless (sem UI visível).
    # DECISÃO: `False` por padrão para facilitar a depuração visual durante o desenvolvimento. Pode ser `True` em produção/CI.
    HEADLESS: bool = Field(default=False, env="HEADLESS")
    # CONFIGURAÇÃO: Largura padrão da janela do navegador.
    WINDOW_WIDTH: int = Field(default=1280, env="WINDOW_WIDTH")
    # CONFIGURAÇÃO: Altura padrão da janela do navegador.
    WINDOW_HEIGHT: int = Field(default=800, env="WINDOW_HEIGHT")

    # --- Configurações de Segurança Avançadas (específicas do agente) ---
    # CONFIGURAÇÃO: Número máximo de tarefas de automação concorrentes.
    # RACIOCÍNIO: Limita o uso de recursos e potenciais abusos.
    MAX_CONCURRENT_TASKS: int = Field(default=5, env="MAX_CONCURRENT_TASKS")
    # CONFIGURAÇÃO: Se comandos perigosos (ex: `rm -rf /`) devem ser bloqueados.
    # RACIOCÍNIO: Medida de segurança para evitar que o agente execute comandos destrutivos.
    BLOCK_DANGEROUS_COMMANDS: bool = Field(default=True, env="BLOCK_DANGEROUS_COMMANDS")
    # CONFIGURAÇÃO: Se a autenticação é necessária para interagir com o agente.
    REQUIRE_AUTHENTICATION: bool = Field(default=True, env="REQUIRE_AUTHENTICATION")

    # --- Configurações de Voz (para interações de voz, se aplicável) ---
    # CONFIGURAÇÃO: Idioma padrão para reconhecimento e síntese de voz.
    VOICE_LANGUAGE: str = Field(default="pt-BR", env="VOICE_LANGUAGE")
    # CONFIGURAÇÃO: Velocidade da fala para síntese de voz.
    VOICE_RATE: int = Field(default=150, env="VOICE_RATE")

    # CONFIGURAÇÃO: Configurações internas do Pydantic para o carregamento de settings.
    class Config:
        # DECISÃO: `case_sensitive = True` significa que os nomes das variáveis de ambiente devem corresponder exatamente (maiúsculas/minúsculas).
        case_sensitive = True
        # DECISÃO: Especifica o nome do arquivo .env a ser carregado.
        env_file = ".env"
        # DECISÃO: Encoding do arquivo .env.
        env_file_encoding = "utf-8"

    # ESTRATÉGIA: Usar validadores Pydantic para processar ou validar campos específicos após serem carregados.
    # RACIOCÍNIO: `@validator("DATABASE_URL", pre=True)`: O validador é chamado *antes* da tentativa de parsear/validar o tipo do campo.
    # `pre=True` permite modificar o valor antes da validação principal.
    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v: Optional[str]) -> str:
        """Fornece um fallback para SQLite se DATABASE_URL não estiver definida."""
        # LÓGICA: Se `v` (o valor de DATABASE_URL) for None ou string vazia (Falsy),
        # define um fallback para um banco de dados SQLite no `BASE_DIR`.
        # RACIOCÍNIO: Facilita o início rápido do desenvolvimento sem precisar configurar um DB externo.
        if not v:
            # DECISÃO: Usar um arquivo `sqlite.db` no diretório base como fallback.
            return f"sqlite:///{BASE_DIR}/sqlite.db"
        return v

    # RACIOCÍNIO: `@validator("LOG_FILE")`: Chamado *após* o valor ser carregado e convertido para `Path`.
    @validator("LOG_FILE")
    def validate_log_file(cls, v: Path) -> Path:
        """Garante que o diretório pai do arquivo de log exista."""
        # LÓGICA: Antes de a aplicação tentar escrever no arquivo de log,
        # este validador garante que o diretório onde o arquivo será colocado exista.
        # `v.parent` obtém o diretório pai, `mkdir(parents=True, exist_ok=True)` cria
        # o diretório e quaisquer pais necessários, sem erro se já existirem.
        v.parent.mkdir(parents=True, exist_ok=True)
        return v

    # ESTRATÉGIA: Método auxiliar para lógica de configuração mais complexa.
    def get_database_url(self) -> str:
        """Retorna a URL do banco de dados apropriada para o ambiente."""
        # LÓGICA: Se o ambiente for "test" e `TEST_DATABASE_URL` estiver definida, usá-la.
        # Caso contrário, usar a `DATABASE_URL` principal.
        # RACIOCÍNIO: Permite que os testes usem um banco de dados dedicado e isolado.
        if self.ENVIRONMENT == "test" and self.TEST_DATABASE_URL:
            return self.TEST_DATABASE_URL
        return self.DATABASE_URL

# ESTRATÉGIA: Criar uma instância global única da classe `Settings`.
# RACIOCÍNIO: `settings` será importado em outros módulos da aplicação para acessar
# as configurações de forma consistente e centralizada.
# A criação da instância aqui garante que as variáveis de ambiente e o .env
# sejam lidos e validados no momento da importação do módulo `config`.
settings = Settings()

# --- Configuração de Logging ---
# ESTRATÉGIA: Definir a configuração de logging como um dicionário,
# que pode ser usado com `logging.config.dictConfig()`.
# RACIOCÍNIO: Centraliza a configuração de logging, tornando-a consistente em toda a aplicação.
LOGGING_CONFIG = {
    "version": 1, # Versão do schema de configuração de logging.
    "disable_existing_loggers": False, # DECISÃO: Não desabilitar loggers existentes (ex: de bibliotecas).
                                      # Pode ser definido como True se houver conflitos ou para controle total.
    "formatters": {
        # CONFIGURAÇÃO: Define formatos de mensagem de log.
        "standard": {
            # `format`: Define o layout da mensagem de log.
            #   %(asctime)s: Data/hora do log.
            #   %(levelname)s: Nível do log (INFO, DEBUG, etc.).
            #   %(name)s: Nome do logger (geralmente o nome do módulo).
            #   %(message)s: A mensagem de log real.
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            # `datefmt`: Define o formato da data/hora em `%(asctime)s`.
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        # CONFIGURAÇÃO: Define para onde as mensagens de log são enviadas.
        "console": {
            # Handler para enviar logs para o console (stdout).
            "level": settings.LOG_LEVEL, # Nível de log para este handler, controlado pela configuração global.
            "formatter": "standard",     # Usa o formatter "standard" definido acima.
            "class": "logging.StreamHandler", # Classe do handler.
            "stream": "ext://sys.stdout", # Envia para a saída padrão.
        },
        "file": {
            # Handler para enviar logs para um arquivo com rotação.
            "level": settings.LOG_LEVEL, # Nível de log para este handler.
            "formatter": "standard",     # Usa o formatter "standard".
            "class": "logging.handlers.RotatingFileHandler", # Rotaciona o arquivo de log quando atinge um certo tamanho.
            "filename": settings.LOG_FILE, # Caminho do arquivo de log, da configuração global.
            "maxBytes": 10 * 1024 * 1024,  # 10 MB: Tamanho máximo do arquivo antes da rotação.
            "backupCount": 5,             # Número de arquivos de backup a serem mantidos.
            "encoding": "utf8",           # Encoding do arquivo de log.
        },
    },
    "loggers": {
        # CONFIGURAÇÃO: Define o comportamento de loggers específicos.
        "": {  # Root logger (logger padrão para todos os módulos se não houver um logger mais específico).
            "handlers": ["console", "file"], # Envia para os handlers de console e arquivo.
            "level": settings.LOG_LEVEL,     # Nível de log do root logger.
            "propagate": True,               # Se True, mensagens também são passadas para handlers de loggers pai (não relevante para root).
        },
        "__main__": { # Logger específico para o script principal (`if __name__ == "__main__":`).
            "handlers": ["console", "file"],
            "level": settings.LOG_LEVEL,
            "propagate": False, # DECISÃO: `False` para evitar que mensagens do `__main__` sejam duplicadas pelo root logger,
                                # já que ambos usam os mesmos handlers.
        },
        # Pode-se adicionar outros loggers específicos aqui, por exemplo:
        # "uvicorn.access": { "handlers": ["console"], "level": "INFO", "propagate": False } para logs de acesso do Uvicorn.
    },
}

# Resumo Técnico Final
# Pontos fortes da implementação:
# - Uso de `pydantic-settings` para uma gestão de configuração robusta, tipada e com validação automática.
# - Carregamento de configurações a partir de variáveis de ambiente e arquivos `.env`, o que é uma prática padrão.
# - Configurações agrupadas logicamente (básicas, log, API, segurança, DB, LLM, navegador, etc.).
# - Validadores customizados para `DATABASE_URL` e `LOG_FILE`, garantindo a criação de diretórios e fallbacks.
# - Configuração detalhada de logging (formatters, handlers, loggers) em um dicionário.
# Maturidade técnica demonstrada:
# - Separação clara entre configurações e código da aplicação.
# - Utilização de `pathlib` para manipulação de caminhos de forma independente de sistema operacional.
# - Consideração de diferentes ambientes (e.g., `TEST_DATABASE_URL`).
# - Definição de tipos para todas as configurações, melhorando a clareza e prevenindo erros.
# Aderência às boas práticas:
# - Nomenclatura de constantes em maiúsculas (e.g., `BASE_DIR`).
# - Docstrings e comentários explicativos.
# - Configuração de logging centralizada e flexível.
# - Uso de `Field` do Pydantic para definir metadados e valores padrão para as configurações.
