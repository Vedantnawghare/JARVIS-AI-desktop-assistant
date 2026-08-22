import json

from app.brain.llm import ask


SYSTEM_PROMPT = """
You are JARVIS, a desktop AI assistant.

You have access to tools.

When the user asks for an action that requires a tool, respond ONLY with valid JSON:

{
    "action": "tool",
    "tool": "tool_name",
    "arguments": {
        "argument": "value"
    }
}

When no tool is required, respond ONLY with:

{
    "action": "respond",
    "response": "your response"
}

Available tools:

- open_url(url): Opens a URL in the default browser.

Never invent tools.
Never execute code.
"""


def decide(user_input: str) -> dict:
    prompt = f"{SYSTEM_PROMPT}\n\nUser: {user_input}"

    response = ask(prompt)

    try:
        return json.loads(response)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"JARVIS produced invalid JSON: {response}"
        ) from exc