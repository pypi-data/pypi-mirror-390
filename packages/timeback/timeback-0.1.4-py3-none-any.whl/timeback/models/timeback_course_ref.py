"""CourseRef model for OneRoster API.

This Pydantic model matches the schema defined in
`timeback/schemas/entities/course_ref.json`.
"""

from pydantic import BaseModel, Field


class TimebackCourseRef(BaseModel):
    """Reference to a course, used when linking classes to courses.

    See: `timeback/schemas/entities/course_ref.json`
    - required: sourcedId
    """

    sourcedId: str = Field(..., description="Unique identifier of the course being referenced")


