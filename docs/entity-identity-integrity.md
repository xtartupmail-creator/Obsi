# Canonical Entity Identifier and Cross-Store Integrity Strategy

## Scope
This strategy applies to entities that are represented across PostgreSQL, Neo4j, and Redis:

- `Observation`
- `Infrastructure`
- `Chain`

## 1) Canonical ID definition
Use **UUIDv4** as the single platform-level canonical identifier format for all three entity classes.

### Canonical ID rules
- Field name: `canonical_id`
- Type/format: RFC 4122 UUIDv4 string (`xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx`)
- ID ownership: generated once at creation time in the application service layer
- Immutability: `canonical_id` is write-once and never mutated

### Why UUIDv4 (vs ULID)
- Native PostgreSQL `uuid` type support (storage and index efficiency)
- Mature support in Neo4j properties/drivers
- No cross-language lexicographic ordering assumptions required

If ordered IDs become necessary later, ULID can be introduced behind a compatibility layer, but UUIDv4 is the canonical format for now.

## 2) Storage in PostgreSQL, Neo4j, and Redis

### PostgreSQL
- Add `canonical_id uuid not null unique` to each entity table.
- Keep surrogate integer primary keys if they exist for local joins/performance.
- External references across bounded contexts must use `canonical_id`.

### Neo4j
- Store `canonical_id` on each corresponding node label.
- Add uniqueness constraints per label for `canonical_id`.

Example:
- `(:Observation { canonical_id: "..." })`
- `(:Infrastructure { canonical_id: "..." })`
- `(:Chain { canonical_id: "..." })`

### Redis
- Use `canonical_id` in keys and payload fields.
- Key pattern examples:
  - `observation:{canonical_id}`
  - `infrastructure:{canonical_id}`
  - `chain:{canonical_id}`

## 3) SQL comment language for graph references
Columns in PostgreSQL that refer to graph objects should not imply database-enforced foreign keys to Neo4j.

Use comment text:
- `logical reference to Neo4j Observation(canonical_id)`
- `logical reference to Neo4j Infrastructure(canonical_id)`
- `logical reference to Neo4j Chain(canonical_id)`

Do **not** use comment language such as `FK to Neo4j ...`.

## 4) Ingestion-time integrity validation (application-level)
Before writing a PostgreSQL row that includes a graph object reference, ingestion must verify the target Neo4j node exists by `canonical_id`.

Validation sequence:
1. Parse incoming canonical IDs and validate UUIDv4 format.
2. Query Neo4j for existence of each referenced node.
3. If any node is missing:
   - reject write with `422 Unprocessable Entity` (or domain equivalent)
   - emit structured error with missing canonical IDs and entity type
   - increment integrity-failure metric
4. If all exist:
   - proceed with PostgreSQL write
   - cache positive existence check briefly in Redis to reduce repeated lookups

Operational guidance:
- Neo4j lookup timeout should be short and explicit.
- Validation failures are business/data errors, not retriable transport errors.
- Neo4j transient/network failures are retriable and should return `503`.

## 5) Reconciliation job for orphaned references and conflict handling
Run a periodic reconciliation job (e.g., every 15 minutes) to identify and resolve cross-store drift.

### Job responsibilities
- Scan PostgreSQL logical-reference columns.
- Verify corresponding Neo4j nodes exist by `canonical_id`.
- Detect conflicts where a canonical ID exists with incompatible type/shape metadata.

### Orphan handling
- Mark records with missing graph target as `orphaned`.
- Emit audit event and alert when orphan count exceeds threshold.
- Optionally queue re-link workflow if upstream events are eventually consistent.

### Conflict handling
- Treat canonical ID as source-of-truth identity.
- If type mismatch is detected for same canonical ID:
  - quarantine affected records
  - prevent serving inconsistent aggregates
  - open incident with reconciliation payload snapshot

### Idempotency and observability
- Use deterministic reconciliation run IDs.
- Persist outcome per canonical ID (`ok`, `orphaned`, `conflict`, `relinked`).
- Expose metrics: scan count, orphan count, conflict count, mean resolution latency.
