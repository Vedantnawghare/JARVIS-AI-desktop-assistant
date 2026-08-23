import pyautogui


KEY_ALIASES = {
    "escape": "esc",
    "return": "enter",
    "control": "ctrl",
    "windows": "win",
    "spacebar": "space",
    "backspace": "backspace",
    "delete": "delete",
    "tab": "tab",
}


def _normalize_key(key: str) -> str:
    key = key.strip().lower()
    return KEY_ALIASES.get(key, key)


def type_text(text: str) -> str:
    text = str(text)

    pyautogui.write(
        text,
        interval=0.03,
    )

    return f"Typed: {text}"


def press_key(key: str) -> str:
    key = _normalize_key(key)

    pyautogui.press(key)

    return f"Pressed: {key}"


def hotkey(keys: str) -> str:
    parts = [
        _normalize_key(key)
        for key in keys.split("+")
        if key.strip()
    ]

    if not parts:
        return "No keys provided"

    pyautogui.hotkey(*parts)

    return f"Pressed: {'+'.join(parts)}"