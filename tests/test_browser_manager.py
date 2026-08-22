import time

from app.browser.browser import BrowserTools
from app.browser.manager import BrowserManager


def main():
    browser = BrowserManager()
    browser.start()

    tools = BrowserTools(browser)

    print(tools.open_url("https://www.google.com"))

    time.sleep(2)

    print(tools.search_youtube("OSI model"))

    time.sleep(5)

    browser.close()


if __name__ == "__main__":
    main()