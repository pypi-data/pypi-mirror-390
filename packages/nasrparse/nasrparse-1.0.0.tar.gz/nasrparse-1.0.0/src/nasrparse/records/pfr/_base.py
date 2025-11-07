from nasrparse.functions import to_nullable_date, to_nullable_int, to_nullable_string
from nasrparse.records.types import PrefRouteTypeCode

from nasrparse.records.table_base import TableBase

from datetime import date


class Base(TableBase):
    eff_date: date | None
    """The 28 Day NASR Subscription Effective Date in format 'YYYY/MM/DD'."""
    origin_id: str | None
    """Origin Facility Location Identifier (Depending on NAR Type and Direction, Origin ID Is either Coastal Fix or Inland NAV Facility or Fix)"""
    dstn_id: str | None
    """Destination Facility Location Identifier (Depending on NAR Type and Direction, Destination ID Is either Airport, Coastal Fix or Inland NAV Facility or Fix)"""
    pfr_type_code: PrefRouteTypeCode
    """Type Code of Preferred Route Description."""
    route_no: int | None
    """Route Identifier Sequence Number (1-99)"""

    def __init__(
        self,
        table_name: str,
        eff_date: str,
        origin_id: str,
        dstn_id: str,
        pfr_type_code: str,
        route_no: str,
    ) -> None:
        super().__init__(table_name)
        self.eff_date = to_nullable_date(eff_date, "YYYY/MM/DD")
        self.origin_id = to_nullable_string(origin_id)
        self.dstn_id = to_nullable_string(dstn_id)
        self.pfr_type_code = PrefRouteTypeCode.from_value(
            to_nullable_string(pfr_type_code)
        )
        self.route_no = to_nullable_int(route_no)

    def __repr__(self) -> str:
        return (
            f"EFF_DATE={self.eff_date!r}, "
            f"ORIGIN_ID={self.origin_id!r}, "
            f"DSTN_ID={self.dstn_id!r}, "
            f"PFR_TYPE_CODE={self.pfr_type_code!r}, "
            f"ROUTE_NO={self.route_no!r}, "
        )

    def ordered_fields(self) -> list:
        return [
            "eff_date",
            "origin_id",
            "dstn_id",
            "pfr_type_code",
            "route_no",
        ]

    def to_dict(self) -> dict:
        return {
            "eff_date": self.eff_date.strftime("%Y-%m-%d") if self.eff_date else None,
            "origin_id": self.origin_id,
            "dstn_id": self.dstn_id,
            "pfr_type_code": self.pfr_type_code.value if self.pfr_type_code else None,
            "route_no": self.route_no,
        }
