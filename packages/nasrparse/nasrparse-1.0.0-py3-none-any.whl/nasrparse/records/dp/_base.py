from nasrparse.functions import to_nullable_date, to_nullable_string

from nasrparse.records.table_base import TableBase

from datetime import date


class Base(TableBase):
    eff_date: date | None
    """The 28 Day NASR Subscription Effective Date in format 'YYYY/MM/DD'."""
    dp_computer_code: str | None
    """FAA-Assigned Computer Identifier for the DP. EX. ADELL6.ADELL"""
    dp_name: str | None
    """Name Assigned to the Departure Procedure."""
    artcc: str | None
    """List of all Responsible ARTCCs based on Airports Served."""

    def __init__(
        self,
        table_name: str,
        eff_date: str,
        dp_computer_code: str,
        dp_name: str,
        artcc: str,
    ) -> None:
        super().__init__(table_name)
        self.eff_date = to_nullable_date(eff_date, "YYYY/MM/DD")
        self.dp_computer_code = to_nullable_string(dp_computer_code)
        self.dp_name = to_nullable_string(dp_name)
        self.artcc = to_nullable_string(artcc)

    def __repr__(self) -> str:
        return (
            f"EFF_DATE={self.eff_date!r}, "
            f"DP_COMPUTER_CODE={self.dp_computer_code!r}, "
            f"DP_NAME={self.dp_name!r}, "
            f"ARTCC={self.artcc!r}, "
        )

    def ordered_fields(self) -> list:
        return [
            "eff_date",
            "dp_computer_code",
            "dp_name",
            "artcc",
        ]

    def to_dict(self) -> dict:
        return {
            "eff_date": self.eff_date.strftime("%Y-%m-%d") if self.eff_date else None,
            "dp_computer_code": self.dp_computer_code,
            "dp_name": self.dp_name,
            "artcc": self.artcc,
        }
