from app.brain.agent import decide
from app.tools.registry import ToolRegistry
from app.tools.browser import open_url


def main():
    registry = ToolRegistry()

    registry.register("open_url", open_url)

    user_input = "Open YouTube"

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