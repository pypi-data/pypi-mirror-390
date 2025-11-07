from ._base_enum import BaseEnum


class FacilityTypeCode(BaseEnum):
    ATCT = "ATCT"
    ATCT_APPROACH = "ATCT-A/C"
    ATCT_RAPCON = "ATCT-RAPCON"
    ATCT_RATCF = "ATCT-RATCF"
    ATCT_TRACON = "ATCT-TRACON"
    NON_ATCT = "NON-ATCT"
    TRACON = "TRACON"
    ARTCC = "ARTCC"
    CERAP = "CERAP"
    NULL = None
