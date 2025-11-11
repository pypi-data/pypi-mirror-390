from ._base_enum import BaseEnum


class MTRAgencyTypeCode(BaseEnum):
    ORIGINATING = "O"
    SCHEDULING_1 = "S1"
    SCHEDULING_2 = "S2"
    SCHEDULING_3 = "S3"
    SCHEDULING_4 = "S4"
    NULL = None
