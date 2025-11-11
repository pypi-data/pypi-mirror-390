from ._base_enum import BaseEnum


class InspectionMethodCode(BaseEnum):
    FEDERAL = "F"
    STATE = "S"
    CONTRACTOR = "C"
    PUBLIC_PROGRAM = "1"
    PRIVATE_PROGRAM = "2"
    NULL = None
