# User Guide

## Introdução

Automation-Computer é um sistema de RPA (Robotic Process Automation) que permite automatizar tarefas computacionais usando Python.

## Instalação

### Windows

```powershell
# Clonar repositório
git clone https://github.com/Lelolima/Automation-Computer.git
cd Automation-Computer

# Criar ambiente virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt

# Instalar browsers do Playwright
playwright install
```

## Primeiros Passos

### 1. Automação Desktop Básica

```python
from src.automation.desktop_controller import DesktopController

# Inicializar
desktop = DesktopController()

# Abrir aplicação
desktop.start_app("notepad.exe")

# Digitar texto
desktop.type_text("Hello World!")

# Pressionar tecla
desktop.press_key("enter")

# Click em posição
desktop.click(x=100, y=200)
```

### 2. Automação Web

```python
import asyncio
from src.automation.web_automation import WebAutomation

async def main():
    async with WebAutomation() as browser:
        # Navegar
        await browser.navigate("https://google.com")

        # Preencher busca
        await browser.fill("input[name='q']", "Python RPA")
        await browser.press_key("Enter")

        # Esperar resultados
        await browser.wait_for_selector("#search")

        # Extrair dados
        titles = await browser.extract_all("h3")
        for title in titles:
            print(title["value"])

asyncio.run(main())
```

### 3. Usando a CLI

```bash
# Ver status
python -m src.ui.cli status

# Versão
python -m src.ui.cli version

# Ajudar
python -m src.ui.cli --help
```

## Segurança

### Criptografar Dados Sensíveis

```python
from src.security import EncryptionService

enc = EncryptionService()

# Criptografar
segredo = enc.encrypt("minha_senha")

# Descriptografar
senha = enc.decrypt(segredo)
```

### Auditoria

```python
from src.security import Auditor

auditor = Auditor()

# Logar ação
auditor.log_action("click", "usuario1", {"element": "btn_submit"})

# Salvar logs
auditor.save_logs()

# Consultar logs
logs = auditor.get_logs(agent="usuario1")
```

## Integração com IA

```python
from src.ai import LLMOrchestrator

llm = LLMOrchestrator()

# Gerar plano
plano = await llm.generate_plan(
    "Abra o bloco de notas e digite 'Ola Mundo'"
)

# Chat
resposta = await llm.chat("Como faço para capturar uma tela?")
```

## Troubleshooting

### Playwright não funciona

```bash
playwright install
```

### Erro de permissão no Windows

Execute o PowerShell como Administrador ou:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Ollama não conecta

Verifique se o Ollama está rodando:

```bash
ollama serve
```

## Próximos Passos

- Veja os exemplos em `examples/`
- Leia `GOVERNANCA_LGPD.md` para conformidade
- Consulte `ROADMAP.md` para funcionalidades futuras