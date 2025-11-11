from typing import Optional, Sequence, Union

"""Utilities for normalizing fields."""


def normalize_fields(fields: Optional[Union[str, Sequence[str]]]) -> Optional[str]:
    if fields is None:
        return None
    if isinstance(fields, str):
        return fields
    return ",".join(fields)
