from ._base_enum import BaseEnum


class RunwayMarkCode(BaseEnum):
    PRECISION = "PIR"
    NON_PRECISION = "NPI"
    BASIC = "BSC"
    NUMBERS_ONLY = "NRS"
    NON_STANDARD = "NSTD"
    BUOY = "BUOY"
    STOL = "STOL"
    NONE = "NONE"
    NULL = None
