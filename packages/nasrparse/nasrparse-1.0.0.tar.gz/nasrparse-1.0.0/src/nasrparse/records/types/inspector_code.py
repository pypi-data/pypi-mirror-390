from ._base_enum import BaseEnum


class InspectorCode(BaseEnum):
    FAA_PERSONNEL = "F"
    STATE_PERSONNEL = "S"
    CONTRACT_PERSONNEL = "C"
    OWNER = "N"
    NULL = None
