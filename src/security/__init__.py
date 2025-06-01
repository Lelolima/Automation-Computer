"""
Módulo de segurança do Agente de Automação Integrada.

Este módulo fornece funcionalidades de segurança, incluindo:
- Autenticação e autorização
- Criptografia de dados
- Gerenciamento de tokens JWT
- Validação de entrada
"""

from .auth import (
    User,
    UserInDB,
    TokenData,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    verify_token,
    check_permissions,
    get_password_hash,
    verify_password,
)

from .encryption import (
    EncryptionError,
    EncryptionManager,
    encrypt_string,
    decrypt_string,
    hash_data,
)

__all__ = [
    # Modelos
    'User',
    'UserInDB',
    'TokenData',
    
    # Autenticação
    'authenticate_user',
    'create_access_token',
    'create_refresh_token',
    'verify_token',
    'check_permissions',
    'get_password_hash',
    'verify_password',
    
    # Criptografia
    'EncryptionError',
    'EncryptionManager',
    'encrypt_string',
    'decrypt_string',
    'hash_data',
]
