import os

from langchain_core.documents import Document

from app.config import OPENAI_CHAT_MODEL
from app.prompts import SYSTEM_PROMPT, build_prompt


def format_context(documents: list[Document]) -> str:
    blocks = []
    for idx, document in enumerate(documents, start=1):
        source = document.metadata.get("source", "unknown")
        chunk = document.metadata.get("chunk", "?")
        blocks.append(
            f"[{idx}] Source: {source} (chunk {chunk})\n{document.page_content}"
        )
    return "\n\n".join(blocks)


def generate_answer(question: str, documents: list[Document]) -> str:
    context = format_context(documents)

    if os.getenv("OPENAI_API_KEY"):
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(model=OPENAI_CHAT_MODEL)
        response = llm.invoke(
            [
                ("system", SYSTEM_PROMPT),
                ("human", build_prompt(question=question, context=context)),
            ]
        )
        return str(response.content)

    return (
        "OPENAI_API_KEY is not set, so this response is extractive only.\n\n"
        f"Most relevant indexed context:\n\n{context}"
    )
