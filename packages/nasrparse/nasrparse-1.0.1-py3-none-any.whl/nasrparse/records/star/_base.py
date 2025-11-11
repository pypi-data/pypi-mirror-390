from nasrparse.functions import to_nullable_date, to_nullable_string

from nasrparse.records.table_base import TableBase

from datetime import date


class Base(TableBase):
    eff_date: date | None
    """The 28 Day NASR Subscription Effective Date in format 'YYYY/MM/DD'."""
    star_computer_code: str | None
    """FAA-Assigned Computer Identifier for the STAR. EX. GLAND.BLUMS5"""
    artcc: str | None
    """List of all Responsible ARTCCs based on Airports Served."""

    def __init__(
        self,
        table_name: str,
        eff_date: str,
        star_computer_code: str,
        artcc: str,
    ) -> None:
        super().__init__(table_name)
        self.eff_date = to_nullable_date(eff_date, "YYYY/MM/DD")
        self.star_computer_code = to_nullable_string(star_computer_code)
        self.artcc = to_nullable_string(artcc)

    def __repr__(self) -> str:
        return (
            f"EFF_DATE={self.eff_date!r}, "
            f"STAR_COMPUTER_CODE={self.star_computer_code!r}, "
            f"ARTCC={self.artcc!r}, "
        )

    def ordered_fields(self) -> list:
        return [
            "eff_date",
            "star_computer_code",
            "artcc",
        ]

    def to_dict(self) -> dict:
        return {
            "eff_date": self.eff_date.strftime("%Y-%m-%d") if self.eff_date else None,
            "star_computer_code": self.star_computer_code,
            "artcc": self.artcc,
        }
