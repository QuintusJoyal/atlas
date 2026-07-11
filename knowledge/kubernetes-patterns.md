---
name: toc of contents for Kubernetes patterns
description: Kubernetes pod design, Helm, service mesh, resource management, and security contexts. Load when container orchestration or K8s tasks are in motion.
load-when: task mentions Kubernetes, pods, Helm, service mesh, or container orchestration
skip-when: task is about VMs, serverless, or non-containerized infrastructure
---

# Kubernetes patterns

Kubernetes is the dominant container orchestration platform. Design for its strengths: self-healing, horizontal scaling, declarative state.

## Quick Reference

Pod design: single-container pods by default. Sidecar for logging, proxying, or augmentation. Init containers for setup. Avoid multi-container pods unless tight coupling is justified.

Resource management: always set requests and limits. Requests for scheduling, limits for safety. Use LimitRange for namespace defaults. Use ResourceQuota for namespace caps.

Helm: package manager for K8s. Charts template manifests. Values override defaults per environment. Use Chart.yaml for versioning. Store charts in charts/ directory.

Service mesh: Istio, Linkerd, or Cilium for mTLS, traffic management, observability. Add only when you need inter-service security or traffic shaping. Default to no mesh.

Security: run as non-root. Drop all capabilities, add only needed ones. Read-only root filesystem. Network policies for pod-to-pod communication. Pod Security Standards (restricted, baseline, privileged).

## Deep Dive

### Pod design
- **Single responsibility:** one process per container, one container per pod unless sidecar needed.
- **Health checks:** liveness (restart if unhealthy), readiness (remove from service if not ready), startup (slow-starting apps).
- **Graceful shutdown:** handle SIGTERM, drain connections, use preStop hooks for connection draining.
- **Anti-affinity:** spread replicas across nodes/zones for high availability.

### Workload resources
- **Deployment:** stateless apps, rolling updates, rollback support.
- **StatefulSet:** stateful apps (databases, message brokers). Stable network identity, persistent volumes.
- **DaemonSet:** one pod per node (logging, monitoring, node agents).
- **Job/CronJob:** batch and scheduled work.

### Networking
- **Services:** ClusterIP (internal), NodePort (external via node), LoadBalancer (cloud LB), ExternalName (DNS alias).
- **Ingress:** HTTP routing, TLS termination. NGINX, Traefik, or cloud-native.
- **Network Policies:** default deny, allow by label. Essential for multi-tenant clusters.

### Configuration and secrets
- **ConfigMaps:** non-sensitive configuration. Mount as files or env vars.
- **Secrets:** base64-encoded (not encrypted at rest by default). Use external secrets operator for production.
- **External Secrets Operator:** sync from AWS Secrets Manager, Vault, GCP Secret Manager.

### Observability
- **Metrics:** Prometheus for collection, Grafana for dashboards. Use ServiceMonitor for auto-discovery.
- **Logging:** structured JSON logs to stdout/stderr. Fluentd or Fluent Bit for collection.
- **Tracing:** OpenTelemetry collector. Jaeger or Tempo for storage.
- **Alerting:** PrometheusAlertManager. Alert on SLOs, not raw metrics.

## See Also
- `k/aws-well-architected.md` for cloud architecture
- `k/cis-benchmarks.md` for security hardening
- `k/google-sre-practices.md` for reliability practices
- `k/finops-practices.md` for cost management
