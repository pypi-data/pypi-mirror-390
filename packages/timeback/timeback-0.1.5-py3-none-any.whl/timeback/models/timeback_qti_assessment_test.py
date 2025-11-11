"""QTI Assessment Test model."""

from typing import List, Optional
from pydantic import BaseModel, Field
from timeback.models.timeback_qti_test_part import TimebackQTITestPart
from timeback.models.timeback_qti_outcome_declaration import (
    TimebackQTIOutcomeDeclaration,
)


class TimebackQTIAssessmentTest(BaseModel):
    """QTI Assessment Test model."""

    identifier: str
    title: str
    toolVersion: Optional[str] = None
    toolName: Optional[str] = None
    qti_test_part: List[TimebackQTITestPart] = Field(alias="qti-test-part")
    qti_outcome_declaration: Optional[List[TimebackQTIOutcomeDeclaration]] = Field(
        None, alias="qti-outcome-declaration"
    )


