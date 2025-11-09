from __future__ import annotations
from datetime import datetime, timezone
from pydantic import BaseModel, HttpUrl, Field
from typing import Dict, List, Optional


class AuditRequest(BaseModel):
    url: HttpUrl


class HeaderResult(BaseModel):
    present: bool
    value: Optional[str] = None
    ok: bool


class AuditResult(BaseModel):
    url: str
    effective_url: str
    scheme: str
    score: int
    headers: Dict[str, HeaderResult]
    missing: List[str]
    checked_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))


class AuditList(BaseModel):
    results: List[AuditResult]