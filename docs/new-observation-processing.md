# New Observation Processing Standard

## Decision (single supported mechanism)

We standardize on **application-layer publish-on-write** for all “new Observation” processing.

- **Do not use APOC triggers** (`apoc.trigger.add`) for this flow.
- **Do not use Neo4j CDC** for this flow.
- Event emission happens in the writer service transaction boundary (see ownership section below).

## Ownership boundary

- **Event emitter (source of truth):** `observation-api` service.
  - Responsibility: persist `Observation` and publish `observation.created` event.
- **Path computation consumer:** `chain-discovery-worker` service.
  - Responsibility: consume `observation.created`, compute/update chain paths in Neo4j.

No other service may emit `observation.created`.

## Deployment prerequisites

1. Redis 7+ with persistence enabled (AOF) for durable stream storage.
2. Neo4j reachable from `chain-discovery-worker`.
3. Both services configured with shared event contract version.
4. `observation_id` must be globally unique (UUID recommended).

### Redis setup (exact commands)

```bash
# 1) Start Redis with AOF enabled (durable append-only log)
docker run -d --name obsi-redis -p 6379:6379 redis:7 \
  redis-server --appendonly yes --appendfsync everysec

# 2) Create stream and consumer group (idempotent: ignore BUSYGROUP)
redis-cli -h 127.0.0.1 -p 6379 XGROUP CREATE observation.events chain-discovery 0 MKSTREAM

# 3) Verify persistence and group state
redis-cli -h 127.0.0.1 -p 6379 CONFIG GET appendonly
redis-cli -h 127.0.0.1 -p 6379 XINFO GROUPS observation.events
```

### Service configuration

`observation-api` environment:

```bash
export REDIS_URL=redis://127.0.0.1:6379
export OBSERVATION_EVENTS_STREAM=observation.events
export OBSERVATION_EVENT_TYPE=observation.created
```

`chain-discovery-worker` environment:

```bash
export REDIS_URL=redis://127.0.0.1:6379
export OBSERVATION_EVENTS_STREAM=observation.events
export OBSERVATION_CONSUMER_GROUP=chain-discovery
export OBSERVATION_CONSUMER_NAME=worker-1
export OBSERVATION_RETRY_MAX=20
export OBSERVATION_VISIBILITY_TIMEOUT_SECONDS=60
export OBSERVATION_DLQ_STREAM=observation.events.dlq
```

## Event contract

`observation.created` payload must include:

- `event_id` (UUID)
- `event_type` = `observation.created`
- `observation_id` (UUID) ← **idempotency key**
- `created_at` (RFC3339 timestamp)
- `schema_version` (integer)

## Failure and retry semantics (durability requirements)

1. `observation-api` writes observation first, then publishes `observation.created` to Redis stream before request success is returned.
2. `chain-discovery-worker` reads via consumer group (`XREADGROUP`) and only acknowledges (`XACK`) after Neo4j path write succeeds.
3. If worker crashes after read and before ack, message remains pending and is reclaimed after visibility timeout (`XAUTOCLAIM`), then retried.
4. Retries use exponential backoff with jitter; max attempts set by `OBSERVATION_RETRY_MAX`.
5. On max-attempt exhaustion, event is copied to `observation.events.dlq` with error metadata and then acked in primary stream.
6. Processing is idempotent by `observation_id`:
   - Worker must upsert a processing ledger entry keyed by `observation_id`.
   - If ledger shows already completed, worker acks without recomputation.

This guarantees at-least-once delivery with idempotent processing, so chain discovery is durable under crashes and transient failures.

## Implementation-specific instruction (replaces generic trigger wording)

Use this instruction everywhere in docs and runbooks:

> “When an Observation is created, `observation-api` must publish an `observation.created` event to `observation.events` (Redis Stream). `chain-discovery-worker` consumes that event and computes paths in Neo4j with idempotent retry semantics keyed by `observation_id`.”

Do **not** describe this as an “AFTER CREATE trigger”.
