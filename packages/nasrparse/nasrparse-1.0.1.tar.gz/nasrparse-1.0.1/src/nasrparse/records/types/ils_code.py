from ._base_enum import BaseEnum


class ILSCode(BaseEnum):
    ILS = "ILS"
    MLS = "MLS"
    SDF = "SDF"
    LOCALIZER = "LOCALIZER"
    LDA = "LDA"
    INTERIM_STANDARD_MLS = "ISMLS"
    ILS_DME = "ILS/DME"
    SDF_DME = "SDF/DME"
    LOC_DME = "LOC/DME"
    LOC_GS = "LOC/GS"
    LDA_DME = "LDA/DME"
    NULL = None
