from typing import Dict, List, Optional
from pydantic import BaseModel, Field, RootModel


class TimebackCodeMinorField(BaseModel):
    imsx_codeMinorFieldName: str = Field(...)
    imsx_codeMinorFieldValue: str = Field(...)


class TimebackCodeMinor(BaseModel):
    imsx_codeMinorField: List[TimebackCodeMinorField] = Field(...)


class TimebackErrorDetailsItem(RootModel[Dict[str, str]]):
    pass


class TimebackErrorBase(BaseModel):
    imsx_codeMajor: str = Field(...)
    imsx_severity: str = Field(...)
    imsx_description: str = Field(...)
    imsx_CodeMinor: TimebackCodeMinor = Field(...)
    imsx_error_details: Optional[List[TimebackErrorDetailsItem]] = None


