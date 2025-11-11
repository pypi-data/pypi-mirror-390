from nasrparse.functions import to_nullable_date, to_nullable_string

from nasrparse.records.table_base import TableBase

from datetime import date


class Base(TableBase):
    eff_date: date | None
    """The 28 Day NASR Subscription Effective Date in format 'YYYY/MM/DD'."""
    location_id: str | None
    """Location Identifier. 3-4 character alphanumeric identifier."""
    location_name: str | None
    """Center Name."""

    def __init__(
        self,
        table_name: str,
        eff_date: str,
        location_id: str,
        location_name: str,
    ) -> None:
        super().__init__(table_name)
        self.eff_date = to_nullable_date(eff_date, "YYYY/MM/DD")
        self.location_id = to_nullable_string(location_id)
        self.location_name = to_nullable_string(location_name)

    def __repr__(self):
        return (
            f"EFF_DATE={self.eff_date!r}, "
            f"LOCATION_ID={self.location_id!r}, "
            f"LOCATION_NAME={self.location_name!r}, "
        )

    def ordered_fields(self) -> list:
        return [
            "eff_date",
            "location_id",
            "location_name",
        ]

    def to_dict(self) -> dict:
        return {
            "eff_date": self.eff_date.strftime("%Y-%m-%d") if self.eff_date else None,
            "location_id": self.location_id,
            "location_name": self.location_name,
        }
