from ._base_enum import BaseEnum


class AgencyTypeCode(BaseEnum):
    AIRPORT = "A"
    ARTCC = "C"
    SPECIAL = "S"
    TRACON = "T"
    NULL = None
