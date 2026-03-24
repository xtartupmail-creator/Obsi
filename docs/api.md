# API Queueing Contract

## `POST /task`

`POST /task` maps to a **single backend queueing flow**:

1. Validate request and assign `task_id`.
2. Enqueue exactly once into `stream:tasks:ingress` via `XADD`.
3. Return `202 Accepted` with `task_id` and enqueue metadata.

No alternate queueing backend is permitted for this endpoint.

### Request (example)

```json
{
  "category": "general",
  "type": "document.index",
  "payload": {
    "document_id": "doc_123"
  },
  "max_attempts": 5
}
```

### Enqueued Stream Fields

- `task_id`
- `category`
- `type`
- `payload` (serialized)
- `attempt` (starts at `0`)
- `max_attempts`
- `created_at`
- `next_attempt_at` (initially equals `created_at`)

### Response (example)

```json
{
  "task_id": "task_01HT...",
  "status": "queued",
  "queue": "stream:tasks:ingress"
}
```

## Notification Channels (Non-Critical)

Pub/Sub may be used only for live observability hints, such as:
- `notify:telemetry:task_events`
- `notify:ui:task_progress`

These channels are optional and non-durable; consumers must treat missing events as normal.

