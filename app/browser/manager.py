from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    sync_playwright,
)


class BrowserManager:
    def __init__(self):
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    def start(self) -> None:
        if self._playwright is not None:
            return

        self._playwright = sync_playwright().start()

        self._browser = self._playwright.chromium.launch(
            channel="chrome",
            headless=False,
        )

        self._context = self._browser.new_context()

        self._page = self._context.new_page()

        self._page.goto(
            "https://www.google.com",
            wait_until="domcontentloaded",
        )

        print("Chrome browser started.")

    @property
    def page(self) -> Page:
        if self._page is None:
            raise RuntimeError(
                "Browser is not started."
            )

        return self._page

    def close(self) -> None:
        if self._browser is not None:
            self._browser.close()

        if self._playwright is not None:
            self._playwright.stop()

        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None