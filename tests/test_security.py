"""
Testes unitários para o módulo de segurança
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.security.encryption import (
    EncryptionService,
    PasswordService,
    RateLimiter,
    Auditor
)


class TestEncryptionService:
    """Testes para EncryptionService."""

    def test_encrypt_decrypt(self):
        """Testa criptografia e descriptografia."""
        enc = EncryptionService()
        original = "dados_sensiveis_123"

        encrypted = enc.encrypt(original)
        decrypted = enc.decrypt(encrypted)

        assert original == decrypted
        assert encrypted != original.encode()

    def test_hash_sensitive(self):
        """Testa hash de dados sensíveis."""
        enc = EncryptionService()
        dados = "senha123"

        hash1 = enc.hash_sensitive(dados)
        hash2 = enc.hash_sensitive(dados)

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex
        assert "senha" not in hash1


class TestPasswordService:
    """Testes para PasswordService."""

    def test_hash_and_verify(self):
        """Testa hash e verificação de senha."""
        senha = "minha_senha_secreta"
        hashed = PasswordService.hash_password(senha)

        assert PasswordService.verify_password(senha, hashed)
        assert not PasswordService.verify_password("senha_errada", hashed)

    def test_different_hashes(self):
        """Testa que hashes são diferentes mesmo para senhas iguais."""
        senha = "senha123"
        hash1 = PasswordService.hash_password(senha)
        hash2 = PasswordService.hash_password(senha)

        assert hash1 != hash2  # bcrypt usa salt aleatório
        assert PasswordService.verify_password(senha, hash1)
        assert PasswordService.verify_password(senha, hash2)


class TestRateLimiter:
    """Testes para RateLimiter."""

    def test_basic_acquire(self):
        """Testa aquisição básica de requests."""
        limiter = RateLimiter(requests_per_minute=10, burst=5)

        # Deve permitir até burst requests
        for i in range(5):
            assert limiter.acquire() is True

    def test_rate_limit_exceeded(self):
        """Testa que rate limit é respeitado."""
        limiter = RateLimiter(requests_per_minute=3, burst=2)

        # Primeiro 2 (burst) + 1 (normal) = 3 devem passar
        assert limiter.acquire() is True
        assert limiter.acquire() is True
        assert limiter.acquire() is True

        # O quarto deve ser bloqueado
        assert limiter.acquire() is False


class TestAuditor:
    """Testes para Auditor."""

    def test_log_action(self):
        """Testa log de ações."""
        auditor = Auditor(log_path="test_audit.json")

        auditor.log_action(
            action="click",
            agent="test_user",
            details={"element": "button_submit"},
            success=True
        )

        logs = auditor.get_logs(agent="test_user")
        assert len(logs) == 1
        assert logs[0]["action"] == "click"

    def test_get_logs_filter(self):
        """Testa filtro de logs."""
        auditor = Auditor()

        auditor.log_action("click", "user1")
        auditor.log_action("type", "user2")
        auditor.log_action("click", "user2")

        all_logs = auditor.get_logs()
        user2_logs = auditor.get_logs(agent="user2")
        click_logs = auditor.get_logs(action="click")

        assert len(all_logs) == 3
        assert len(user2_logs) == 2
        assert len(click_logs) == 1