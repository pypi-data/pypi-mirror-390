from ._base_enum import BaseEnum


class MarkerTypeCode(BaseEnum):
    MARKER_ONLY = "M"
    COMPASS_LOCATOR = "C"
    NDB = "R"
    MARKER_COMPASS_LOCATOR = "MC"
    MARKER_NDB = "MR"
    NULL = None
