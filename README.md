# Agente Autônomo de Automação Integrada

Sistema avançado de automação que combina navegação web complexa e controle local em Windows, com interface de voz/texto e segurança robusta. Desenvolvido para automatizar tarefas repetitivas, integrar sistemas e melhorar a produtividade com foco em segurança e confiabilidade.

## 🌟 Funcionalidades Detalhadas

### 🖥️ Automação Desktop
- **Controle de Mouse e Teclado**
  - Movimento preciso do mouse com aceleração controlável
  - Cliques personalizáveis (simples, duplo, botão direito/esquerdo/meio)
  - Roda de rolagem programável com controle de intensidade
  - Simulação de digitação natural com atrasos configuráveis
  - Suporte a atalhos de teclado complexos

- **Gerenciamento de Janelas**
  - Ativação de janelas por título, classe ou identificador
  - Listagem e filtragem de janelas abertas
  - Controle preciso de tamanho, posição e estado (minimizado/maximizado)
  - Identificação de janelas ativas e monitoramento de foco

- **Captura e Análise de Tela**
  - Captura de tela completa ou por região específica
  - Reconhecimento óptico de caracteres (OCR) multilíngue
  - Localização de imagens na tela com tolerância a variações
  - Extração de texto e elementos visuais com formatação

### 🌐 Automação Web
- **Navegação Avançada**
  - Suporte a múltiplos navegadores (Chrome, Firefox, Edge)
  - Preenchimento inteligente de formulários
  - Navegação em SPAs com carregamento dinâmico
  - Interação com elementos web complexos (menus suspensos, modais)

- **Extração de Dados**
  - Web scraping com suporte a JavaScript
  - Coleta estruturada de dados de tabelas e listas
  - Extração de mídia (imagens, vídeos, documentos)
  - Exportação para CSV, JSON, Excel e bancos de dados

- **Integração com APIs**
  - Cliente HTTP com suporte a múltiplos formatos
  - Autenticação OAuth 2.0, JWT e API Keys
  - Processamento assíncrono de requisições
  - Webhooks e filas de mensagens

### 🔒 Segurança Avançada
- **Criptografia**
  - Criptografia simétrica com Fernet (AES-128)
  - Hash de senhas com bcrypt e salt
  - Mascaramento de dados sensíveis em logs
  - Armazenamento seguro de credenciais
  - Gerenciamento de ciclos de vida de chaves

### 🤖 Integração com IA
- **Processamento de Linguagem Natural**
  - Análise de sentimento
  - Extração de entidades nomeadas
  - Tradução automática
  - Geração de resumos

- **Visão Computacional**
  - Reconhecimento de objetos
  - Detecção facial
  - Análise de imagens
  - OCR avançado

### 📊 Monitoramento e Logs
- **Registro de Atividades**
  - Logs detalhados com diferentes níveis de severidade
  - Rastreamento de execução
  - Auditoria de segurança

- **Métricas de Desempenho**
  - Tempo de execução
  - Uso de recursos
  - Estatísticas de erros

## 🛠️ Tecnologias Utilizadas

- **Linguagem**: Python 3.8+
- **Automação Web**: Playwright, Selenium
- **Automação Desktop**: PyAutoGUI, PyWinAuto
- **Segurança**: Cryptography, python-jose
- **IA/ML**: Transformers, spaCy, OpenCV
- **Testes**: pytest, pytest-cov
- **CI/CD**: GitHub Actions
- **Documentação**: MkDocs, Sphinx

- **Autenticação**
  - Autenticação JWT (JSON Web Tokens)
  - Controle de acesso baseado em funções (RBAC)
  - Refresh tokens
  - Validação de sessão

- **Proteções**
  - Sanitização de entrada/saída
  - Prevenção contra injeção SQL/HTML
  - Rate limiting
  - Auditoria de operações

### 🤖 Inteligência Artificial
- **Análise de Documentos**
  - Processamento de texto com LLMs
  - Comparação semântica de documentos
  - Extração de cláusulas e termos
  - Análise de conformidade

- **Scraping Inteligente**
  - Navegação adaptativa
  - Resolução de CAPTCHAs
  - Detecção de mudanças estruturais
  - Fallback entre estratégias

### 📊 Monitoramento e Logs
- **Auditoria**
  - Registro detalhado de operações
  - Histórico de execuções
  - Métricas de desempenho
  - Alertas de segurança

- **Relatórios**
  - Geração de relatórios em PDF/Excel
  - Dashboards interativos
  - Exportação de dados
  - Análise de tendências

## 🚀 Começando

### 📋 Pré-requisitos

- Python 3.10+
- Git
- Tesseract OCR (para reconhecimento de texto)
- Navegadores modernos (Chrome, Firefox, Edge)
- Acesso a APIs de IA (OpenAI, Anthropic - opcional)

### 🛠️ Instalação

1. **Clone o repositório**
   ```bash
   git clone https://github.com/Lelolima/automation-Computer.git
   cd automation-agent
   ```

2. **Configure o ambiente virtual**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # Linux/MacOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure os navegadores**
   ```bash
   playwright install
   playwright install-deps  # Dependências do sistema
   ```

5. **Configure o ambiente**
   ```bash
   # Copie o arquivo de exemplo
   cp .env.example .env
   
   # Edite o arquivo .env com suas configurações
   # Inclua suas chaves de API e configurações específicas
   ```

6. **Instale o Tesseract OCR**
   - Windows: Baixe o instalador do [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
   - Linux: `sudo apt install tesseract-ocr`
   - Mac: `brew install tesseract`

7. **Execute os testes**
   ```bash
   pytest tests/unit/ -v
   ```

## 🚦 Como Usar

### ⚡ Iniciando o Sistema

```bash
# Modo interativo
python main.py

# Executar tarefa específica
python main.py --task "nome_da_tarefa"

# Modo silencioso (sem interface)
python main.py --headless
```

### 🎯 Exemplos de Uso

#### Automação Desktop
```python
from automation.desktop.controller import DesktopController

# Inicializa o controlador
desktop = DesktopController()

# Mover o mouse e clicar
desktop.move_mouse(100, 200)
desktop.click(button="left")

# Digitar texto
desktop.type_text("Olá, mundo!")

# Capturar tela
desktop.capture_screen(save_path="screenshot.png")
```

#### Automação Web
```python
from automation.web.browser import WebAutomation

# Inicializa o navegador
browser = WebAutomation()
browser.navigate("https://exemplo.com")

# Preencher formulário
browser.fill_form({
    "#username": "usuario",
    "#password": "senha_segura"
})

# Extrair dados
data = browser.extract_data({
    "titulo": "h1",
    "itens": ["li.item"]
})
```

### 🛠️ Configuração Avançada

Edite o arquivo `config/settings.py` para personalizar:

```python
# Configurações de segurança
SECURITY = {
    "ENABLE_ENCRYPTION": True,
    "SENSITIVE_FIELDS": ["senha", "token", "chave"]
}

# Configurações de IA
AI = {
    "PROVIDER": "openai",  # ou "anthropic"
    "MODEL": "gpt-4",
    "TEMPERATURE": 0.7
}
```

### 📊 Monitoramento

Acesse o painel de monitoramento em:
```
http://localhost:8000/dashboard
```

## 🧪 Testes

```bash
# Todos os testes
pytest

# Testes unitários
pytest tests/unit

# Testes de integração
pytest tests/integration

# Com cobertura de código
pytest --cov=src --cov-report=html
```

## 🔒 Segurança

### 🚨 Boas Práticas

1. **Proteja suas credenciais**
   - Nunca faça commit do arquivo `.env`
   - Use variáveis de ambiente para dados sensíveis
   - Revise as permissões de arquivos regularmente

2. **Atualizações**
   - Mantenha todas as dependências atualizadas
   - Assine nossa lista de segurança para alertas
   - Aplique patches de segurança imediatamente

3. **Monitoramento**
   - Revise os logs regularmente
   - Configure alertas para atividades suspeitas
   - Mantenha backups seguros

### 🛡️ Recursos de Segurança

- **Criptografia em Repouso**
  - Dados sensíveis são criptografados antes do armazenamento
  - Chaves de criptografia são gerenciadas de forma segura
  
- **Proteções de Execução**
  - Sandbox para operações não confiáveis
  - Timeout para operações demoradas
  - Limites de recursos para prevenir abuso
  
- **Conformidade**
  - LGPD/GDPR ready
  - Logs de auditoria detalhados
  - Política de retenção de dados

## 🌐 Suporte

### 📚 Documentação
- [Guia do Usuário](docs/user_guide.md)
- [API Reference](docs/api.md)
- [FAQ](docs/faq.md)
- [Troubleshooting](docs/troubleshooting.md)

### 🆘 Suporte Técnico
1. Consulte nossa [documentação](docs/)
2. Verifique as [issues abertas](https://github.com/Lelolima/automation-Computer/issues)
3. [Abra um ticket](https://github.com/Lelolima/automation-Computer/issues/new/choose)

## 🤝 Contribuindo

1. Faça um Fork do projeto
2. Crie sua Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a Branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

## ✨ Reconhecimentos

- [Playwright](https://playwright.dev/) - Automação de navegadores
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Validação de dados
- [FastAPI](https://fastapi.tiangolo.com/) - API Web
- [Rich](https://github.com/willmcgugan/rich) - Interface no terminal

## 📞 Contato

Equipe de Desenvolvimento - [lelolima806@gmail.com
Link do Projeto: [https://github.com/Lelolima/automation-Computer](https://github.com/Lelolima/automation-Computer)

---

<div align="center">
  <sub>Criado com ❤️ por [Wellington de lima catarina>
</div>
