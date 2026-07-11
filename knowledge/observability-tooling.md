---
name: toc of contents for observability tooling
description: Prometheus, Grafana, OpenTelemetry, structured logging, alert routing. Load when setting up observability or debugging production systems.
load-when: task mentions Prometheus, Grafana, OpenTelemetry, Jaeger, logging, alerting, or observability tooling
skip-when: task is about application logic, design, or non-operational work
---

# Observability tooling

Observability is the ability to understand what a system is doing from its outputs. Logs, metrics, and traces are the three pillars.

## Quick Reference

Prometheus: pull-based metrics collection. PromQL for querying. Service discovery for dynamic environments. AlertManager for routing alerts. Retention: typically 15-30 days.

Grafana: visualization layer. Dashboards for metrics, logs, traces. Alert rules from dashboards. Data source plugins for Prometheus, Loki, Tempo, Elasticsearch.

OpenTelemetry (OTel): vendor-neutral instrumentation. Auto-instrumentation for common libraries. OTel Collector for processing and exporting. Supports logs, metrics, traces.

Jaeger / Tempo: distributed tracing backends. Jaeger is standalone. Tempo is Grafana-integrated. Trace context propagation via W3C Trace Context headers.

Loki: log aggregation. LogQL for querying. Labels for indexing (not full-text). Integrates with Grafana.

Structured logging: JSON logs with consistent fields. Include: timestamp, level, service, trace_id, message, and relevant context.

## Deep Dive

### Metrics (Prometheus)
- **Four golden signals:** latency, traffic, errors, saturation. Start here for any service.
- **RED method:** Rate, Errors, Duration. Per-request metrics.
- **USE method:** Utilization, Saturation, Errors. Per-resource metrics (CPU, memory, disk).
- **Histograms:** for latency distributions. Better than averages. Use for SLO calculations.
- **Recording rules:** pre-compute expensive queries. Reduce dashboard load time.

### Dashboards (Grafana)
- **Service dashboard:** golden signals at a glance. Latency p50/p95/p99, error rate, request rate, saturation.
- **Infrastructure dashboard:** CPU, memory, disk, network per node/pod.
- **Business dashboard:** key business metrics (orders/min, revenue, active users).
- **Alerting dashboard:** current alerts, alert history, silence management.

### Distributed tracing (OTel + Jaeger/Tempo)
- **Trace context propagation:** inject/extract headers at service boundaries.
- **Sampling:** head-based (decide at start), tail-based (decide after completion). Tail-based is better for catching errors but requires more infrastructure.
- **Span attributes:** add relevant context (user ID, request ID, feature flag) to spans for debugging.
- **Service dependency map:** derived from traces. Shows how services communicate.

### Logging (Loki)
- **Structured logs:** JSON format with consistent fields. Avoid unstructured text logs.
- **Log levels:** ERROR (action needed), WARN (investigate), INFO (normal operations), DEBUG (verbose).
- **Correlation:** include trace_id in logs. Enables jumping from log to trace.
- **Retention:** hot (7 days), warm (30 days), cold (90+ days). Different storage tiers.

### Alerting
- **Alert on symptoms, not causes:** alert on "error rate > 1%" not "pod restarted."
- **SLO-based alerting:** alert when error budget is being consumed too fast.
- **Alert routing:** PagerDuty for SEV1/SEV2, Slack for SEV3, email for informational.
- **Alert fatigue:** reduce noise. Tune thresholds. Use recording rules for complex conditions.

## See Also
- `k/google-sre-practices.md` for SRE concepts (SLOs, SLIs, error budgets)
- `k/dora-metrics.md` for delivery metrics
- `k/kubernetes-patterns.md` for K8s observability
- `k/aws-well-architected.md` for operational excellence pillar
