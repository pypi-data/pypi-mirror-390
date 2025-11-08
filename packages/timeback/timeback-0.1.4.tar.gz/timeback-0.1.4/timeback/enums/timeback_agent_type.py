from enum import Enum


class TimebackAgentType(str, Enum):
    """Valid agent types in the TimeBack API."""
    STUDENT = "student"
    USER = "user"
    PARENT = "parent"