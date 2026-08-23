import time
from urllib.parse import quote_plus

import pyautogui

from app.tools.system import open_application


def _open_chrome_url(url: str) -> str:
    result = open_application("Chrome")

    if result.startswith("Could not"):
        return result

    time.sleep(1.2)

    pyautogui.hotkey(
        "ctrl",
        "l",
    )

    time.sleep(0.2)

    pyautogui.write(
        url,
        interval=0.02,
    )

    pyautogui.press("enter")

    time.sleep(2)

    return url


def open_url(url: str) -> str:
    url = url.strip()

    if not url:
        return "URL is empty"

    if not (
        url.startswith("http://")
        or url.startswith("https://")
    ):
        url = "https://" + url

    result = _open_chrome_url(url)

    if result.startswith("Could not"):
        return result

    return f"Opened {url}"


def youtube_search(query: str) -> str:
    query = query.strip()

    if not query:
        return "YouTube search query is empty"

    url = (
        "https://www.youtube.com/results"
        "?search_query="
        + quote_plus(query)
    )

    result = _open_chrome_url(url)

    if result.startswith("Could not"):
        return result

    return (
        f"YouTube search opened for: "
        f"{query}"
    )


def open_google() -> str:
    result = _open_chrome_url(
        "https://www.google.com"
    )

    if result.startswith("Could not"):
        return result

    return "Opened Google"


def open_youtube() -> str:
    result = _open_chrome_url(
        "https://www.youtube.com"
    )

    if result.startswith("Could not"):
        return result

    return "Opened YouTube"


def open_github() -> str:
    result = _open_chrome_url(
        "https://github.com"
    )

    if result.startswith("Could not"):
        return result

    return "Opened GitHub"


def open_gmail() -> str:
    result = _open_chrome_url(
        "https://mail.google.com"
    )

    if result.startswith("Could not"):
        return result

    return "Opened Gmail"