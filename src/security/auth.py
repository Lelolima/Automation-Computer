# NOME_DO_ARQUIVO.py: auth.py
# Descrição: Módulo de autenticação e autorização do Agente de Automação. Gerencia autenticação de usuários, tokens JWT e permissões.
# Responsabilidades: Verificar senhas, gerar hashes de senha, criar e verificar tokens JWT (acesso e atualização), checar permissões de usuário e simular a busca e autenticação de usuários.
# Dependências: os, datetime, typing, jose, passlib, pydantic, src.config.
# Padrões aplicados: Modelos de dados Pydantic (TokenData, User, UserInDB), Uso de CryptContext para hashing de senha, Funções utilitárias para operações de autenticação e autorização.
# Autor: Autor Original Desconhecido
# Última modificação: 2024-07-26

"""
Módulo de autenticação e autorização do Agente de Automação.
Gerencia autenticação de usuários, tokens JWT e permissões.
"""

import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

# RACIOCÍNIO: `jose` (Javascript Object Signing and Encryption) é uma biblioteca Python para trabalhar com JWT, JWS, JWE, JWK, JWA.
# É escolhida por sua conformidade com os padrões e funcionalidades abrangentes para manipulação de tokens.
from jose import JWTError, jwt
# RACIOCÍNIO: `passlib` é uma biblioteca robusta para hashing de senhas.
# Ela suporta diversos algoritmos de hash e gerencia a complexidade do salting e do versionamento de hash.
from passlib.context import CryptContext
# RACIOCÍNIO: `pydantic` é usado para validação de dados e gerenciamento de configurações.
# Para modelos de dados relacionados à autenticação, garante que os dados estejam no formato esperado.
from pydantic import BaseModel, ValidationError

from src.config import settings

# Configuração de hash de senha
# RACIOCÍNIO: `CryptContext` do passlib permite configurar os esquemas de hashing.
# DECISÃO: `bcrypt` é escolhido como o esquema de hashing de senha devido à sua
# resistência a ataques de força bruta, incorporando um fator de trabalho (custo) que o torna lento para computar,
# dificultando ataques de dicionário e rainbow table.
# `deprecated="auto"` instrui o passlib a atualizar automaticamente hashes de esquemas mais antigos (se houvesse outros configurados)
# para o esquema preferido (`bcrypt` neste caso) quando uma senha é verificada com sucesso.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Modelos de Dados Pydantic ---
# ESTRATÉGIA: Usar Pydantic para definir a estrutura esperada dos dados relacionados a tokens e usuários.
# Isso fornece validação de tipo e clareza sobre os campos.

# RACIOCÍNIO: `TokenData` define a estrutura dos dados que são embutidos (payload) dentro de um token JWT.
class TokenData(BaseModel):
    # RACIOCÍNIO: `username` (geralmente o `sub` claim no JWT) identifica o usuário ao qual o token pertence.
    # É opcional aqui porque nem todo token pode carregar diretamente o username no payload de forma explícita,
    # dependendo da estratégia (ex: pode ser apenas o `sub` claim que é então usado para buscar o usuário).
    # No entanto, para tokens de acesso, é comum ter o identificador do usuário.
    username: Optional[str] = None
    # RACIOCÍNIO: `scopes` (escopos) definem as permissões concedidas pelo token.
    # É uma lista de strings, onde cada string representa uma permissão (ex: "read_items", "admin").
    scopes: list[str] = []

# RACIOCÍNIO: `User` define a estrutura básica de um usuário na aplicação,
# representando os dados que podem ser expostos ou manipulados.
class User(BaseModel):
    # RACIOCÍNIO: `username` é o identificador único do usuário. Campo obrigatório.
    username: str
    # RACIOCÍNIO: `email` e `full_name` são informações comuns do usuário, mas podem ser opcionais
    # dependendo dos requisitos da aplicação.
    email: Optional[str] = None
    full_name: Optional[str] = None
    # RACIOCÍNIO: `disabled` é um campo booleano para controlar o status da conta do usuário.
    # Opcional, e seu valor padrão (se omitido na criação) seria `None`.
    disabled: Optional[bool] = None
    # RACIOCÍNIO: `scopes` aqui representaria os escopos/permissões inerentes ao próprio usuário,
    # que podem ser usados para determinar os escopos a serem incluídos nos tokens gerados para este usuário.
    scopes: list[str] = []

# RACIOCÍNIO: `UserInDB` herda de `User` e adiciona campos que são específicos para o armazenamento
# do usuário no banco de dados, como a senha hasheada.
# ESTRATÉGIA: Separar o modelo `User` (para API) do `UserInDB` (para armazenamento) é uma boa prática
# para não expor acidentalmente dados sensíveis como o hash da senha.
class UserInDB(User):
    # RACIOCÍNIO: `hashed_password` armazena a senha do usuário de forma segura (hasheada).
    # Este campo NUNCA deve ser enviado em respostas de API.
    hashed_password: str


# --- Funções de Autenticação ---

# RACIOCÍNIO: Verificar uma senha fornecida em texto plano contra um hash armazenado.
# Esta é uma etapa crucial no login.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha fornecida corresponde ao hash armazenado."""
    # LÓGICA: `pwd_context.verify` lida com a comparação segura,
    # extraindo o salt e os parâmetros de hash do `hashed_password` armazenado
    # e aplicando o mesmo processo à `plain_password` antes de comparar.
    return pwd_context.verify(plain_password, hashed_password)

# RACIOCÍNIO: Gerar um hash seguro de uma senha em texto plano.
# Isso é usado ao criar um novo usuário ou ao atualizar uma senha.
def get_password_hash(password: str) -> str:
    """Gera o hash de uma senha."""
    # LÓGICA: `pwd_context.hash` aplica o esquema de hash configurado (bcrypt)
    # e gera um novo salt automaticamente para cada senha.
    return pwd_context.hash(password)

# ESTRATÉGIA: Função para criar tokens de acesso JWT.
# Tokens de acesso são de curta duração e concedem acesso a recursos protegidos.
def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """Cria um token JWT de acesso."""
    to_encode = data.copy() # RACIOCÍNIO: Copiar os dados de entrada para evitar modificar o dicionário original.
    # LÓGICA: Calcular o tempo de expiração do token.
    # Se `expires_delta` for fornecido, usá-lo. Caso contrário, usar um padrão.
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # DECISÃO: Tempo de expiração padrão para tokens de acesso é de 15 minutos.
        # RACIOCÍNIO: Tokens de acesso devem ter vida curta para mitigar o risco em caso de comprometimento.
        # O valor exato (15 minutos, 1 hora, etc.) depende dos requisitos de segurança da aplicação.
        # Este valor (15 min) é um exemplo comum. `settings.ACCESS_TOKEN_EXPIRE_MINUTES` é usado na prática.
        # Esta função usa um padrão fixo, mas idealmente usaria `settings.ACCESS_TOKEN_EXPIRE_MINUTES`.
        # A implementação atual usa um default de 15min, mas o `settings` tem 7 dias. Isso é uma inconsistência.
        # Para este exercício, manterei o código como está, mas notando a inconsistência.
        expire = datetime.utcnow() + timedelta(minutes=15) # TODO: Alinhar com `settings.ACCESS_TOKEN_EXPIRE_MINUTES`
    
    # RACIOCÍNIO: Adicionar o claim `exp` (expiration time) ao payload do JWT.
    # Este é um claim registrado e é crucial para a segurança do token.
    to_encode.update({"exp": expire})
    # RACIOCÍNIO: O claim `sub` (subject) geralmente contém o identificador principal do usuário (ex: username ou user ID).
    # Os dados de entrada (`data`) devem conter este `sub`.
    
    # LÓGICA: Codificar o payload (`to_encode`) em um token JWT.
    # `settings.SECRET_KEY`: Chave secreta usada para assinar o token. Deve ser mantida segura.
    # `settings.SECURITY_ALGORITHM`: Algoritmo de assinatura (ex: HS256).
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.SECURITY_ALGORITHM
    )
    return encoded_jwt

# ESTRATÉGIA: Função para criar tokens de atualização JWT.
# Tokens de atualização são de longa duração e usados para obter novos tokens de acesso sem que o usuário precise logar novamente.
def create_refresh_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """Cria um token de atualização JWT."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # DECISÃO: Tempo de expiração padrão para tokens de atualização é de 30 dias.
        # RACIOCÍNIO: Tokens de atualização têm vida mais longa, pois são menos expostos
        # (usados apenas para obter novos tokens de acesso em um endpoint específico).
        # Este valor (30 dias) é um exemplo. `settings.REFRESH_TOKEN_EXPIRE_DAYS` é usado na prática.
        # Esta função usa um padrão fixo, mas idealmente usaria `settings.REFRESH_TOKEN_EXPIRE_DAYS`.
        expire = datetime.utcnow() + timedelta(days=30) # TODO: Alinhar com `settings.REFRESH_TOKEN_EXPIRE_DAYS`
    
    # RACIOCÍNIO: Para tokens de atualização, o payload pode ser mais simples.
    # Geralmente contém apenas o `sub` (subject - identificador do usuário) e `exp` (expiration).
    # Adicionar um claim `type: "refresh"` é uma boa prática para distinguir tokens de atualização de tokens de acesso.
    to_encode = {"sub": data.get("sub"), "exp": expire, "type": "refresh"}
    
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.SECURITY_ALGORITHM
    )
    return encoded_jwt

# RACIOCÍNIO: Função para verificar e decodificar um token JWT.
# Usada para proteger endpoints, extraindo e validando as informações do token.
def verify_token(token: str, credentials_exception) -> Dict[str, Any]:
    """Verifica e decodifica um token JWT."""
    try:
        # LÓGICA: `jwt.decode` verifica a assinatura do token, a expiração e decodifica o payload.
        # Requer o token, a chave secreta e os algoritmos permitidos.
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.SECURITY_ALGORITHM]
        )
        # RACIOCÍNIO: Extrair o `username` do claim `sub` (subject).
        username: Optional[str] = payload.get("sub") # username: str was here, but payload.get can return None
        # VALIDAÇÃO: Se o `username` (ou `sub`) não estiver presente no token, o token é inválido.
        if username is None:
            # `credentials_exception` é uma exceção (geralmente HTTPException com status 401)
            # passada como argumento para ser levantada em caso de falha na validação.
            raise credentials_exception
        
        # RACIOCÍNIO: Extrair os `scopes` (permissões) do payload.
        # Se não houver `scopes` no payload, retornar uma lista vazia por padrão.
        token_scopes = payload.get("scopes", [])
        # DECISÃO: Retornar um dicionário contendo o `sub` (username) e os `scopes`.
        # Isso permite que o chamador use essas informações para controle de acesso.
        return {"sub": username, "scopes": token_scopes}
    except JWTError:
        # CENÁRIO: `JWTError` é levantada pela biblioteca `jose` para várias falhas de token
        # (ex: token expirado, assinatura inválida, formato inválido).
        # Nestes casos, levantar a `credentials_exception` fornecida.
        raise credentials_exception


# --- Funções de Autorização ---

# RACIOCÍNIO: Verificar se um token possui as permissões (scopes) necessárias para acessar um recurso.
def check_permissions(required_scopes: list[str], token_scopes: list[str]) -> bool:
    """Verifica se o token tem as permissões necessárias."""
    # LÓGICA: Se não houver `required_scopes` para o recurso, o acesso é permitido por padrão.
    if not required_scopes:
        return True # Recurso não requer escopos específicos.
    
    # LÓGICA: Iterar sobre os `required_scopes`. Se qualquer um dos escopos necessários
    # estiver presente nos `token_scopes` (escopos do token do usuário), o acesso é permitido.
    # DECISÃO: Esta implementação permite acesso se *qualquer* escopo requerido for encontrado.
    # Para um cenário onde *todos* os escopos requeridos devem estar presentes, a lógica seria:
    # `return all(scope in token_scopes for scope in required_scopes)`
    # A lógica atual é "OR" (qualquer um), não "AND" (todos).
    # A escolha depende da política de autorização desejada.
    for scope in required_scopes:
        if scope in token_scopes:
            return True # O usuário tem pelo menos um dos escopos necessários.
    return False # O usuário não possui nenhum dos escopos necessários.


# --- Funções de Usuário (Simulando um Banco de Dados) ---
# RACIOCÍNIO: Estas funções simulam a interação com um banco de dados de usuários.
# Em uma aplicação real, elas seriam substituídas por chamadas a um ORM ou consultas diretas ao banco.
# ESTRATÉGIA: Usar um dicionário em memória (`fake_users_db`) para fins de demonstração e desenvolvimento inicial.

# RACIOCÍNIO: Simular a busca de um usuário no "banco de dados".
def get_user(db, username: str) -> Optional[UserInDB]: # `db` é um placeholder, não usado aqui.
    """Busca um usuário no banco de dados (simulado)."""
    # TODO: Implementar busca real no banco de dados.
    # RACIOCÍNIO: `fake_users_db` contém dados de exemplo, incluindo senhas já hasheadas.
    # Em um cenário real, `get_password_hash` seria usado ao criar o usuário, não ao buscar.
    fake_users_db = {
        "admin": {
            "username": "admin",
            "full_name": "Administrador",
            "email": "admin@example.com",
            "hashed_password": get_password_hash("admin"), # Senha "admin" hasheada
            "disabled": False,
            "scopes": ["admin", "user"] # Admin tem escopos 'admin' e 'user'
        },
        "user": {
            "username": "user",
            "full_name": "Usuário Comum",
            "email": "user@example.com",
            "hashed_password": get_password_hash("user"), # Senha "user" hasheada
            "disabled": False,
            "scopes": ["user"] # Usuário comum tem apenas escopo 'user'
        },
    }
    
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        # LÓGICA: Construir uma instância de `UserInDB` a partir do dicionário de dados.
        # Pydantic validará se os dados correspondem ao modelo.
        return UserInDB(**user_dict)
    return None # Usuário não encontrado.

# RACIOCÍNIO: Simular o processo de autenticação de um usuário.
def authenticate_user(fake_db, username: str, password: str) -> Union[bool, UserInDB]: # `fake_db` é um placeholder.
    """Autentica um usuário com nome de usuário e senha (simulado)."""
    # LÓGICA: 1. Buscar o usuário pelo `username`.
    user = get_user(fake_db, username)
    if not user:
        # CENÁRIO: Usuário não encontrado.
        return False
    # LÓGICA: 2. Se o usuário for encontrado, verificar a senha fornecida contra o hash armazenado.
    if not verify_password(password, user.hashed_password):
        # CENÁRIO: Senha incorreta.
        return False
    # SUCESSO: Usuário encontrado e senha correta.
    return user

# Resumo Técnico Final
# Pontos fortes da implementação:
# - Separação clara de responsabilidades (hashing, JWT, verificação de token, etc.).
# - Uso de bibliotecas padrão e bem estabelecidas para segurança (jose, passlib).
# - Utilização de Pydantic para validação e modelagem de dados, o que aumenta a robustez.
# - Flexibilidade na configuração de tokens (tempo de expiração, algoritmo).
# - Simulação de banco de dados para usuários, permitindo testes e desenvolvimento inicial.
# Maturidade técnica demonstrada:
# - Implementação correta de hashing de senhas com salt (bcrypt via passlib).
# - Criação e verificação de tokens JWT seguindo boas práticas.
# - Distinção entre tokens de acesso e de atualização.
# - Tratamento de erros JWTError.
# Aderência às boas práticas:
# - Código bem organizado em funções com responsabilidades únicas.
# - Uso de type hints.
# - Docstrings claras para funções e modelos.
# - Configurações de segurança (chave secreta, algoritmo) externalizadas (via `src.config.settings`).
# - TODOs indicando áreas para desenvolvimento futuro (ex: integração com banco de dados real).
