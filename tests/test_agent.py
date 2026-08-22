from app.brain.agent import decide
from app.browser.browser import search_youtube
from app.tools.browser import open_url
from app.tools.registry import ToolRegistry


def main():
    registry = ToolRegistry()

    registry.register("open_url", open_url)
    registry.register("search_youtube", search_youtube)

    user_input = "Search YouTube for the OSI model"

    decision = decide(user_input)

    print(f"Decision: {decision}")

    if decision["action"] == "tool":
        result = registry.execute(
            decision["tool"],
            **decision["arguments"],
        )

        print(f"Result: {result}")

    else:
        print(f"JARVIS: {decision['response']}")


if __name__ == "__main__":
    main()