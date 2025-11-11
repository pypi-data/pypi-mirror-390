"""Request model for getting all users.

GET /ims/oneroster/rostering/v1p2/users
"""

from typing import Optional
from pydantic import BaseModel, Field

from timeback.models.request.timeback_query_params import TimebackQueryParams


class TimebackGetAllUsersRequest(BaseModel):
    """Request model for getting all users (paginated list).
    
    Attributes:
        Optional:
            - query_params (TimebackQueryParams, optional): Query parameters for filtering, pagination, sorting, etc.
              See TimebackQueryParams for available options.
    """

    query_params: Optional[TimebackQueryParams] = Field(
        None, description="Optional query parameters (fields, limit, offset, sort, filter, search, etc.)"
    )

