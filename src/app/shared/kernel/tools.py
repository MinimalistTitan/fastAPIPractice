from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel

ToolInvoker = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]


@dataclass(frozen=True, slots=True)
class LocalTool:
    name: str
    description: str
    input_model: type[BaseModel]
    output_model: type[BaseModel]
    invoke: ToolInvoker


class LocalToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, LocalTool] = {}

    def register(self, tool: LocalTool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def list_names(self) -> list[str]:
        return sorted(self._tools.keys())

    async def invoke(self, tool_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        tool = self._tools.get(tool_name)
        if tool is None:
            raise KeyError(f"unknown tool: {tool_name}")

        validated_input = tool.input_model.model_validate(payload)
        raw_output = await tool.invoke(validated_input.model_dump(mode="json"))
        validated_output = tool.output_model.model_validate(raw_output)
        return validated_output.model_dump(mode="json")