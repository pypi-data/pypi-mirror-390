"""Context of the activity where the event was recorded."""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class TimebackActivityContext(BaseModel):
    """Context of the activity where the event was recorded."""

    id: Optional[str] = Field(None, description="Unique identifier for the activity context (URI) - Backend generated")
    type: str = "TimebackActivityContext"
    subject: str = Field(description="Subject of the activity (e.g., Reading)")
    app: Dict[str, Any] = Field(description="Application info (id, name, etc.)")
    activity: Dict[str, Any] = Field(description="Activity info (id, name, etc.)")
    course: Optional[Dict[str, Any]] = Field(None, description="Course info if applicable")
    extensions: Optional[Dict[str, Any]] = Field(None, description="Additional attributes")


