from app.browser.browser import BrowserTools
from app.browser.manager import BrowserManager


class JarvisRuntime:
    def __init__(self):
        self.browser = BrowserManager()
        self.browser_tools = BrowserTools(self.browser)

    def start(self) -> None:
        self.browser.start()

    def shutdown(self) -> None:
        self.browser.close()