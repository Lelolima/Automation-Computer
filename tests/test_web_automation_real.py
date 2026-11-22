"""Teste de integração REAL do WebAutomation com Chromium headless.

Usa uma página HTML local (file://), sem acesso à rede. É pulado se o
navegador do Playwright não estiver instalado (`playwright install chromium`).
"""

import pytest

from src.automation.web_automation import WebAutomation

HTML = """<!doctype html><html><body>
<h1 id="titulo">Olá</h1>
<input id="nome"><button id="btn" onclick="document.getElementById('out').textContent='Oi, '+document.getElementById('nome').value">ok</button>
<p id="out"></p>
<a class="lnk" href="/a">A</a><a class="lnk" href="/b">B</a>
</body></html>"""


@pytest.mark.asyncio
async def test_fluxo_real_no_chromium(tmp_path):
    pagina = tmp_path / "index.html"
    pagina.write_text(HTML, encoding="utf-8")
    try:
        web = WebAutomation(headless=True)
        await web.start()
    except Exception as exc:  # navegador ausente
        pytest.skip(f"Chromium do Playwright indisponível: {exc}")
    try:
        await web.navigate(pagina.as_uri())
        assert await web.get_text("#titulo") == "Olá"
        await web.fill("#nome", "Ana")
        await web.click("#btn")
        assert await web.get_text("#out") == "Oi, Ana"
        links = await web.extract_all(".lnk", attribute="href")
        assert [link["value"] for link in links] == ["/a", "/b"]
        assert await web.extract_data("#nao-existe") == ""
        assert await web.evaluate("1 + 2") == 3
        await web.screenshot(str(tmp_path / "s.png"))
        assert (tmp_path / "s.png").stat().st_size > 0
    finally:
        await web.close()
