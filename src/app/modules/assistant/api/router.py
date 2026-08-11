from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.container import get_container
from app.modules.assistant.application.commands import AssistantQueryCommand
from app.modules.assistant.contracts.messages import (
    AssistantQueryRequestV1,
    AssistantQueryResponseV1,
)
from app.modules.assistant.wiring import AssistantModule

router = APIRouter(prefix="/assistant", tags=["assistant"])
def get_assistant_module(request: Request) -> AssistantModule:
    module = get_container(request).assistant

    if module is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Assistant is not configured",
        )

    return module




@router.post("/query", response_model=AssistantQueryResponseV1)
async def query_assistant(
    payload: AssistantQueryRequestV1,
    module: Annotated[
        AssistantModule,
        Depends(get_assistant_module),
    ],
) -> AssistantQueryResponseV1:
     return await module.query.execute(
        AssistantQueryCommand(
            query=payload.query,
            conversation_id=payload.conversation_id,
            max_tool_calls=payload.max_tool_calls,
            allow_tool_calls=payload.allow_tool_calls,
        )
    )