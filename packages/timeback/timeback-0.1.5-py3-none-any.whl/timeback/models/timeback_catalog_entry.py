"""Additional guidance or annotations for stimulus content."""

from pydantic import BaseModel, Field


class TimebackCatalogEntry(BaseModel):
    """Additional guidance or annotations for stimulus content."""

    id: str = Field(..., description="Unique identifier for the catalog entry")
    support: str = Field(..., description="Type of support provided by this entry")
    content: str = Field(..., description="The actual guidance or annotation content")


