from typing import List
from pydantic import BaseModel, Field
from timeback.models.timeback_user import TimebackUser


class TimebackGetAllUsersResponse(BaseModel):
    """Response model for paginated users list.

    Mirrors OneRoster list response envelope for users as documented in
    `timeback/docs/oneroster/rostering/get_all_users.md`.
    
    Attributes:
        - users (List[TimebackUser]): List of users. See TimebackUser for structure.
        - totalCount (int): Total number of results
        - pageCount (int): Total number of pages
        - pageNumber (int): Current page number
        - offset (int): Offset for pagination
        - limit (int): Limit per page
    """

    users: List[TimebackUser] = Field(..., description="List of users")
    totalCount: int = Field(..., description="Total number of results")
    pageCount: int = Field(..., description="Total number of pages")
    pageNumber: int = Field(..., description="Current page number")
    offset: int = Field(..., description="Offset for pagination")
    limit: int = Field(..., description="Limit per page")
