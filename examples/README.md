# Exemplos de Automação

Este diretório contém exemplos práticos que demonstram como utilizar os diferentes módulos do sistema de automação.

## Exemplos Disponíveis

### 1. Automação Web (`web_automation_example.py`)
Demonstra o uso do módulo de automação web para navegar em páginas, preencher formulários e extrair dados.

**Como executar:**
```bash
python -m examples.web_automation_example
```

### 2. Automação de Desktop (`desktop_automation_example.py`)
Mostra como automatizar tarefas comuns em aplicativos desktop, incluindo:
- Controle do mouse e teclado
- Gerenciamento de janelas
- Captura de tela e OCR

**Pré-requisitos:**
- Python 3.8+
- Dependências instaladas (veja o arquivo `requirements.txt` na raiz do projeto)
- Acesso a um ambiente gráfico (para automação de desktop)

**Como executar:**
```bash
python -m examples.desktop_automation_example
```

**Dicas:**
1. Execute o script e mude rapidamente para a janela onde deseja testar a automação
2. O script aguardará 5 segundos antes de começar
3. Os logs serão exibidos no console e salvos em `desktop_automation.log`

## Estrutura do Código

Cada exemplo é autocontido e inclui:
- Configuração de logging
- Tratamento de erros
- Comentários explicativos
- Validações de segurança

## Personalização

Você pode modificar os exemplos para atender às suas necessidades específicas. Consulte a documentação de cada módulo para obter mais detalhes sobre as funcionalidades disponíveis.

## Solução de Problemas

- **Problemas de permissão:** Certifique-se de que o aplicativo tem permissão para controlar o mouse/teclado
- **Janelas não encontradas:** Verifique se o título da janela está correto e visível
- **Erros de OCR:** Verifique se a região de captura contém texto legível

## Segurança

- Nunca execute exemplos não confiáveis
- Revise o código antes de executar
- Certifique-se de que não há dados sensíveis na área de trabalho durante os testes

## Contribuindo

Sinta-se à vontade para contribuir com novos exemplos ou melhorias nos existentes. Certifique-se de seguir as diretrizes de contribuição do projeto.
