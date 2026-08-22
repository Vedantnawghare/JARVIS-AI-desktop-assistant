from playwright.sync_api import sync_playwright


def search_youtube(query: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://www.youtube.com", wait_until="domcontentloaded")

        search_box = page.get_by_placeholder("Search")
        search_box.fill(query)

        search_button = page.locator(
            "button.ytSearchboxComponentSearchButton"
        )
        search_button.click()

        page.wait_for_load_state("domcontentloaded")

        title = page.title()
        page.wait_for_timeout(10000)
        return f"YouTube search completed: {query} | Page: {title}"