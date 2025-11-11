from enum import Enum


class TimebackDifficulty(str, Enum):
    """Difficulty levels for tasks/items.

    Mirrors DB enum "public.difficulty" in `timeback/schemas/oneroster.sql`.
    """

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


