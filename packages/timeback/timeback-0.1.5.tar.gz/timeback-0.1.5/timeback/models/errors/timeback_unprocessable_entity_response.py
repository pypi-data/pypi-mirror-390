from pydantic import Field
from .timeback_error_common import TimebackErrorBase


class TimebackUnprocessableEntityResponse(TimebackErrorBase):
    imsx_codeMajor: str = Field(default="failure")
    imsx_severity: str = Field(default="error")
