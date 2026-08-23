import pyautogui


def screenshot(path: str = "tests/audio/screen.png") -> str:
    image = pyautogui.screenshot()
    image.save(path)
    return f"Screenshot saved to {path}"