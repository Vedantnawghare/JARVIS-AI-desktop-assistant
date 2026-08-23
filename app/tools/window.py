import time

import pygetwindow as gw


_TARGET_WINDOWS = {}


ALIASES = {
    "chrome": "chrome",
    "google chrome": "chrome",
    "brave": "brave",
    "brave browser": "brave",
    "vs code": "vs code",
    "visual studio code": "vs code",
    "code": "vs code",
    "edge": "edge",
    "microsoft edge": "edge",
}


def remember_window(name: str, window) -> str:
    key = ALIASES.get(
        name.strip().lower(),
        name.strip().lower(),
    )

    _TARGET_WINDOWS[key] = window

    return (
        f"Remembered window: {window.title}"
    )


def _valid_window(window):
    try:
        return (
            window is not None
            and window.title
            and window.title.strip()
        )
    except Exception:
        return False


def _windows():
    return [
        window
        for window in gw.getAllWindows()
        if _valid_window(window)
    ]


def _find_window(name: str):
    key = name.strip().lower()

    app = ALIASES.get(
        key,
        key,
    )

    remembered = _TARGET_WINDOWS.get(app)

    if _valid_window(remembered):
        return remembered

    windows = _windows()

    if app == "chrome":
        matches = [
            window
            for window in windows
            if "google chrome"
            in window.title.lower()
        ]

        if matches:
            return matches[0]

        return None

    if app == "brave":
        matches = [
            window
            for window in windows
            if "brave"
            in window.title.lower()
        ]

        return (
            matches[0]
            if matches
            else None
        )

    if app == "vs code":
        matches = [
            window
            for window in windows
            if (
                "visual studio code"
                in window.title.lower()
                or "vs code"
                in window.title.lower()
            )
        ]

        return (
            matches[0]
            if matches
            else None
        )

    if app == "edge":
        matches = [
            window
            for window in windows
            if "microsoft edge"
            in window.title.lower()
        ]

        return (
            matches[0]
            if matches
            else None
        )

    matches = [
        window
        for window in windows
        if key in window.title.lower()
    ]

    return (
        matches[0]
        if matches
        else None
    )


def focus_window(name: str) -> str:
    window = _find_window(name)

    if window is None:
        return (
            f"Window not found: {name}"
        )

    try:
        if window.isMinimized:
            window.restore()

        window.activate()

        time.sleep(0.4)

        return (
            f"Focused window: "
            f"{window.title}"
        )

    except Exception as exc:
        return (
            f"Could not focus "
            f"{name}: {exc}"
        )


def minimize_window(name: str) -> str:
    window = _find_window(name)

    if window is None:
        return (
            f"Window not found: {name}"
        )

    try:
        title = window.title

        window.minimize()

        time.sleep(0.3)

        return (
            f"Minimized window: {title}"
        )

    except Exception as exc:
        return (
            f"Could not minimize "
            f"{name}: {exc}"
        )


def maximize_window(name: str) -> str:
    window = _find_window(name)

    if window is None:
        return (
            f"Window not found: {name}"
        )

    try:
        title = window.title

        window.maximize()

        time.sleep(0.3)

        return (
            f"Maximized window: {title}"
        )

    except Exception as exc:
        return (
            f"Could not maximize "
            f"{name}: {exc}"
        )


def close_window(name: str) -> str:
    window = _find_window(name)

    if window is None:
        return (
            f"Window not found: {name}"
        )

    try:
        title = window.title

        window.close()

        time.sleep(0.5)

        key = ALIASES.get(
            name.strip().lower(),
            name.strip().lower(),
        )

        _TARGET_WINDOWS.pop(
            key,
            None,
        )

        return (
            f"Closed window: {title}"
        )

    except Exception as exc:
        return (
            f"Could not close "
            f"{name}: {exc}"
        )