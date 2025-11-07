from nasrparse.functions import to_nullable_bool, to_nullable_date, to_nullable_string

from ._base import Base

from datetime import date


class STAR_BASE(Base):
    arrival_name: str | None
    """STAR Name. Name Assigned to the Standard Terminal Arrival."""
    amendment_no: str | None
    """Amendment Number (spelled out) of the STAR that will be Active on the Effective Date."""
    star_amend_eff_date: date | None
    """The First Effective Date for which the STAR Amendment became Active."""
    rnav_flag: bool | None
    """Y/N Flag determines whether a STAR is RNAV required."""
    served_arpt: str | None
    """List of Airports Served by the STAR."""

    def __init__(
        self,
        eff_date: str,
        star_computer_code: str,
        artcc: str,
        arrival_name: str,
        amendment_no: str,
        star_amend_eff_date: str,
        rnav_flag: str,
        served_arpt: str,
    ) -> None:
        super().__init__(
            "arrivals",
            eff_date,
            star_computer_code,
            artcc,
        )
        self.arrival_name = to_nullable_string(arrival_name)
        self.amendment_no = to_nullable_string(amendment_no)
        self.star_amend_eff_date = to_nullable_date(star_amend_eff_date, "YYYY/MM/DD")
        self.rnav_flag = to_nullable_bool(rnav_flag)
        self.served_arpt = to_nullable_string(served_arpt)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"ARRIVAL_NAME={self.arrival_name!r}, "
            f"AMENDMENT_NO={self.amendment_no!r}, "
            f"STAR_AMEND_EFF_DATE={self.star_amend_eff_date!r}, "
            f"RNAV_FLAG={self.rnav_flag!r}, "
            f"SERVED_ARPT={self.served_arpt!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "arrival_name",
                "amendment_no",
                "star_amend_eff_date",
                "rnav_flag",
                "served_arpt",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "arrival_name": self.arrival_name,
            "amendment_no": self.amendment_no,
            "star_amend_eff_date": (
                self.star_amend_eff_date.strftime("%Y-%m-%d")
                if self.star_amend_eff_date
                else None
            ),
            "rnav_flag": self.rnav_flag,
            "served_arpt": self.served_arpt,
        }
        return {**base_dict, **this_dict}
