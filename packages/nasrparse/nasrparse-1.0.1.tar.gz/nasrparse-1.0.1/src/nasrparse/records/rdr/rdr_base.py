from nasrparse.functions import to_nullable_int, to_nullable_string
from nasrparse.records.types import RadarTypeCode

from ._base import Base


class RDR_BASE(Base):
    radar_type: RadarTypeCode
    """RADAR Type Code."""
    radar_no: int | None
    """Unique Sequence Number assigned to each Radar at a Facility."""
    radar_hrs: str | None
    """RADAR Hours of Operation."""
    remark: str | None
    """Remark associated with RADAR Operations."""

    def __init__(
        self,
        eff_date: str,
        facility_id: str,
        facility_type: str,
        state_code: str,
        country_code: str,
        radar_type: str,
        radar_no: str,
        radar_hrs: str,
        remark: str,
    ) -> None:
        super().__init__(
            "radar_sites",
            eff_date,
            facility_id,
            facility_type,
            state_code,
            country_code,
        )
        self.radar_type = RadarTypeCode.from_value(to_nullable_string(radar_type))
        self.radar_no = to_nullable_int(radar_no)
        self.radar_hrs = to_nullable_string(radar_hrs)
        self.remark = to_nullable_string(remark)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"RADAR_TYPE={self.radar_type!r}, "
            f"RADAR_NO={self.radar_no!r}, "
            f"RADAR_HRS={self.radar_hrs!r}, "
            f"REMARK={self.remark!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "radar_type",
                "radar_no",
                "radar_hrs",
                "remark",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "radar_type": self.radar_type.value if self.radar_type else None,
            "radar_no": self.radar_no,
            "radar_hrs": self.radar_hrs,
            "remark": self.remark,
        }
        return {**base_dict, **this_dict}
