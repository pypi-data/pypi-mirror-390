from nasrparse.records.types._base_enum import BaseEnum


class SurveyAccuracyCode(BaseEnum):
    UNKNOWN = "0"
    DEGREE = "1"
    TEN_MINUTES = "2"
    ONE_MINUTE = "3"
    TEN_SECONDS = "4"
    ONE_SECOND_OR_BETTER = "5"
    NOS = "6"
    THIRD_ORDER_TRIANGULATION = "7"
    NULL = None
