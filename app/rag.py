from pydantic import BaseModel, Field

from app.config import TOP_K
from app.llm import generate_answer
from app.search import search_documents


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=TOP_K, ge=1, le=20)


class Source(BaseModel):
    source: str
    chunk: int | str
    preview: str


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]


def answer_question(request: AskRequest) -> AskResponse:
    documents = search_documents(request.question, request.top_k)
    answer = generate_answer(request.question, documents)

    sources = [
        Source(
            source=str(document.metadata.get("source", "unknown")),
            chunk=document.metadata.get("chunk", "?"),
            preview=document.page_content[:300],
        )
        for document in documents
    ]

    return AskResponse(answer=answer, sources=sources)
