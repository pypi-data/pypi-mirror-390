from nasrparse.functions import to_nullable_date, to_nullable_string

from nasrparse.records.table_base import TableBase

from datetime import date


class Base(TableBase):
    eff_date: date | None
    """The 28 Day NASR Subscription Effective Date in format 'YYYY/MM/DD'."""
    facility: str | None
    """Contains FACILITY ID except for FACILITY TYPE AFIS, CTAF, GCO, UNICOM and RCAG which do not contain FACILITY IDs in NASR. The FACILITY NAME is used for RCAG sites. AFIS, CTAF, GCO and UNICOM are NULL since they do not contain either a FACILITY ID or FACILITY NAME in NASR."""
    fac_name: str | None
    """Official Facility Name. AFIS, CTAF, GCO and UNICOM FACILITY TYPEs are NULL since they do not contain either a FACILITY ID or FACILITY NAME in NASR. ASOS/AWOS FACILITY TYPEs are NULL since they do not contain a FACILITY NAME in NASR."""
    facility_type: str | None
    """All records contain a FACILITY TYPE. Please note that RCO or RCO1 both are the same and serve the same function; a remote communication outlet. An RCO1 may exist if two separate sites share the same identifier, e.g. one is collocated with a NAVAID and the other is physically on airport property."""

    def __init__(
        self,
        table_name: str,
        eff_date: str,
        facility: str,
        fac_name: str,
        facility_type: str,
    ) -> None:
        super().__init__(table_name)
        self.eff_date = to_nullable_date(eff_date, "YYYY/MM/DD")
        self.facility = to_nullable_string(facility)
        self.fac_name = to_nullable_string(fac_name)
        self.facility_type = to_nullable_string(facility_type)

    def __repr__(self) -> str:
        return (
            f"EFF_DATE={self.eff_date!r}, "
            f"FACILITY={self.facility!r}, "
            f"FAC_NAME={self.fac_name!r}, "
            f"FACILITY_TYPE={self.facility_type!r}, "
        )

    def ordered_fields(self) -> list:
        return [
            "eff_date",
            "facility",
            "fac_name",
            "facility_type",
        ]

    def to_dict(self) -> dict:
        return {
            "eff_date": self.eff_date.strftime("%Y-%m-%d") if self.eff_date else None,
            "facility": self.facility,
            "fac_name": self.fac_name,
            "facility_type": self.facility_type,
        }
