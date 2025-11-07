from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class HttpAuthBlock:
    base_url: str
    username: str | None = None
    password: str | None = None
    verify_tls: bool = True
    timeout_s: float = 30.0

    @classmethod
    def from_env(cls, prefix: str):
        return cls(
            base_url=os.getenv(f"{prefix}_BASE_URL", ""),
            username=os.getenv(f"{prefix}_USER"),
            password=os.getenv(f"{prefix}_PASS"),
            verify_tls=os.getenv(f"{prefix}_VERIFY_TLS", "true").lower() == "true",
            timeout_s=float(os.getenv(f"{prefix}_TIMEOUT_S", "30")),
        )
