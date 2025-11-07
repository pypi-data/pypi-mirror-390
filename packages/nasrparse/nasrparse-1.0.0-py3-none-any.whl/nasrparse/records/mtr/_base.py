from nasrparse.functions import to_nullable_date, to_nullable_string
from nasrparse.records.types import MilRouteTypeCode

from nasrparse.records.table_base import TableBase

from datetime import date


class Base(TableBase):
    eff_date: date | None
    """The 28 Day NASR Subscription Effective Date in format 'YYYY/MM/DD'."""
    route_type_code: MilRouteTypeCode
    """MTR Type Code."""
    route_id: str | None
    """Route Identifier. Along with the ROUTE_TYPE_CODE creates a unique MTR identifier."""
    artcc: str | None
    """List of ARTCC Idents that MTR traverses."""

    def __init__(
        self,
        table_name: str,
        eff_date: str,
        route_type_code: str,
        route_id: str,
        artcc: str,
    ) -> None:
        super().__init__(table_name)
        self.eff_date = to_nullable_date(eff_date, "YYYY/MM/DD")
        self.route_type_code = MilRouteTypeCode.from_value(
            to_nullable_string(route_type_code)
        )
        self.route_id = to_nullable_string(route_id)
        self.artcc = to_nullable_string(artcc)

    def __repr__(self) -> str:
        return (
            f"EFF_DATE={self.eff_date!r}, "
            f"ROUTE_TYPE_CODE={self.route_type_code!r}, "
            f"ROUTE_ID={self.route_id!r}, "
            f"ARTCC={self.artcc!r}, "
        )

    def ordered_fields(self) -> list:
        return [
            "eff_date",
            "route_type_code",
            "route_id",
            "artcc",
        ]

    def to_dict(self) -> dict:
        return {
            "eff_date": self.eff_date.strftime("%Y-%m-%d") if self.eff_date else None,
            "route_type_code": (
                self.route_type_code.value if self.route_type_code else None
            ),
            "route_id": self.route_id,
            "artcc": self.artcc,
        }
