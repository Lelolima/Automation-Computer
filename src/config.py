"""
Módulo de configuração do Agente de Automação.
Centraliza o gerenciamento de configurações do sistema.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from pydantic import Field, validator
from pydantic.networks import AnyHttpUrl, PostgresDsn
from pydantic_settings import BaseSettings

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Diretório base do projeto
BASE_DIR = Path(__file__).parent.parent.absolute()


class Settings(BaseSettings):
    """Configurações da aplicação."""

    # Configurações básicas
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ENCRYPTION_KEY: str = Field(..., env="ENCRYPTION_KEY")

    # Configurações de log
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: Path = Field(default=BASE_DIR / "logs" / "automation.log", env="LOG_FILE")

    # Configurações de API
    API_PREFIX: str = "/api/v1"
    API_TITLE: str = "Automation Agent API"
    API_DESCRIPTION: str = "API para o Agente de Automação Integrada"
    API_VERSION: str = "0.1.0"

    # Configurações de segurança
    SECURITY_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 dias
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Configurações de banco de dados
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    TEST_DATABASE_URL: Optional[str] = Field(None, env="TEST_DATABASE_URL")
    REDIS_URL: str = Field(..., env="REDIS_URL")

    # Configurações de LLM
    OPENAI_API_KEY: Optional[str] = Field(None, env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    GOOGLE_API_KEY: Optional[str] = Field(None, env="GOOGLE_API_KEY")
    LLM_PROVIDER: str = Field(default="openai", env="LLM_PROVIDER")
    LLM_MODEL: str = Field(default="gpt-4", env="LLM_MODEL")
    LLM_TEMPERATURE: float = Field(default=0.7, env="LLM_TEMPERATURE")
    LLM_MAX_TOKENS: int = Field(default=2000, env="LLM_MAX_TOKENS")

    # Configurações de navegador
    BROWSER: str = Field(default="chrome", env="BROWSER")  # chrome, firefox, edge
    HEADLESS: bool = Field(default=False, env="HEADLESS")
    WINDOW_WIDTH: int = Field(default=1280, env="WINDOW_WIDTH")
    WINDOW_HEIGHT: int = Field(default=800, env="WINDOW_HEIGHT")

    # Configurações de segurança avançadas
    MAX_CONCURRENT_TASKS: int = Field(default=5, env="MAX_CONCURRENT_TASKS")
    BLOCK_DANGEROUS_COMMANDS: bool = Field(default=True, env="BLOCK_DANGEROUS_COMMANDS")
    REQUIRE_AUTHENTICATION: bool = Field(default=True, env="REQUIRE_AUTHENTICATION")

    # Configurações de voz
    VOICE_LANGUAGE: str = Field(default="pt-BR", env="VOICE_LANGUAGE")
    VOICE_RATE: int = Field(default=150, env="VOICE_RATE")

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v: Optional[str]) -> str:
        if not v:
            # SQLite como fallback
            return f"sqlite:///{BASE_DIR}/sqlite.db"
        return v

    @validator("LOG_FILE")
    def validate_log_file(cls, v: Path) -> Path:
        # Garante que o diretório de logs existe
        v.parent.mkdir(parents=True, exist_ok=True)
        return v

    def get_database_url(self) -> str:
        """Retorna a URL do banco de dados apropriada para o ambiente."""
        if self.ENVIRONMENT == "test" and self.TEST_DATABASE_URL:
            return self.TEST_DATABASE_URL
        return self.DATABASE_URL


# Instância única de configurações
settings = Settings()

# Configuração de logging
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level": settings.LOG_LEVEL,
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "level": settings.LOG_LEVEL,
            "formatter": "standard",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": settings.LOG_FILE,
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
            "encoding": "utf8",
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["console", "file"],
            "level": settings.LOG_LEVEL,
            "propagate": True,
        },
        "__main__": {
            "handlers": ["console", "file"],
            "level": settings.LOG_LEVEL,
            "propagate": False,
        },
    },
}
