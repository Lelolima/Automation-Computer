# API Reference

## Automation

### DesktopController

```python
from src.automation import DesktopController
```

#### Métodos

| Método | Parâmetros | Descrição |
|--------|------------|-----------|
| `start_app(app_path)` | `app_path: str` | Inicia aplicação |
| `connect_app(window_title)` | `window_title: str` | Conecta a janela existente |
| `click(x, y, button, clicks)` | `x: int, y: int, button: str, clicks: int` | Click na tela |
| `type_text(text, delay)` | `text: str, delay: float` | Digita texto |
| `press_key(key)` | `key: str` | Pressiona tecla |
| `move_to(x, y)` | `x: int, y: int` | Move mouse |
| `scroll(x, y, dx, dy)` | `x: int, y: int, dx: int, dy: int` | Scroll |

### WebAutomation

```python
from src.automation import WebAutomation
```

#### Métodos

| Método | Parâmetros | Descrição |
|--------|------------|-----------|
| `navigate(url, wait_until)` | `url: str` | Navega para URL |
| `click(selector, timeout)` | `selector: str` | Click em elemento |
| `fill(selector, value)` | `selector: str, value: str` | Preenche input |
| `get_text(selector)` | `selector: str` | Obtém texto |
| `extract_data(selector, attribute)` | `selector: str` | Extrai dado |
| `screenshot(path, full_page)` | `path: str` | Tira screenshot |

## Security

### EncryptionService

```python
from src.security import EncryptionService
```

```python
enc = EncryptionService(key=None)
encrypted = enc.encrypt("dados")
decrypted = enc.decrypt(encrypted)
hashed = enc.hash_sensitive("senha")
```

### PasswordService

```python
from src.security import PasswordService

hashed = PasswordService.hash_password("senha")
valid = PasswordService.verify_password("senha", hashed)
```

### RateLimiter

```python
from src.security import RateLimiter

limiter = RateLimiter(requests_per_minute=60, burst=10)
if limiter.acquire():
    # executar ação
    pass
```

### Auditor

```python
from src.security import Auditor

auditor = Auditor(log_path="audit.json")
auditor.log_action("click", "user1", {"elem": "btn"})
auditor.save_logs()
logs = auditor.get_logs(agent="user1", limit=100)
```

## AI

### LLMOrchestrator

```python
from src.ai import LLMOrchestrator

llm = LLMOrchestrator(
    primary_provider="anthropic",
    fallback_providers=["openai", "ollama"]
)

# Gerar plano
plano = await llm.generate_plan("tarefa em linguagem natural")

# Chat
resposta = await llm.chat("mensagem", system="instrucao")
```

## Configuração

Variáveis de ambiente (`.env`):

```bash
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
OLLAMA_HOST=http://localhost:11434

RATE_LIMIT_REQUESTS_PER_MINUTE=60
SANDBOX_ENABLED=true
AUDIT_ENABLED=true
```