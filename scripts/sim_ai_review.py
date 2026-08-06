#!/usr/bin/env python3
"""Simulated AI review for the RAG project.

This is intentionally deterministic so it can run safely in CI without an API key.
Replace or extend it with a real AI reviewer later if needed.
"""

from __future__ import annotations

from pathlib import Path


REQUIRED_FILES = [
    "app/main.py",
    "app/rag.py",
    "app/search.py",
    "app/embeddings.py",
    "requirements.txt",
    "Dockerfile",
    "README.md",
]


def main() -> None:
    output_dir = Path("artifacts")
    output_dir.mkdir(exist_ok=True)

    findings: list[str] = []
    for file_name in REQUIRED_FILES:
        if not Path(file_name).exists():
            findings.append(f"- Missing required file: `{file_name}`")

    docs = sorted(Path("docs").rglob("*.md")) if Path("docs").exists() else []
    if not docs:
        findings.append("- No Markdown documentation files found under `docs/`.")

    readme = Path("README.md").read_text(encoding="utf-8") if Path("README.md").exists() else ""
    for expected in ["Local Setup", "Ingest Documents", "Docker Setup"]:
        if expected not in readme:
            findings.append(f"- README is missing `{expected}` setup guidance.")

    if findings:
        status = "needs-attention"
        body = "\n".join(findings)
    else:
        status = "passed"
        body = "- Required files are present.\n- Sample docs are present.\n- README includes setup, ingestion, and Docker sections."

    report = f"""# Sim AI Review

Status: `{status}`

## Findings

{body}
"""
    (output_dir / "sim-ai-review.md").write_text(report, encoding="utf-8")

    if findings:
        raise SystemExit("Sim AI review found issues. See artifacts/sim-ai-review.md")


if __name__ == "__main__":
    main()
