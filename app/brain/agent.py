import json

from app.brain.llm import ask


SYSTEM_PROMPT = """
You are JARVIS, a desktop AI assistant.

Return ONLY valid JSON.

For a normal answer:

{
    "action": "respond",
    "response": "your response"
}

For one or more actions:

{
    "action": "plan",
    "steps": [
        {
            "tool": "tool_name",
            "arguments": {
                "argument": "value"
            }
        }
    ]
}

Available tools:

- open_url(url)
- search_youtube(query)
- web_search(query)
- open_chrome(profile)
- open_application(name)
- open_path(path)
- focus_window(name)
- type_text(text)
- press_key(key)
- hotkey(keys)
- click(x, y)
- double_click(x, y)
- move_mouse(x, y)
- scroll(amount)
- screenshot(path)
- remember(key, value)
- recall(key)
- forget(key)

Chrome rules:
- When the user says "open Chrome", use open_chrome.
- If a profile is mentioned, pass the profile name exactly.
- Examples of profile names include Sheetal, Vedant, Sanskruti, or Ved College Mail.
- Do not use open_application for Chrome.

Example:

User: Open Chrome in profile Vedant

{
    "action": "plan",
    "steps": [
        {
            "tool": "open_chrome",
            "arguments": {
                "profile": "Vedant"
            }
        }
    ]
}

User: Open Chrome

{
    "action": "plan",
    "steps": [
        {
            "tool": "open_chrome",
            "arguments": {
                "profile": "Default"
            }
        }
    ]
}

Use the smallest number of tools needed.
Use previous conversation context when relevant.
Never invent tools.
Never execute code.
Never return Markdown.
Return JSON only.
"""


def decide(
    user_input: str,
    context: list[dict] | None = None,
) -> dict:
    context = context or []

    context_text = ""

    if context:
        context_text = "\n\nRecent conversation:\n"

        for item in context[-8:]:
            role = item.get(
                "role",
                "user",
            )
            content = item.get(
                "content",
                "",
            )

            context_text += (
                f"{role}: {content}\n"
            )

    prompt = (
        f"{SYSTEM_PROMPT}"
        f"{context_text}"
        f"\n\nCurrent user command:\n"
        f"{user_input}"
    )

    response = ask(prompt)

    try:
        return json.loads(response)

    except json.JSONDecodeError as exc:
        raise ValueError(
            f"JARVIS produced invalid JSON: {response}"
        ) from exc


def recover(
    user_input: str,
    failed_tool: str,
    error: str,
) -> dict:
    prompt = f"""
You are JARVIS recovery planner.

The user's original request was:
{user_input}

The tool that failed was:
{failed_tool}

The failure was:
{error}

Available tools:
- open_url
- search_youtube
- web_search
- open_chrome
- open_application
- open_path
- focus_window
- type_text
- press_key
- hotkey
- click
- double_click
- move_mouse
- scroll
- screenshot
- remember
- recall
- forget

Return ONLY valid JSON:

{{
    "action": "retry",
    "steps": [
        {{
            "tool": "tool_name",
            "arguments": {{
                "argument": "value"
            }}
        }}
    ]
}}

Or:

{{
    "action": "respond",
    "response": "clear explanation"
}}

Do not invent tools.
Do not return Markdown.
"""

    response = ask(prompt)

    try:
        return json.loads(response)

    except json.JSONDecodeError as exc:
        raise ValueError(
            f"JARVIS recovery produced invalid JSON: {response}"
        ) from exc