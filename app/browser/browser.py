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

        search_box = page.get_by_placeholder("Search")
        search_box.fill(query)

        search_button = page.locator(
            "button.ytSearchboxComponentSearchButton"
        )

        search_button.click()

        page.wait_for_load_state("domcontentloaded")

        return (
            f"YouTube search completed: {query} | "
            f"Page: {page.title()}"
        )

    def web_search(self, query: str) -> str:
        from urllib.parse import quote_plus

        page = self.browser.page

        search_url = (
            "https://www.bing.com/search?q="
            + quote_plus(query)
        )

        print(f"🌐 Searching: {query}")

        try:
            page.goto(
                search_url,
                wait_until="domcontentloaded",
                timeout=15000,
            )
        except Exception as exc:
            return f"Web search failed: {exc}"

        page.wait_for_timeout(2000)

        print(f"🌐 Page: {page.url}")

        results = page.locator("li.b_algo")

        collected = []

        for i in range(min(results.count(), 5)):
            result = results.nth(i)
            text = result.inner_text().strip()

            if text:
                collected.append(text)

        if not collected:
            return (
                f"No search results found for: {query}\n"
                f"Page title: {page.title()}\n"
                f"Page URL: {page.url}"
            )

        return (
            f"Web search results for: {query}\n\n"
            + "\n\n".join(collected)
        )