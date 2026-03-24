# STIX Processor

The STIX Processor validates all inbound objects before persistence.

## Validation rules

1. `id` is required and must match `object-type--<RFC4122 UUID>`.
2. The object type prefix in `id` must match the `type` field.
3. ATT&CK IDs like `T1190` are prohibited in `id` and belong under `external_references.external_id`.

`validate_before_persistence` in `validator.py` must be called before writing records to storage.
