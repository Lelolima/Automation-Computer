"""
Módulo de autenticação e autorização do Agente de Automação.
Gerencia autenticação de usuários, tokens JWT e permissões.
"""

import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError

from src.config import settings

# Configuração de hash de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Modelos de dados
class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: list[str] = []


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    scopes: list[str] = []


class UserInDB(User):
    hashed_password: str


# Funções de autenticação
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha fornecida corresponde ao hash armazenado."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Gera o hash de uma senha."""
    return pwd_context.hash(password)


def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """Cria um token JWT de acesso."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.SECURITY_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """Cria um token de atualização JWT."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=30)
    
    to_encode = {"sub": data.get("sub"), "exp": expire, "type": "refresh"}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.SECURITY_ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str, credentials_exception) -> Dict[str, Any]:
    """Verifica e decodifica um token JWT."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.SECURITY_ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        return {"sub": username, "scopes": token_scopes}
    except JWTError:
        raise credentials_exception


# Funções de autorização
def check_permissions(required_scopes: list[str], token_scopes: list[str]) -> bool:
    """Verifica se o token tem as permissões necessárias."""
    if not required_scopes:
        return True
    
    for scope in required_scopes:
        if scope in token_scopes:
            return True
    return False


# Funções de usuário (simulando um banco de dados)
# Em um ambiente real, isso seria substituído por consultas ao banco de dados
def get_user(db, username: str) -> Optional[UserInDB]:
    """Busca um usuário no banco de dados."""
    # TODO: Implementar busca real no banco de dados
    fake_users_db = {
        "admin": {
            "username": "admin",
            "full_name": "Administrador",
            "email": "admin@example.com",
            "hashed_password": get_password_hash("admin"),
            "disabled": False,
            "scopes": ["admin", "user"]
        },
        "user": {
            "username": "user",
            "full_name": "Usuário Comum",
            "email": "user@example.com",
            "hashed_password": get_password_hash("user"),
            "disabled": False,
            "scopes": ["user"]
        },
    }
    
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)
    return None


def authenticate_user(fake_db, username: str, password: str) -> Union[bool, UserInDB]:
    """Autentica um usuário com nome de usuário e senha."""
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
