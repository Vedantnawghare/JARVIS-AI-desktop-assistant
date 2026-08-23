from ollama import chat


MODEL = "qwen3:4b"


def clean_response(text: str) -> str:
    text = text.strip()

    if "</think>" in text:
        text = text.split("</think>", 1)[1].strip()

    if text.startswith("```"):
        lines = text.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    return text


def ask(prompt: str) -> str:
    response = chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        think=False,
        format="json",
        stream=False,
        options={
            "temperature": 0.1,
        },
    )

    return clean_response(
        response.message.content
    )


def stream(prompt: str):
    response = chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        think=False,
        stream=True,
        options={
            "temperature": 0.2,
        },
    )

    for chunk in response:
        content = chunk.message.content

        if content:
            yield content