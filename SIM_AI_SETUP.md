# Sim.ai Setup for RAG CI Review

This guide connects the GitHub Actions pipeline in this repo to Sim.ai.

The goal is:

```text
Git push
  -> GitHub Actions
  -> Validate app
  -> Sim AI Review
  -> Send review report to Sim.ai webhook
  -> Build and push Docker image
```

## 1. Open the Workflow

In Sim.ai:

1. Open your workspace.
2. In the left sidebar, find `Workflows`.
3. Open `RAG CI Review`.
4. Make sure you are in the workflow builder screen.

From your screenshot, you are already in the right place.

## 2. Add the Webhook Trigger

In the right panel:

1. Click `Toolbar`.
2. Under `Triggers`, click `Webhook Trigger`.
3. Place the webhook trigger on the canvas.

You should see a block named something like:

```text
Webhook Trigger 2
```

This webhook is what GitHub Actions calls after the local `scripts/sim_ai_review.py` script generates the review report.

## 3. Configure Webhook Authentication

Select the `Webhook Trigger` block.

In the right-side editor:

1. Keep `Require Authentication` enabled.
2. Copy the `Webhook URL`.
3. Copy the `Authentication Token`.

Do not paste these values into the repository files. They must be stored as GitHub Actions secrets.

The GitHub Actions workflow sends the token like this:

```http
Authorization: Bearer <SIM_AI_AUTH_TOKEN>
```

## 4. Optional Input Format

If Sim.ai lets you define the input format, add these fields:

| Field | Type | Description |
| --- | --- | --- |
| `repository` | String | GitHub repository name |
| `branch` | String | Branch that triggered the workflow |
| `sha` | String | Commit SHA |
| `report` | String | Markdown Sim AI review report |
| `agent_prompt` | String | Full ready-to-use prompt for the Sim.ai agent |

GitHub Actions sends this payload:

```json
{
  "repository": "kmc-1234/Rag-Kubernetes-Search",
  "branch": "main",
  "sha": "commit-sha",
  "report": "Sim AI review markdown report",
  "agent_prompt": "Full prompt for Agent 1"
}
```

## 5. Add a Useful Review Step in Sim.ai

The webhook alone receives data. To make the Sim.ai UI useful, add one or more blocks after the webhook.

Recommended simple setup:

1. Add an AI / LLM block after the webhook.
2. Connect `Webhook Trigger` to the AI block.
3. In the agent message, insert the webhook output field named `agent_prompt` using Sim.ai's variable picker.

The message should contain the actual variable chip for:

```text
Webhook Trigger -> Output -> agent_prompt
```

Do not type placeholder text like `[Webhook Trigger 1 output report]`. If the value appears as plain text in the Sim.ai log, it was not mapped correctly.

Alternative manual prompt:

```text
Review this GitHub Actions CI report.

Repository: {{repository}}
Branch: {{branch}}
Commit: {{sha}}

Report:
{{report}}

Return:
1. Overall status
2. Deployment risk
3. Docker image readiness
4. Missing setup items
5. Recommended next action
```

If Sim.ai uses a different variable syntax, select the fields from the webhook output picker instead of typing the placeholders manually.

## 6. Deploy the Sim.ai Workflow

Click:

```text
Deploy
```

Important: Sim.ai webhooks only receive external requests after the workflow is deployed.

If the button says `Update`, click `Update` after making changes.

## 7. Add GitHub Secrets

Open your GitHub repository:

```text
https://github.com/kmc-1234/Rag-Kubernetes-Search
```

Go to:

```text
Settings -> Secrets and variables -> Actions -> New repository secret
```

Add:

```text
SIM_AI_WEBHOOK_URL=<your Sim.ai webhook URL>
SIM_AI_AUTH_TOKEN=<your Sim.ai authentication token>
```

You also need Docker Hub secrets for the image push:

```text
DOCKERHUB_USERNAME=kmc173
DOCKERHUB_TOKEN=<Docker Hub read/write access token>
```

## 8. Trigger a Test Run

Push a new commit:

```bash
git commit --allow-empty -m "Test Sim.ai webhook"
git push
```

Or rerun the latest workflow from GitHub Actions:

```text
GitHub repo -> Actions -> RAG CI/CD -> latest run -> Re-run jobs
```

## 9. Check GitHub Actions

In GitHub:

1. Open `Actions`.
2. Open the latest `RAG CI/CD` workflow run.
3. Open the `Sim AI Review` job.
4. Confirm these steps pass:

```text
Run simulated AI review
Add Sim AI review to workflow summary
Send review to Sim.ai
```

If `Send review to Sim.ai` fails, check:

- `SIM_AI_WEBHOOK_URL` is set.
- `SIM_AI_AUTH_TOKEN` is set.
- The Sim.ai workflow is deployed.
- `Require Authentication` is enabled in Sim.ai.
- The copied token has no extra spaces.

## 10. Check Sim.ai Logs

In Sim.ai:

1. Click `Logs` in the left sidebar.
2. Open the latest run for `RAG CI Review`.
3. Confirm the webhook received:

```text
repository
branch
sha
report
```

The `report` field contains the markdown output from:

```text
scripts/sim_ai_review.py
```

## 11. Troubleshooting

### Sim.ai shows no logs

Most common causes:

- Workflow was not deployed or updated.
- GitHub secret `SIM_AI_WEBHOOK_URL` is missing.
- GitHub Actions did not reach the `Sim AI Review` job.

### Sim.ai returns unauthorized

Most common causes:

- `SIM_AI_AUTH_TOKEN` is missing in GitHub.
- Wrong token copied from Sim.ai.
- Token was copied with extra spaces.
- Sim.ai expects bearer authentication and the workflow was not updated.

This repo already sends:

```http
Authorization: Bearer $SIM_AI_AUTH_TOKEN
```

### Docker image push still fails

That is separate from Sim.ai.

For Docker Hub, confirm:

```text
DOCKERHUB_USERNAME=kmc173
DOCKERHUB_TOKEN=<read/write Docker Hub token>
```

The token must be allowed to push to:

```text
kmc173/rag-kubernetes-search
```

## 12. Expected Result

After a successful run:

- GitHub Actions shows `Sim AI Review` as passed.
- The Sim.ai `Logs` page shows a new run.
- Docker Hub gets tags like:

```text
kmc173/rag-kubernetes-search:v4
kmc173/rag-kubernetes-search:<commit-sha>
kmc173/rag-kubernetes-search:latest
```
