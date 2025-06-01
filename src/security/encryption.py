"""
Módulo de criptografia do Agente de Automação.
Fornece funções para criptografia e descriptografia de dados sensíveis.
"""

import base64
import hashlib
import os
from typing import Optional, Union

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from src.config import settings

# Constantes
SALT_LENGTH = 16
KEY_LENGTH = 32
ITERATIONS = 100000


class EncryptionError(Exception):
    """Exceção para erros de criptografia."""
    pass


class EncryptionManager:
    """Gerencia operações de criptografia e descriptografia."""
    
    def __init__(self, key: Optional[bytes] = None):
        """Inicializa o gerenciador de criptografia.
        
        Args:
            key: Chave de criptografia. Se não fornecida, usa a chave das configurações.
        """
        self.key = key or settings.ENCRYPTION_KEY.encode()
        if len(self.key) != 32:
            self.key = self._derive_key(self.key)
    
    def _derive_key(self, password: bytes, salt: Optional[bytes] = None) -> bytes:
        """Deriva uma chave segura a partir de uma senha.
        
        Args:
            password: Senha para derivar a chave.
            salt: Salt para a derivação. Se não fornecido, um novo será gerado.
            
        Returns:
            bytes: Chave derivada.
        """
        if salt is None:
            salt = os.urandom(SALT_LENGTH)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=KEY_LENGTH,
            salt=salt,
            iterations=ITERATIONS,
            backend=default_backend()
        )
        return kdf.derive(password)
    
    def encrypt(self, data: Union[str, bytes]) -> str:
        """Criptografa dados.
        
        Args:
            data: Dados a serem criptografados (string ou bytes).
            
        Returns:
            str: Dados criptografados em formato base64.
            
        Raises:
            EncryptionError: Se ocorrer um erro durante a criptografia.
        """
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Gera um IV aleatório
            iv = os.urandom(16)
            
            # Cria o cifrador
            cipher = Cipher(
                algorithms.AES(self.key),
                modes.CBC(iv),
                backend=default_backend()
            )
            
            # Aplica padding PKCS7
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(data) + padder.finalize()
            
            # Criptografa os dados
            encryptor = cipher.encryptor()
            encrypted = encryptor.update(padded_data) + encryptor.finalize()
            
            # Combina IV e dados criptografados
            result = iv + encrypted
            
            # Retorna em base64 para facilitar armazenamento
            return base64.urlsafe_b64encode(result).decode('utf-8')
            
        except Exception as e:
            raise EncryptionError(f"Falha ao criptografar dados: {str(e)}")
    
    def decrypt(self, encrypted_data: str) -> str:
        """Descriptografa dados.
        
        Args:
            encrypted_data: Dados criptografados em base64.
            
        Returns:
            str: Dados descriptografados como string.
            
        Raises:
            EncryptionError: Se os dados estiverem corrompidos ou a chave for inválida.
        """
        try:
            # Decodifica de base64
            encrypted_data = base64.urlsafe_b64decode(encrypted_data)
            
            # Extrai o IV (primeiros 16 bytes)
            iv = encrypted_data[:16]
            encrypted = encrypted_data[16:]
            
            # Cria o decifrador
            cipher = Cipher(
                algorithms.AES(self.key),
                modes.CBC(iv),
                backend=default_backend()
            )
            
            # Descriptografa
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(encrypted) + decryptor.finalize()
            
            # Remove o padding
            unpadder = padding.PKCS7(128).unpadder()
            data = unpadder.update(padded_data) + unpadder.finalize()
            
            return data.decode('utf-8')
            
        except (ValueError, TypeError, InvalidToken) as e:
            raise EncryptionError("Falha ao descriptografar dados: Dados inválidos ou chave incorreta.")
        except Exception as e:
            raise EncryptionError(f"Erro inesperado ao descriptografar: {str(e)}")


# Instância global para uso em todo o aplicativo
encryption_manager = EncryptionManager()


def encrypt_string(data: str) -> str:
    """Função de conveniência para criptografar uma string."""
    return encryption_manager.encrypt(data)


def decrypt_string(encrypted_data: str) -> str:
    """Função de conveniência para descriptografar uma string."""
    return encryption_manager.decrypt(encrypted_data)


def hash_data(data: Union[str, bytes], algorithm: str = 'sha256') -> str:
    """Gera um hash dos dados fornecidos.
    
    Args:
        data: Dados a serem hasheados.
        algorithm: Algoritmo de hash a ser usado (padrão: 'sha256').
        
    Returns:
        str: Hash em hexadecimal.
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    if algorithm.lower() == 'sha256':
        hasher = hashlib.sha256()
    elif algorithm.lower() == 'sha512':
        hasher = hashlib.sha512()
    elif algorithm.lower() == 'md5':
        hasher = hashlib.md5()
    else:
        raise ValueError(f"Algoritmo de hash não suportado: {algorithm}")
    
    hasher.update(data)
    return hasher.hexdigest()
