"""Rubric for assessment items."""

from pydantic import BaseModel


class TimebackQTIRubric(BaseModel):
    """Rubric for assessment items."""

    use: str
    view: str
    body: str


