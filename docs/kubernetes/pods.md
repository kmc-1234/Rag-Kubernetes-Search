# Kubernetes Pods

A Pod is the smallest deployable unit in Kubernetes. A Pod can contain one or more containers that share networking and storage.

Pods are usually managed by higher-level controllers such as Deployments, StatefulSets, DaemonSets, and Jobs. If a Pod fails, a controller can create a replacement Pod to keep the desired state.

Common troubleshooting steps include checking Pod events, container logs, readiness probes, liveness probes, image pull status, and resource limits.
