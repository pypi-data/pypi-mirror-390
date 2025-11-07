from ._base_enum import BaseEnum


class OwnershipCode(BaseEnum):
    PUBLIC = "PU"
    PRIVATE = "PR"
    AIR_FORCE = "MA"
    NAVY = "MN"
    ARMY = "MR"
    COAST_GUARD = "CG"
    NULL = None
