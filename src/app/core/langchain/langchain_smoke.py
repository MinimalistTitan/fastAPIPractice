from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app.core.config import Settings


@dataclass(frozen=True, slots=True)
class LangChainSmokeResult:
    chat_model: str
    embedding_dimensions: int
    model_response: str | None = None


type LangChainSmokeCheck = Callable[[], Awaitable[LangChainSmokeResult]]


def build_langchain_smoke_check(
    settings: Settings,
) -> LangChainSmokeCheck | None:
    if not settings.langchain_smoke_enabled:
        return None

    chat_api_key = settings.langchain_chat_openai_api_key
    if chat_api_key is None:
        raise RuntimeError(
            "langchain_chat_openai_api_key is required for the LangChain smoke check"
        )

    embedding_api_key = settings.langchain_embedding_openai_api_key
    if embedding_api_key is None:
        raise RuntimeError(
            "langchain_embedding_openai_api_key is required for the LangChain smoke check"
        )

    llm = ChatOpenAI(
        api_key=chat_api_key,
        model=settings.langchain_chat_model,
        base_url=settings.openai_base_url,
        temperature=0.0,
        timeout=settings.langchain_timeout_seconds,
    )

    embeddings = OpenAIEmbeddings(
        api_key=embedding_api_key,
        model=settings.langchain_embedding_model,
        base_url=settings.openai_base_url,
        timeout=settings.langchain_timeout_seconds,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Return exactly one short word: pong."),
            ("human", "ping"),
        ]
    )

    async def check() -> LangChainSmokeResult:
        vector = await embeddings.aembed_query("smoke_check")
        if not vector:
            raise RuntimeError("Embedding provider returned an empty vector")

        chain = prompt | llm
        response = await chain.ainvoke({})
        content = str(response.content).strip().lower()

        if not content:
            raise RuntimeError("Chat model returned an empty response")

        return LangChainSmokeResult(
            chat_model=settings.langchain_chat_model,
            embedding_dimensions=len(vector),
            model_response=content,
        )

    return check