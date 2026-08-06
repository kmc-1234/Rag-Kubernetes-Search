#!/usr/bin/env python3
"""Generate simple release notes from the current GitHub Actions context."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path


def env(name: str, default: str = "unknown") -> str:
    return os.getenv(name, default)


def main() -> None:
    output_dir = Path("artifacts")
    output_dir.mkdir(exist_ok=True)

    branch = env("GITHUB_REF_NAME")
    sha = env("GITHUB_SHA")
    short_sha = sha[:7] if sha != "unknown" else sha
    repository = env("GITHUB_REPOSITORY")
    actor = env("GITHUB_ACTOR")
    workflow = env("GITHUB_WORKFLOW")
    run_id = env("GITHUB_RUN_ID")
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    notes = f"""# Release Notes

Generated: {generated_at}

## Build

- Repository: `{repository}`
- Branch: `{branch}`
- Commit: `{short_sha}`
- Triggered by: `{actor}`
- Workflow: `{workflow}`
- Run ID: `{run_id}`

## Summary

This build validated the FastAPI RAG service, checked Python syntax, and built the Docker image.

## Deployment Review

- Confirm `/health` returns `{{"status":"ok"}}` after deployment.
- Run `POST /ingest` after changing files in `docs/`.
- Test `POST /ask` with a Kubernetes or runbook question.
- Confirm returned answers include relevant `sources`.

## Rollback

Redeploy the previous known-good container image or commit if health checks fail.
"""

    (output_dir / "release-notes.md").write_text(notes, encoding="utf-8")


if __name__ == "__main__":
    main()
