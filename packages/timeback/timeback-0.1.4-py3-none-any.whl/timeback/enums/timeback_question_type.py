from enum import Enum


class TimebackQuestionType(str, Enum):
    """Question types aligned with assessment items.

    Mirrors DB enum "public.question_type" in `timeback/schemas/oneroster.sql`.
    Note: Overlaps with QTI interaction types but mirrors DB values exactly.
    """

    CHOICE = "choice"
    ORDER = "order"
    ASSOCIATE = "associate"
    MATCH = "match"
    HOTSPOT = "hotspot"
    HOTTEXT = "hottext"
    SELECT_POINT = "select-point"
    GRAPHIC_ORDER = "graphic-order"
    GRAPHIC_ASSOCIATE = "graphic-associate"
    GRAPHIC_GAP_MATCH = "graphic-gap-match"
    TEXT_ENTRY = "text-entry"
    EXTENDED_TEXT = "extended-text"
    INLINE_CHOICE = "inline-choice"
    UPLOAD = "upload"
    SLIDER = "slider"
    DRAWING = "drawing"
    MEDIA = "media"
    CUSTOM = "custom"


