from nasrparse.records.types._base_enum import BaseEnum


class TowerCode(BaseEnum):
    ATCT = "ATCT"
    NON_ATCT = "NON-ATCT"
    ATCT_AC = "ATCT-A/C"
    ATCT_RAPCON = "ATCT-RAPCON"
    ATCT_RATCF = "ATCT-RATCF"
    ATCT_TRACON = "ATCT-TRACON"
    NULL = None
