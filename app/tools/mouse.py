import time

import pyautogui


def move_mouse(x: int, y: int) -> str:
    x = int(x)
    y = int(y)

    pyautogui.moveTo(
        x,
        y,
        duration=0.25,
    )

    time.sleep(0.3)

    return f"Moved mouse to ({x}, {y})"


def click(x: int, y: int) -> str:
    x = int(x)
    y = int(y)

    pyautogui.moveTo(
        x,
        y,
        duration=0.25,
    )

    time.sleep(0.2)

    pyautogui.click()

    return f"Clicked at ({x}, {y})"


def double_click(x: int, y: int) -> str:
    x = int(x)
    y = int(y)

    pyautogui.moveTo(
        x,
        y,
        duration=0.25,
    )

    time.sleep(0.2)

    pyautogui.doubleClick()

    return f"Double-clicked at ({x}, {y})"


def scroll(amount: int) -> str:
    amount = int(amount)

    pyautogui.scroll(amount)

    time.sleep(0.3)

    return f"Scrolled {amount}"