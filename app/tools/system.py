import os
import subprocess
from pathlib import Path


COMMON_APPS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "explorer": "explorer.exe",
    "chrome": "chrome.exe",
    "edge": "msedge.exe",
}


def open_application(name: str) -> str:
    name = name.lower().strip()

    executable = COMMON_APPS.get(name, name)

    try:
        subprocess.Popen(
            executable,
            shell=True,
        )

        return f"Opened {name}"

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