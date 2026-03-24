# Task Delivery Mechanism (Primary: Redis Streams)

## Decision

**Primary transport for task delivery is Redis Streams.**

Rationale:
- Durable persistence and replay support for at-least-once processing.
- Native consumer groups for horizontal scaling across agents.
- Explicit acknowledgment (`XACK`) and pending-entry tracking (`XPENDING`) needed for retries and dead-letter handling.

`Redis Pub/Sub` is **not** used for authoritative task dispatch.

## Redis Primitive Allowlist

| Redis Primitive | Allowed For | Not Allowed For |
| --- | --- | --- |
| `Streams` (`XADD`, `XREADGROUP`, `XACK`, `XCLAIM`/`XAUTOCLAIM`) | All task creation, delivery, retry, and completion flow | Live-only fan-out notifications |
| `Pub/Sub` (`PUBLISH`/`SUBSCRIBE`) | Non-critical live notifications (telemetry fan-out, UI progress hints, ephemeral status pings) | Task ingestion, ownership, retries, guaranteed processing |

## Stream Key Model

### Canonical stream key
- `stream:tasks:ingress` (single entrypoint stream for all `POST /task` requests)

### Optional category partitioning (if volume requires)
- `stream:tasks:category:{category}`
- Routing into category streams happens **after** ingest from `stream:tasks:ingress` by dispatcher workers; public API still writes to one canonical ingress flow.

## Consumer Groups

Each agent class gets its own consumer group per stream to keep ownership and lag visible.

### Ingress stream groups
- `cg:dispatcher` on `stream:tasks:ingress`

### Category stream groups (when enabled)
- `cg:agent:general` on `stream:tasks:category:general`
- `cg:agent:priority` on `stream:tasks:category:priority`
- `cg:agent:batch` on `stream:tasks:category:batch`

Consumer names should use host + process identity, e.g.:
- `dispatcher-{hostname}-{pid}`
- `agent-general-{hostname}-{pid}`

## Acknowledge, Retry, and Dead-Letter Behavior

### Ack policy
- Workers acknowledge only after successful handler completion (`XACK`).
- No pre-acknowledgment is allowed.

### Retry policy
- Failed tasks remain pending and are retried through reclamation.
- Reclaim stale pending entries via `XAUTOCLAIM` using an idle threshold (`retry_idle_ms`, default 30000).
- Increment `attempt` metadata in task payload on every retry.
- Exponential backoff is applied by scheduler metadata fields:
  - `next_attempt_at`
  - `attempt`
  - `max_attempts`

### Dead-letter policy
- If `attempt >= max_attempts`, write the payload to:
  - `stream:tasks:dlq`
- Include failure context fields:
  - `failed_at`
  - `failure_reason`
  - `original_stream`
  - `original_message_id`
- Acknowledge original message after successful DLQ write to avoid poison-message loops.

## Delivery Guarantees

- Processing semantics: **at-least-once**.
- Handlers must be idempotent by `task_id`.
- Duplicate delivery is expected under reclaim/retry and must not cause duplicate side effects.

## Security and Governance

- ACL profile for task workers must include stream commands only.
- Pub/Sub channels for notifications must be namespaced under `notify:*` and carry no authoritative task state.

