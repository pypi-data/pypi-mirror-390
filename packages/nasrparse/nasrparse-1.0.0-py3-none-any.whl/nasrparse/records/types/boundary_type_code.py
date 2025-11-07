from ._base_enum import BaseEnum


class BoundaryTypeCode(BaseEnum):
    ARTCC = "ARTCC"
    FIR = "FIR"
    CTA = "CTA"
    CTA_FIR = "CTA/FIR"
    UTA = "UTA"
    NULL = None
