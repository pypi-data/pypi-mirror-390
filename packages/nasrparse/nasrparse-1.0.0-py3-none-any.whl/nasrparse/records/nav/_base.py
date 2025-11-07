from nasrparse.functions import to_nullable_date, to_nullable_string
from nasrparse.records.types import PointCode

from nasrparse.records.table_base import TableBase

from datetime import date


class Base(TableBase):
    eff_date: date | None
    """The 28 Day NASR Subscription Effective Date in format 'YYYY/MM/DD'."""
    nav_id: str | None
    """NAVAID Facility Identifier."""
    nav_type: PointCode
    """NAVAID Facility Type."""
    state_code: str | None
    """Associated State Post Office Code standard two letter abbreviation for US States and Territories."""
    city: str | None
    """NAVAID Associated City Name"""
    country_code: str | None
    """Country Post Office Code NAVAID Located"""

    def __init__(
        self,
        table_name: str,
        eff_date: str,
        nav_id: str,
        nav_type: str,
        state_code: str,
        city: str,
        country_code: str,
    ) -> None:
        super().__init__(table_name)
        self.eff_date = to_nullable_date(eff_date, "YYYY/MM/DD")
        self.nav_id = to_nullable_string(nav_id)
        self.nav_type = PointCode.from_value(to_nullable_string(nav_type))
        self.state_code = to_nullable_string(state_code)
        self.city = to_nullable_string(city)
        self.country_code = to_nullable_string(country_code)

    def __repr__(self) -> str:
        return (
            f"EFF_DATE={self.eff_date!r}, "
            f"NAV_ID={self.nav_id!r}, "
            f"NAV_TYPE={self.nav_type!r}, "
            f"STATE_CODE={self.state_code!r}, "
            f"CITY={self.city!r}, "
            f"COUNTRY_CODE={self.country_code!r}, "
        )

    def ordered_fields(self) -> list:
        return [
            "eff_date",
            "nav_id",
            "nav_type",
            "state_code",
            "city",
            "country_code",
        ]

    def to_dict(self) -> dict:
        return {
            "eff_date": self.eff_date.strftime("%Y-%m-%d") if self.eff_date else None,
            "nav_id": self.nav_id,
            "nav_type": self.nav_type.value if self.nav_type else None,
            "state_code": self.state_code,
            "city": self.city,
            "country_code": self.country_code,
        }
