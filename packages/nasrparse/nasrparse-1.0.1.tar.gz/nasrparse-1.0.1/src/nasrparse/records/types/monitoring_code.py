from ._base_enum import BaseEnum


class MonitoringCode(BaseEnum):
    INTERNAL_PLUS_INDICATOR = "1"
    PILOT_REPORTED = "2"
    INTERNAL_NO_INDICATOR = "3"
    NO_INTERNAL_MONITOR = "4"
    NULL = None
