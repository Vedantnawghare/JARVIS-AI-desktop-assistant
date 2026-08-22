import pyautogui


def type_text(text: str) -> str:
    pyautogui.write(
        text,
        interval=0.01,
    )

    return f"Typed: {text}"


def press_key(key: str) -> str:
    pyautogui.press(key)

    return f"Pressed: {key}"


def hotkey(keys: str) -> str:
    parts = [
        key.strip()
        for key in keys.split("+")
        if key.strip()
    ]

    pyautogui.hotkey(*parts)

    return f"Pressed: {keys}"