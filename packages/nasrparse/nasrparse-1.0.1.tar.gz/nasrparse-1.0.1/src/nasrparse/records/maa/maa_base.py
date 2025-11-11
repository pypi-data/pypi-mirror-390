from nasrparse.functions import (
    to_nullable_float,
    to_nullable_position,
    to_nullable_string,
)
from nasrparse.records.types import DirectionCode, MAATypeCode, PointCode

from ._base import Base


class MAA_BASE(Base):
    maa_type_name: MAATypeCode
    """Type of Miscellaneous Activity Area"""
    nav_id: str | None
    """NAVAID Facility Identifier with which MAA is Associated."""
    nav_type: PointCode
    """NAVAID Facility Type with which the MAA is Associated."""
    nav_radial: float | None
    """Azimuth (Degrees) From NAVAID (0-359.99)"""
    nav_distance: float | None
    """Distance, In Nautical Miles, From NAVAID"""
    state_code: str | None
    """MAA State Abbreviation (Two-Letter Post Office)"""
    city: str | None
    """MAA Associated City Name"""
    latitude: float | None
    """MAA Latitude (Formatted)"""
    longitude: float | None
    """MAA Longitude (Formatted)"""
    arpt_ids: list[str]
    """LIST of Landing Facility Identifiers with which MAA is Associated."""
    nearest_arpt: str | None
    """Nearest Airport ID Only Applies to Space Launch Activity Areas"""
    nearest_arpt_dist: float | None
    """Nearest Airport Distance in Nautical Miles Only Applies to Space Launch Activity Areas"""
    nearest_arpt_dir: DirectionCode
    """Nearest Airport Direction Only Applies to Space Launch Activity Areas"""
    maa_name: str | None
    """MAA Area Name"""
    max_alt: str | None
    """MAA Maximum Altitude Allowed"""
    min_alt: str | None
    """MAA Minimum Altitude Allowed"""
    maa_radius: float | None
    """MAA Area Radius, in Nautical Miles from Center Point"""
    description: str | None
    """Additional Descriptive Text for MAA Area"""
    maa_use: str | None
    """MAA Use Description"""
    check_notams: str | None
    """Check for NOTAMs Only Applies to Space Launch Activity Areas"""
    time_of_use: str | None
    """Times of Use Description"""
    user_group_name: str | None
    """MAA User Group Name and Description"""

    def __init__(
        self,
        eff_date: str,
        maa_id: str,
        maa_type_name: str,
        nav_id: str,
        nav_type: str,
        nav_radial: str,
        nav_distance: str,
        state_code: str,
        city: str,
        latitude: str,
        longitude: str,
        arpt_ids: str,
        nearest_arpt: str,
        nearest_arpt_dist: str,
        nearest_arpt_dir: str,
        maa_name: str,
        max_alt: str,
        min_alt: str,
        maa_radius: str,
        description: str,
        maa_use: str,
        check_notams: str,
        time_of_use: str,
        user_group_name: str,
    ) -> None:
        super().__init__(
            "misc_activity_areas",
            eff_date,
            maa_id,
        )
        self.maa_type_name = MAATypeCode.from_value(to_nullable_string(maa_type_name))
        self.nav_id = to_nullable_string(nav_id)
        self.nav_type = PointCode.from_value(to_nullable_string(nav_type))
        self.nav_radial = to_nullable_float(nav_radial)
        self.nav_distance = to_nullable_float(nav_distance)
        self.state_code = to_nullable_string(state_code)
        self.city = to_nullable_string(city)
        self.latitude = to_nullable_position(latitude)
        self.longitude = to_nullable_position(longitude)
        arpt_ids_string = to_nullable_string(arpt_ids)
        self.arpt_ids = arpt_ids_string.split() if arpt_ids_string else []
        self.nearest_arpt = to_nullable_string(nearest_arpt)
        self.nearest_arpt_dist = to_nullable_float(nearest_arpt_dist)
        self.nearest_arpt_dir = DirectionCode.from_value(
            to_nullable_string(nearest_arpt_dir)
        )
        self.maa_name = to_nullable_string(maa_name)
        self.max_alt = to_nullable_string(max_alt)
        self.min_alt = to_nullable_string(min_alt)
        self.maa_radius = to_nullable_float(maa_radius)
        self.description = to_nullable_string(description)
        self.maa_use = to_nullable_string(maa_use)
        self.check_notams = to_nullable_string(check_notams)
        self.time_of_use = to_nullable_string(time_of_use)
        self.user_group_name = to_nullable_string(user_group_name)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"MAA_TYPE_NAME={self.maa_type_name!r}, "
            f"NAV_ID={self.nav_id!r}, "
            f"NAV_TYPE={self.nav_type!r}, "
            f"NAV_RADIAL={self.nav_radial!r}, "
            f"NAV_DISTANCE={self.nav_distance!r}, "
            f"STATE_CODE={self.state_code!r}, "
            f"CITY={self.city!r}, "
            f"LATITUDE={self.latitude!r}, "
            f"LONGITUDE={self.longitude!r}, "
            f"ARPT_IDS={self.arpt_ids!r}, "
            f"NEAREST_ARPT={self.nearest_arpt!r}, "
            f"NEAREST_ARPT_DIST={self.nearest_arpt_dist!r}, "
            f"NEAREST_ARPT_DIR={self.nearest_arpt_dir!r}, "
            f"MAA_NAME={self.maa_name!r}, "
            f"MAX_ALT={self.max_alt!r}, "
            f"MIN_ALT={self.min_alt!r}, "
            f"MAA_RADIUS={self.maa_radius!r}, "
            f"DESCRIPTION={self.description!r}, "
            f"MAA_USE={self.maa_use!r}, "
            f"CHECK_NOTAMS={self.check_notams!r}, "
            f"TIME_OF_USE={self.time_of_use!r}, "
            f"USER_GROUP_NAME={self.user_group_name!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "maa_type_name",
                "nav_id",
                "nav_type",
                "nav_radial",
                "nav_distance",
                "state_code",
                "city",
                "latitude",
                "longitude",
                "arpt_ids",
                "nearest_arpt",
                "nearest_arpt_dist",
                "nearest_arpt_dir",
                "maa_name",
                "max_alt",
                "min_alt",
                "maa_radius",
                "description",
                "maa_use",
                "check_notams",
                "time_of_use",
                "user_group_name",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "maa_type_name": self.maa_type_name.value if self.maa_type_name else None,
            "nav_id": self.nav_id,
            "nav_type": self.nav_type.value if self.nav_type else None,
            "nav_radial": self.nav_radial,
            "nav_distance": self.nav_distance,
            "state_code": self.state_code,
            "city": self.city,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "arpt_ids": " ".join(self.arpt_ids),
            "nearest_arpt": self.nearest_arpt,
            "nearest_arpt_dist": self.nearest_arpt_dist,
            "nearest_arpt_dir": (
                self.nearest_arpt_dir.value if self.nearest_arpt_dir else None
            ),
            "maa_name": self.maa_name,
            "max_alt": self.max_alt,
            "min_alt": self.min_alt,
            "maa_radius": self.maa_radius,
            "description": self.description,
            "maa_use": self.maa_use,
            "check_notams": self.check_notams,
            "time_of_use": self.time_of_use,
            "user_group_name": self.user_group_name,
        }
        return {**base_dict, **this_dict}
