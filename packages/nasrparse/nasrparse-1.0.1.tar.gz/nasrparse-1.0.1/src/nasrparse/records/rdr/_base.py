from nasrparse.functions import to_nullable_date, to_nullable_string
from nasrparse.records.types import RadarFacilityTypeCode

from nasrparse.records.table_base import TableBase

from datetime import date


class Base(TableBase):
    eff_date: date | None
    """The 28 Day NASR Subscription Effective Date in format 'YYYY/MM/DD'."""
    facility_id: str | None
    """Location Identifier. Unique 3-4 character alphanumeric identifier assigned to the Landing Facility or TRACON."""
    facility_type: RadarFacilityTypeCode
    """Type of Facility associated with the RADAR data - either AIRPORT or TRACON."""
    state_code: str | None
    """Associated State Post Office Code standard two letter abbreviation for US States and Territories."""
    country_code: str | None
    """Country Post Office Code Airport or TRACON is Located."""

    def __init__(
        self,
        table_name: str,
        eff_date: str,
        facility_id: str,
        facility_type: str,
        state_code: str,
        country_code: str,
    ) -> None:
        super().__init__(table_name)
        self.eff_date = to_nullable_date(eff_date, "YYYY/MM/DD")
        self.facility_id = to_nullable_string(facility_id)
        self.facility_type = RadarFacilityTypeCode.from_value(
            to_nullable_string(facility_type)
        )
        self.state_code = to_nullable_string(state_code)
        self.country_code = to_nullable_string(country_code)

    def __repr__(self) -> str:
        return (
            f"EFF_DATE={self.eff_date!r}, "
            f"FACILITY_ID={self.facility_id!r}, "
            f"FACILITY_TYPE={self.facility_type!r}, "
            f"STATE_CODE={self.state_code!r}, "
            f"COUNTRY_CODE={self.country_code!r}, "
        )

    def ordered_fields(self) -> list:
        return [
            "eff_date",
            "facility_id",
            "facility_type",
            "state_code",
            "country_code",
        ]

    def to_dict(self) -> dict:
        return {
            "eff_date": self.eff_date.strftime("%Y-%m-%d") if self.eff_date else None,
            "facility_id": self.facility_id,
            "facility_type": self.facility_type.value if self.facility_type else None,
            "state_code": self.state_code,
            "country_code": self.country_code,
        }
