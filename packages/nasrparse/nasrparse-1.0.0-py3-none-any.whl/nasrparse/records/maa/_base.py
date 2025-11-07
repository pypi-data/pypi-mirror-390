from nasrparse.functions import to_nullable_date, to_nullable_string

from nasrparse.records.table_base import TableBase

from datetime import date


class Base(TableBase):
    eff_date: date | None
    """The 28 Day NASR Subscription Effective Date in format 'YYYY/MM/DD'."""
    maa_id: str | None
    """MAA ID that uniquely identifies a Miscellaneous Activity Area."""

    def __init__(
        self,
        table_name: str,
        eff_date: str,
        maa_id: str,
    ) -> None:
        super().__init__(table_name)
        self.eff_date = to_nullable_date(eff_date, "YYYY/MM/DD")
        self.maa_id = to_nullable_string(maa_id)

    def __repr__(self) -> str:
        return f"EFF_DATE={self.eff_date!r}, " f"MAA_ID={self.maa_id!r}, "

    def ordered_fields(self) -> list:
        return [
            "eff_date",
            "maa_id",
        ]

    def to_dict(self) -> dict:
        return {
            "eff_date": self.eff_date.strftime("%Y-%m-%d") if self.eff_date else None,
            "maa_id": self.maa_id,
        }
