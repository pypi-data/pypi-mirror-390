from typing import Literal
from pydantic import BaseModel, Field
from timeback.enums import TimebackGuidType


class TimebackOrgRef(BaseModel):
    """Organization reference per `schemas/entities/org_ref.json`.

    Required fields: `sourcedId`, `type` (must equal "org").
    """

    sourcedId: str = Field(..., description="Unique identifier of the organization being referenced")
    type: TimebackGuidType = Field(default=TimebackGuidType.ORG, description="Reference type (org)")
