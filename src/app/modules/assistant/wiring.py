from collections.abc import Iterable
from dataclasses import dataclass

from app.core.config import Settings
from app.modules.assistant.application.ports import (
    AgentOrchestratorPort,
    AssistantTelemetryPort,
    ConversationStorePort,
    ToolRuntimePort,
)
from app.modules.assistant.application.use_cases import (
    OrchestrateAssistantQuery,
)
from app.modules.assistant.domain.tool_call import ToolCallPolicy
from app.modules.assistant.infrastructure.agents.langchain_agent_orchestrator import (
    LangChainAgentOrchestrator,
)
from app.modules.assistant.infrastructure.conversation_memory.inmemory_conversation_store import (
    InMemoryConversationStore,
)
from app.modules.assistant.infrastructure.llm.langchain_llm_client import (
    LangChainChatModelFactory,
)
from app.modules.assistant.infrastructure.telemetry.orchestration_observability import (
    StructlogAssistantTelemetry,
)
from app.modules.assistant.infrastructure.tool_runtime.guarded_registry import (
    GuardedLocalRegistryRuntime,
)
from app.shared.kernel.tools import LocalTool, LocalToolRegistry


@dataclass(frozen=True, slots=True)
class AssistantModule:
    query: OrchestrateAssistantQuery


def build_assistant_module(
    settings: Settings,
    tools: Iterable[LocalTool],
    *,
    tool_runtime: ToolRuntimePort | None = None,
    agent_orchestrator: AgentOrchestratorPort | None = None,
    conversation_store: ConversationStorePort | None = None,
    telemetry: AssistantTelemetryPort | None = None,
    tool_policy: ToolCallPolicy | None = None,
) -> AssistantModule | None:
    registered_tools = tuple(tools)

    effective_orchestrator = agent_orchestrator
    if effective_orchestrator is None:
        if settings.langchain_chat_openai_api_key is None:
            return None

        effective_orchestrator = LangChainAgentOrchestrator(
            llm=LangChainChatModelFactory(settings).build()
        )

    effective_policy = tool_policy
    if effective_policy is None:
        effective_policy = ToolCallPolicy(
            allowed_tool_names=frozenset(
                tool.name for tool in registered_tools
            ),
            max_total_calls=1,
            max_calls_per_tool=1,
            fail_on_policy_violation=True,
        )

    effective_tool_runtime = tool_runtime
    if effective_tool_runtime is None:
        registry = LocalToolRegistry()

        for tool in registered_tools:
            registry.register(tool)

        effective_tool_runtime = GuardedLocalRegistryRuntime(
            registry=registry,
            allowed_tool_names=effective_policy.allowed_tool_names,
        )

    effective_conversation_store = (
        conversation_store
        if conversation_store is not None
        else InMemoryConversationStore(
            max_turns_per_conversation=12
        )
    )

    effective_telemetry = (
        telemetry
        if telemetry is not None
        else StructlogAssistantTelemetry()
    )

    return AssistantModule(
        query=OrchestrateAssistantQuery(
            tool_runtime=effective_tool_runtime,
            agent_orchestrator=effective_orchestrator,
            conversation_store=effective_conversation_store,
            telemetry=effective_telemetry,
            tool_policy=effective_policy,
        )
    )