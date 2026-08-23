import os
import subprocess
import time

import pygetwindow as gw


def close_all_applications() -> str:
    current_window = gw.getActiveWindow()
    current_handle = (
        current_window._hWnd
        if current_window
        else None
    )

    closed = []
    skipped = []

    windows = gw.getAllWindows()

    for window in windows:
        try:
            title = window.title.strip()

            if not title:
                continue

            if not window.visible:
                continue

            if current_handle is not None:
                if window._hWnd == current_handle:
                    skipped.append(title)
                    continue

            if title in {
                "Program Manager",
                "Windows Input Experience",
                "Settings",
            }:
                skipped.append(title)
                continue

            window.close()
            closed.append(title)

            time.sleep(0.15)

        except Exception:
            continue

    if not closed:
        return "No applications needed closing."

    return (
        f"Closed {len(closed)} application window(s)."
    )


def shutdown_pc() -> str:
    try:
        subprocess.Popen(
            [
                "shutdown.exe",
                "/s",
                "/t",
                "5",
            ],
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

        return "Windows shutdown scheduled in 5 seconds."

    except Exception as exc:
        return f"Could not shut down Windows: {exc}"