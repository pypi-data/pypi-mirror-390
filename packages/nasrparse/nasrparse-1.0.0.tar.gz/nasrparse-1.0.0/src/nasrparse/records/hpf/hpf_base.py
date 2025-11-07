from nasrparse.functions import to_nullable_int, to_nullable_string
from nasrparse.records.types import DirectionCode, PointCode

from ._base import Base


class HPF_BASE(Base):
    fix_id: str | None
    """Fix with which Holding is Associated."""
    icao_region_code: str | None
    """ICAO Region Code of the Fix with which the Holding is Associated."""
    nav_id: str | None
    """NAVAID with which Holding is Associated."""
    nav_type: PointCode
    """Facility Type of the NAVAID with which the Holding is Associated."""
    hold_direction: DirectionCode
    """Direction of Holding on the NAVAID or Fix"""
    hold_deg_or_crs: str | None
    """Magnetic Bearing, Radial (Degrees) or Course Direction of Holding"""
    azimuth: str | None
    """Azimuth (Degrees Shown Above is a Radial, Course, Bearing, or RNAV Track)"""
    course_inbound_deg: int | None
    """Inbound Course."""
    turn_direction: str | None
    """Turning Direction"""
    leg_length_dist: int | None
    """Leg Length Outbound DME (NM)"""

    def __init__(
        self,
        eff_date: str,
        hp_name: str,
        hp_no: str,
        state_code: str,
        country_code: str,
        fix_id: str,
        icao_region_code: str,
        nav_id: str,
        nav_type: str,
        hold_direction: str,
        hold_deg_or_crs: str,
        azimuth: str,
        course_inbound_deg: str,
        turn_direction: str,
        leg_length_dist: str,
    ) -> None:
        super().__init__(
            "holding_patterns",
            eff_date,
            hp_name,
            hp_no,
            state_code,
            country_code,
        )
        self.fix_id = to_nullable_string(fix_id)
        self.icao_region_code = to_nullable_string(icao_region_code)
        self.nav_id = to_nullable_string(nav_id)
        self.nav_type = PointCode.from_value(to_nullable_string(nav_type))
        self.hold_direction = DirectionCode.from_value(
            to_nullable_string(hold_direction)
        )
        self.hold_deg_or_crs = to_nullable_string(hold_deg_or_crs)
        self.azimuth = to_nullable_string(azimuth)
        self.course_inbound_deg = to_nullable_int(course_inbound_deg)
        self.turn_direction = to_nullable_string(turn_direction)
        self.leg_length_dist = to_nullable_int(leg_length_dist)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"FIX_ID={self.fix_id!r}, "
            f"ICAO_REGION_CODE={self.icao_region_code!r}, "
            f"NAV_ID={self.nav_id!r}, "
            f"NAV_TYPE={self.nav_type!r}, "
            f"HOLD_DIRECTION={self.hold_direction!r}, "
            f"HOLD_DEG_OR_CRS={self.hold_deg_or_crs!r}, "
            f"AZIMUTH={self.azimuth!r}, "
            f"COURSE_INBOUND_DEG={self.course_inbound_deg!r}, "
            f"TURN_DIRECTION={self.turn_direction!r}, "
            f"LEG_LENGTH_DIST={self.leg_length_dist!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "fix_id",
                "icao_region_code",
                "nav_id",
                "nav_type",
                "hold_direction",
                "hold_deg_or_crs",
                "azimuth",
                "course_inbound_deg",
                "turn_direction",
                "leg_length_dist",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "fix_id": self.fix_id,
            "icao_region_code": self.icao_region_code,
            "nav_id": self.nav_id,
            "nav_type": self.nav_type.value if self.nav_type else None,
            "hold_direction": (
                self.hold_direction.value if self.hold_direction else None
            ),
            "hold_deg_or_crs": self.hold_deg_or_crs,
            "azimuth": self.azimuth,
            "course_inbound_deg": self.course_inbound_deg,
            "turn_direction": self.turn_direction,
            "leg_length_dist": self.leg_length_dist,
        }
        return {**base_dict, **this_dict}
