"""QTI Outcome Declaration for test results."""

from typing import Dict, Optional, Union, List
from pydantic import BaseModel


class TimebackQTIOutcomeDeclaration(BaseModel):
    """QTI Outcome Declaration for test results."""

    identifier: str
    cardinality: str
    baseType: str
    normalMaximum: Optional[float] = None
    normalMinimum: Optional[float] = None
    defaultValue: Optional[Dict[str, Union[str, int, float]]] = None


