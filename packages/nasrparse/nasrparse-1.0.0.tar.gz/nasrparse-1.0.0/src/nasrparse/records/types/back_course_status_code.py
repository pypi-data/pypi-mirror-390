from ._base_enum import BaseEnum


class BackCourseStatusCode(BaseEnum):
    NO_RESTRICTIONS = "N"
    RESTRICTED = "R"
    UNUSABLE = "U"
    USABLE = "Y"
    NULL = None
