# Segurança

## Visão Geral

A segurança é um pilar fundamental do Automation-Computer. Este documento descreve as medidas de segurança implementadas.

## Criptografia

### Dados em Repouso

- **Algoritmo**: Fernet (AES-128-CBC)
- **Chave**: Gerada automaticamente na primeira execução
- **Armazenamento**: Arquivo `.encryption_key` (não versionado)

```python
from src.security import EncryptionService

# Gerar nova chave
enc = EncryptionService()
enc.save_key(".encryption_key")

# Carregar chave existente
enc = EncryptionService.load_key(".encryption_key")
segredo = enc.encrypt("dados_sensiveis")
```

### Senhas

- **Algoritmo**: bcrypt
- **Custo**: 12 rounds (configurável)
- **Salt**: Aleatório por senha

```python
from src.security import PasswordService

hashed = PasswordService.hash_password("minha_senha")
valid = PasswordService.verify_password("minha_senha", hashed)
```

## Rate Limiting

Previne abuso acidental de APIs e sistemas:

- **Padrão**: 60 requisições/minuto
- **Burst**: 10 requisições imediatas
- **Ação**: Bloqueio temporário

```python
from src.security import RateLimiter

limiter = RateLimiter(requests_per_minute=60, burst=10)

if not limiter.acquire():
    print("Rate limit excedido. Aguarde.")
```

## Sandboxing

Isola execuções de automação:

- **Paths permitidos**: Lista branca de diretórios
- **Domínios permitidos**: Lista branca de URLs
- **Limite de memória**: 512MB (configurável)

```python
from src.security import Sandbox

with Sandbox(
    allowed_paths=["./outputs", "./temp"],
    allowed_domains=["example.com", "api.github.com"]
) as sandbox:
    # Execuções seguras aqui
    if sandbox.is_path_allowed("/etc/passwd"):
        print("Acesso permitido")
    else:
        print("Acesso negado - fora da sandbox")
```

## Auditoria

Todas as ações são registradas:

- **Timestamp**: ISO 8601
- **Agente**: Usuário ou sistema
- **Ação**: Nome da operação
- **Detalhes**: Contexto (sem dados sensíveis)
- **Resultado**: Sucesso ou falha

```python
from src.security import Auditor

auditor = Auditor(log_path="audit_logs.json")

# Logar ação
auditor.log_action(
    action="web_scraping",
    agent="usuario123",
    details={"url": "https://example.com", "status": "success"}
)

# Salvar logs
auditor.save_logs()

# Consultar
logs = auditor.get_logs(agent="usuario123", limit=50)
```

## Mascaramento de Dados Sensíveis

Logs não expõem dados sensíveis:

| Tipo | Máscara |
|------|---------|
| CPF | `***.***.***-**` |
| Email | `***@***.***` |
| API Key | `sk-***...***` |
| Senha | `[REDACTED]` |

## LGPD

O projeto é conforme com a Lei Geral de Proteção de Dados. Veja `GOVERNANCA_LGPD.md` para detalhes.

## Boas Práticas

1. **Nunca commitar `.env` ou chaves de criptografia**
2. **Sempre usar sandbox para automações não testadas**
3. **Habilitar auditoria em produção**
4. **Rotacionar chaves de API regularmente**
5. **Revisar logs de auditoria periodicamente**

## Vulnerabilidades Reportadas

Para reportar vulnerabilidades de segurança:
- Email: security@automation-computer.dev
- Não abra issues públicas para vulnerabilidades