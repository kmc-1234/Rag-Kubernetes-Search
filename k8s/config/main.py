from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.rag import AskRequest, AskResponse, answer_question
from app.search import ingest_documents, search_documents


app = FastAPI(
    title="RAG Kubernetes Documentation Search",
    description="Search local Kubernetes, Helm, Docker, and runbook documentation with RAG.",
    version="0.1.0",
)


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ingest")
def ingest() -> dict[str, int]:
    return ingest_documents()


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    return answer_question(request)


@app.get("/search")
def search(q: str, top_k: int = 5) -> list[dict[str, object]]:
    documents = search_documents(q, top_k)
    return [
        {
            "source": document.metadata.get("source"),
            "chunk": document.metadata.get("chunk"),
            "content": document.page_content,
        }
        for document in documents
    ]
