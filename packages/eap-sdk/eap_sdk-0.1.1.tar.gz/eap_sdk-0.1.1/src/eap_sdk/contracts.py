from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RunRequest(BaseModel):
    flow: str = Field(..., description="Registered flow name")
    params: dict[str, Any] = Field(default_factory=dict)


class RunResponse(BaseModel):
    success: bool
    message: str
    data: dict[str, Any] | None = None
    error: str | None = None
