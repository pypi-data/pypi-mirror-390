from nasrparse.functions.record import to_nullable_string
from nasrparse.records.types import ArrestDeviceCode

from ._base import Base


class APT_ARS(Base):
    rwy_id: str | None
    """Runway Identification"""
    rwy_end_id: str | None
    """Runway End Identifier (The Runway End described by the Arresting System Information.)"""
    arrest_device_code: ArrestDeviceCode
    """Type of Aircraft Arresting Device (Indicates Type of Jet Arresting Barrier installed at the Far End.)"""

    def __init__(
        self,
        eff_date: str,
        site_no: str,
        site_type_code: str,
        state_code: str,
        arpt_id: str,
        city: str,
        country_code: str,
        rwy_id: str,
        rwy_end_id: str,
        arrest_device_code: str,
    ) -> None:
        super().__init__(
            "airport_arresting",
            eff_date,
            site_no,
            site_type_code,
            state_code,
            arpt_id,
            city,
            country_code,
        )
        self.rwy_id = to_nullable_string(rwy_id)
        self.rwy_end_id = to_nullable_string(rwy_end_id)
        self.arrest_device_code = ArrestDeviceCode.from_value(
            to_nullable_string(arrest_device_code)
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"RWY_ID={self.rwy_id!r}, "
            f"RWY_END_ID={self.rwy_end_id!r}, "
            f"ARREST_DEVICE_CODE={self.arrest_device_code.value!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "rwy_id",
                "rwy_end_id",
                "arrest_device_code",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "rwy_id": self.rwy_id,
            "rwy_end_id": self.rwy_end_id,
            "arrest_device_code": (
                self.arrest_device_code.value if self.arrest_device_code else None
            ),
        }
        return {**base_dict, **this_dict}
