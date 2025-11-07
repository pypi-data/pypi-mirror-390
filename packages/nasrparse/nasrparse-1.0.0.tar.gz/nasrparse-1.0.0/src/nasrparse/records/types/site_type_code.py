from ._base_enum import BaseEnum


class SiteTypeCode(BaseEnum):
    AIRPORT = "A"
    BALLOONPORT = "B"
    SEAPLANE_BASE = "C"
    GLIDERPORT = "G"
    HELIPORT = "H"
    ULTRALIGHT = "U"
    VERTIPORT = "V"
    NULL = None
