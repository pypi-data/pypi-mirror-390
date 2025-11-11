"""QTI Response Declaration that defines the expected response."""

from typing import Dict, List, Optional
from pydantic import BaseModel


class TimebackQTIResponseDeclaration(BaseModel):
    """QTI Response Declaration that defines the expected response."""

    identifier: str
    cardinality: str
    baseType: str
    correctResponse: Optional[Dict[str, List[str]]] = None


