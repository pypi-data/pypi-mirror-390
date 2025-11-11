from ._base_enum import BaseEnum


class CommunicationStatusCode(BaseEnum):
    OPERATIONAL_IFR = "A"
    TO_BE_COMMISSIONED = "Q"
    DECOMMISSIONED = "Z"
    NULL = None
