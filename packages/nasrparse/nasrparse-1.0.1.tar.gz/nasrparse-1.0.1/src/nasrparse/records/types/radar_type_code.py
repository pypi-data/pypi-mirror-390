from ._base_enum import BaseEnum


class RadarTypeCode(BaseEnum):
    AIR_ROUTE_SURVEILLANCE_RADAR = "ARSR"
    AIRPORT_SURVEILLANCE_RADAR = "ASR"
    ASR_WITH_PAR = "ASR_PAR"
    BEACON = "BCN"  # Not included in the definition file, but in the CSV data; this is the only translation in the FAA reference, even though it doesn't make sense.
    GROUND_CONTROL_APPROACH = "GCA"
    PRECISION_APPROACH_RADAR = "PAR"
    SECONDARY_RADAR = "SECRA"
    NULL = None
