from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.rag import AskRequest, AskResponse, answer_question
from app.search import ingest_documents, search_documents


app = FastAPI(
    title="RAG Kubernetes Documentation Search",
    description="Search local Kubernetes, Helm, Docker, and runbook documentation with RAG.",
    version="0.1.0",
)


@app.get("/", include_in_schema=False)
def root() -> HTMLResponse:
    page = HTMLResponse(
        """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>RAG Kubernetes Search</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f6f8fb;
      --panel: #ffffff;
      --ink: #172033;
      --muted: #607089;
      --line: #d9e1ec;
      --blue: #2563eb;
      --green: #16875d;
      --amber: #b7791f;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--ink);
    }
    header {
      background: #12213a;
      color: white;
      padding: 22px 28px;
      border-bottom: 1px solid #203654;
    }
    header h1 {
      margin: 0 0 6px;
      font-size: 26px;
      letter-spacing: 0;
    }
    header p {
      margin: 0;
      color: #c5d4e8;
      font-size: 14px;
    }
    main {
      display: grid;
      grid-template-columns: minmax(320px, 420px) minmax(0, 1fr);
      gap: 18px;
      padding: 18px;
      max-width: 1280px;
      margin: 0 auto;
    }
    section {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      min-width: 0;
    }
    h2 {
      margin: 0 0 14px;
      font-size: 18px;
      letter-spacing: 0;
    }
    label {
      display: block;
      font-weight: 650;
      margin: 12px 0 6px;
      font-size: 13px;
    }
    textarea, input {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px 12px;
      font: inherit;
      background: white;
      color: var(--ink);
    }
    textarea { min-height: 130px; resize: vertical; }
    .row { display: flex; gap: 10px; align-items: center; }
    .row > * { flex: 1; }
    button, a.button {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      border: 0;
      border-radius: 6px;
      padding: 10px 14px;
      font: inherit;
      font-weight: 700;
      cursor: pointer;
      text-decoration: none;
      color: white;
      background: var(--blue);
      min-height: 40px;
    }
    button.secondary, a.secondary { background: #526174; }
    button.green { background: var(--green); }
    .actions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 14px; }
    .status {
      margin-top: 12px;
      padding: 10px 12px;
      border-radius: 6px;
      border: 1px solid var(--line);
      color: var(--muted);
      background: #f8fafc;
      font-size: 13px;
      min-height: 40px;
    }
    .answer {
      white-space: pre-wrap;
      line-height: 1.48;
      min-height: 220px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 14px;
      background: #fbfdff;
    }
    .sources {
      display: grid;
      gap: 10px;
      margin-top: 12px;
    }
    .source {
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 12px;
      background: white;
    }
    .source strong { display: block; margin-bottom: 6px; }
    .source p { margin: 0; color: var(--muted); font-size: 13px; line-height: 1.4; }
    .pill {
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      padding: 4px 8px;
      background: #e9f2ff;
      color: #174ea6;
      font-size: 12px;
      font-weight: 700;
      margin-left: 8px;
    }
    @media (max-width: 820px) {
      main { grid-template-columns: 1fr; padding: 12px; }
      header { padding: 18px; }
      header h1 { font-size: 22px; }
    }
  </style>
</head>
<body>
  <header>
    <h1>RAG Kubernetes Documentation Search <span class="pill">Live</span></h1>
    <p>Ask questions across Kubernetes, Helm, Docker, and runbook docs.</p>
  </header>
  <main>
    <section>
      <h2>Query</h2>
      <label for="question">Question</label>
      <textarea id="question">How do I troubleshoot a PVC stuck in Pending?</textarea>
      <div class="row">
        <div>
          <label for="topK">Sources</label>
          <input id="topK" type="number" min="1" max="10" value="5">
        </div>
      </div>
      <div class="actions">
        <button onclick="askQuestion()">Ask</button>
        <button class="green" onclick="ingestDocs()">Ingest Docs</button>
        <a class="button secondary" href="/docs">API Docs</a>
      </div>
      <div id="status" class="status">Ready.</div>
    </section>
    <section>
      <h2>Answer</h2>
      <div id="answer" class="answer">Run ingestion once, then ask a question.</div>
      <div id="sources" class="sources"></div>
    </section>
  </main>
  <script>
    const statusEl = document.getElementById("status");
    const answerEl = document.getElementById("answer");
    const sourcesEl = document.getElementById("sources");

    async function ingestDocs() {
      try {
        statusEl.textContent = "Ingesting documents...";
        const response = await fetch("/ingest", { method: "POST" });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || JSON.stringify(data));
        statusEl.textContent = `Indexed ${data.documents} documents into ${data.chunks} chunks.`;
      } catch (error) {
        statusEl.textContent = `Ingestion failed: ${error.message}`;
      }
    }

    async function askQuestion() {
      try {
        const question = document.getElementById("question").value.trim();
        const topK = Number(document.getElementById("topK").value || 5);
        if (!question) {
          statusEl.textContent = "Enter a question first.";
          return;
        }
        statusEl.textContent = "Searching documentation...";
        answerEl.textContent = "";
        sourcesEl.innerHTML = "";
        const response = await fetch("/ask", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question, top_k: topK })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || JSON.stringify(data));
        answerEl.textContent = data.answer;
        for (const source of data.sources) {
          const item = document.createElement("div");
          const title = document.createElement("strong");
          const preview = document.createElement("p");
          item.className = "source";
          title.textContent = `${source.source} · chunk ${source.chunk}`;
          preview.textContent = source.preview;
          item.append(title, preview);
          sourcesEl.appendChild(item);
        }
        statusEl.textContent = data.sources.length
          ? `Returned ${data.sources.length} source matches.`
          : "No sources found. Run Ingest Docs, then ask again.";
      } catch (error) {
        answerEl.textContent = "";
        statusEl.textContent = `Ask failed: ${error.message}`;
      }
    }

    window.addEventListener("error", (event) => {
      statusEl.textContent = event.message;
    });
  </script>
</body>
</html>
        """,
    )
    page.headers["Cache-Control"] = "no-store, max-age=0"
    return page


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
