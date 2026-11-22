"""Testes da CLI (Typer)."""

from typer.testing import CliRunner

from src.ui import cli

runner = CliRunner()


def test_version():
    result = runner.invoke(cli.app, ["version"])
    assert result.exit_code == 0
    assert "v0.1.0" in result.stdout


def test_status_reflete_import_real(monkeypatch):
    monkeypatch.setitem(cli.MODULOS, "Modulo Fantasma", "src.nao_existe")
    result = runner.invoke(cli.app, ["status"])
    assert result.exit_code == 0
    assert "Indisponível" in result.stdout
    assert "Disponível" in result.stdout  # módulos reais continuam disponíveis


def test_status_modulo():
    assert cli._status_modulo("src.security.encryption").startswith("✅")
    assert cli._status_modulo("src.nao_existe").startswith("❌")
