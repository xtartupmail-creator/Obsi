from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


class DomainError(Exception):
    """Base exception for domain-level failures."""


@dataclass(slots=True)
class PolicyDeniedError(DomainError):
    reasons: list[str]


@dataclass(slots=True)
class ValidationError(DomainError):
    message: str
    details: Dict[str, Any] | None = None


@dataclass(slots=True)
class StorageError(DomainError):
    message: str
    op: str = "unknown"


@dataclass(slots=True)
class IntegrationError(DomainError):
    message: str
    service: str
