from ._base_enum import BaseEnum


class RVRCode(BaseEnum):
    TOUCHDOWN = "T"
    MIDFIELD = "M"
    ROLLOUT = "R"
    NONE = "N"
    TOUCHDOWN_MIDFIELD = "TM"
    TOUCHDOWN_ROLLOUT = "TR"
    MIDFIELD_ROLLOUT = "MR"
    TOUCHDOWN_MIDFIELD_ROLLOUT = "TMR"
    NULL = None
