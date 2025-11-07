from nasrparse.records.types._base_enum import BaseEnum


class SystemTypeCode(BaseEnum):
    ILS = "LS"
    SDF = "SF"
    LOC = "LC"
    LDA = "LA"
    ILS_DME = "LD"
    SDF_DME = "SD"
    LOC_DME = "LE"
    LOC_GS = "LG"
    LDA_DME = "DD"
    NULL = None
