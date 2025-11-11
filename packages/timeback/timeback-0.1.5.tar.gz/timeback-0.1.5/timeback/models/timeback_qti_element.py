"""QTI Element for item body content."""

from typing import Optional
from pydantic import BaseModel


class TimebackQTIElement(BaseModel):
    """QTI Element for item body content."""

    type: str
    content: str
    identifier: Optional[str] = None
    responseIdentifier: Optional[str] = None


