"""QTI Item Body containing elements."""

from typing import List
from pydantic import BaseModel, Field
from timeback.models.timeback_qti_element import TimebackQTIElement


class TimebackQTIItemBody(BaseModel):
    """QTI Item Body containing elements."""

    elements: List[TimebackQTIElement] = Field(default_factory=list)


