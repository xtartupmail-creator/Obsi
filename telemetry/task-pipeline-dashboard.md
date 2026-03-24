# Task Pipeline Telemetry Dashboard

This dashboard is required for Redis Streams task operations.

## Core Metrics

### Lag
- `tasks_stream_lag_messages{stream,consumer_group}`
  - Definition: difference between stream tail and last delivered ID per group.
- `tasks_stream_lag_seconds{stream,consumer_group}`
  - Definition: age of oldest pending message in group.

### Retries
- `tasks_retry_total{stream,consumer_group,category}`
  - Counter incremented whenever a task is reclaimed for another attempt.
- `tasks_retry_scheduled_total{category}`
  - Counter for retries deferred by backoff scheduling.

### Redeliveries
- `tasks_redelivery_total{stream,consumer_group}`
  - Counter for messages delivered more than once.
- `tasks_redelivery_ratio{stream,consumer_group}`
  - Ratio = `redelivered / delivered` over rolling interval.

## Supporting Metrics

- `tasks_ack_total{stream,consumer_group}`
- `tasks_fail_total{stream,consumer_group,error_class}`
- `tasks_dlq_total{source_stream,category,error_class}`
- `tasks_processing_duration_ms{stream,consumer_group,task_type}`

## Alerts

- **Lag critical**: `tasks_stream_lag_seconds > 120` for 5m.
- **Retry storm**: `rate(tasks_retry_total[5m])` above baseline + 3 sigma.
- **Redelivery regression**: `tasks_redelivery_ratio > 0.05` for 15m.
- **DLQ growth**: `increase(tasks_dlq_total[15m]) > 50`.

## Dashboard Panels

1. Lag by stream/group (messages + seconds).
2. Retry rate by category.
3. Redelivery ratio trend.
4. DLQ inflow and top error classes.
5. P95 processing duration by task type.

