from validator import StixValidationError, validate_before_persistence, validate_stix_id


def test_validate_stix_id_accepts_compliant_id():
    result = validate_stix_id("attack-pattern--7b3b4d3e-92a1-4f7f-84f4-1007fb1f7d2f", "attack-pattern")
    assert result.valid is True


def test_validate_stix_id_rejects_non_compliant_id():
    result = validate_stix_id("attack-pattern--T1190", "attack-pattern")
    assert result.valid is False


def test_validate_before_persistence_rejects_legacy_id():
    obj = {
        "type": "attack-pattern",
        "id": "attack-pattern--T1190",
    }

    try:
        validate_before_persistence(obj)
        raise AssertionError("Expected StixValidationError")
    except StixValidationError:
        pass
