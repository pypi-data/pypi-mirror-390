from nasrparse.functions import to_nullable_bool, to_nullable_date, to_nullable_string

from ._base import Base

from datetime import date


class DP_BASE(Base):
    amendment_no: str | None
    """Amendment Number (spelled out) of the DP that will be Active on the Effective Date."""
    dp_amend_eff_date: date | None
    """The First Effective Date for which the DP Amendment became Active."""
    rnav_flag: bool | None
    """Y/N Flag determines whether a DP is RNAV required."""
    graphical_dp_type: str | None
    """Identifies whether the Graphical DP is type SID or OBSTACLE."""
    served_arpt: str | None
    """List of Airports Served by the DP."""

    def __init__(
        self,
        eff_date: str,
        dp_computer_code: str,
        dp_name: str,
        artcc: str,
        amendment_no: str,
        dp_amend_eff_date: str,
        rnav_flag: str,
        graphical_dp_type: str,
        served_arpt: str,
    ) -> None:
        super().__init__(
            "departure_procedures",
            eff_date,
            dp_computer_code,
            dp_name,
            artcc,
        )
        self.amendment_no = to_nullable_string(amendment_no)
        self.dp_amend_eff_date = to_nullable_date(dp_amend_eff_date, "YYYY/MM/DD")
        self.rnav_flag = to_nullable_bool(rnav_flag)
        self.graphical_dp_type = to_nullable_string(graphical_dp_type)
        self.served_arpt = to_nullable_string(served_arpt)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"AMENDMENT_NO={self.amendment_no!r}, "
            f"DP_AMEND_EFF_DATE={self.dp_amend_eff_date!r}, "
            f"RNAV_FLAG={self.rnav_flag!r}, "
            f"GRAPHICAL_DP_TYPE={self.graphical_dp_type!r}, "
            f"SERVED_ARPT={self.served_arpt!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "amendment_no",
                "dp_amend_eff_date",
                "rnav_flag",
                "graphical_dp_type",
                "served_arpt",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "amendment_no": self.amendment_no,
            "dp_amend_eff_date": (
                self.dp_amend_eff_date.strftime("%Y-%m-%d")
                if self.dp_amend_eff_date
                else None
            ),
            "rnav_flag": self.rnav_flag,
            "graphical_dp_type": self.graphical_dp_type,
            "served_arpt": self.served_arpt,
        }
        return {**base_dict, **this_dict}
