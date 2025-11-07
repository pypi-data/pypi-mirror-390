from nasrparse.functions import to_nullable_date, to_nullable_string

from nasrparse.records.table_base import TableBase

from datetime import date


class Base(TableBase):
    eff_date: date | None
    """The 28 Day NASR Subscription Effective Date in format 'YYYY/MM/DD'."""
    pja_id: str | None
    """PJA ID that uniquely identifies a Parachute Jump Area."""

    def __init__(
        self,
        table_name: str,
        eff_date: str,
        pja_id: str,
    ) -> None:
        super().__init__(table_name)
        self.eff_date = to_nullable_date(eff_date, "YYYY/MM/DD")
        self.pja_id = to_nullable_string(pja_id)

    def __repr__(self):
        return f"EFF_DATE={self.eff_date!r}, " f"PJA_ID={self.pja_id!r}, "

    def ordered_fields(self) -> list:
        return [
            "eff_date",
            "pja_id",
        ]

    def to_dict(self) -> dict:
        return {
            "eff_date": self.eff_date.strftime("%Y-%m-%d") if self.eff_date else None,
            "pja_id": self.pja_id,
        }
