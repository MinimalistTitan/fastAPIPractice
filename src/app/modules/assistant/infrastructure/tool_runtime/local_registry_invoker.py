from dataclasses import dataclass

from app.modules.assistant.application.ports import ToolRuntimePort
from app.modules.assistant.domain.entities import ToolDescriptor
from app.shared.kernel.tools import LocalToolRegistry


@dataclass(slots=True)
class LocalRegistryInvoker(ToolRuntimePort):
    registry: LocalToolRegistry

    async def list_tools(self) -> list[ToolDescriptor]:
        names = self.registry.list_names()
        # TODO: extend LocalToolRegistry to expose description and JSON schema metadata
        return [ToolDescriptor(name=name, description="local tool") for name in names]

    async def invoke(self, tool_name: str, payload: dict[str, object]) -> dict[str, object]:
        return await self.registry.invoke(tool_name, payload)