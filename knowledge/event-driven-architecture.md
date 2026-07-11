---
name: toc of contents for event-driven architecture
description: Event sourcing, CQRS, saga patterns, message brokers, eventual consistency. Load when designing event-driven or async systems.
load-when: task mentions event-driven, event sourcing, CQRS, saga, message broker, Kafka, RabbitMQ, or async messaging
skip-when: task is about synchronous REST APIs, CLI tools, or batch processing without messaging
---

# Event-driven architecture

Event-driven systems decouple producers from consumers. Events are facts that happened. Design for eventual consistency, not immediate consistency.

## Quick Reference

Event: immutable record of something that happened. Contains what happened, when, and relevant data. No commands in events (past tense: OrderPlaced, not PlaceOrder).

Event sourcing: store events, not state. State is derived by replaying events. Gives you full audit trail, time travel, and ability to rebuild state.

CQRS: separate read and write models. Write model optimizes for correctness. Read model optimizes for query performance. Use when read and write patterns diverge significantly.

Saga: multi-step transaction across services. Choreography: each service reacts to events. Orchestration: a coordinator directs the flow. Use choreography for simple flows, orchestration for complex ones.

Message brokers: Kafka (durable, ordered, replay), RabbitMQ (flexible routing, transient), NATS (lightweight, high-throughput), Redis Streams (simple, in-memory).

## Deep Dive

### Event sourcing
- **Aggregate roots:** events belong to aggregates. Each aggregate has an event stream.
- **Projections:** derived read models built from event streams. Can be rebuilt from events.
- **Snapshots:** periodically snapshot aggregate state to avoid replaying long streams.
- **Versioning:** schema evolution requires event versioning. Use upcasters for migration.

### CQRS
- **When to use:** read and write patterns diverge significantly. Read-heavy systems benefit most. Write-heavy systems rarely need CQRS.
- **Consistency:** eventual consistency between write and read models. Design UIs to handle this (optimistic updates, loading states).
- **Implementation:** separate databases, separate services, or separate schemas within one database.

### Saga patterns
- **Choreography:** each service publishes events and reacts to events. No central coordinator. Simple but hard to debug.
- **Orchestration:** a saga orchestrator directs the flow. Centralized logic. Easier to understand and debug.
- **Compensating transactions:** every step needs a compensating action for rollback. Design compensations before implementing the forward path.
- **Failure handling:** what happens when step 3 of 5 fails? Compensate steps 1 and 2.

### Message broker selection

| Broker | Use case | Guarantees |
|--------|----------|------------|
| Kafka | High throughput, event sourcing, replay | Durable, ordered, partitioned |
| RabbitMQ | Flexible routing, task queues, RPC | Durable or transient, competing consumers |
| NATS | Microservices, low latency, simplicity | At-most-once or at-least-once |
| Redis Streams | Simple pub/sub, lightweight eventing | In-memory, persistence optional |
| Pulsar | Multi-tenancy, geo-replication | Durable, ordered, tiered storage |

### Eventual consistency
- **Accept it:** most systems don't need strong consistency everywhere. Identify where eventual consistency is acceptable.
- **Read-your-writes:** after a write, the read model may not reflect it immediately. Use strategies like returning write data directly or version stamps.
- **Conflict resolution:** last-write-wins, vector clocks, or CRDTs. Choose based on consistency requirements.

## See Also
- `k/domain-driven-design.md` for bounded contexts and aggregates
- `k/solid-principles.md` for interface design
- `k/google-sre-practices.md` for operational concerns
- `k/trade-off-analysis.md` for evaluating consistency models
