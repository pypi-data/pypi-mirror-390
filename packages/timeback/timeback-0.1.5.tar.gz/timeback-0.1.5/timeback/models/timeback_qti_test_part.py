"""QTI Test Part model."""

from typing import List
from pydantic import BaseModel, Field
from timeback.models.timeback_qti_section import TimebackQTISection

# TODO: Check to see if we can extract an enum for the navigationMode and submissionMode
class TimebackQTITestPart(BaseModel):
    """QTI Test Part model."""

    identifier: str
    navigationMode: str = "linear"
    submissionMode: str = "individual"
    qti_assessment_section: List[TimebackQTISection] = Field(alias="qti-assessment-section")


