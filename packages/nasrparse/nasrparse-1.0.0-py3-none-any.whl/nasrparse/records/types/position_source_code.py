from ._base_enum import BaseEnum


class PositionSourceCode(BaseEnum):
    AIR_FORCE = "A"
    COAST_GUARD = "C"
    CANADIAN_AIRAC = "D"
    FAA = "F"
    FAA_TECH_OPS = "FS"
    NOS_HISTORICAL = "G"
    NGS = "K"
    DOD = "M"
    US_NAVY = "N"
    OWNER = "O"
    NOS_PHOTO_HISTORICAL = "P"
    QUAD_PLOT_HISTORICAL = "Q"
    ARMY = "R"
    SIAP = "S"
    THIRD_PARTY_SURVEY = "T"
    SURVEYED = "Z"
    NULL = None
