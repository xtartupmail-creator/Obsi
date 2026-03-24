from __future__ import annotations

from enum import Enum


class FindingType(str, Enum):
    MISCONFIGURATION = "misconfiguration"
    VULNERABILITY = "vulnerability"
    EXPOSURE = "exposure"
    IDENTITY_RISK = "identity_risk"
    ANOMALY = "anomaly"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ChainStatus(str, Enum):
    POTENTIAL = "POTENTIAL"
    CANDIDATE = "CANDIDATE"
    VALIDATED = "VALIDATED"
    CRITICAL = "CRITICAL"
    CONTAINED = "CONTAINED"
    MITIGATED = "MITIGATED"
    CLOSED = "CLOSED"


class LinkDecision(str, Enum):
    SEED = "seed"
    APPEND = "append"
    MERGE = "merge"
    ORPHAN = "orphan"


class LinkType(str, Enum):
    TAG_OVERLAP = "tag_overlap"
    VECTOR_OVERLAP = "vector_overlap"
    TEMPORAL = "temporal"
    PHASE = "phase"
    BRIDGE = "bridge"
