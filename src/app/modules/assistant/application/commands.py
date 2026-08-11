from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class AssistantQueryCommand:
    query: str
    conversation_id: UUID | None = None
    max_tool_calls: int = 4
    allow_tool_calls: bool = True