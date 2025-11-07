from ._base_enum import BaseEnum


class FuelCode(BaseEnum):
    GRADE_100 = "100"
    GRADE_100LL = "100LL"
    JET_A = "A"
    JET_A_PLUS = "A+"
    JET_A_PLUS_PLUS = "A++"
    JET_A_PLUS_PLUS_100 = "A++10"
    JET_A1 = "A1"
    JET_A1_PLUS = "A1+"
    JP5 = "J5"
    JP8 = "J8"
    JP8_100 = "J8+10"
    JET_UNKNOWN = "J"
    MOGAS = "MOGAS"
    UL91 = "UL91"
    UL94 = "UL94"
    UL100 = "UL100"
    NULL = None
