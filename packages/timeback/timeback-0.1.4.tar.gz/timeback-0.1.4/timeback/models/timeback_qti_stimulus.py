"""QTI 3.0 compliant stimulus that can be referenced by assessment items."""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from timeback.models.timeback_catalog_entry import TimebackCatalogEntry


class TimebackQTIStimulus(BaseModel):
    """QTI 3.0 compliant stimulus that can be referenced by assessment items."""

    identifier: str = Field(..., description="Unique identifier for the stimulus")
    title: str = Field(..., description="Title or name of the stimulus")
    language: str = Field(..., description="Language code for the stimulus content")
    content: str = Field(
        ..., description="The actual stimulus content in QTI-compliant format"
    )
    catalog_info: Optional[List[TimebackCatalogEntry]] = Field(
        None, description="Additional guidance or annotations for this stimulus"
    )
    raw_xml: Optional[str] = Field(
        None, description="Raw XML representation of the stimulus"
    )
    created_at: Optional[datetime] = Field(
        None, description="Timestamp when the stimulus was created"
    )
    updated_at: Optional[datetime] = Field(
        None, description="Timestamp when the stimulus was last updated"
    )
    is_valid_xml: Optional[bool] = Field(
        None, description="Whether the stimulus XML is valid according to QTI schema"
    )


