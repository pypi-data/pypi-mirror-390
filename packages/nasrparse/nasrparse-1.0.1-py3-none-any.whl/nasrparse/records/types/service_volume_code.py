from nasrparse.records.types._base_enum import BaseEnum


class ServiceVolumeCode(BaseEnum):
    HIGH_ALTITUDE = "H"
    LOW_ALTITUDE = "L"
    TERMINAL = "T"
    DME_HIGH = "DH"
    DME_LOW = "DL"
    VOR_HIGH = "VH"
    VOR_LOW = "VL"
    NULL = None
