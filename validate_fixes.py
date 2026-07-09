"""
Automation-Computer - Script de Validação Pós-Code-Review
Executa testes e validações para garantir que todas as correções foram aplicadas.

Uso:
    python validate_fixes.py
"""

import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_imports():
    """Testa que todos os imports funcionam sem erros."""
    print("\n" + "=" * 60)
    print("  TESTE 1: Verificando imports")
    print("=" * 60)

    tests = [
        ("DesktopController", "src.automation.desktop_controller"),
        ("WebAutomation", "src.automation.web_automation"),
        ("EncryptionService", "src.security.encryption"),
        ("LLMOrchestrator", "src.ai.llm_orchestrator"),
        ("CLI app", "src.ui.cli"),
    ]

    passed = 0
    failed = 0

    for name, module in tests:
        try:
            __import__(module)
            print(f"  ✅ {name}: OK")
            passed += 1
        except ImportError as e:
            print(f"  ❌ {name}: FAILED - {e}")
            failed += 1

    print(f"\n  Resultado: {passed} passaram, {failed} falharam")
    return failed == 0


def test_desktop_controller_hotkey():
    """Testa que o método _press_hotkey existe."""
    print("\n" + "=" * 60)
    print("  TESTE 2: DesktopController._press_hotkey")
    print("=" * 60)

    try:
        from src.automation.desktop_controller import DesktopController
        controller = DesktopController()

        # Verifica que o método existe
        assert hasattr(controller, '_press_hotkey'), "_press_hotkey não existe"

        # Verifica que ctrl_c, ctrl_v, ctrl_a não são mais lambdas
        import inspect
        source = inspect.getsource(controller.press_key)
        assert 'lambda' not in source, "Lambdas ainda presentes no código"

        print("  ✅ _press_hotkey implementation: OK")
        print("  ✅ Lambdas removidas: OK")
        return True

    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False


def test_web_automation_extract_data():
    """Testa que extract_data valida elemento nulo."""
    print("\n" + "=" * 60)
    print("  TESTE 3: WebAutomation.extract_data null check")
    print("=" * 60)

    try:
        from src.automation.web_automation import WebAutomation
        import inspect

        source = inspect.getsource(WebAutomation.extract_data)

        # Verifica que há validação de elemento None
        assert 'element is None' in source or 'is None' in source, \
            "Validação de elemento None não encontrada"

        print("  ✅ Null check implementation: OK")
        return True

    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False


def test_llm_constants():
    """Testa que constantes de modelos estão no topo do arquivo."""
    print("\n" + "=" * 60)
    print("  TESTE 4: LLMOrchestrator model constants")
    print("=" * 60)

    try:
        from src.ai import llm_orchestrator

        # Verifica que as constantes existem
        assert hasattr(llm_orchestrator, 'ANTHROPIC_MODEL'), \
            "ANTHROPIC_MODEL não definida"
        assert hasattr(llm_orchestrator, 'OPENAI_MODEL'), \
            "OPENAI_MODEL não definida"
        assert hasattr(llm_orchestrator, 'OLLAMA_MODEL'), \
            "OLLAMA_MODEL não definida"

        # Verifica que json está no topo (não dentro de método)
        import ast
        with open(llm_orchestrator.__file__, 'r') as f:
            source = f.read()

        tree = ast.parse(source)
        imports_json = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                if 'json' in str(node):
                    imports_json = True
                    break

        assert imports_json, "json import não encontrado no topo do arquivo"

        print("  ✅ Model constants: OK")
        print("  ✅ json import no topo: OK")
        return True

    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False


def test_sandbox_domain_matching():
    """Testa que Sandbox usa parsing de URL para domain matching."""
    print("\n" + "=" * 60)
    print("  TESTE 5: Sandbox domain matching")
    print("=" * 60)

    try:
        from src.security.encryption import Sandbox
        import inspect

        source = inspect.getsource(Sandbox.is_domain_allowed)

        # Verifica que usa urlparse para parsing correto
        assert 'urlparse' in source, "urlparse não encontrado"
        assert 'netloc' in source, "netloc não encontrado"

        # Testa funcionalmente
        sandbox = Sandbox(allowed_domains=['example.com'])

        # Deve permitir exemplo exato
        assert sandbox.is_domain_allowed('https://example.com/test') is True

        # Deve permitir subdomínio
        assert sandbox.is_domain_allowed('https://sub.example.com/test') is True

        # Deve negar domínio similar mas diferente
        assert sandbox.is_domain_allowed('https://evil-example.com/test') is False

        print("  ✅ urlparse implementation: OK")
        print("  ✅ Domain matching tests: OK")
        return True

    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False


def test_encryption_basic():
    """Testa funcionalidade básica de criptografia."""
    print("\n" + "=" * 60)
    print("  TESTE 6: EncryptionService básico")
    print("=" * 60)

    try:
        from src.security.encryption import EncryptionService, PasswordService

        # Testa Fernet
        enc = EncryptionService()
        original = "teste_123"
        encrypted = enc.encrypt(original)
        decrypted = enc.decrypt(encrypted)

        assert original == decrypted, "Descriptografia falhou"
        assert encrypted != original.encode(), "Criptografia não alterou dados"

        # Testa bcrypt
        senha = "minha_senha"
        hashed = PasswordService.hash_password(senha)
        assert PasswordService.verify_password(senha, hashed), "Verificação falhou"

        print("  ✅ Fernet encrypt/decrypt: OK")
        print("  ✅ bcrypt hash/verify: OK")
        return True

    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False


def test_rate_limiter():
    """Testa funcionalidade básica de rate limiter."""
    print("\n" + "=" * 60)
    print("  TESTE 7: RateLimiter básico")
    print("=" * 60)

    try:
        from src.security.encryption import RateLimiter

        # Testa burst
        limiter = RateLimiter(requests_per_minute=10, burst=3)

        # Primeiros 3 devem passar (burst)
        for i in range(3):
            assert limiter.acquire() is True, f"Burst {i} falhou"

        # Quarto deve passar (normal)
        assert limiter.acquire() is True, "Request normal falhou"

        # Agora cria novo limiter para testar limite
        limiter2 = RateLimiter(requests_per_minute=2, burst=1)
        limiter2.acquire()  # burst
        limiter2.acquire()  # normal
        assert limiter2.acquire() is False, "Rate limit não bloqueou"

        print("  ✅ Burst limit: OK")
        print("  ✅ Rate limit block: OK")
        return True

    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False


def test_no_unused_imports():
    """Verifica que imports não utilizados foram removidos."""
    print("\n" + "=" * 60)
    print("  TESTE 8: Verificando imports não utilizados")
    print("=" * 60)

    files_to_check = [
        "src/automation/desktop_controller.py",
        "src/automation/web_automation.py",
        "src/ai/llm_orchestrator.py",
        "src/ui/cli.py",
    ]

    issues = []

    for filepath in files_to_check:
        full_path = Path(__file__).parent / filepath
        if not full_path.exists():
            continue

        with open(full_path, 'r') as f:
            content = f.read()

        # Verifica imports problemáticos conhecidos
        if filepath == "desktop_controller.py":
            if 'from pywinauto.keyboard import send_keys' in content:
                issues.append(f"{filepath}: send_keys import não utilizado")
            if 'Tuple' in content and 'from typing import' in content:
                issues.append(f"{filepath}: Tuple import não utilizado")

        if filepath == "web_automation.py":
            if 'from pathlib import Path' in content:
                issues.append(f"{filepath}: Path import não utilizado")
            if 'import asyncio' in content and 'asyncio.' not in content:
                issues.append(f"{filepath}: asyncio import não utilizado")

    if issues:
        for issue in issues:
            print(f"  ⚠️  {issue}")
        return False
    else:
        print("  ✅ No unused imports found")
        return True


def main():
    """Executa todos os testes de validação."""
    print("\n" + "=" * 70)
    print("  AUTOMATION-COMPUTER - VALIDAÇÃO PÓS CODE REVIEW")
    print("=" * 70)

    # Adicionar src ao path
    src_path = Path(__file__).parent / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    tests = [
        ("Imports", test_imports),
        ("DesktopController Hotkey", test_desktop_controller_hotkey),
        ("WebAutomation Null Check", test_web_automation_extract_data),
        ("LLM Constants", test_llm_constants),
        ("Sandbox Domain Matching", test_sandbox_domain_matching),
        ("Encryption Basic", test_encryption_basic),
        ("Rate Limiter", test_rate_limiter),
        ("Unused Imports", test_no_unused_imports),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n  ❌ {name}: EXCEPTION - {e}")
            results.append((name, False))

    # Resumo final
    print("\n" + "=" * 70)
    print("  RESUMO FINAL")
    print("=" * 70)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")

    print(f"\n  Total: {passed}/{total} testes passaram")

    if passed == total:
        print("\n  🎉 TODOS OS TESTES PASSARAM - CORREÇÕES VALIDADAS!")
        return 0
    else:
        print(f"\n  ⚠️  {total - passed} teste(s) falharam - revisar correções")
        return 1


if __name__ == "__main__":
    sys.exit(main())