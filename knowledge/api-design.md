---
name: toc of contents for API design
description: REST API design conventions, GraphQL schema design, gRPC patterns, pagination, rate limiting. Load when designing or reviewing APIs.
load-when: task mentions API design, REST conventions, GraphQL schema, gRPC, or API versioning
skip-when: task is about internal functions, CLI tools, or non-API work
---

# API design

Good APIs are consistent, predictable, and hard to misuse. Design for the consumer, not the implementer.

## Quick Reference

REST: resources are nouns (/users, /orders), HTTP methods are verbs (GET, POST, PUT, PATCH, DELETE). Status codes communicate outcome. Version via URL path (/v1/) or header.

GraphQL: schema-first. Types define the contract. Queries read, mutations write. Use connections for pagination (edges/nodes/pageInfo). N+1 queries are the primary performance hazard.

gRPC: protobuf schemas. Streaming (unary, server, client, bidirectional). Use for service-to-service. HTTP/2 transport. Code generation from .proto files.

Pagination: cursor-based for large/dynamic datasets (consistent). Offset-based for small, stable datasets (simple). Always return total count.

Rate limiting: per-client limits. Use 429 status with Retry-After header. Token bucket or sliding window algorithms.

## Deep Dive

### REST conventions
- **Naming:** plural nouns for collections (/users), singular for singletons not needed. Nested resources for relationships (/users/{id}/orders).
- **Methods:** GET (read, safe, idempotent), POST (create), PUT (full replace, idempotent), PATCH (partial update), DELETE (remove, idempotent).
- **Status codes:** 200 (OK), 201 (Created), 204 (No Content), 400 (Bad Request), 401 (Unauthorized), 403 (Forbidden), 404 (Not Found), 409 (Conflict), 422 (Unprocessable), 429 (Too Many Requests), 500 (Internal Error).
- **Error format:** consistent structure with code, message, and details. Example: `{ "error": { "code": "VALIDATION_ERROR", "message": "...", "details": [...] } }`.
- **HATEOAS:** include links for discoverability where it adds value.

### Versioning strategies
- **URL path:** /v1/users, /v2/users. Simple, explicit. Most common.
- **Header:** Accept: application/vnd.api+json;version=2. Clean URLs but harder to test.
- **Deprecation:** Sunsetting header (draft-ietf-httpapi-deprecation-header). Clear timeline.

### Authentication and authorization
- **OAuth 2.0 + JWT:** standard for web and mobile APIs. Short-lived access tokens, refresh tokens for renewal.
- **API keys:** for server-to-server. Not for client-facing APIs.
- **Scopes:** fine-grained permissions. Request only what you need.

### Error handling
- **Idempotency keys:** POST endpoints should accept Idempotency-Key header for safe retries.
- **Correlation IDs:** propagate request ID across services for distributed tracing.
- **Circuit breaker:** client-side circuit breaker to prevent cascade failures.

## See Also
- `k/solid-principles.md` for interface design
- `k/owasp-asvs.md` for API security requirements
- `k/architecture-decision-records.md` for API design decisions
- `k/trade-off-analysis.md` for evaluating API approaches
