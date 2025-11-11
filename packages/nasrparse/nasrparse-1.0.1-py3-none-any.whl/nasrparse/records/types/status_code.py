from ._base_enum import BaseEnum


class StatusCode(BaseEnum):
    CLOSED_INDEFINITELY = "CI"
    CLOSED_PERMANENTLY = "CP"
    OPERATIONAL = "O"
    NULL = None
