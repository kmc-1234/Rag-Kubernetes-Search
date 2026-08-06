from langchain_core.embeddings import Embeddings

from app.config import EMBEDDING_PROVIDER, OPENAI_EMBEDDING_MODEL


class ChromaDefaultEmbeddings(Embeddings):
    """LangChain adapter for Chroma's local ONNX MiniLM embedding function."""

    def __init__(self) -> None:
        from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

        self._embedding_function = DefaultEmbeddingFunction()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[float(value) for value in vector] for vector in self._embedding_function(texts)]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


def get_embeddings() -> Embeddings:
    if EMBEDDING_PROVIDER == "openai":
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(model=OPENAI_EMBEDDING_MODEL)

    return ChromaDefaultEmbeddings()
