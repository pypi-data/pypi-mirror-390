"""Shared query parameters model for GET endpoints.

This model can be reused across GET endpoints that support standard OneRoster
query parameters like fields, pagination, sorting, filtering, and searching.
"""

from typing import Optional, Sequence, Union
from pydantic import BaseModel, ConfigDict, Field


class TimebackQueryParams(BaseModel):
    """Shared query parameters for GET endpoints.

    All attributes are optional and map to standard OneRoster query parameters.
    
    Attributes:
        Optional:
            - fields (str | List[str], optional): Comma-separated field list or sequence of field names to include
            - limit (int, optional): Number of items per page (default: 100, maximum: 3000)
            - offset (int, optional): Offset for pagination
            - sort (str, optional): Field to sort by
            - order_by (str, optional): Sort direction (asc/desc)
            - filter (str, optional): Filtering expression following 1EdTech specification
            - search (str, optional): Free-text search parameter (proprietary extension)
    """

    model_config = ConfigDict(populate_by_name=True)

    fields: Optional[Union[str, Sequence[str]]] = Field(
        None, description="Comma-separated field list or sequence of field names to include"
    )
    limit: Optional[int] = Field(None, description="Number of items per page (default: 100, maximum: 3000)")
    offset: Optional[int] = Field(None, description="Offset for pagination")
    sort: Optional[str] = Field(None, description="Field to sort by")
    order_by: Optional[str] = Field(
        None, description="Sort direction (asc/desc)", alias="orderBy"
    )
    filter: Optional[str] = Field(None, description="Filtering expression following 1EdTech specification")
    search: Optional[str] = Field(None, description="Free-text search parameter (proprietary extension)")

    def to_query_dict(self) -> dict:
        """Convert to query parameters dictionary, excluding None values.
        
        Returns:
            Dictionary of query parameters ready for HTTP client
        """
        query: dict = {}
        if self.fields is not None:
            if isinstance(self.fields, (list, tuple)):
                query["fields"] = ",".join(self.fields)
            else:
                query["fields"] = self.fields
        if self.limit is not None:
            query["limit"] = self.limit
        if self.offset is not None:
            query["offset"] = self.offset
        if self.sort is not None:
            query["sort"] = self.sort
        if self.order_by is not None:
            query["orderBy"] = self.order_by
        if self.filter is not None:
            query["filter"] = self.filter
        if self.search is not None:
            query["search"] = self.search
        return query

