from nasrparse.functions import to_nullable_bool, to_nullable_date, to_nullable_string
from nasrparse.records.types import AirwayLocationCode

from nasrparse.records.table_base import TableBase

from datetime import date


class Base(TableBase):
    eff_date: date | None
    """The 28 Day NASR Subscription Effective Date in format ‘YYYY/MM/DD’."""
    regulatory: bool | None
    """Identifies Airways published under 14 CFR (Code of Federal Regulation) Part-71 and Part-95."""
    awy_location: AirwayLocationCode
    """Airway Type which identifies the General Location of the Airway."""
    awy_id: str | None
    """Airway Identifier."""

    def __init__(
        self,
        table_name: str,
        eff_date: str,
        regulatory: str,
        awy_location: str,
        awy_id: str,
    ) -> None:
        super().__init__(table_name)
        self.eff_date = to_nullable_date(eff_date, "YYYY/MM/DD")
        self.regulatory = to_nullable_bool(regulatory)
        self.awy_location = AirwayLocationCode.from_value(
            to_nullable_string(awy_location)
        )
        self.awy_id = to_nullable_string(awy_id)

    def __repr__(self) -> str:
        return (
            f"EFF_DATE={self.eff_date!r}, "
            f"REGULATORY={self.regulatory!r}, "
            f"AWY_LOCATION={self.awy_location!r}, "
            f"AWY_ID={self.awy_id!r}, "
        )

    def ordered_fields(self) -> list:
        return [
            "eff_date",
            "regulatory",
            "awy_location",
            "awy_id",
        ]

    def to_dict(self) -> dict:
        return {
            "eff_date": self.eff_date.strftime("%Y-%m-%d") if self.eff_date else None,
            "regulatory": self.regulatory,
            "awy_location": self.awy_location.value if self.awy_location else None,
            "awy_id": self.awy_id,
        }
