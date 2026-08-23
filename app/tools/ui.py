import difflib
import re
import time

import pyautogui
import pygetwindow as gw
from pywinauto import Desktop


def _normalize(text: str) -> str:
    text = (text or "").lower().strip()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text


def _get_active_window_title():
    try:
        window = gw.getActiveWindow()

        if window is not None:
            return (
                window.title or ""
            ).strip()

    except Exception:
        pass

    return ""


def _get_chrome_window():
    try:
        from app.tools.window import (
            _TARGET_WINDOWS,
            _window_from_handle,
        )

        remembered = _TARGET_WINDOWS.get(
            "chrome"
        )

        if remembered:
            handle = remembered.get(
                "handle"
            )

            if handle:
                window = _window_from_handle(
                    handle
                )

                if window is not None:
                    return window

    except Exception:
        pass

    active = gw.getActiveWindow()

    if active is not None:
        try:
            if "google chrome" in (
                active.title or ""
            ).lower():
                return active
        except Exception:
            pass

    for window in gw.getAllWindows():
        try:
            title = (
                window.title or ""
            ).lower()

            if "google chrome" in title:
                return window

        except Exception:
            continue

    return None


def _focus_chrome():
    window = _get_chrome_window()

    if window is None:
        return None

    try:
        if window.isMinimized:
            window.restore()

        window.activate()

        time.sleep(0.4)

        return window

    except Exception:
        return None


def _get_chrome_uia_window():
    chrome = _get_chrome_window()

    if chrome is None:
        return None

    chrome_handle = None

    try:
        chrome_handle = chrome._hWnd
    except Exception:
        pass

    desktop = Desktop(
        backend="uia"
    )

    candidates = []

    for window in desktop.windows():

        try:
            if not window.is_visible():
                continue

            title = (
                window.window_text()
                or ""
            ).strip()

            if (
                "google chrome"
                not in title.lower()
            ):
                continue

            handle = None

            try:
                handle = window.handle
            except Exception:
                pass

            if (
                chrome_handle is not None
                and handle == chrome_handle
            ):
                return window

            candidates.append(
                window
            )

        except Exception:
            continue

    if len(candidates) == 1:
        return candidates[0]

    chrome_title = (
        chrome.title or ""
    ).lower()

    for window in candidates:

        try:
            title = (
                window.window_text()
                or ""
            ).lower()

            if title == chrome_title:
                return window

        except Exception:
            continue

    return None


def _control_to_dict(control):

    try:
        text = (
            control.window_text()
            or ""
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


def _collect_chrome_controls():

    chrome_window = (
        _get_chrome_uia_window()
    )

    if chrome_window is None:
        return []

    controls = []
    seen = set()

    try:
        descendants = (
            chrome_window.descendants()
        )
    except Exception:
        return []

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

    _focus_chrome()

    time.sleep(0.2)

    controls = _collect_chrome_controls()

    for element in controls:

        if (
            element["control_type"]
            == "Edit"
            and element["class_name"]
            == "OmniboxViewViews"
        ):

            return {
                "name": "address bar",
                "control_type": "Edit",
                "class_name": (
                    "OmniboxViewViews"
                ),
                "automation_id": (
                    element["automation_id"]
                ),
                "x": element["x"],
                "y": element["y"],
            }

    return None


def _is_address_bar(element):

    if element["class_name"] == (
        "OmniboxViewViews"
    ):
        return True

    searchable = " ".join(
        [
            _normalize(
                element["name"]
            ),
            _normalize(
                element["class_name"]
            ),
            _normalize(
                element["automation_id"]
            ),
        ]
    )

    return (
        "omnibox" in searchable
        or "address and search bar"
        in searchable
    )


def _search_candidates(
    controls
):

    candidates = []

    for control in controls:

        if (
            control["control_type"]
            != "Edit"
        ):
            continue

        if _is_address_bar(
            control
        ):
            continue

        searchable = " ".join(
            [
                _normalize(
                    control["name"]
                ),
                _normalize(
                    control["class_name"]
                ),
                _normalize(
                    control["automation_id"]
                ),
            ]
        )

        score = 0

        # Strong indicators
        if "search" in searchable:
            score += 100

        if "searchbox" in searchable:
            score += 80

        if "search-box" in searchable:
            score += 80

        if "search input" in searchable:
            score += 80

        if "searchboxinput" in searchable:
            score += 80

        # YouTube-specific indicators
        if (
            "youtube" in searchable
        ):
            score += 30

        if (
            "yt" in searchable
        ):
            score += 10

        # Common HTML/UI names
        if (
            control["name"]
            and _normalize(
                control["name"]
            )
            in {
                "search",
                "search box",
                "searchbox",
                "search field",
            }
        ):
            score += 100

        # Strongly reject unrelated editors
        if (
            "omnibox"
            in searchable
        ):
            score -= 1000

        if (
            "address"
            in searchable
        ):
            score -= 1000

        if (
            "prompt textarea"
            in searchable
        ):
            score -= 1000

        if (
            "promirror"
            in searchable
        ):
            score -= 500

        if (
            "prosemirror"
            in searchable
        ):
            score -= 500

        if score > 0:
            candidates.append(
                (
                    score,
                    control,
                )
            )

    candidates.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return candidates


def find_search_box():

    _focus_chrome()

    time.sleep(0.5)

    for attempt in range(5):

        controls = (
            _collect_chrome_controls()
        )

        candidates = (
            _search_candidates(
                controls
            )
        )

        if candidates:

            best_score, best = (
                candidates[0]
            )

            print(
                "Search box candidate:",
                best["name"],
                "|",
                best["class_name"],
                "|",
                best["automation_id"],
                "| score:",
                best_score,
            )

            # Only accept a candidate if
            # we actually have evidence that
            # it is a search control.
            if best_score >= 50:

                return {
                    "name": (
                        best["name"]
                        or "search box"
                    ),
                    "control_type": (
                        best["control_type"]
                    ),
                    "class_name": (
                        best["class_name"]
                    ),
                    "automation_id": (
                        best["automation_id"]
                    ),
                    "x": best["x"],
                    "y": best["y"],
                }

        time.sleep(0.7)

    return None


def _strip_role_words(text):

    words = text.split()

    removable = {
        "button",
        "field",
        "box",
        "textbox",
        "text",
        "input",
        "control",
        "element",
        "ui",
    }

    return " ".join(
        word
        for word in words
        if word not in removable
    ).strip()


def _requested_control_type(text):

    normalized = _normalize(text)

    if any(
        phrase in normalized
        for phrase in (
            "button",
            "btn",
        )
    ):
        return "Button"

    if any(
        phrase in normalized
        for phrase in (
            "textbox",
            "text box",
            "input",
            "field",
            "search box",
            "search field",
            "address bar",
            "chat box",
        )
    ):
        return "Edit"

    if "tab" in normalized:
        return "TabItem"

    return None


def _semantic_candidates(
    query,
    controls,
):

    normalized = _normalize(
        query
    )

    if normalized in {
        "search box",
        "search field",
        "searchbox",
    }:

        result = find_search_box()

        if result is None:
            return []

        return [result]

    if normalized in {
        "address bar",
        "addressbar",
        "omnibox",
    }:

        result = find_address_bar()

        if result is None:
            return []

        return [result]

    requested_type = (
        _requested_control_type(
            normalized
        )
    )

    stripped = _strip_role_words(
        normalized
    )

    candidates = []

    for control in controls:

        if (
            requested_type
            and control["control_type"]
            != requested_type
        ):
            continue

        if (
            control["control_type"]
            == "Edit"
            and _is_address_bar(
                control
            )
            and normalized
            not in {
                "address bar",
                "addressbar",
                "omnibox",
            }
        ):
            continue

        control_name = _normalize(
            control["name"]
        )

        if not stripped:
            continue

        if (
            control_name
            == stripped
        ):
            score = 1.0

        elif (
            stripped
            in control_name
        ):
            score = 0.88

        elif (
            control_name
            in stripped
        ):
            score = 0.82

        else:
            score = (
                difflib.SequenceMatcher(
                    None,
                    stripped,
                    control_name,
                ).ratio()
            )

        if score >= 0.55:
            candidates.append(
                (
                    score,
                    control,
                )
            )

    candidates.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return [
        item[1]
        for item in candidates
    ]


def _resolve_element(name):

    normalized = _normalize(
        name
    )

    if normalized in {
        "address bar",
        "addressbar",
        "omnibox",
    }:

        return find_address_bar()

    if normalized in {
        "search box",
        "search field",
        "searchbox",
    }:

        return find_search_box()

    # Browser elements
    browser_elements = {
        "address bar",
        "addressbar",
        "omnibox",
        "search box",
        "search field",
        "searchbox",
    }

    if normalized in browser_elements:

        _focus_chrome()

        controls = (
            _collect_chrome_controls()
        )

        candidates = (
            _semantic_candidates(
                name,
                controls,
            )
        )

        return (
            candidates[0]
            if candidates
            else None
        )

    controls = (
        _collect_chrome_controls()
    )

    semantic_names = {
        "chat box",
        "chat field",
        "text box",
        "textbox",
    }

    if normalized in semantic_names:

        candidates = (
            _semantic_candidates(
                name,
                controls,
            )
        )

        return (
            candidates[0]
            if candidates
            else None
        )

    exact_target = (
        _strip_role_words(
            normalized
        )
    )

    exact_matches = []

    for control in controls:

        control_name = _normalize(
            control["name"]
        )

        if (
            control_name
            == exact_target
        ):
            exact_matches.append(
                control
            )

    if exact_matches:
        return exact_matches[0]

    candidates = (
        _semantic_candidates(
            name,
            controls,
        )
    )

    if candidates:
        return candidates[0]

    return None


def find_ui_element(
    name: str
):

    element = _resolve_element(
        name
    )

    if element is None:
        return None

    return {
        "name": element["name"],
        "control_type": (
            element["control_type"]
        ),
        "class_name": (
            element["class_name"]
        ),
        "automation_id": (
            element["automation_id"]
        ),
        "x": element["x"],
        "y": element["y"],
    }


def click_ui_element(
    name: str
) -> str:

    element = _resolve_element(
        name
    )

    if element is None:
        return (
            f"UI element not found: "
            f"{name}"
        )

    _focus_chrome()

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

    # YouTube / browser search box
    # Use YouTube's "/" shortcut instead
    # of trying to detect the webpage input
    # through Windows UI Automation.
    if normalized in {
        "search box",
        "search field",
        "searchbox",
    }:

        _focus_chrome()

        time.sleep(0.5)

        pyautogui.press("/")

        time.sleep(0.3)

        pyautogui.write(
            text,
            interval=0.03,
        )

        return (
            f"Typed '{text}' into "
            f"search box"
        )

    # Address bar still uses UIA
    if normalized in {
        "address bar",
        "addressbar",
        "omnibox",
    }:

        element = find_address_bar()

        if element is None:
            return (
                "Address bar not found"
            )

        _focus_chrome()

        time.sleep(0.2)

        pyautogui.click(
            element["x"],
            element["y"],
        )

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
            "address bar"
        )

    # Everything else uses normal UI
    element = _resolve_element(
        name
    )

    if element is None:
        return (
            f"UI element not found: "
            f"{name}"
        )

    _focus_chrome()

    time.sleep(0.2)

    pyautogui.click(
        element["x"],
        element["y"],
    )

    time.sleep(0.1)

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

def read_ui_element(
    name: str
) -> str:

    element = _resolve_element(
        name
    )

    if element is None:
        return (
            f"UI element not found: "
            f"{name}"
        )

    return (
        f"{element['name']} | "
        f"type: {element['control_type']} | "
        f"class: {element['class_name']} | "
        f"automation_id: "
        f"{element['automation_id']}"
    )