"""STIX object validation for ingest pipeline."""

from __future__ import annotations

import re
from dataclasses import dataclass

# object-type--<RFC4122 UUID>
STIX_ID_RE = re.compile(
    r"^(?P<object_type>[a-z][a-z0-9-]*)--"
    r"(?P<uuid>[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})$"
)


class StixValidationError(ValueError):
    """Raised when a STIX object does not satisfy ingest validation rules."""


@dataclass(frozen=True)
class StixValidationResult:
    valid: bool
    reason: str | None = None


def validate_stix_id(stix_id: str, expected_type: str | None = None) -> StixValidationResult:
    """Validate STIX id format and optional type consistency."""
    match = STIX_ID_RE.match(stix_id)
    if not match:
        return StixValidationResult(
            valid=False,
            reason=(
                "Invalid STIX id; expected object-type--<RFC4122 UUID> "
                "(example: attack-pattern--7b3b4d3e-92a1-4f7f-84f4-1007fb1f7d2f)."
            ),
        )

    if expected_type and match.group("object_type") != expected_type:
        return StixValidationResult(
            valid=False,
            reason=f"STIX id type '{match.group('object_type')}' does not match object type '{expected_type}'.",
        )

    return StixValidationResult(valid=True)


def validate_before_persistence(stix_object: dict) -> None:
    """Reject non-conforming STIX ids before persistence."""
    stix_id = stix_object.get("id")
    stix_type = stix_object.get("type")

    if not stix_id or not isinstance(stix_id, str):
        raise StixValidationError("Missing required string field: id")

    if not stix_type or not isinstance(stix_type, str):
        raise StixValidationError("Missing required string field: type")

    id_result = validate_stix_id(stix_id=stix_id, expected_type=stix_type)
    if not id_result.valid:
        raise StixValidationError(id_result.reason or "Invalid STIX id")

    # Prevent ATT&CK technique IDs from being used as STIX ids.
    if stix_id.endswith("--T1190") or re.search(r"--T\d{4,5}$", stix_id):
        raise StixValidationError(
            "ATT&CK technique IDs belong in external_references.external_id, not in id."
        )
