# Migration Notes: STIX ID Format Compliance

## Context

Prototype datasets previously used non-compliant IDs such as:

- `attack-pattern--T1190`
- `agent--EXT-01`

These values violate STIX identifier requirements and can no longer be ingested.

## Required migration

1. Generate a stable RFC4122 UUID for each affected record.
2. Rewrite `id` to `object-type--<uuid>` where `object-type` matches `type`.
3. Move ATT&CK values (for example `T1190`) to `external_references[*].external_id`.
4. Preserve legacy internal agent identifiers (for example `EXT-01`) in `agent_id` or an extension field such as `x_internal_agent_id`.

## Example

Before:

```json
{
  "type": "attack-pattern",
  "id": "attack-pattern--T1190"
}
```

After:

```json
{
  "type": "attack-pattern",
  "id": "attack-pattern--7b3b4d3e-92a1-4f7f-84f4-1007fb1f7d2f",
  "external_references": [
    {
      "source_name": "mitre-attack",
      "external_id": "T1190"
    }
  ]
}
```
