"""
Testes para WebAutomation
"""

import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestWebAutomation:
    """Testes para WebAutomation."""

    def test_init(self):
        """Testa inicialização."""
        from src.automation.web_automation import WebAutomation

        browser = WebAutomation(headless=True, browser_type="chromium")

        assert browser.headless is True
        assert browser.browser_type == "chromium"
        assert browser.page is None

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Testa context manager async."""
        with patch('src.automation.web_automation.async_playwright') as mock_playwright:
            from src.automation.web_automation import WebAutomation

            # Mock da resposta do playwright
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.start = AsyncMock()
            mock_playwright.return_value.start.return_value.chromium.launch = AsyncMock(return_value=mock_browser)
            mock_browser.new_context = AsyncMock(return_value=mock_context)
            mock_context.new_page = AsyncMock(return_value=mock_page)

            browser = WebAutomation()

            # Testa entry
            async with browser:
                assert browser.page is not None

            # Testa exit (close foi chamado)
            mock_page.close.assert_called()

    def test_get_text_selector(self):
        """Testa extração de texto."""
        from src.automation.web_automation import WebAutomation

        browser = WebAutomation()
        browser.page = AsyncMock()
        browser.page.text_content = AsyncMock(return_value="Texto de teste")

        async def run_test():
            result = await browser.get_text("#selector")
            assert result == "Texto de teste"

        asyncio.run(run_test())