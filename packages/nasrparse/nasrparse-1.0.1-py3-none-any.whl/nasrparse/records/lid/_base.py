from nasrparse.functions import to_nullable_date, to_nullable_string
from nasrparse.records.types import RegionCode

from nasrparse.records.table_base import TableBase

from datetime import date


class Base(TableBase):
    eff_date: date | None
    """The 28 Day NASR Subscription Effective Date in format 'YYYY/MM/DD'."""
    country_code: str | None
    """Country Code Associated with The Location Identifier."""
    loc_id: str | None
    """Location Identifier. 3-4 character alphanumeric identifier."""
    region_code: RegionCode
    """FAA Region Code Associated with The Location Identifier"""
    state_code: str | None
    """Associated State Code standard two letter abbreviation for US States and Territories."""
    city: str | None
    """City Name Associated with The Location Identifier."""

    def __init__(
        self,
        table_name: str,
        eff_date: str,
        country_code: str,
        loc_id: str,
        region_code: str,
        state_code: str,
        city: str,
    ) -> None:
        super().__init__(table_name)
        self.eff_date = to_nullable_date(eff_date, "YYYY/MM/DD")
        self.country_code = to_nullable_string(country_code)
        self.loc_id = to_nullable_string(loc_id)
        self.region_code = RegionCode.from_value(to_nullable_string(region_code))
        self.state_code = to_nullable_string(state_code)
        self.city = to_nullable_string(city)

    def __repr__(self) -> str:
        return (
            f"EFF_DATE={self.eff_date!r}, "
            f"COUNTRY_CODE={self.country_code!r}, "
            f"LOC_ID={self.loc_id!r}, "
            f"REGION_CODE={self.region_code!r}, "
            f"STATE_CODE={self.state_code!r}, "
            f"CITY={self.city!r}, "
        )

    def ordered_fields(self) -> list:
        return [
            "eff_date",
            "country_code",
            "loc_id",
            "region_code",
            "state_code",
            "city",
        ]

    def to_dict(self) -> dict:
        return {
            "eff_date": self.eff_date.strftime("%Y-%m-%d") if self.eff_date else None,
            "country_code": self.country_code,
            "loc_id": self.loc_id,
            "region_code": self.region_code.value if self.region_code else None,
            "state_code": self.state_code,
            "city": self.city,
        }
