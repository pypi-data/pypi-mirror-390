from nasrparse.records.types._base_enum import BaseEnum


class FacilityOperatorCode(BaseEnum):
    USAF = "A"
    USCG = "C"
    CITY = "CITY"
    COUNTY = "COUNTY"
    CANADIAN_MOT = "D"
    FAA = "F"
    FAA_CONTRACT = "FCT"
    OTHER_GOV = "G"
    USN = "N"
    NON_FED_TOWER = "NFCT"
    OTHER = "O"
    PRIVATE = "P"
    USA = "R"
    NWS = "W"
    RCAF = "X"
    UNKNOWN = "Z"
    NULL = None
