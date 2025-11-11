from pydantic import BaseModel, Field


class TimebackSourcedIdPairs(BaseModel):
    """SourcedId mapping returned when creating a user.
    
    Attributes:
        - suppliedSourcedId (str): Client-supplied sourcedId
        - allocatedSourcedId (str): Server-allocated sourcedId
    """
    
    suppliedSourcedId: str = Field(..., description="Client-supplied sourcedId")
    allocatedSourcedId: str = Field(..., description="Server-allocated sourcedId")