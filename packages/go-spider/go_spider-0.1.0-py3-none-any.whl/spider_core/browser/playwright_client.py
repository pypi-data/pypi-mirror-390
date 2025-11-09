import asyncio
from typing import Tuple
from playwright.async_api import async_playwright, Browser, Page
from spider_core.browser.browser_client import BrowserClient


class PlaywrightBrowserClient(BrowserClient):
    """
    A Playwright-based implementation of BrowserClient.
    Launches Chromium and renders pages asynchronously.
    """

    def __init__(self, headless: bool = True, viewport: Tuple[int, int] = (1200, 900)):
        self.headless = headless
        self.viewport = viewport
        self.browser: Browser | None = None

    async def _ensure_browser(self):
        """Launches the browser if it's not already running."""
        if self.browser is None:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=self.headless)

    async def render(self, url: str) -> Tuple[str, str, int]:
        """
        Render a page and return:
          - html (str)
          - visible_text (str)
          - status_code (int)
        """
        await self._ensure_browser()
        page: Page = await self.browser.new_page(viewport={"width": self.viewport[0], "height": self.viewport[1]})

        response = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        status_code = response.status if response else 0

        # Optional scroll to trigger lazy-loaders
        try:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2);")
            await asyncio.sleep(0.5)
        except Exception:
            pass

        html = await page.content()

        # Visible text (scripts/styles removed by Playwright's innerText handling)
        visible_text = await page.evaluate("""
            () => {
                const clone = document.body.cloneNode(true);
                clone.querySelectorAll('script, style, noscript').forEach(el => el.remove());
                return clone.innerText;
            }
        """)

        await page.close()
        return html, visible_text, status_code

    async def close(self):
        """Close the browser when done."""
        if self.browser is not None:
            await self.browser.close()
            self.browser = None
