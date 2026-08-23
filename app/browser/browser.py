from urllib.parse import quote_plus

from app.browser.manager import BrowserManager


class BrowserTools:
    def __init__(self, browser: BrowserManager):
        self.browser = browser

    def open_url(self, url: str) -> str:
        self.browser.page.goto(
            url,
            wait_until="domcontentloaded",
        )

        return f"Opened {url}"

    def search_youtube(self, query: str) -> str:
        page = self.browser.page

        page.goto(
            "https://www.youtube.com",
            wait_until="domcontentloaded",
        )

        search_box = page.get_by_placeholder(
            "Search"
        )

        search_box.fill(query)

        search_button = page.locator(
            "button.ytSearchboxComponentSearchButton"
        )

        search_button.click()

        page.wait_for_load_state(
            "domcontentloaded"
        )

        return (
            f"YouTube search completed: {query} | "
            f"Page: {page.title()}"
        )

    def web_search(self, query: str) -> str:
        page = self.browser.page

        search_url = (
            "https://www.bing.com/search?q="
            + quote_plus(query)
        )

        page.goto(
            search_url,
            wait_until="domcontentloaded",
        )

        return (
            f"Web search completed: {query} | "
            f"Page: {page.url}"
        )

    def current_page(self) -> str:
        return (
            f"URL: {self.browser.page.url} | "
            f"Title: {self.browser.page.title()}"
        )