from nasrparse.functions import to_nullable_date, to_nullable_string
from nasrparse.records.types import SiteTypeCode

from nasrparse.records.table_base import TableBase

from datetime import date


class Base(TableBase):
    eff_date: date | None
    """The 28 Day NASR Subscription Effective Date in format 'YYYY/MM/DD'."""
    site_no: str | None
    """Landing Facility Site Number. A unique identifying number."""
    site_type_code: SiteTypeCode
    """Landing Facility Type Code."""
    state_code: str | None
    """Associated State Post Office Code standard two letter abbreviation for US States and Territories."""
    arpt_id: str | None
    """Location Identifier. Unique 3-4 character alphanumeric identifier assigned to the Landing Facility."""
    city: str | None
    """Airport Associated City Name"""
    country_code: str | None
    """Country Post Office Code Airport Located"""

    def __init__(
        self,
        table_name: str,
        eff_date: str,
        site_no: str,
        site_type_code: str,
        state_code: str,
        arpt_id: str,
        city: str,
        country_code: str,
    ) -> None:
        super().__init__(table_name)
        self.eff_date = to_nullable_date(eff_date, "YYYY/MM/DD")
        self.site_no = to_nullable_string(site_no)
        self.site_type_code = SiteTypeCode.from_value(
            to_nullable_string(site_type_code)
        )
        self.state_code = to_nullable_string(state_code)
        self.arpt_id = to_nullable_string(arpt_id)
        self.city = to_nullable_string(city)
        self.country_code = to_nullable_string(country_code)

    def __repr__(self) -> str:
        return (
            f"EFF_DATE={self.eff_date!r}, "
            f"SITE_NO={self.site_no!r}, "
            f"SITE_TYPE_CODE={self.site_type_code!r}, "
            f"STATE_CODE={self.state_code!r}, "
            f"ARPT_ID={self.arpt_id!r}, "
            f"CITY={self.city!r}, "
            f"COUNTRY_CODE={self.country_code!r}, "
        )

    def ordered_fields(self) -> list:
        return [
            "eff_date",
            "site_no",
            "site_type_code",
            "state_code",
            "arpt_id",
            "city",
            "country_code",
        ]

    def to_dict(self) -> dict:
        return {
            "eff_date": self.eff_date.strftime("%Y-%m-%d") if self.eff_date else None,
            "site_no": self.site_no,
            "site_type_code": (
                self.site_type_code.value if self.site_type_code else None
            ),
            "state_code": self.state_code,
            "arpt_id": self.arpt_id,
            "city": self.city,
            "country_code": self.country_code,
        }
