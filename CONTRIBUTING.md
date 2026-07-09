# Contribuindo para o Automation-Computer

Obrigado pelo seu interesse em contribuir! Este guia ajuda você a começar.

## 🌟 Como Contribuir

### 1. Reportar Bugs
- Verifique se o bug já foi reportado nas [Issues](https://github.com/Lelolima/Automation-Computer/issues)
- Use o template de bug report
- Inclua: Python version, OS, passos para reproduzir, logs

### 2. Sugerir Features
- Discuta a feature em uma Issue antes de implementar
- Explique o caso de uso e benefícios
- Considere impactos na segurança

### 3. Enviar Código

#### Setup de Desenvolvimento

```bash
# Fork e clone
git clone https://github.com/SEU-USER/Automation-Computer.git
cd Automation-Computer

# Ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\Activate.ps1  # Windows

# Dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Playwright browsers
playwright install
```

#### Padrões de Código

```python
# Type hints obrigatórios
def process_data(data: dict, retries: int = 3) -> dict:
    """Processa dados com retry automático.
    
    Args:
        data: Dicionário com dados de entrada
        retries: Número máximo de tentativas
        
    Returns:
        Dicionário processado
        
    Raises:
        ProcessError: Se falhar após retries
    """
    pass

# Docstrings no formato Google
# Logs estruturados
# Tratamento de exceções específico
```

#### Testes

```bash
# Todos os testes
pytest tests/ -v

# Com coverage
pytest tests/ -v --cov=src --cov-report=html

# Tipo checking
mypy src/

# Formatação
black src/ tests/
isort src/ tests/
```

#### Commit Messages

Siga [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: adiciona OCR para capturas de tela
fix: corrige vazamento de memória no desktop controller
docs: atualiza README com exemplos de uso
test: adiciona testes para encryption module
refactor: simplifica lógica do decision engine
```

#### Pull Request

1. Branch do seu fork
2. Nome descritivo: `feature/nome-da-feature` ou `fix/nome-do-bug`
3. Preencha o template de PR
4. Aguarde CI passar
5. Mantenha o PR atualizado com a main

## 🏷️ Tipos de Contribuição

| Tipo | Descrição | Exemplos |
|------|-----------|----------|
| `feat` | Nova feature | Novo módulo de automação |
| `fix` | Correção de bug | Fix em race condition |
| `docs` | Documentação | README, docstrings |
| `style` | Formatação | Black, isort |
| `refactor` | Refatoração | Melhoria de código existente |
| `test` | Testes | Novos testes unitários |
| `chore` | Build/CI | GitHub Actions, requirements |

## 🔒 Segurança

Contribuições que envolvem segurança devem:
1. Não expor credenciais em logs
2. Usar as funções de encryption existentes
3. Seguir princípio do menor privilégio
4. Passar por revisão de segurança extra

## 📜 Código de Conduta

- Seja respeitoso e inclusivo
- Construa sobre o trabalho existente
- Discuta mudanças significativas antes de implementar
- Aceite feedback construtivo

## 🎯 Issues Boas para Começar

Procure por labels:
- `good first issue` - Simples, ideal para primeira contribuição
- `help wanted` - Precisamos de ajuda
- `bug` - Correções de bugs
- `documentation` - Melhorias na docs

## 📞 Dúvidas?

- Abra uma Issue com a tag `question`
- Discord: [link a definir]
- Email: contrib@automation-computer.dev

---

Obrigado por contribuir! 🚀