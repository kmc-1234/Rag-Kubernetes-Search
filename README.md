# RAG-based Kubernetes Documentation Search

This project is a beginner-friendly Retrieval-Augmented Generation (RAG) API for searching Kubernetes, Helm, Docker, Terraform, Prometheus, Grafana, Loki, and internal runbook documentation.

The app loads local Markdown/text files from `docs/`, splits them into chunks, creates embeddings, stores those vectors in ChromaDB, retrieves relevant chunks for a question, and returns an answer with source citations.

## Architecture

```text
User question
    |
FastAPI API
    |
Embed question
    |
ChromaDB vector search
    |
Top matching documentation chunks
    |
LLM answer generation, or extractive context fallback
    |
Answer with sources
```

## Project Structure

```text
rag-kubernetes-search/
├── app/
│   ├── main.py          # FastAPI routes
│   ├── rag.py           # Request/response models and RAG orchestration
│   ├── embeddings.py    # Local or OpenAI embedding model selection
│   ├── loader.py        # Document loading and chunking
│   ├── search.py        # ChromaDB ingestion and similarity search
│   ├── llm.py           # OpenAI answer generation or extractive fallback
│   └── prompts.py       # RAG prompt template
├── docs/
│   ├── kubernetes/
│   ├── helm/
│   ├── docker/
│   ├── terraform/
│   ├── prometheus/
│   ├── grafana/
│   ├── loki/
│   └── runbooks/
├── chroma_db/           # Persistent vector database
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

## Prerequisites

- Python 3.11 or 3.12
- `pip`
- Optional: Docker
- Optional: OpenAI API key for generated answers

By default, the project uses Chroma's local ONNX MiniLM embedding model. The first ingest may take time because the model is downloaded.

Do not use Python 3.14 for this project yet. Some RAG dependencies, especially packages with Rust/Python native extensions such as `pydantic-core` and `tokenizers`, may fail to build on Python 3.14.

## Local Setup

1. Check your Python version:

```bash
python3 --version
```

Use Python 3.11 or 3.12. If your default `python3` is a newer unsupported version, install Python 3.11 or 3.12 and use that command instead:

```bash
python3.11 --version
python3.12 --version
```

2. Create and activate a virtual environment:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

If you accidentally created `.venv` with the wrong Python version, remove it and recreate it with Python 3.11 or 3.12:

```bash
rm -rf .venv
python3.11 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create your local environment file:

```bash
cp .env.example .env
```

5. Optional: add your OpenAI key to `.env` if you want full generated answers:

```bash
OPENAI_API_KEY=sk-your-key
OPENAI_CHAT_MODEL=gpt-5-mini
```

If `OPENAI_API_KEY` is not set, the API still works, but `/ask` returns the most relevant retrieved context instead of calling an LLM.

6. Start the API:

```bash
uvicorn app.main:app --reload
```

7. Open the API docs:

```text
http://127.0.0.1:8000/docs
```

## Add Documentation

Put Markdown, text, or reStructuredText files under `docs/`.

Recommended folders:

```text
docs/kubernetes/
docs/helm/
docs/docker/
docs/terraform/
docs/prometheus/
docs/grafana/
docs/loki/
docs/runbooks/
```

Example files already included:

- `docs/kubernetes/pods.md`
- `docs/kubernetes/hpa.md`
- `docs/helm/charts.md`
- `docs/runbooks/pvc-pending.md`

## Ingest Documents

After adding or changing docs, run ingestion:

```bash
curl -X POST http://127.0.0.1:8000/ingest
```

Expected response:

```json
{
  "documents": 4,
  "chunks": 4
}
```

The vector database is stored in `chroma_db/`.

## Ask Questions

Use `/ask` for RAG answers:

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"How does HPA work?","top_k":5}'
```

Example response shape:

```json
{
  "answer": "Kubernetes HPA changes the number of Pod replicas based on metrics...",
  "sources": [
    {
      "source": "kubernetes/hpa.md",
      "chunk": 0,
      "preview": "The Horizontal Pod Autoscaler changes..."
    }
  ]
}
```

## Search Without Generation

Use `/search` when you only want matching chunks:

```bash
curl "http://127.0.0.1:8000/search?q=PVC%20stuck%20pending&top_k=3"
```

## Docker Setup

1. Build the image:

```bash
docker build -t rag-kubernetes-search .
```

2. Run the container:

```bash
docker run --rm -p 8000:8000 \
  -v "$PWD/docs:/app/docs" \
  -v "$PWD/chroma_db:/app/chroma_db" \
  --env-file .env \
  rag-kubernetes-search
```

3. Ingest documents:

```bash
curl -X POST http://127.0.0.1:8000/ingest
```

4. Ask a question:

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"How do I troubleshoot a PVC stuck in Pending?"}'
```

## GitHub Actions CI/CD

This repository includes a GitHub Actions workflow at `.github/workflows/rag-ci-cd.yml`.

Pipeline:

```text
Git Push
    |
GitHub Actions
    |
Validate Application
    |
Sim AI Review
    |
Review Deployment
    |
Generate Release Notes
    |
Analyze Failure
    |
Notify Team
```

What it does:

- Runs on pushes to `main` or `master`, pull requests, and manual workflow dispatch.
- Uses Python 3.11 in CI.
- Installs `requirements.txt`.
- Runs `python -m compileall app scripts`.
- Imports the FastAPI app to catch startup import errors.
- Runs a deterministic simulated AI review with `scripts/sim_ai_review.py`.
- Builds the Docker image.
- Pushes the Docker image to Docker Hub on `main` or `master` push builds.
- Uploads deployment review notes as a workflow artifact.
- Generates release notes with `scripts/generate_release_notes.py` on push builds.
- Generates failure analysis with `scripts/analyze_failure.py` if the workflow fails.

### Enable Docker Hub Push

Create a Docker Hub repository named:

```text
rag-kubernetes-search
```

Then add these GitHub Actions repository secrets:

```text
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
```

On every push to `main` or `master`, GitHub Actions publishes:

```text
DOCKERHUB_USERNAME/rag-kubernetes-search:<commit-sha>
DOCKERHUB_USERNAME/rag-kubernetes-search:latest
```

Pull requests build the image but do not push it.

### Enable Sim.ai

The workflow runs a deterministic local Sim AI review script in CI. To send that review report to Sim.ai, add this GitHub Actions repository secret:

```text
SIM_AI_WEBHOOK_URL
```

The Sim.ai handoff happens after validation and before Docker image build/push. That is the best place to use it because it can review the app structure, docs, Dockerfile, and release readiness before anything is published.

### Enable Team Notifications

The workflow has an optional Slack notification step.

Add this GitHub Actions repository secret:

```text
SLACK_WEBHOOK_URL
```

If the secret is present, the `Notify Team` job sends a message when a push workflow finishes. If the secret is not present, the workflow still runs and prints the notification summary in the job logs.

## Configuration

Environment variables:

| Variable | Default | Description |
| --- | --- | --- |
| `DOCS_DIR` | `docs` | Folder containing documentation files |
| `CHROMA_DIR` | `chroma_db` | Persistent ChromaDB folder |
| `COLLECTION_NAME` | `kubernetes_docs` | ChromaDB collection name |
| `EMBEDDING_PROVIDER` | `local` | Use `local` or `openai` embeddings |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | OpenAI embedding model |
| `OPENAI_CHAT_MODEL` | `gpt-5-mini` | OpenAI chat model |
| `CHUNK_SIZE` | `1000` | Characters per document chunk |
| `CHUNK_OVERLAP` | `150` | Character overlap between chunks |
| `TOP_K` | `5` | Default number of chunks to retrieve |

## Development Checks

Run a syntax check:

```bash
python3 -m compileall app
```

Run the app locally:

```bash
uvicorn app.main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

## Typical Workflow

1. Add documentation files to `docs/`.
2. Start the API with `uvicorn app.main:app --reload`.
3. Call `POST /ingest`.
4. Ask questions with `POST /ask`.
5. Review the returned `sources` to confirm the answer is grounded in your documentation.

## Notes

- Re-run `/ingest` after changing files in `docs/`.
- For production, add authentication before exposing runbooks or internal documentation.
- For larger documentation sets, consider scheduled ingestion, metadata filtering, and version-specific collections.
