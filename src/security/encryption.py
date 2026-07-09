"""
Automation-Computer - Módulo de Segurança
Criptografia, rate limiting, sandboxing e auditoria

Criado por Wellington de Lima Catarina
"""

import hashlib
import logging
import time
import json
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

from cryptography.fernet import Fernet
import bcrypt

logger = logging.getLogger(__name__)


class EncryptionService:
    """Serviço de criptografia usando Fernet (AES-128)."""

    def __init__(self, key: Optional[bytes] = None):
        """
        Inicializa o serviço de criptografia.

        Args:
            key: Chave de criptografia (gera nova se None)
        """
        self.key = key or Fernet.generate_key()
        self.cipher = Fernet(self.key)
        logger.info("EncryptionService inicializado")

    def save_key(self, path: str) -> None:
        """Salva a chave em um arquivo."""
        with open(path, 'wb') as f:
            f.write(self.key)
        logger.info(f"Chave salva em: {path}")

    @classmethod
    def load_key(cls, path: str) -> "EncryptionService":
        """Carrega chave de um arquivo."""
        with open(path, 'rb') as f:
            key = f.read()
        return cls(key=key)

    def encrypt(self, data: str) -> bytes:
        """Criptografa uma string."""
        try:
            return self.cipher.encrypt(data.encode('utf-8'))
        except Exception as e:
            logger.error(f"Erro ao criptografar: {e}")
            raise

    def decrypt(self, encrypted: bytes) -> str:
        """Descriptografa dados."""
        try:
            return self.cipher.decrypt(encrypted).decode('utf-8')
        except Exception as e:
            logger.error(f"Erro ao descriptografar: {e}")
            raise

    def hash_sensitive(self, data: str) -> str:
        """
        Gera hash de dados sensíveis (para logs seguros).

        Args:
            data: Dado sensível

        Returns:
            Hash SHA-256
        """
        return hashlib.sha256(data.encode()).hexdigest()


class PasswordService:
    """Serviço de hash de senhas usando bcrypt."""

    @staticmethod
    def hash_password(password: str, rounds: int = 12) -> str:
        """
        Gera hash de senha.

        Args:
            password: Senha para hashear
            rounds: Custo do bcrypt

        Returns:
            Hash da senha
        """
        try:
            salt = bcrypt.gensalt(rounds=rounds)
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"Erro ao hashear senha: {e}")
            raise

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        Verifica senha contra hash.

        Args:
            password: Senha para verificar
            hashed: Hash armazenado

        Returns:
            True se válido
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            logger.error(f"Erro ao verificar senha: {e}")
            return False


class RateLimiter:
    """Rate limiter para prevenir abuso acidental."""

    def __init__(
        self,
        requests_per_minute: int = 60,
        burst: int = 10
    ):
        """
        Inicializa o rate limiter.

        Args:
            requests_per_minute: Limite de requisições por minuto
            burst: Limite de burst imediato
        """
        self.requests_per_minute = requests_per_minute
        self.burst = burst
        self.requests: list = []
        self.burst_count = 0
        self.last_burst_reset = time.time()
        logger.info(f"RateLimiter inicializado: {requests_per_minute}/min, burst={burst}")

    def acquire(self) -> bool:
        """
        Tenta adquirir permissão para uma requisição.

        Returns:
            True se permitido, False se limitado
        """
        now = time.time()

        # Limpa requests antigos (mais de 1 minuto)
        self.requests = [t for t in self.requests if now - t < 60]

        # Verifica limite por minuto
        if len(self.requests) >= self.requests_per_minute:
            logger.warning("Rate limit excedido (requests/min)")
            return False

        # Verifica burst
        if now - self.last_burst_reset > 1:
            self.burst_count = 0
            self.last_burst_reset = now

        if self.burst_count >= self.burst:
            logger.warning("Burst limit excedido")
            return False

        self.requests.append(now)
        self.burst_count += 1
        return True

    async def acquire_async(self) -> bool:
        """Versão assíncrona do acquire."""
        return self.acquire()

    def wait_and_acquire(self, timeout: int = 60) -> bool:
        """
        Aguarda e tenta adquirir.

        Args:
            timeout: Tempo máximo de espera em segundos

        Returns:
            True se adquirido, False se timeout
        """
        start = time.time()
        while time.time() - start < timeout:
            if self.acquire():
                return True
            time.sleep(1)
        return False


class Sandbox:
    """Contexto de sandboxing para execuções seguras."""

    def __init__(
        self,
        allowed_paths: Optional[list] = None,
        allowed_domains: Optional[list] = None,
        max_memory_mb: int = 512
    ):
        """
        Inicializa o sandbox.

        Args:
            allowed_paths: Caminhos de arquivo permitidos
            allowed_domains: Domínios de rede permitidos
            max_memory_mb: Limite de memória em MB (placeholder - implementação futura com psutil)
        """
        self.allowed_paths = allowed_paths or []
        self.allowed_domains = allowed_domains or []
        # ponytail: max_memory_mb é placeholder para implementação futura
        # que requereria integração com psutil ou resource limits do OS
        # Upgrade path: implementar com psutil.process.memory_limit()
        self.max_memory_mb = max_memory_mb
        self.active = False
        logger.info("Sandbox inicializado")

    def __enter__(self):
        """Entry do context manager."""
        self.active = True
        logger.info("Sandbox ativado")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit do context manager."""
        self.active = False
        logger.info("Sandbox desativado")

    def is_path_allowed(self, path: str) -> bool:
        """Verifica se caminho é permitido."""
        path_obj = Path(path).resolve()
        for allowed in self.allowed_paths:
            if str(path_obj).startswith(str(Path(allowed).resolve())):
                return True
        logger.warning(f"Caminho não permitido: {path}")
        return False

    def is_domain_allowed(self, url: str) -> bool:
        """
        Verifica se domínio é permitido.

        Usa parsing de URL para matching estrito - evita falsos positivos
        de substring (ex: 'evil-example.com' não passa por 'example.com')
        """
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.split(':')[0]  # Remove porta se presente

            for allowed in self.allowed_domains:
                # Matching exato ou subdomínio
                if domain == allowed or domain.endswith('.' + allowed):
                    return True

            logger.warning(f"Domínio não permitido: {url} (domain={domain})")
            return False
        except Exception as e:
            logger.error(f"Erro ao verificar domínio: {e}")
            return False


class Auditor:
    """Serviço de auditoria e logging de ações."""

    def __init__(self, log_path: str = "audit_logs.json"):
        """
        Inicializa o auditor.

        Args:
            log_path: Caminho para o arquivo de logs
        """
        self.log_path = Path(log_path)
        self.logs: list = []
        logger.info(f"Auditor inicializado: {log_path}")

    def log_action(
        self,
        action: str,
        agent: str,
        details: Optional[Dict[str, Any]] = None,
        success: bool = True
    ) -> None:
        """
        Loga uma ação.

        Args:
            action: Nome da ação
            agent: Agente que executou (usuário/sistema)
            details: Detalhes da ação
            success: Se a ação foi bem-sucedida
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "agent": agent,
            "details": details or {},
            "success": success
        }
        self.logs.append(entry)
        logger.info(f"Ação auditada: {action} por {agent}")

    def save_logs(self) -> None:
        """Salva logs em arquivo."""
        try:
            existing = []
            if self.log_path.exists():
                with open(self.log_path, 'r') as f:
                    existing = json.load(f)

            existing.extend(self.logs)

            with open(self.log_path, 'w') as f:
                json.dump(existing, f, indent=2)

            self.logs.clear()
            logger.info(f"Logs salvos: {len(existing)} entradas")
        except Exception as e:
            logger.error(f"Erro ao salvar logs: {e}")
            raise

    def get_logs(
        self,
        agent: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100
    ) -> list:
        """
        Obtém logs com filtro.

        Args:
            agent: Filtrar por agente
            action: Filtrar por ação
            limit: Limite de resultados

        Returns:
            Lista de logs
        """
        filtered = self.logs
        if agent:
            filtered = [l for l in filtered if l.get('agent') == agent]
        if action:
            filtered = [l for l in filtered if l.get('action') == action]
        return filtered[-limit:]