from ._base_enum import BaseEnum


class ObstructionMarkingCode(BaseEnum):
    MARKED = "M"
    LIGHTED = "L"
    MARKED_LIGHTED = "ML"
    NONE = "NONE"
    NULL = None
