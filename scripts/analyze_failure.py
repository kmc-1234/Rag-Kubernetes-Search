#!/usr/bin/env python3
"""Write a lightweight failure analysis report for GitHub Actions."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path


def env(name: str, default: str = "unknown") -> str:
    return os.getenv(name, default)


def main() -> None:
    output_dir = Path("artifacts")
    output_dir.mkdir(exist_ok=True)

    sha = env("GITHUB_SHA")
    short_sha = sha[:7] if sha != "unknown" else sha
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    report = f"""# Failure Analysis

Generated: {generated_at}

## Context

- Repository: `{env("GITHUB_REPOSITORY")}`
- Branch: `{env("GITHUB_REF_NAME")}`
- Commit: `{short_sha}`
- Workflow: `{env("GITHUB_WORKFLOW")}`
- Run ID: `{env("GITHUB_RUN_ID")}`
- Actor: `{env("GITHUB_ACTOR")}`

## First Checks

1. Open the failed GitHub Actions job and inspect the first failing step.
2. If dependency installation failed, confirm the workflow is using Python 3.11 or 3.12.
3. If Docker build failed, check `requirements.txt`, `Dockerfile`, and network/package availability.
4. If application import failed, run `python -m compileall app` locally.
5. If deployment validation failed, check `/health`, container logs, and required environment variables.

## Likely Causes

- Unsupported Python version.
- Dependency resolver or package download issue.
- Docker build context missing files.
- Missing secrets such as `OPENAI_API_KEY` or notification webhook.
- Runtime configuration mismatch between local and CI.

## Suggested Recovery

- Re-run the workflow after transient network failures.
- Recreate the virtual environment with Python 3.11 or 3.12.
- Verify the service locally with `uvicorn app.main:app --reload`.
- Roll back to the previous known-good commit if deployment health checks fail.
"""

    (output_dir / "failure-analysis.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
