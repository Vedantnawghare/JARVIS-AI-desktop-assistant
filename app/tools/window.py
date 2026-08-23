import time

import pygetwindow as gw


def focus_window(name: str) -> str:
    name = name.lower().strip()

    for window in gw.getAllWindows():
        title = (window.title or "").lower()

        if name in title:
            try:
                if window.isMinimized:
                    window.restore()

                window.activate()
                time.sleep(0.4)

                return f"Focused window: {window.title}"

            except Exception as exc:
                return f"Could not focus {name}: {exc}"

    return f"Window not found: {name}"