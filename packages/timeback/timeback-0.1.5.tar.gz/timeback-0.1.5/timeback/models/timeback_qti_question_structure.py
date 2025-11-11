"""Structure containing the details of a question."""

from typing import Optional, List
from pydantic import BaseModel
from timeback.models.timeback_qti_choice import TimebackQTIChoice


class TimebackQTIQuestionStructure(BaseModel):
    """Structure containing the details of a question."""

    prompt: str
    choices: Optional[List[TimebackQTIChoice]] = None


