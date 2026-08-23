import os
from datetime import datetime

import pyautogui


def _get_folder(location: str = "desktop") -> str:
    location = (location or "desktop").strip().lower()

    folders = {
        "desktop": os.path.join(
            os.path.expanduser("~"),
            "Desktop",
        ),
        "downloads": os.path.join(
            os.path.expanduser("~"),
            "Downloads",
        ),
        "documents": os.path.join(
            os.path.expanduser("~"),
            "Documents",
        ),
        "pictures": os.path.join(
            os.path.expanduser("~"),
            "Pictures",
        ),
        "photos": os.path.join(
            os.path.expanduser("~"),
            "Pictures",
        ),
    }

    return folders.get(
        location,
        folders["desktop"],
    )


def screenshot(
    location: str = "desktop",
) -> str:

    folder = _get_folder(location)

    os.makedirs(
        folder,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    path = os.path.join(
        folder,
        f"JARVIS_Screenshot_{timestamp}.png",
    )

    image = pyautogui.screenshot()

    image.save(path)

    return (
        f"Screenshot saved to {path}"
    )