import os
import shutil
import subprocess
import time

import psutil
import pyautogui
import pygetwindow as gw

from app.tools.window import remember_window


CHROME_PROFILE = "Profile 1"


APPLICATIONS = {
    "chrome": [
        os.path.expandvars(
            r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"
        ),
        os.path.expandvars(
            r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
        ),
        os.path.expandvars(
            r"%LocalAppData%\Google\Chrome\Application\chrome.exe"
        ),
    ],
    "google chrome": [
        os.path.expandvars(
            r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"
        ),
        os.path.expandvars(
            r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
        ),
        os.path.expandvars(
            r"%LocalAppData%\Google\Chrome\Application\chrome.exe"
        ),
    ],
    "brave": [
        os.path.expandvars(
            r"%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe"
        ),
        os.path.expandvars(
            r"%ProgramFiles(x86)%\BraveSoftware\Brave-Browser\Application\brave.exe"
        ),
        os.path.expandvars(
            r"%LocalAppData%\BraveSoftware\Brave-Browser\Application\brave.exe"
        ),
    ],
    "brave browser": [
        os.path.expandvars(
            r"%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe"
        ),
        os.path.expandvars(
            r"%ProgramFiles(x86)%\BraveSoftware\Brave-Browser\Application\brave.exe"
        ),
        os.path.expandvars(
            r"%LocalAppData%\BraveSoftware\Brave-Browser\Application\brave.exe"
        ),
    ],
    "edge": [
        os.path.expandvars(
            r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
        ),
        os.path.expandvars(
            r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"
        ),
    ],
    "microsoft edge": [
        os.path.expandvars(
            r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
        ),
        os.path.expandvars(
            r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"
        ),
    ],
    "notepad": [
        "notepad.exe",
    ],
    "calculator": [
        "calc.exe",
    ],
    "vs code": [
        os.path.expandvars(
            r"%LocalAppData%\Programs\Microsoft VS Code\Code.exe"
        ),
        os.path.expandvars(
            r"%ProgramFiles%\Microsoft VS Code\Code.exe"
        ),
    ],
    "visual studio code": [
        os.path.expandvars(
            r"%LocalAppData%\Programs\Microsoft VS Code\Code.exe"
        ),
        os.path.expandvars(
            r"%ProgramFiles%\Microsoft VS Code\Code.exe"
        ),
    ],
}


def _find_executable(name: str):
    key = name.strip().lower()

    candidates = APPLICATIONS.get(key)

    if not candidates:
        return None

    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate

    for candidate in candidates:
        found = shutil.which(candidate)

        if found:
            return found

    return None


def _window_ids():
    ids = set()

    for window in gw.getAllWindows():
        try:
            if window.title:
                ids.add(window._hWnd)
        except Exception:
            continue

    return ids


def _find_new_chrome_window(before_ids):
    for window in gw.getAllWindows():
        try:
            if not window.title:
                continue

            if window._hWnd in before_ids:
                continue

            if "google chrome" in window.title.lower():
                return window

        except Exception:
            continue

    return None


def open_application(name: str) -> str:
    name = name.strip()
    key = name.lower()

    if key in {
        "chrome",
        "google chrome",
    }:
        chrome = _find_executable("chrome")

        if chrome is None:
            return (
                "Could not find installed "
                "application: Chrome"
            )

        try:
            before_ids = _window_ids()

            subprocess.Popen(
                [
                    chrome,
                    f"--profile-directory={CHROME_PROFILE}",
                ],
                shell=False,
            )

            target = None

            for _ in range(40):
                time.sleep(0.25)

                target = _find_new_chrome_window(
                    before_ids
                )

                if target is not None:
                    break

            if target is None:
                return (
                    "Chrome opened, but its "
                    "window could not be tracked"
                )

            remember_window(
                "Chrome",
                target,
            )

            try:
                target.activate()
            except Exception:
                pass

            return (
                "Opened and focused Chrome "
                "with Vedant profile"
            )

        except Exception as exc:
            return (
                f"Could not open Chrome: {exc}"
            )

    executable = _find_executable(name)

    if executable is None:
        return (
            f"Application not configured: "
            f"{name}"
        )

    try:
        subprocess.Popen(
            [executable],
            shell=False,
        )

        return (
            f"Opened application: {name}"
        )

    except Exception as exc:
        return (
            f"Could not open "
            f"{name}: {exc}"
        )


def close_application(name: str) -> str:
    name = name.strip()
    key = name.lower()

    aliases = {
        "chrome": "chrome.exe",
        "google chrome": "chrome.exe",
        "brave": "brave.exe",
        "brave browser": "brave.exe",
        "edge": "msedge.exe",
        "microsoft edge": "msedge.exe",
        "vs code": "Code.exe",
        "visual studio code": "Code.exe",
        "notepad": "notepad.exe",
        "calculator": "CalculatorApp.exe",
    }

    process_name = aliases.get(
        key,
        key,
    )

    if not process_name.endswith(".exe"):
        process_name += ".exe"

    closed = False

    for process in psutil.process_iter(
        ["pid", "name"]
    ):
        try:
            current_name = (
                process.info["name"] or ""
            )

            if (
                current_name.lower()
                == process_name.lower()
            ):
                process.terminate()
                closed = True

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
        ):
            continue

    if closed:
        return (
            f"Closed application: {name}"
        )

    return (
        f"Application not running: {name}"
    )


def open_path(path: str) -> str:
    path = os.path.expandvars(
        os.path.expanduser(
            path.strip()
        )
    )

    try:
        if not os.path.exists(path):
            return (
                f"Path does not exist: "
                f"{path}"
            )

        os.startfile(path)

        return (
            f"Opened path: {path}"
        )

    except Exception as exc:
        return (
            f"Could not open path "
            f"{path}: {exc}"
        )


def volume_up() -> str:
    pyautogui.press(
        "volumeup",
        presses=2,
        interval=0.1,
    )

    return "Volume increased"


def volume_down() -> str:
    pyautogui.press(
        "volumedown",
        presses=2,
        interval=0.1,
    )

    return "Volume decreased"


def mute() -> str:
    pyautogui.press("volumemute")

    return "Volume muted"


def unmute() -> str:
    pyautogui.press("volumemute")

    return "Volume unmuted"


def lock_pc() -> str:
    try:
        subprocess.run(
            [
                "rundll32.exe",
                "user32.dll,LockWorkStation",
            ],
            check=True,
        )

        return "PC locked"

    except Exception as exc:
        return f"Could not lock PC: {exc}"