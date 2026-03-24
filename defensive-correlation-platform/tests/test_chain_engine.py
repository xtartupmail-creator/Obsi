from datetime import datetime, timezone, timedelta

from app.domain.scoring import jaccard, link_score, LinkScoreInput, status_from_score, temporal_decay


def test_jaccard():
    assert jaccard({"a", "b"}, {"b", "c"}) == 1 / 3


def test_link_score_range():
    s = link_score(LinkScoreInput(0.4, 0.5, 0.8, 0.7, 1.0))
    assert 0 <= s <= 1


def test_status():
    assert status_from_score(0.2).value == "POTENTIAL"
    assert status_from_score(0.35).value == "CANDIDATE"
    assert status_from_score(0.55).value == "VALIDATED"
    assert status_from_score(0.75).value == "CRITICAL"


def test_temporal_decay():
    now = datetime.now(timezone.utc)
    prev = now - timedelta(hours=12)
    assert temporal_decay(now, prev) > temporal_decay(now, now - timedelta(hours=48))
