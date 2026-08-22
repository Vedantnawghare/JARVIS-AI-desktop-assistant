from typing import Callable


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Callable] = {}

    def register(self, tool_name: str, function: Callable) -> None:
        self._tools[tool_name] = function

    def get(self, tool_name: str) -> Callable | None:
        return self._tools.get(tool_name)

    def execute(self, tool_name: str, **kwargs):
        tool = self.get(tool_name)

        if tool is None:
            raise ValueError(
                f"Unknown tool: {tool_name}"
            )

        return tool(**kwargs)