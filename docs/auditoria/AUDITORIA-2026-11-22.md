# Auditoria — 2026-11-22

**Repositório:** Lelolima/Automation-Computer (branch padrão: `master`)
**Finalidade real:** biblioteca/CLI de RPA em Python com automação desktop (pywinauto/pynput, só Windows), automação web (Playwright), orquestração de LLMs (Anthropic/OpenAI/Ollama com fallback) e utilitários de segurança. Vários recursos citados no README (visão computacional, dashboard, chat persistente, detecção por imagem) **não existem no código**.

## Estado anterior
- CI (run 29037644959): o job **lint** falhava e test/build eram pulados. Os logs expiraram; reproduzi localmente: `black --check` reformataria 15 arquivos e `mypy` acusava 28 erros. O flake8 (E9/F63/F7/F82) passava. Além disso, o job de build usava `actions/upload-artifact@v3`, que foi descontinuada.
- Testes locais: 14 coletados, **2 falhando** (expectativas inconsistentes em `test_get_logs_filter` e `test_rate_limit_exceeded`).
- `validate_fixes.py`: 6/8 (rate limiter e erro de encoding `charmap`).
- `requirements.txt` instalava torch, transformers, mediapipe, opencv, fastapi etc., que nenhum módulo em `src/` importa. `pywinauto` sem marcador de plataforma.

## Problemas encontrados

| # | Sev. | Problema | Evidência | Correção |
|---|------|----------|-----------|----------|
| 1 | P0 | `Sandbox.is_path_allowed` comparava por `startswith` de string: com `/dados` permitido, `/dados_evil/x` passava | `test_caminho_com_mesmo_prefixo_negado` falhava | Comparação por componentes (`parents`) |
| 2 | P2 | `is_domain_allowed` rejeitava host em maiúsculas (falso negativo; não era bypass) | `test_dominio_maiusculo_e_credenciais` | `parsed.hostname.lower()` |
| 3 | P1 | `generate_plan` com Anthropic nunca extraía o plano: passava a lista de blocos ao parser e devolvia a lista crua na descrição | `test_generate_plan_anthropic_parseia_blocos` falhava | Concatena o `.text` dos blocos |
| 4 | P1 | `status` da CLI mostrava "✅ Disponível" fixo (estado simulado exibido como real) | código | Importa cada módulo de verdade e mostra o erro se falhar |
| 5 | P2 | `python-dotenv` era dependência, mas o `.env` nunca era carregado; `.env.example` listava variáveis que nada lê (ENCRYPTION_KEY, RATE_LIMIT_*, VOICE_*) | grep por `getenv` | `load_dotenv()` na CLI; `.env.example` só com as variáveis lidas, sem valores |
| 6 | P1 | CI quebrado | run 29037644959 | Workflow enxuto novo |
| 7 | P2 | Testes com expectativas incoerentes com os dados (auditor: 2 "click" esperando 1) e com a semântica do burst | — | Testes corrigidos, mais teste do limite por minuto com tempo controlado |
| 8 | P2 | Sem testes de Sandbox, LLMOrchestrator, CLI ou navegador real | — | `test_llm_orchestrator.py` (clientes falsos, nenhuma API paga), `test_cli.py`, testes de Sandbox e `test_web_automation_real.py` (Chromium headless em HTML local) |
| 9 | P2 | Instalação pesada com dependências não usadas | grep de imports | Movidas para `requirements-optional.txt` (nada foi removido); `pywinauto; sys_platform == "win32"` |
| 10 | P3 | black, imports não usados, `validate_fixes.py` frágil (encoding, checagem de AST sempre falsa) | — | Corrigido; agora 8/8 |

**Segredos:** nada encontrado. Busquei padrões AWS, GitHub, OpenAI/Anthropic (`sk-`, `sk-ant-`), Slack, Google e chaves privadas na árvore e em `git log -p --all`; gitleaks não está instalado. O `.env.example` tinha placeholders `sk-ant-...`/`sk-...`, não chaves reais; agora estão vazios.
**Dependências:** `pip-audit -r requirements.txt` e `pip-audit -r requirements-optional.txt` → "No known vulnerabilities found".

## Testes executados (local, Windows 11, Python 3.13.15)
- `pytest -rs --cov=src` → **28 passed**, 0 skipped, cobertura de 52%. Inclui o teste real com Chromium (`playwright install chromium` executado). A suíte foi repetida após o aviso de `taskkill` de outro worker, com o mesmo resultado.
- `flake8 ... --select=E9,F63,F7,F82,F401,F841` → 0; `black --check` → ok.
- `python validate_fixes.py` → 8/8.
- `python -m src status` → tabela com os 5 módulos disponíveis.
- `python -m build` → sdist e wheel gerados.
- **Não executado:** automação desktop real (mover mouse, teclado, janelas). Ela controlaria a sessão gráfica do usuário, por isso os testes de `DesktopController` continuam com mocks. Também não executei chamadas reais a Anthropic/OpenAI (APIs pagas, sem credenciais) nem ao Ollama (servidor não instalado).

## CI novo
`.github/workflows/ci.yml`: `permissions: contents: read`, actions fixadas por SHA, ferramentas com versão fixa. Lint no Ubuntu, testes no **Windows** (pywinauto) com Chromium e build do pacote. Sem deploy nem upload de artefato.

## Riscos residuais / decisões do dono
- `mypy` acusa 28 erros (principalmente `Optional[Page]` sem checagem: chamar métodos antes de `start()` gera `AttributeError` pouco claro). Saiu do CI obrigatório; corrigir é débito P2.
- Confirme se a semântica do `RateLimiter` (burst = máximo de requisições por segundo) é a desejada. Os testes antigos esperavam outra coisa.
- Decida se os extras de `requirements-optional.txt` devem continuar no projeto e se o README deve remover as promessas não implementadas (só adicionei uma nota de "estado real").
- A cobertura de `desktop_controller` e `web_automation` com mocks é limitada.
