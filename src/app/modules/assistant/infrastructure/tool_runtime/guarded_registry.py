from dataclasses import dataclass

from app.modules.assistant.application.ports import ToolRuntimePort
from app.modules.assistant.domain.entities import ToolDescriptor
from app.shared.kernel.tools import LocalToolRegistry


@dataclass(slots=True)
class GuardedLocalRegistryRuntime(ToolRuntimePort):
    registry: LocalToolRegistry
    allowed_tool_names: frozenset[str]

    async def list_tools(self) -> list[ToolDescriptor]:
        names = [n for n in self.registry.list_names() if n in self.allowed_tool_names]
        return [ToolDescriptor(name=n, description="local tool") for n in names]

    async def invoke(self, tool_name: str, payload: dict[str, object]) -> dict[str, object]:
        if tool_name not in self.allowed_tool_names:
            raise PermissionError(f"tool not allowed: {tool_name}")
        return await self.registry.invoke(tool_name, payload)