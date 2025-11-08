"""
Timeback - A Python library for interfacing with the TimeBack API.
"""

__version__ = "0.1.4"
__author__ = "Casey Schmid"
__email__ = "casey.schmid@2hourlearning.com"

__all__ = ["Timeback"]

def __getattr__(name: str):
    if name == "Timeback":
        from .client import Timeback  # lazy import to avoid circulars during package init
        return Timeback
    raise AttributeError(name)
