from typing import Callable


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Callable] = {}

    def register(self, name: str, function: Callable) -> None:
        self._tools[name] = function

    def get(self, name: str) -> Callable | None:
        return self._tools.get(name)

    def execute(self, name: str, **kwargs):
        tool = self.get(name)

        if tool is None:
            raise ValueError(f"Unknown tool: {name}")

        return tool(**kwargs)