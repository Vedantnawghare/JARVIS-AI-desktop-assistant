import os
import subprocess
import time
from pathlib import Path

import pygetwindow as gw


COMMON_APPS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "explorer": "explorer.exe",
    "chrome": "chrome.exe",
    "edge": "msedge.exe",
}


def _focus_window(name: str) -> bool:
    name = name.lower().strip()

    for window in gw.getAllWindows():
        title = (window.title or "").lower()

        if name in title:
            try:
                if window.isMinimized:
                    window.restore()

                window.activate()
                time.sleep(0.5)
                return True
            except Exception:
                pass

    return False


def open_application(name: str) -> str:
    name = name.lower().strip()

    executable = COMMON_APPS.get(
        name,
        name,
    )

    try:
        subprocess.Popen(
            executable,
            shell=True,
        )

        for _ in range(20):
            time.sleep(0.25)

            if _focus_window(name):
                return f"Opened and focused {name}"

        return f"Opened {name}, but could not focus the window."

    except Exception as exc:
        return f"Could not open {name}: {exc}"


def open_path(path: str) -> str:
    path = os.path.expandvars(
        os.path.expanduser(path)
    )

    target = Path(path)

    if not target.exists():
        return f"Path does not exist: {path}"

    try:
        os.startfile(str(target))
        return f"Opened {path}"

    except Exception as exc:
        return f"Could not open {path}: {exc}"