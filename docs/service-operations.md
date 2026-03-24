# Service Operations: Task Pipeline

## End-to-End Flow

1. API receives `POST /task` and writes to `stream:tasks:ingress`.
2. `cg:dispatcher` consumes ingress tasks and routes by `category`.
3. Category agents consume routed streams from their consumer groups.
4. Workers `XACK` on success.
5. Retry coordinator reclaims stale pending tasks (`XAUTOCLAIM`) and increments attempts.
6. Exhausted tasks are moved to `stream:tasks:dlq`.

## Operational Rules

- Stream retention uses `MAXLEN ~` trimming policy with configured minimum history.
- DLQ messages are retained longer than primary streams.
- Re-drive from DLQ requires explicit operator action and audit logging.

## Runbook Triggers

- High pending idle time in a consumer group: scale workers or investigate stuck handlers.
- Rising redelivery count: verify idempotency and downstream dependency health.
- DLQ growth: inspect error classes and deploy fix before re-drive.

