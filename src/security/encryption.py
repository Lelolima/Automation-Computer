# NOME_DO_ARQUIVO.py: encryption.py
# Descrição: Módulo de criptografia do Agente de Automação. Fornece funções para criptografia e descriptografia de dados sensíveis, além de hashing.
# Responsabilidades: Derivar chaves seguras, criptografar e descriptografar dados usando AES CBC, e gerar hashes de dados (SHA256, SHA512, MD5).
# Dependências: base64, hashlib, os, typing, cryptography, src.config.
# Padrões aplicados: Programação Orientada a Objetos (EncryptionManager), Funções utilitárias, Tratamento de exceções, Uso de IVs aleatórios para AES CBC, Padding PKCS7.
# Autor: Autor Original Desconhecido
# Última modificação: 2024-07-26

"""
Módulo de criptografia do Agente de Automação.
Fornece funções para criptografia e descriptografia de dados sensíveis.
"""

import base64
import hashlib
import os
from typing import Optional, Union

# RACIOCÍNIO: A biblioteca `cryptography` é uma escolha padrão em Python para operações criptográficas de baixo e alto nível.
# Ela fornece primitivas seguras e é ativamente mantida.
# `Fernet` é uma cifra de alto nível (e uma implementação específica dentro de `cryptography`), mas aqui estamos usando as primitivas `hazmat` (Hazardous Materials)
# para um controle mais granular sobre o algoritmo AES, modo de operação (CBC), padding (PKCS7) e IVs.
# Isso é útil quando se precisa de interoperabilidade com outros sistemas ou requisitos criptográficos específicos
# que podem não ser cobertos diretamente por Fernet.
from cryptography.fernet import Fernet, InvalidToken # InvalidToken é usado no tratamento de erro. Fernet em si não é usado para a criptografia principal aqui.
from cryptography.hazmat.backends import default_backend # Permite que `cryptography` escolha o melhor backend disponível (OpenSSL, CommonCrypto, etc.).
from cryptography.hazmat.primitives import hashes, padding # Módulos para funções de hash e esquemas de padding.
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes # Primitivas para cifradores simétricos.
# PBKDF2HMAC é usado para derivação de chave a partir de uma senha ou material de chave.
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from src.config import settings # Para acessar configurações como ENCRYPTION_KEY.

# --- Constantes Criptográficas ---
# CRIPTOGRAFIA: Tamanho do salt em bytes. Um salt aleatório é crucial para a derivação de chave (PBKDF2).
# 16 bytes (128 bits) é um tamanho comum e seguro para salts.
SALT_LENGTH = 16
# CRIPTOGRAFIA: Tamanho desejado da chave de criptografia em bytes.
# AES-256 (Advanced Encryption Standard com chave de 256 bits) requer uma chave de 32 bytes.
KEY_LENGTH = 32
# CRIPTOGRAFIA: Número de iterações para PBKDF2.
# Aumentar o número de iterações torna a derivação da chave mais lenta e, portanto, mais resistente a ataques de força bruta.
# O valor (ex: 100.000) deve ser o mais alto possível sem impactar inaceitavelmente o desempenho da aplicação.
# Recomendações do OWASP são tipicamente mais altas (ex: 310.000 para PBKDF2-SHA256 em 2023). Este valor é um exemplo e pode precisar de ajuste.
ITERATIONS = 100000

# ESTRATÉGIA: Definir uma exceção personalizada para erros específicos de criptografia.
# Isso permite um tratamento de erro mais específico e informativo no código que utiliza este módulo.
class EncryptionError(Exception):
    """Exceção para erros de criptografia."""
    pass

# ESTRATÉGIA: Encapsular a lógica de criptografia e descriptografia em uma classe Manager.
# Isso promove a organização, facilita o gerenciamento da chave e o reuso das configurações criptográficas.
class EncryptionManager:
    """Gerencia operações de criptografia e descriptografia."""
    
    def __init__(self, key: Optional[bytes] = None):
        """Inicializa o gerenciador de criptografia.
        
        Args:
            key: Chave de criptografia em bytes. Se não fornecida, usa a ENCRYPTION_KEY das configurações.
                 # RACIOCÍNIO: Permitir que uma chave seja injetada facilita testes e cenários onde a chave
                 # pode vir de outras fontes seguras (ex: gerenciador de segredos, variáveis de ambiente específicas).
        """
        # LÓGICA: Obter o material da chave. Priorizar a chave passada como argumento; se não houver, usar a das configurações.
        # A chave das configurações (`settings.ENCRYPTION_KEY`) é esperada como string e precisa ser encodada para bytes.
        # DECISÃO: Usar 'utf-8' como encoding padrão para a chave vinda das configurações.
        _key_material = key or settings.ENCRYPTION_KEY.encode('utf-8')
        
        # CRIPTOGRAFIA: AES-256, o algoritmo usado aqui, requer uma chave de exatamente 32 bytes (256 bits).
        # RACIOCÍNIO: Se a chave fornecida (ou das settings) não tiver 32 bytes,
        # ela não pode ser usada diretamente com AES-256 de forma segura ou correta.
        # DECISÃO: Derivar uma chave de 32 bytes usando `_derive_key` se o material da chave original
        # não tiver o tamanho correto. Isso garante que sempre teremos uma chave de tamanho válido para AES-256.
        # CENÁRIO: Isso é particularmente útil se `settings.ENCRYPTION_KEY` for uma senha/frase secreta de fácil memorização
        # em vez de uma chave binária já formatada e com a entropia correta.
        if len(_key_material) != KEY_LENGTH:
            # Usar o `_key_material` como "senha" para a função de derivação de chave (KDF).
            # `_derive_key` gerará seu próprio salt aleatório se não for fornecido um explicitamente.
            self.key = self._derive_key(_key_material)
            # Um log warning aqui seria útil em um cenário de produção para alertar sobre a derivação.
            # Ex: logger.warning(f"Chave original não tinha {KEY_LENGTH} bytes. Uma nova chave foi derivada para uso interno.")
        else:
            self.key = _key_material
    
    def _derive_key(self, password: bytes, salt: Optional[bytes] = None) -> bytes:
        """Deriva uma chave criptograficamente forte de 32 bytes a partir de uma 'senha' (material de chave) fornecida.
        
        Args:
            password: A 'senha' ou material de chave a partir do qual derivar a chave final.
            salt: Salt opcional em bytes. Se None, um novo salt aleatório de `SALT_LENGTH` bytes será gerado.
                  # CRIPTOGRAFIA: O salt é um valor aleatório usado no processo de derivação de chave.
                  # Sua principal função é proteger contra ataques de rainbow table e garantir que
                  # entradas (senhas) idênticas resultem em chaves derivadas diferentes se salts diferentes forem usados.
                  # IMPORTANTE: Para poder recriar (e, portanto, verificar ou usar para descriptografar) uma chave derivada
                  # de uma senha específica, o *mesmo salt* usado na derivação original *deve* ser usado novamente.
                  # No contexto deste `__init__`, o salt é gerado e usado internamente para produzir `self.key`.
                  # A instância então usa consistentemente esta `self.key`. Se esta função fosse usada para, por exemplo,
                  # derivar uma chave para criptografar algo que precisa ser descriptografado *por outra instância ou processo*
                  # que só conhece a senha original, então o salt usado teria que ser armazenado e fornecido na descriptografia.
            
        Returns:
            bytes: Chave derivada de 32 bytes, adequada para AES-256.
        """
        # CRIPTOGRAFIA: Gerar um salt aleatório e seguro se nenhum for fornecido.
        # `os.urandom` é a forma recomendada em Python para gerar bytes criptograficamente seguros.
        _salt = salt if salt is not None else os.urandom(SALT_LENGTH)
        
        # CRIPTOGRAFIA: PBKDF2 (Password-Based Key Derivation Function 2) é um padrão (RFC 2898)
        # para derivar chaves criptográficas a partir de senhas ou frases secretas.
        # Ele aplica repetidamente uma função pseudoaleatória (aqui, HMAC-SHA256) à senha e ao salt.
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(), # DECISÃO: SHA256 é um algoritmo de hash seguro e comum para usar com PBKDF2.
            length=KEY_LENGTH,        # Comprimento desejado da chave derivada (32 bytes para AES-256).
            salt=_salt,               # O salt para a derivação.
            iterations=ITERATIONS,    # Número de iterações (fator de trabalho) para tornar a computação mais lenta.
            backend=default_backend() # Usa o backend criptográfico padrão disponível (ex: OpenSSL).
        )
        # LÓGICA: Derivar a chave a partir da "senha" (material de chave de entrada).
        derived_key = kdf.derive(password)
        return derived_key
    
    def encrypt(self, data: Union[str, bytes]) -> str:
        """Criptografa dados usando AES-256 em modo CBC.
        
        Args:
            data: Dados a serem criptografados (string UTF-8 ou bytes).
            
        Returns:
            str: Dados criptografados como uma string URL-safe base64 (contendo IV + ciphertext).
            
        Raises:
            EncryptionError: Se ocorrer um erro durante a criptografia.
        """
        try:
            # LÓGICA: Garantir que os dados de entrada sejam bytes. Se for string, codificar para UTF-8, um encoding comum.
            _data_bytes = data.encode('utf-8') if isinstance(data, str) else data
            
            # CRIPTOGRAFIA: IV (Initialization Vector) para o modo CBC.
            # Deve ser aleatório e único para cada operação de criptografia realizada com a mesma chave.
            # O tamanho do IV para AES é igual ao tamanho do bloco (16 bytes / 128 bits).
            # O IV não precisa ser secreto, mas deve ser imprevisível e usado apenas uma vez por chave.
            # `os.urandom(16)` é usado para gerar um IV criptograficamente seguro.
            iv = os.urandom(16) # AES block size is 128 bits (16 bytes)
            
            # CRIPTOGRAFIA: Configurar o cifrador AES.
            # AES (Advanced Encryption Standard) é um algoritmo de criptografia simétrica por blocos,
            # considerado muito seguro e é um padrão global. `self.key` deve ter 32 bytes para AES-256.
            # CBC (Cipher Block Chaining) é um modo de operação que encadeia blocos de texto cifrado.
            # No CBC, cada bloco de texto cifrado depende de todos os blocos de texto plano processados até aquele ponto.
            # Isso significa que blocos de texto plano idênticos resultarão em blocos de texto cifrado diferentes se estiverem em posições diferentes
            # ou se o IV for diferente, o que é uma propriedade de segurança desejável. Requer um IV para o primeiro bloco.
            cipher = Cipher(
                algorithms.AES(self.key), # Algoritmo AES com a chave da instância (deve ser 256-bit).
                modes.CBC(iv),            # Modo CBC com o IV aleatório gerado.
                backend=default_backend()
            )
            
            # CRIPTOGRAFIA: Padding PKCS7.
            # AES é um cifrador de bloco, o que significa que opera em blocos de dados de tamanho fixo (16 bytes para AES).
            # Se os dados de entrada não forem um múltiplo do tamanho do bloco, eles precisam ser preenchidos (padded)
            # para formar um bloco final completo. PKCS7 é um esquema de padding padrão que especifica como
            # adicionar bytes para completar o último bloco e como removê-los na descriptografia.
            padder = padding.PKCS7(algorithms.AES.block_size).padder() # algorithms.AES.block_size é 128 bits (16 bytes)
            padded_data = padder.update(_data_bytes) + padder.finalize()
            
            # LÓGICA: Criptografar os dados (já preenchidos).
            encryptor = cipher.encryptor()
            encrypted_payload = encryptor.update(padded_data) + encryptor.finalize()
            
            # ESTRATÉGIA: Preceder o ciphertext com o IV.
            # RACIOCÍNIO: O IV é necessário para a descriptografia no modo CBC e não é secreto.
            # Armazená-lo junto com o ciphertext (geralmente no início) é uma prática comum e conveniente,
            # pois garante que o IV correto esteja disponível quando os dados forem descriptografados.
            # Formato resultante: [IV (16 bytes)][Ciphertext (restante)]
            encrypted_result_bytes = iv + encrypted_payload
            
            # LÓGICA: Codificar o resultado combinado (IV + ciphertext) em base64.
            # RACIOCÍNIO: Base64 converte dados binários em uma string de caracteres ASCII.
            # Isso é útil para armazenamento ou transmissão em meios que lidam melhor com texto
            # (ex: JSON, XML, URLs, arquivos de configuração).
            # `urlsafe_b64encode` usa caracteres ('-' e '_') que são seguros para uso em URLs e nomes de arquivo,
            # em vez dos caracteres padrão ('+' e '/') do base64 comum.
            return base64.urlsafe_b64encode(encrypted_result_bytes).decode('utf-8')
            
        except Exception as e:
            # CENÁRIO: Qualquer erro durante o processo de criptografia (ex: problema com a chave, dados).
            # Um log de erro aqui seria apropriado em um sistema de produção.
            # Ex: logger.error(f"Erro durante a criptografia: {e}", exc_info=True)
            raise EncryptionError(f"Falha ao criptografar dados: {str(e)}")
    
    def decrypt(self, encrypted_data_b64: str) -> str:
        """Descriptografa dados criptografados com AES-256 CBC.
        
        Args:
            encrypted_data_b64: Dados criptografados em formato URL-safe base64 (espera-se que contenham IV + ciphertext).
            
        Returns:
            str: Dados descriptografados como string UTF-8.
            
        Raises:
            EncryptionError: Se os dados estiverem corrompidos, a chave for inválida, o padding for incorreto, ou ocorrer outro erro.
        """
        try:
            # LÓGICA: Decodificar os dados de URL-safe base64 para bytes.
            encrypted_result_bytes = base64.urlsafe_b64decode(encrypted_data_b64)
            
            # LÓGICA: Extrair o IV do início dos dados. O IV tem 16 bytes (tamanho do bloco AES).
            # VALIDAÇÃO: Verificar se os dados têm comprimento suficiente para conter pelo menos o IV.
            if len(encrypted_result_bytes) < 16: # Tamanho mínimo seria IV + pelo menos um bloco de dados (mesmo que seja só padding)
                raise EncryptionError("Dados criptografados inválidos: muito curtos para conter IV.")
            iv = encrypted_result_bytes[:16]
            encrypted_payload = encrypted_result_bytes[16:] # O restante é o payload criptografado.
            
            # CRIPTOGRAFIA: Configurar o cifrador AES para descriptografia.
            # É crucial usar a mesma chave e o mesmo IV que foram usados na criptografia.
            cipher = Cipher(
                algorithms.AES(self.key), # A mesma chave da instância.
                modes.CBC(iv),            # O IV extraído dos dados criptografados.
                backend=default_backend()
            )
            
            # LÓGICA: Descriptografar os dados.
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(encrypted_payload) + decryptor.finalize()
            
            # CRIPTOGRAFIA: Remover o padding PKCS7.
            # Se o padding estiver incorreto, isso geralmente indica que a chave está errada ou os dados foram corrompidos,
            # pois a descriptografia com a chave errada resultaria em dados aleatórios que não teriam um padding válido.
            # A biblioteca `cryptography` levantará um erro (frequentemente `ValueError` ou específico do padding) se o padding for inválido.
            unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
            data_bytes = unpadder.update(padded_data) + unpadder.finalize()
            
            # LÓGICA: Decodificar os bytes resultantes para uma string UTF-8.
            return data_bytes.decode('utf-8')
            
        except (ValueError, TypeError, InvalidToken) as e:
            # CENÁRIO:
            # `ValueError` ou `TypeError` podem ser levantados por `base64.urlsafe_b64decode` se a entrada for malformada,
            # ou pela remoção do padding se os dados descriptografados não tiverem um padding válido.
            # `InvalidToken` (de `cryptography.fernet`) é capturado aqui por precaução, embora este código não use Fernet diretamente,
            # erros de descriptografia (como falha na verificação de tag em modos autenticados como GCM, ou falha de padding em CBC)
            # são conceitualmente similares. Para CBC, uma falha de padding é o principal indicador de chave errada/corrupção.
            # Estes erros geralmente significam que os dados estão corrompidos, a chave de descriptografia está incorreta, ou o IV está errado.
            # Um log de erro aqui seria apropriado.
            # Ex: logger.error(f"Erro de descriptografia (dados inválidos, chave incorreta ou padding inválido): {e}", exc_info=True)
            raise EncryptionError("Falha ao descriptografar dados: Dados inválidos ou chave incorreta.")
        except Exception as e:
            # CENÁRIO: Outros erros inesperados durante a descriptografia.
            # Um log de erro aqui seria apropriado.
            # Ex: logger.error(f"Erro inesperado durante a descriptografia: {e}", exc_info=True)
            raise EncryptionError(f"Erro inesperado ao descriptografar: {str(e)}")

# ESTRATÉGIA: Fornecer uma instância global do EncryptionManager.
# RACIOCÍNIO: Para casos de uso simples onde uma única configuração de chave (definida em `settings.ENCRYPTION_KEY`)
# é usada em toda a aplicação. Isso simplifica o uso, pois não é necessário instanciar `EncryptionManager` repetidamente.
# CUIDADO: Se a aplicação precisar lidar com múltiplas chaves de criptografia ou configurações diferentes
# (ex: chaves diferentes para usuários diferentes, ou algoritmos diferentes), então instâncias locais de `EncryptionManager`
# devem ser criadas e gerenciadas conforme necessário, em vez de depender desta instância global.
encryption_manager = EncryptionManager()

# ESTRATÉGIA: Funções de conveniência que usam a instância global `encryption_manager`.
# RACIOCÍNIO: Simplificam chamadas comuns para criptografar e descriptografar strings,
# tornando a API do módulo mais fácil de usar para os casos mais frequentes.
def encrypt_string(data: str) -> str:
    """Função de conveniência para criptografar uma string usando o gerenciador global."""
    return encryption_manager.encrypt(data)

def decrypt_string(encrypted_data: str) -> str:
    """Função de conveniência para descriptografar uma string usando o gerenciador global."""
    return encryption_manager.decrypt(encrypted_data)

# RACIOCÍNIO: Função para gerar hashes de dados.
# Hash é uma operação unidirecional (one-way) que produz uma string de tamanho fixo (o "hash" ou "digest")
# a partir de dados de entrada de tamanho arbitrário.
# Principais usos:
# 1. Verificação de integridade de dados (checksums): Se o hash de um dado muda, o dado mudou.
# 2. Indexação de dados ou criação de identificadores únicos.
# 3. Como parte de construções criptográficas mais complexas (ex: HMACs, assinaturas digitais).
# IMPORTANTE: Esta função `hash_data` *não* deve ser usada para armazenar senhas de usuário.
# Para senhas, é crucial usar algoritmos de hashing lentos e com salt, como bcrypt,
# o que é tratado pelo `pwd_context` em `src/security/auth.py`.
def hash_data(data: Union[str, bytes], algorithm: str = 'sha256') -> str:
    """Gera um hash dos dados fornecidos usando o algoritmo especificado.
    
    Args:
        data: Dados a serem hasheados (string UTF-8 ou bytes).
        algorithm: Algoritmo de hash a ser usado ('sha256', 'sha512', 'md5'). Padrão 'sha256'.
        
    Returns:
        str: Hash resultante em formato string hexadecimal.
    """
    # LÓGICA: Garantir que os dados de entrada sejam bytes, pois as funções de hash operam sobre bytes.
    # DECISÃO: Usar UTF-8 como encoding padrão para strings.
    _data_bytes = data.encode('utf-8') if isinstance(data, str) else data
    
    # LÓGICA: Selecionar o algoritmo de hash com base no parâmetro `algorithm`.
    # DECISÃO: Suportar SHA256 (padrão seguro e recomendado), SHA512 (mais seguro, hash mais longo, pode ser mais lento) e MD5.
    # ALERTA DE SEGURANÇA: MD5 é considerado criptograficamente quebrado para fins de resistência a colisões e preimagem.
    # Não deve ser usado para novas aplicações que requerem segurança (ex: assinatura digital, proteção de senha).
    # Sua inclusão aqui pode ser por compatibilidade com sistemas legados ou para usos não relacionados à segurança
    # (ex: checksums não críticos onde a performance é mais importante e a segurança de colisão não é uma preocupação).
    algo_lower = algorithm.lower()
    if algo_lower == 'sha256':
        hasher = hashlib.sha256()
    elif algo_lower == 'sha512':
        hasher = hashlib.sha512()
    elif algo_lower == 'md5': # CRIPTOGRAFIA: MD5 é fraco e não recomendado para fins de segurança.
        hasher = hashlib.md5()
    else:
        # VALIDAÇÃO: Levantar um erro se um algoritmo não suportado for especificado.
        raise ValueError(f"Algoritmo de hash não suportado: {algorithm}")
    
    # LÓGICA: Atualizar o hasher com os bytes dos dados e obter o digest em formato hexadecimal.
    hasher.update(_data_bytes)
    return hasher.hexdigest()

# Resumo Técnico Final
# Pontos fortes da implementação:
# - Utilização da biblioteca `cryptography` para operações criptográficas, que é um padrão robusto em Python.
# - Implementação de derivação de chave (PBKDF2HMAC) para fortalecer a chave de criptografia.
# - Uso correto de AES em modo CBC com IVs aleatórios e padding PKCS7.
# - Funções de conveniência para criptografia/descriptografia e hashing.
# - Suporte a múltiplos algoritmos de hash.
# - Tratamento de exceções específico para erros de criptografia.
# Maturidade técnica demonstrada:
# - Compreensão de conceitos importantes de criptografia como derivação de chave, IVs e padding.
# - A chave de criptografia é externalizada (via `src.config.settings`).
# - A classe `EncryptionManager` encapsula a lógica de criptografia.
# Aderência às boas práticas:
# - Código bem estruturado e comentado.
# - Nomenclatura clara.
# - Uso de type hints.
# - Conversão segura de strings para bytes antes da criptografia/hashing.
# - Uso de `base64.urlsafe_b64encode` para garantir que o output seja seguro para URLs e nomes de arquivo.
