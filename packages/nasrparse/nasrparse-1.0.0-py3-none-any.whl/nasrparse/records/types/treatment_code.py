from nasrparse.records.types._base_enum import BaseEnum


class TreatmentCode(BaseEnum):
    GROOVED = "GRVD"
    POROUS_FRICTION_COURSE = "PFC"
    AGGREGATE_FRICTION_SEAL_COAT = "AFSC"
    RUBBERIZED_FRICTION_SEAL_COAT = "RFSC"
    WIRE_COMB = "WC"
    NONE = "NONE"
    NULL = None
