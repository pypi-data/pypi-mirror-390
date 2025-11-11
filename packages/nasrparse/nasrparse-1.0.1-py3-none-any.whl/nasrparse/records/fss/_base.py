from nasrparse.functions import to_nullable_date, to_nullable_string

from nasrparse.records.table_base import TableBase

from datetime import date


class Base(TableBase):
    eff_date: date | None
    """The 28 Day NASR Subscription Effective Date in format 'YYYY/MM/DD'."""
    fss_id: str | None
    """Flight Service Station Identifier"""
    name: str | None
    """Flight Service Station Name"""
    city: str | None
    """Associated City Name"""
    state_code: str | None
    """Associated State Post Office Code standard two letter abbreviation for US States and Territories."""
    country_code: str | None
    """Country Post Office Code"""

    def __init__(
        self,
        table_name: str,
        eff_date: str,
        fss_id: str,
        name: str,
        city: str,
        state_code: str,
        country_code: str,
    ) -> None:
        super().__init__(table_name)
        self.eff_date = to_nullable_date(eff_date, "YYYY/MM/DD")
        self.fss_id = to_nullable_string(fss_id)
        self.name = to_nullable_string(name)
        self.city = to_nullable_string(city)
        self.state_code = to_nullable_string(state_code)
        self.country_code = to_nullable_string(country_code)

    def __repr__(self) -> str:
        return (
            f"EFF_DATE={self.eff_date!r}, "
            f"FSS_ID={self.fss_id!r}, "
            f"NAME={self.name!r}, "
            f"CITY={self.city!r}, "
            f"STATE_CODE={self.state_code!r}, "
            f"COUNTRY_CODE={self.country_code!r}, "
        )

    def ordered_fields(self) -> list:
        return [
            "eff_date",
            "fss_id",
            "name",
            "city",
            "state_code",
            "country_code",
        ]

    def to_dict(self) -> dict:
        return {
            "eff_date": self.eff_date.strftime("%Y-%m-%d") if self.eff_date else None,
            "fss_id": self.fss_id,
            "name": self.name,
            "city": self.city,
            "state_code": self.state_code,
            "country_code": self.country_code,
        }
