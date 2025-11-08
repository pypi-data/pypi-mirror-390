from pydantic import BaseModel
from typing import Optional


class TimebackQTIObjectAttributes(BaseModel):
    """QTI Object Attributes for media and graphical interactions."""

    data: str
    height: int
    width: int
    type: str
    mediaType: Optional[str] = None
