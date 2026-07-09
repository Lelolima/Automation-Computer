# Roadmap - Automation-Computer

Visão geral do desenvolvimento do projeto.

## Fase 1: Fundação (Q3 2026) ✅

- [x] Estrutura básica do projeto
- [x] README e documentação inicial
- [x] Setup de desenvolvimento (requirements, .env.example)
- [x] GoVERNANCA_LGPD.md e LICENSE
- [x] CONTRIBUTING.md

### Entregáveis
- Projeto organizato no GitHub
- Dependências versionadas
- CI/CD básico configurado

## Fase 2: Core de Automação (Q3-Q4 2026) 🟡

### 2.1 Desktop Controller
- [ ] Implementação completa com pywinauto
- [ ] Suporte a múltiplas janelas
- [ ] Detecção de elementos por imagem
- [ ] Gravação e playback de macros

### 2.2 Web Automation
- [ ] Playwright totalmente integrado
- [ ] Selectores inteligentes (CSS, XPath, text)
- [ ] Captcha solver básico
- [ ] Extração de dados estruturados

### 2.3 OCR e Visão
- [ ] Integração Tesseract + OpenCV
- [ ] Detecção de texto em qualquer aplicação
- [ ] Leitura de PDFs

### Entregáveis
- Módulos core funcionais
- Cobertura de testes > 80%
- API estável

## Fase 3: IA e Autonomia (Q4 2026 - Q1 2027) 🔜

### 3.1 LLM Orchestration
- [ ] Integrações: Claude, GPT, Ollama (local)
- [ ] Fallback automático entre providers
- [ ] Contexto persistente entre sessões
- [ ] Plan generation e execução

### 3.2 Decision Engine
- [ ] Árvore de decisão para automação
- [ ] Detecção e recuperação de erros
- [ ] Aprendizado com execuções anteriores

### 3.3 Visão Computacional
- [ ] MediaPipe para detecção de UI elements
- [ ] Modelo YOLO customizado para apps comuns
- [ ] Reconhecimento de padrões visuais

### Entregáveis
- Agente capaz de executar tarefas descritas em NL
- Dashboard de acompanhamento
- Modo "observador" (apenas log, sem execução)

## Fase 4: Interface e UX (Q1 2027) 🔜

### 4.1 CLI Avançada
- [ ] Typer + Rich com autocomplete
- [ ] Histórico de comandos
- [ ] Templates de automação
- [ ] Modo interativo

### 4.2 Voice Interface
- [ ] Speech-to-text (Whisper local)
- [ ] Text-to-speech (pyttsx3)
- [ ] Comandos de voz naturais

### 4.3 Dashboard Web
- [ ] FastAPI backend
- [ ] React frontend
- [ ] Visualização em tempo real
- [ ] Configuração via UI

### Entregáveis
- Múltiplas interfaces (CLI, Voz, Web)
- Experiência de usuário polida

## Fase 5: Produção (Q2 2027) 🔜

### 5.1 Escalabilidade
- [ ] Sistema de filas (Celery + Redis)
- [ ] Execuções paralelas
- [ ] Rate limiting distribuído

### 5.2 Monitoramento
- [ ] Prometheus + Grafana
- [ ] Alertas configuráveis
- [ ] Métricas de performance

### 5.3 Docker e Deploy
- [ ] Dockerfile para Linux e Windows (nanoserver)
- [ ] Docker Compose para stack completo
- [ ] Helm charts para Kubernetes

### Entregáveis
- Pronto para produção
- Documentação completa de deploy

## Fase 6: Ecossistema (Q3 2027+) 🔜

### 6.1 Comunidade
- [ ] Plugin system
- [ ] Marketplace de automações
- [ ] API pública documentada

### 6.2 Enterprise
- [ ] SSO/SAML
- [ ] RBAC avançado
- [ ] Audit trails para compliance (SOC2, HIPAA)

---

## Prioridades

A qualquer momento, focamos em:
1. **Segurança**: Nunca comprometer
2. **Confiabilidade**: Funciona sempre ou falha de forma segura
3. **Usabilidade**: Fácil de usar e entender
4. **Performance**: Rápido e eficiente

## Como Acompanhar

- [GitHub Projects](https://github.com/Lelolima/Automation-Computer/projects)
- [Issues em aberto](https://github.com/Lelolima/Automation-Computer/issues)
- [Changelog](CHANGELOG.md) - a definir

## Contribuir

Quer ajudar com alguma fase? Veja as issues marcadas com `help wanted` ou proponha novas features!

---

*Última atualização: Julho de 2026*
*Próxima revisão: Agosto de 2026*