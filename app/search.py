from pathlib import Path

import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.config import CHROMA_DIR, COLLECTION_NAME, DOCS_DIR
from app.embeddings import get_embeddings
from app.loader import load_documents, split_documents


def get_vector_store() -> Chroma:
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return Chroma(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding_function=get_embeddings(),
    )


def ingest_documents(docs_dir: Path = DOCS_DIR) -> dict[str, int]:
    documents = load_documents(docs_dir)
    chunks = split_documents(documents)

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    vector_store = get_vector_store()
    if chunks:
        ids = [
            f"{chunk.metadata['source']}::chunk-{chunk.metadata['chunk']}"
            for chunk in chunks
        ]
        vector_store.add_documents(chunks, ids=ids)

    return {"documents": len(documents), "chunks": len(chunks)}


def search_documents(question: str, top_k: int) -> list[Document]:
    vector_store = get_vector_store()
    return vector_store.similarity_search(question, k=top_k)
