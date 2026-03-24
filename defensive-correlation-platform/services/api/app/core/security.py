from __future__ import annotations

import hashlib
import hmac
import os
from dataclasses import dataclass


@dataclass(slots=True)
class SignatureVerifier:
    secret: str

    @classmethod
    def from_env(cls) -> "SignatureVerifier":
        return cls(secret=os.getenv("INGEST_HMAC_SECRET", "dev-secret"))

    def verify(self, body: bytes, signature_header: str | None) -> bool:
        if not signature_header:
            return False
        expected = hmac.new(self.secret.encode(), body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature_header.strip())
