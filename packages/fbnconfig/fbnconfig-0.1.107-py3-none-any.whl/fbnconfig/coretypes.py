from __future__ import annotations

from pydantic import BaseModel


class ResourceId(BaseModel):
    scope: str
    code: str
