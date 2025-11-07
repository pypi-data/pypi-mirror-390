from nasrparse.functions import to_nullable_date, to_nullable_string

from nasrparse.records.table_base import TableBase

from datetime import date


class Base(TableBase):
    eff_date: date | None
    """The 28 Day NASR Subscription Effective Date in format 'YYYY/MM/DD'."""
    fix_id: str | None
    """Fixed Geographical Position Identifier."""
    icao_region_code: str | None
    """International Civil Aviation Organization (ICAO) Code. In General, the First Letter of an ICAO Code refers to the Country. The Second Letter discerns the Region within the Country."""
    state_code: str | None
    """Associated State Post Office Code standard two letter abbreviation for US States and Territories."""
    country_code: str | None
    """Country Post Office Code"""

    def __init__(
        self,
        table_name: str,
        eff_date: str,
        fix_id: str,
        icao_region_code: str,
        state_code: str,
        country_code: str,
    ) -> None:
        super().__init__(table_name)
        self.eff_date = to_nullable_date(eff_date, "YYYY/MM/DD")
        self.fix_id = to_nullable_string(fix_id)
        self.icao_region_code = to_nullable_string(icao_region_code)
        self.state_code = to_nullable_string(state_code)
        self.country_code = to_nullable_string(country_code)

    def __repr__(self) -> str:
        return (
            f"EFF_DATE={self.eff_date!r}, "
            f"FIX_ID={self.fix_id!r}, "
            f"ICAO_REGION_CODE={self.icao_region_code!r}, "
            f"STATE_CODE={self.state_code!r}, "
            f"COUNTRY_CODE={self.country_code!r}, "
        )

    def ordered_fields(self) -> list:
        return [
            "eff_date",
            "fix_id",
            "icao_region_code",
            "state_code",
            "country_code",
        ]

    def to_dict(self) -> dict:
        return {
            "eff_date": self.eff_date.strftime("%Y-%m-%d") if self.eff_date else None,
            "fix_id": self.fix_id,
            "icao_region_code": self.icao_region_code,
            "state_code": self.state_code,
            "country_code": self.country_code,
        }
