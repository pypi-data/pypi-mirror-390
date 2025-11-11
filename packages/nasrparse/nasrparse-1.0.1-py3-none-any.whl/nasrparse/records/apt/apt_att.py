from nasrparse.functions import to_nullable_int, to_nullable_string

from ._base import Base


class APT_ATT(Base):
    sked_seq_no: int | None
    """Attendance Schedule Sequence Number (A Number which, together with the Site Number, uniquely identifies the Attendance Schedule Component.)"""
    month: str | None
    """Describes the Months that the Facility is Attended. This field may also contain 'UNATNDD' for unattended Facilities."""
    day: str | None
    """Describes the Days of the Week that the Facility is Open"""
    hour: str | None
    """Describes the Hours within the Day that the Facility is Attended"""

    def __init__(
        self,
        eff_date: str,
        site_no: str,
        site_type_code: str,
        state_code: str,
        arpt_id: str,
        city: str,
        country_code: str,
        sked_seq_no: str,
        month: str,
        day: str,
        hour: str,
    ) -> None:
        super().__init__(
            "airport_attendance",
            eff_date,
            site_no,
            site_type_code,
            state_code,
            arpt_id,
            city,
            country_code,
        )
        self.sked_seq_no = to_nullable_int(sked_seq_no)
        self.month = to_nullable_string(month)
        self.day = to_nullable_string(day)
        self.hour = to_nullable_string(hour)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"SKED_SEQ_NO={self.sked_seq_no!r}, "
            f"MONTH={self.month!r}, "
            f"DAY={self.day!r}, "
            f"HOUR={self.hour!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "sked_seq_no",
                "month",
                "day",
                "hour",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "sked_seq_no": self.sked_seq_no,
            "month": self.month,
            "day": self.day,
            "hour": self.hour,
        }
        return {**base_dict, **this_dict}
