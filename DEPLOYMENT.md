# Deployment Guide

This guide deploys the RAG Kubernetes Search API to Kubernetes and explains how Sim.ai fits into the deployment workflow.

## Deployment Flow

```text
Git push
  -> GitHub Actions
  -> Validate app
  -> Sim.ai review
  -> Build and push Docker image
  -> Deploy image to Kubernetes
  -> Ingest docs
  -> Ask questions through the API
```

## Prerequisites

- Kubernetes cluster access with `kubectl`
- Docker image available in Docker Hub:

```text
kmc173/rag-kubernetes-search:latest
```

- GitHub Actions secrets configured:

```text
DOCKERHUB_USERNAME=kmc173
DOCKERHUB_TOKEN=<Docker Hub read/write token>
SIM_AI_WEBHOOK_URL=<Sim.ai webhook URL>
SIM_AI_AUTH_TOKEN=<Sim.ai webhook auth token>
```

## Deploy to Kubernetes

Apply the manifests:

```bash
kubectl apply -k k8s
```

Check rollout:

```bash
kubectl rollout status deployment/rag-kubernetes-search -n rag-kubernetes-search
```

Check pods:

```bash
kubectl get pods -n rag-kubernetes-search
```

Check service:

```bash
kubectl get svc -n rag-kubernetes-search
```

## Access the API

The service is exposed as a NodePort. Kubernetes assigns an available node port automatically.

Find the assigned port:

```bash
kubectl get svc rag-kubernetes-search -n rag-kubernetes-search
```

```text
http://<node-ip>:<node-port>
```

For local testing, port-forward instead:

```bash
kubectl port-forward svc/rag-kubernetes-search 8000:8000 -n rag-kubernetes-search
```

Then open:

```text
http://127.0.0.1:8000/docs
```

## Ingest Documents

After the pod is running:

```bash
curl -X POST http://127.0.0.1:8000/ingest
```

If using NodePort:

```bash
curl -X POST http://<node-ip>:<node-port>/ingest
```

## Ask a Question

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"How do I troubleshoot a PVC stuck in Pending?"}'
```

## Sim.ai Usage

Sim.ai does not host the FastAPI app. It reviews the CI/CD pipeline and deployment readiness.

The Sim.ai workflow should be:

```text
Webhook Trigger 1 -> Agent 1
```

`Agent 1` should use this webhook output field as its message:

```text
Webhook Trigger 1 -> Output -> input
```

When GitHub Actions runs, it sends Sim.ai:

```text
repository
branch
sha
report
agent_prompt
prompt
message
input
```

The expected Agent output is:

```text
Status: Ready
Risk: Low
Docker image: Ready to publish
Main finding: Required files, sample docs, and README setup are present.
Next action: Continue deployment.
```

## Update Deployment Image

GitHub Actions publishes versioned tags:

```text
kmc173/rag-kubernetes-search:v1
kmc173/rag-kubernetes-search:v2
kmc173/rag-kubernetes-search:v3
```

To deploy a specific version:

```bash
kubectl set image deployment/rag-kubernetes-search \
  api=kmc173/rag-kubernetes-search:v3 \
  -n rag-kubernetes-search
```

Then check rollout:

```bash
kubectl rollout status deployment/rag-kubernetes-search -n rag-kubernetes-search
```

## Troubleshooting

If the pod is stuck in `ImagePullBackOff`, confirm the image exists in Docker Hub and the repository is public or the cluster has an image pull secret.

If MicroK8s or containerd reports an image unpack error for a versioned tag, confirm the GitHub Actions Docker build uses:

```yaml
provenance: false
```

This repo disables Docker provenance attestations so MicroK8s can pull the pushed image tags.

If `/ingest` fails, check pod logs:

```bash
kubectl logs deployment/rag-kubernetes-search -n rag-kubernetes-search
```

If Sim.ai has no new logs, confirm the GitHub secrets are set and the Sim.ai workflow is live.
