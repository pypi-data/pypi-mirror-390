from nasrparse.functions import to_nullable_date, to_nullable_string
from nasrparse.records.types import CommunicationOutletCode, PointCode, RegionCode

from nasrparse.records.table_base import TableBase

from datetime import date


class Base(TableBase):
    eff_date: date | None
    """The 28 Day NASR Subscription Effective Date in format 'YYYY/MM/DD'."""
    comm_loc_id: str | None
    """Communications Outlet Ident. A 3-4 character alphanumeric identifier. COMM_TYPE RCAG do not currently have a 3-4 character identifier stored in NASR."""
    comm_type: CommunicationOutletCode
    """Communication Outlet Type - RCAG, RCO or RCO1. RCAG is a Remote Communications, Air/Ground. RCO and RCO1 are the same and Serve the Same Function; A Remote Communication Outlet. An RCO1 may exist if two separate sites share the same identifier, e.g. one is collocated with a NAVAID, the Other Is Physically on Airport Property."""
    nav_id: str | None
    """Associated NAVAID Ident - Applies to RCO/RCO1 types only."""
    nav_type: PointCode
    """Associated NAVAID Type - Applies to RCO/RCO1 types only."""
    city: str | None
    """Communications Outlet City Name. RCAG do not have an Associated City stored in NASR."""
    state_code: str | None
    """Associated State Code standard two letter abbreviation for US States and Territories."""
    region_code: RegionCode
    """FAA Region responsible for Communications Outlet (code)"""
    country_code: str | None
    """Country Code Communications Outlet is Located."""

    def __init__(
        self,
        table_name: str,
        eff_date: str,
        comm_loc_id: str,
        comm_type: str,
        nav_id: str,
        nav_type: str,
        city: str,
        state_code: str,
        region_code: str,
        country_code: str,
    ) -> None:
        super().__init__(table_name)
        self.eff_date = to_nullable_date(eff_date, "YYYY/MM/DD")
        self.comm_loc_id = to_nullable_string(comm_loc_id)
        self.comm_type = CommunicationOutletCode.from_value(
            to_nullable_string(comm_type)
        )
        self.nav_id = to_nullable_string(nav_id)
        self.nav_type = PointCode.from_value(to_nullable_string(nav_type))
        self.city = to_nullable_string(city)
        self.state_code = to_nullable_string(state_code)
        self.region_code = RegionCode.from_value(to_nullable_string(region_code))
        self.country_code = to_nullable_string(country_code)

    def __repr__(self) -> str:
        return (
            f"EFF_DATE={self.eff_date!r}, "
            f"COMM_LOC_ID={self.comm_loc_id!r}, "
            f"COMM_TYPE={self.comm_type!r}, "
            f"NAV_ID={self.nav_id!r}, "
            f"NAV_TYPE={self.nav_type!r}, "
            f"CITY={self.city!r}, "
            f"STATE_CODE={self.state_code!r}, "
            f"REGION_CODE={self.region_code!r}, "
            f"COUNTRY_CODE={self.country_code!r}, "
        )

    def ordered_fields(self) -> list:
        return [
            "eff_date",
            "comm_loc_id",
            "comm_type",
            "nav_id",
            "nav_type",
            "city",
            "state_code",
            "region_code",
            "country_code",
        ]

    def to_dict(self) -> dict:
        return {
            "eff_date": self.eff_date.strftime("%Y-%m-%d") if self.eff_date else None,
            "comm_loc_id": self.comm_loc_id,
            "comm_type": self.comm_type.value if self.comm_type else None,
            "nav_id": self.nav_id,
            "nav_type": self.nav_type.value if self.nav_type else None,
            "city": self.city,
            "state_code": self.state_code,
            "region_code": self.region_code.value if self.region_code else None,
            "country_code": self.country_code,
        }
