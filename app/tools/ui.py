import difflib
import re
import time

import pyautogui
import pygetwindow as gw
from pywinauto import Desktop

from app.tools.window import focus_specific_window


def _normalize(text: str) -> str:
    text = (text or "").lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text)


def _get_active_window_title():
    try:
        window = gw.getActiveWindow()

        if window:
            return (window.title or "").strip()

    except Exception:
        pass

    return ""


def _is_youtube_active():
    return "youtube" in _normalize(
        _get_active_window_title()
    )


def _focus_youtube():
    result = focus_specific_window(
        "YouTube"
    )

    if result.startswith("Focused window:"):
        time.sleep(0.5)
        return True

    return False


def _get_windows():
    desktop = Desktop(backend="uia")

    windows = [
        w
        for w in desktop.windows()
        if w.is_visible()
    ]

    active = _normalize(
        _get_active_window_title()
    )

    if active:
        windows.sort(
            key=lambda w: (
                0
                if active in _normalize(
                    w.window_text()
                )
                else 1
            )
        )

    return windows


def _control_to_dict(control):
    try:
        text = (
            control.window_text() or ""
        ).strip()

        rect = control.rectangle()

        return {
            "name": text,
            "control_type": (
                control.element_info.control_type
            ),
            "class_name": (
                control.element_info.class_name
            ),
            "automation_id": (
                control.element_info.automation_id
            ),
            "x": (
                rect.left + rect.right
            ) // 2,
            "y": (
                rect.top + rect.bottom
            ) // 2,
        }

    except Exception:
        return None


def _collect_controls():
    controls = []
    seen = set()

    for window in _get_windows():

        try:
            descendants = window.descendants()

        except Exception:
            continue

        for control in descendants:

            item = _control_to_dict(
                control
            )

            if item is None:
                continue

            identity = (
                item["name"],
                item["control_type"],
                item["class_name"],
                item["automation_id"],
                item["x"],
                item["y"],
            )

            if identity in seen:
                continue

            seen.add(identity)
            controls.append(item)

    return controls


def find_address_bar():
    for element in _collect_controls():

        if (
            element["control_type"] == "Edit"
            and element["class_name"]
            == "OmniboxViewViews"
        ):
            return {
                "name": "address bar",
                "control_type": "Edit",
                "class_name": "OmniboxViewViews",
                "automation_id": (
                    element["automation_id"]
                ),
                "x": element["x"],
                "y": element["y"],
            }

    return None


def _is_address_bar(element):
    return (
        element["control_type"] == "Edit"
        and element["class_name"]
        == "OmniboxViewViews"
    )


def _is_chat_editor(element):
    return (
        _normalize(
            element["class_name"]
        ) == "prosemirror"
        or element["automation_id"]
        == "prompt-textarea"
    )


def _is_code_editor(element):
    searchable = " ".join(
        (
            _normalize(element["name"]),
            _normalize(element["class_name"]),
            _normalize(
                element["automation_id"]
            ),
        )
    )

    blocked = (
        "native edit context",
        "monaco",
        "code editor",
        "codeeditor",
        "terminal",
        "powershell",
    )

    return any(
        value in searchable
        for value in blocked
    )


def _get_active_browser():
    title = _normalize(
        _get_active_window_title()
    )

    browsers = (
        "google chrome",
        "chrome",
        "brave",
        "microsoft edge",
        "edge",
    )

    if any(
        browser in title
        for browser in browsers
    ):
        return title

    return ""


def _is_search_candidate(element):
    if element["control_type"] != "Edit":
        return False

    if _is_address_bar(element):
        return False

    if _is_chat_editor(element):
        return False

    if _is_code_editor(element):
        return False

    searchable = " ".join(
        (
            _normalize(element["name"]),
            _normalize(element["class_name"]),
            _normalize(
                element["automation_id"]
            ),
        )
    )

    return any(
        word in searchable
        for word in (
            "search",
            "searchbox",
            "searchfield",
            "searchinput",
        )
    )


def _find_search_box():
    controls = _collect_controls()

    active_browser = _get_active_browser()

    candidates = []

    for element in controls:

        if not _is_search_candidate(
            element
        ):
            continue

        score = 0

        searchable = " ".join(
            (
                _normalize(element["name"]),
                _normalize(
                    element["class_name"]
                ),
                _normalize(
                    element["automation_id"]
                ),
            )
        )

        if "search" in searchable:
            score += 50

        if (
            "youtube" in active_browser
            and "search" in searchable
        ):
            score += 100

        if (
            "google" in active_browser
            and "search" in searchable
        ):
            score += 90

        candidates.append(
            (score, element)
        )

    candidates.sort(
        key=lambda x: x[0],
        reverse=True,
    )

    if candidates:
        return candidates[0][1]

    return None


def _semantic_candidates(
    query,
    controls,
):
    normalized = _normalize(query)

    if normalized in {
        "address bar",
        "addressbar",
        "omnibox",
    }:
        element = find_address_bar()

        return (
            [element]
            if element
            else []
        )

    if normalized in {
        "search box",
        "search field",
        "searchbox",
    }:
        element = _find_search_box()

        return (
            [element]
            if element
            else []
        )

    if normalized in {
        "chat box",
        "chat field",
    }:
        return [
            e
            for e in controls
            if _is_chat_editor(e)
        ]

    requested_type = None

    if "button" in normalized:
        requested_type = "Button"

    elif any(
        x in normalized
        for x in (
            "box",
            "field",
            "input",
            "textbox",
        )
    ):
        requested_type = "Edit"

    target = re.sub(
        r"\b(button|field|box|textbox|input|element)\b",
        "",
        normalized,
    ).strip()

    candidates = []

    for element in controls:

        if (
            requested_type
            and element["control_type"]
            != requested_type
        ):
            continue

        name = _normalize(
            element["name"]
        )

        if not target:
            continue

        score = difflib.SequenceMatcher(
            None,
            target,
            name,
        ).ratio()

        if target in name:
            score += 0.25

        if score >= 0.55:
            candidates.append(
                (score, element)
            )

    candidates.sort(
        key=lambda x: x[0],
        reverse=True,
    )

    return [
        element
        for _, element in candidates
    ]


def _resolve_element(name):
    normalized = _normalize(name)

    if normalized in {
        "search box",
        "search field",
        "searchbox",
    }:
        return _find_search_box()

    if normalized in {
        "address bar",
        "addressbar",
        "omnibox",
    }:
        return find_address_bar()

    controls = _collect_controls()

    candidates = _semantic_candidates(
        name,
        controls,
    )

    if candidates:
        return candidates[0]

    target = _normalize(name)

    for element in controls:

        if (
            _normalize(element["name"])
            == target
        ):
            return element

    return None


def find_ui_element(name: str):
    normalized = _normalize(name)

    if normalized in {
        "search box",
        "search field",
        "searchbox",
    } and _is_youtube_active():

        return {
            "name": "YouTube search box",
            "control_type": "KeyboardShortcut",
            "class_name": "",
            "automation_id": "",
            "x": 0,
            "y": 0,
        }

    element = _resolve_element(name)

    if element is None:
        return None

    return {
        "name": element["name"],
        "control_type": element[
            "control_type"
        ],
        "class_name": element[
            "class_name"
        ],
        "automation_id": element[
            "automation_id"
        ],
        "x": element["x"],
        "y": element["y"],
    }


def click_ui_element(name: str) -> str:
    normalized = _normalize(name)

    if normalized in {
        "search box",
        "search field",
        "searchbox",
    }:

        if not _is_youtube_active():

            if not _focus_youtube():
                return (
                    "YouTube window not found"
                )

        pyautogui.press("/")

        time.sleep(0.5)

        return (
            "Focused YouTube search box"
        )

    element = _resolve_element(name)

    if element is None:
        return (
            f"UI element not found: {name}"
        )

    pyautogui.moveTo(
        element["x"],
        element["y"],
        duration=0.2,
    )

    pyautogui.click()

    return (
        f"Clicked '{element['name']}' "
        f"at ({element['x']}, "
        f"{element['y']})"
    )


def type_into_ui_element(
    name: str,
    text: str,
) -> str:

    normalized = _normalize(name)

    if normalized in {
        "search box",
        "search field",
        "searchbox",
    }:

        if not _is_youtube_active():

            if not _focus_youtube():
                return (
                    "YouTube window not found"
                )

            time.sleep(0.5)

        pyautogui.press("/")

        time.sleep(0.5)

        pyautogui.write(
            text,
            interval=0.03,
        )

        return (
            f"Typed '{text}' into "
            "YouTube search box"
        )

    element = _resolve_element(name)

    if element is None:
        return (
            f"UI element not found: "
            f"{name}"
        )

    pyautogui.moveTo(
        element["x"],
        element["y"],
        duration=0.2,
    )

    pyautogui.click()

    time.sleep(0.2)

    pyautogui.hotkey(
        "ctrl",
        "a",
    )

    pyautogui.write(
        text,
        interval=0.03,
    )

    return (
        f"Typed '{text}' into "
        f"'{element['name']}'"
    )


def read_ui_element(name: str) -> str:
    element = _resolve_element(name)

    if element is None:
        return (
            f"UI element not found: {name}"
        )

    return (
        f"{element['name']} | "
        f"type: {element['control_type']} | "
        f"class: {element['class_name']} | "
        f"automation_id: "
        f"{element['automation_id']}"
    )