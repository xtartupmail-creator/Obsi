# Ingestion-Time Graph Reference Validation

## Objective
Prevent insertion of PostgreSQL rows that logically reference Neo4j objects that do not exist.

## Validation contract
Input payloads containing:
- `observation_canonical_id`
- `infrastructure_canonical_id`
- `chain_canonical_id`

must pass two checks before PostgreSQL write:
1. UUIDv4 format validation.
2. Neo4j existence validation by label + `canonical_id`.

## Pseudocode
```text
for each referenced entity in payload:
  assert is_uuid_v4(canonical_id)

missing = []
for each (label, canonical_id) pair:
  exists = neo4j.exists(label=label, canonical_id=canonical_id)
  if not exists:
    missing.append({label, canonical_id})

if missing not empty:
  emit_metric('integrity.graph_reference_missing', count=len(missing))
  return error 422 with missing list

write_postgres_row(payload)
return success
```

## Error behavior
- Missing node(s): `422` with machine-readable `missing_references` list.
- Neo4j transient failure/timeout: `503`, retryable.

## Reconciliation dependency
The periodic reconciliation job is still required to catch:
- eventual-consistency race conditions
- manual data edits
- historical bad records that predate this validation
