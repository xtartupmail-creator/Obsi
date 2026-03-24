from app.services.chain_engine import jaccard, link_confidence, score_to_status


def test_jaccard():
    assert jaccard({"a", "b"}, {"b", "c"}) == 1 / 3


def test_link_confidence_range():
    s = link_confidence(["x", "y"], ["y"], ["web"], ["web", "id"])
    assert 0 <= s <= 1


def test_status():
    assert score_to_status(0.2) == "POTENTIAL"
    assert score_to_status(0.35) == "CANDIDATE"
    assert score_to_status(0.55) == "VALIDATED"
    assert score_to_status(0.75) == "CRITICAL"
