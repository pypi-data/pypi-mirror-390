from nasrparse.functions import to_nullable_date, to_nullable_string
from nasrparse.records.types import AirwayDesignationCode

from ._base import Base

from datetime import date


class AWY_BASE(Base):
    awy_designation: AirwayDesignationCode
    """Airway Designation."""
    update_date: date | None
    """The Last Date for which the AIRWAY Data amended."""
    remark: str | None
    """Remark Text (Free Form Text that further describes a specific Information Item.)"""
    airway_string: str | None
    """List of FIX and NAVAID that make up the AIRWAY in order adapted."""

    def __init__(
        self,
        eff_date: str,
        regulatory: str,
        awy_location: str,
        awy_id: str,
        awy_designation: str,
        update_date: str,
        remark: str,
        airway_string: str,
    ) -> None:
        super().__init__(
            "airways",
            eff_date,
            regulatory,
            awy_location,
            awy_id,
        )
        self.awy_designation = AirwayDesignationCode.from_value(
            to_nullable_string(awy_designation)
        )
        self.update_date = to_nullable_date(update_date, "YYYY/MM/DD")
        self.remark = to_nullable_string(remark)
        self.airway_string = to_nullable_string(airway_string)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"AWY_DESIGNATION={self.awy_designation!r}, "
            f"UPDATE_DATE={self.update_date!r}, "
            f"REMARK={self.remark!r}, "
            f"AIRWAY_STRING={self.airway_string!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "awy_designation",
                "update_date",
                "remark",
                "airway_string",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "awy_designation": (
                self.awy_designation.value if self.awy_designation else None
            ),
            "update_date": (
                self.update_date.strftime("%Y-%m-%d") if self.update_date else None
            ),
            "remark": self.remark,
            "airway_string": self.airway_string,
        }
        return {**base_dict, **this_dict}
