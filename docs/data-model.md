# STIX Data Model

## Identifier requirements

All STIX Domain Objects (SDOs) and STIX Cyber-observable Objects (SCOs) must use the STIX identifier format:

- `id`: `object-type--<RFC4122 UUID>`
- Example: `attack-pattern--7b3b4d3e-92a1-4f7f-84f4-1007fb1f7d2f`

Non-compliant identifiers such as `attack-pattern--T1190` and `agent--EXT-01` are invalid and must not be persisted.

## ATT&CK external IDs

MITRE ATT&CK technique IDs (for example `T1190`) are external references and **must not** be stored in STIX `id`.

Use this structure instead:

```json
{
  "external_references": [
    {
      "source_name": "mitre-attack",
      "external_id": "T1190",
      "url": "https://attack.mitre.org/techniques/T1190/"
    }
  ]
}
```

## Agent representation

- `id`: STIX identifier, e.g. `identity--0c7d5f0f-ae4f-4f24-9bf9-2495f4642f4e`
- `agent_id`: internal human-readable identifier, e.g. `EXT-01`

`agent_id` is not a STIX field and should be treated as an internal extension.
