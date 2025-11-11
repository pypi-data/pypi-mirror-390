from nasrparse.functions import to_nullable_date, to_nullable_int, to_nullable_string

from nasrparse.records.table_base import TableBase

from datetime import date


class Base(TableBase):
    eff_date: date | None
    """The 28 Day NASR Subscription Effective Date in format 'YYYY/MM/DD'."""
    hp_name: str | None
    """Holding Pattern Identifier (NAVAID_NAME FACILITY_TYPE*STATE_CODE) OR (FIX_NAME FIX_TYPE*STATE_CODE*ICAO_REGION_CODE)."""
    hp_no: int | None
    """Pattern Number to Uniquely Identify Holding Pattern"""
    state_code: str | None
    """Associated State Post Office Code standard two letter abbreviation for US States and Territories."""
    country_code: str | None
    """Country Post Office Code"""

    def __init__(
        self,
        table_name: str,
        eff_date: str,
        hp_name: str,
        hp_no: str,
        state_code: str,
        country_code: str,
    ) -> None:
        super().__init__(table_name)
        self.eff_date = to_nullable_date(eff_date, "YYYY/MM/DD")
        self.hp_name = to_nullable_string(hp_name)
        self.hp_no = to_nullable_int(hp_no)
        self.state_code = to_nullable_string(state_code)
        self.country_code = to_nullable_string(country_code)

    def __repr__(self) -> str:
        return (
            f"EFF_DATE={self.eff_date!r}, "
            f"HP_NAME={self.hp_name!r}, "
            f"HP_NO={self.hp_no!r}, "
            f"STATE_CODE={self.state_code!r}, "
            f"COUNTRY_CODE={self.country_code!r}, "
        )

    def ordered_fields(self) -> list:
        return [
            "eff_date",
            "hp_name",
            "hp_no",
            "state_code",
            "country_code",
        ]

    def to_dict(self) -> dict:
        return {
            "eff_date": self.eff_date.strftime("%Y-%m-%d") if self.eff_date else None,
            "hp_name": self.hp_name,
            "hp_no": self.hp_no,
            "state_code": self.state_code,
            "country_code": self.country_code,
        }
