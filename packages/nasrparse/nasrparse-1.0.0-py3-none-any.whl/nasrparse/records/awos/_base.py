from nasrparse.functions import to_nullable_date, to_nullable_string

from nasrparse.records.table_base import TableBase

from datetime import date


class Base(TableBase):
    eff_date: date | None
    """The 28 Day NASR Subscription Effective Date in format 'YYYY/MM/DD'."""
    asos_awos_id: str | None
    """Weather System Identifier. Unique 3-4 character alphanumeric identifier."""
    asos_awos_type: str | None
    """Weather System Type."""
    state_code: str | None
    """Associated State Code standard two letter abbreviation for US States and Territories."""
    city: str | None
    """Weather System associated City Name."""
    country_code: str | None
    """Country Code Weather System is Located."""

    def __init__(
        self,
        table_name: str,
        eff_date: str,
        asos_awos_id: str,
        asos_awos_type: str,
        state_code: str,
        city: str,
        country_code: str,
    ) -> None:
        super().__init__(table_name)
        self.eff_date = to_nullable_date(eff_date, "YYYY/MM/DD")
        self.asos_awos_id = to_nullable_string(asos_awos_id)
        self.asos_awos_type = to_nullable_string(asos_awos_type)
        self.state_code = to_nullable_string(state_code)
        self.city = to_nullable_string(city)
        self.country_code = to_nullable_string(country_code)

    def __repr__(self) -> str:
        return (
            f"EFF_DATE={self.eff_date!r}, "
            f"ASOS_AWOS_ID={self.asos_awos_id!r}, "
            f"ASOS_AWOS_TYPE={self.asos_awos_type!r}, "
            f"STATE_CODE={self.state_code!r}, "
            f"CITY={self.city!r}, "
            f"COUNTRY_CODE={self.country_code!r}, "
        )

    def ordered_fields(self) -> list:
        return [
            "eff_date",
            "asos_awos_id",
            "asos_awos_type",
            "state_code",
            "city",
            "country_code",
        ]

    def to_dict(self) -> dict:
        return {
            "eff_date": self.eff_date.strftime("%Y-%m-%d") if self.eff_date else None,
            "asos_awos_id": self.asos_awos_id,
            "asos_awos_type": self.asos_awos_type,
            "state_code": self.state_code,
            "city": self.city,
            "country_code": self.country_code,
        }
