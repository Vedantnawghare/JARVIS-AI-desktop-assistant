import webbrowser


def open_url(url: str) -> str:
    webbrowser.open(url)

    return f"Opened {url}"