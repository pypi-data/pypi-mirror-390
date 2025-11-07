from nasrparse.functions import to_nullable_date, to_nullable_string
from nasrparse.records.types import FacilityTypeCode, SiteTypeCode

from nasrparse.records.table_base import TableBase

from datetime import date


class Base(TableBase):
    eff_date: date | None
    """The 28 Day NASR Subscription Effective Date in format 'YYYY/MM/DD'."""
    site_no: str | None
    """Landing Facility Site Number. A unique identifying number. Not applicable to TRACON, ARTCC or CERAP"""
    site_type_code: SiteTypeCode
    """Facility Type Code"""
    facility_type: FacilityTypeCode
    """Facility Type"""
    state_code: str | None
    """Associated State Post Office Code standard two letter abbreviation for US States and Territories"""
    facility_id: str | None
    """Location Identifier. Unique 3-4 character alphanumeric identifier assigned to the Landing Facility or TRACON"""
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
        facility_type: str,
        state_code: str,
        facility_id: str,
        city: str,
        country_code: str,
    ):
        super().__init__(table_name)
        self.eff_date = to_nullable_date(eff_date, "YYYY/MM/DD")
        self.site_no = to_nullable_string(site_no)
        self.site_type_code = SiteTypeCode.from_value(
            to_nullable_string(site_type_code)
        )
        self.facility_type = FacilityTypeCode.from_value(
            to_nullable_string(facility_type)
        )
        self.state_code = to_nullable_string(state_code)
        self.facility_id = to_nullable_string(facility_id)
        self.city = to_nullable_string(city)
        self.country_code = to_nullable_string(country_code)

    def __repr__(self) -> str:
        return (
            f"EFF_DATE={self.eff_date!r}, "
            f"SITE_NO={self.site_no!r}, "
            f"SITE_TYPE_CODE={self.site_type_code!r}, "
            f"FACILITY_TYPE={self.facility_type!r}, "
            f"STATE_CODE={self.state_code!r}, "
            f"FACILITY_ID={self.facility_id!r}, "
            f"CITY={self.city!r}, "
            f"COUNTRY_CODE={self.country_code!r}, "
        )

    def ordered_fields(self) -> list:
        return [
            "eff_date",
            "site_no",
            "site_type_code",
            "facility_type",
            "state_code",
            "facility_id",
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
            "facility_type": self.facility_type.value if self.facility_type else None,
            "state_code": self.state_code,
            "facility_id": self.facility_id,
            "city": self.city,
            "country_code": self.country_code,
        }
