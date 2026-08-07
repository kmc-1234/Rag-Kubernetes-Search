import os
import json
from urllib import request
from urllib.error import HTTPError, URLError

from langchain_core.documents import Document

from app.config import (
    LLM_PROVIDER,
    LLM_TIMEOUT_SECONDS,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OPENAI_CHAT_MODEL,
)
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

    if LLM_PROVIDER == "ollama":
        return generate_ollama_answer(question=question, context=context)

    if LLM_PROVIDER == "openai" and os.getenv("OPENAI_API_KEY"):
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
        "No LLM provider is configured, so this response is extractive only.\n\n"
        f"Most relevant indexed context:\n\n{context}"
    )


def generate_ollama_answer(question: str, context: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_prompt(question=question, context=context)},
        ],
    }
    body = json.dumps(payload).encode("utf-8")
    endpoint = OLLAMA_BASE_URL.rstrip("/") + "/api/chat"
    req = request.Request(
        endpoint,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=LLM_TIMEOUT_SECONDS) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        return (
            f"Ollama request failed: {exc}\n\n"
            "Falling back to retrieved context only.\n\n"
            f"Most relevant indexed context:\n\n{context}"
        )

    message = data.get("message", {})
    content = message.get("content")
    if not content:
        return (
            "Ollama returned an empty response.\n\n"
            "Falling back to retrieved context only.\n\n"
            f"Most relevant indexed context:\n\n{context}"
        )

    return str(content)
