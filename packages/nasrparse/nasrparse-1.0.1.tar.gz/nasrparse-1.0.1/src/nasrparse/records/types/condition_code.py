from ._base_enum import BaseEnum


class ConditionCode(BaseEnum):
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    FAIR = "FAIR"
    POOR = "POOR"
    FAILED = "FAILED"
    NULL = None
