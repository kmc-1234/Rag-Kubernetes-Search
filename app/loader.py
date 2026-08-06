from pathlib import Path
from typing import Iterable

from langchain_core.documents import Document

from app.config import CHUNK_OVERLAP, CHUNK_SIZE


SUPPORTED_EXTENSIONS = {".md", ".txt", ".rst"}


def load_documents(docs_dir: Path) -> list[Document]:
    documents: list[Document] = []
    for path in sorted(docs_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        text = path.read_text(encoding="utf-8", errors="ignore").strip()
        if not text:
            continue

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": str(path.relative_to(docs_dir)),
                    "path": str(path),
                },
            )
        )
    return documents


def split_documents(documents: Iterable[Document]) -> list[Document]:
    chunks: list[Document] = []
    for document in documents:
        text = document.page_content
        start = 0
        index = 0

        while start < len(text):
            end = min(start + CHUNK_SIZE, len(text))
            chunk_text = text[start:end].strip()
            if chunk_text:
                metadata = dict(document.metadata)
                metadata["chunk"] = index
                chunks.append(Document(page_content=chunk_text, metadata=metadata))

            if end == len(text):
                break

            start = max(end - CHUNK_OVERLAP, start + 1)
            index += 1

    return chunks
