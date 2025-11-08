"""QTI Item Reference used in sections."""

from typing import Optional, List
from pydantic import BaseModel, Field


class TimebackQTIItemRef(BaseModel):
    """QTI Item Reference used in sections."""

    identifier: str
    href: str
    required: Optional[bool] = None
    fixed: Optional[bool] = None
    class_: Optional[List[str]] = Field(None, alias="class")
    category: Optional[List[str]] = None


