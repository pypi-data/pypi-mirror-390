from nasrparse.functions import to_nullable_bool, to_nullable_float, to_nullable_string
from nasrparse.records.types import AltitudeTypeCode, PointCode, SiteTypeCode

from ._base import Base


class PJA_BASE(Base):
    nav_id: str | None
    """NAVAID Facility Identifier with which PJA is Associated."""
    nav_type: PointCode
    """NAVAID Facility Type with which the PJA is Associated."""
    radial: float | None
    """Azimuth (Degrees) From NAVAID (0-359.99)"""
    distance: float | None
    """Distance, In Nautical Miles, From NAVAID"""
    navaid_name: str | None
    """Name of NAVAID with which PJA is Associated."""
    state_code: str | None
    """PJA State Abbreviation (Two-Letter Post Office)"""
    city: str | None
    """PJA Associated City Name"""
    latitude: str | None
    """PJA Latitude (Formatted)"""
    lat_decimal: float | None
    """PJA Latitude in Decimal Format"""
    longitude: str | None
    """PJA Longitude (Formatted)"""
    long_decimal: float | None
    """PJA Longitude in Decimal Format"""
    arpt_id: str | None
    """Landing Facility Identifier with which PJA is Associated."""
    site_no: str | None
    """Site Number of Associated Landing Facility"""
    site_type_code: SiteTypeCode
    """Landing Facility Type Code."""
    drop_zone_name: str | None
    """PJA Drop Zone Name"""
    max_altitude: str | None
    """PJA Maximum Altitude Allowed"""
    max_altitude_type_code: AltitudeTypeCode
    """PJA Maximum Altitude Allowed Type (AGL, MSL, UNR)"""
    pja_radius: float | None
    """PJA Area Radius, in Nautical Miles from Center Point"""
    chart_request_flag: bool | None
    """Sectional Charting Required (Y/N)"""
    publish_criteria: bool | None
    """PJA to be Published in Airport/Facility Directory (Y/N)"""
    description: str | None
    """Additional Descriptive Text for PJA Area"""
    time_of_use: str | None
    """Times of Use Description"""
    fss_id: str | None
    """FSS Ident with which PJA is Associated"""
    fss_name: str | None
    """FSS Name with which PJA is Associated"""
    pja_use: str | None
    """PJA Use Description"""
    volume: str | None
    """PJA Area Volume"""
    pja_user: str | None
    """PJA User Group Name and Description"""
    remark: str | None
    """Remark Text (Free Form Text that further describes a PJA.)"""

    def __init__(
        self,
        eff_date: str,
        pja_id: str,
        nav_id: str,
        nav_type: str,
        radial: str,
        distance: str,
        navaid_name: str,
        state_code: str,
        city: str,
        latitude: str,
        lat_decimal: str,
        longitude: str,
        long_decimal: str,
        arpt_id: str,
        site_no: str,
        site_type_code: str,
        drop_zone_name: str,
        max_altitude: str,
        max_altitude_type_code: str,
        pja_radius: str,
        chart_request_flag: str,
        publish_criteria: str,
        description: str,
        time_of_use: str,
        fss_id: str,
        fss_name: str,
        pja_use: str,
        volume: str,
        pja_user: str,
        remark: str,
    ) -> None:
        super().__init__("parachute_jump_areas", eff_date, pja_id)
        self.nav_id = to_nullable_string(nav_id)
        self.nav_type = PointCode.from_value(to_nullable_string(nav_type))
        self.radial = to_nullable_float(radial)
        self.distance = to_nullable_float(distance)
        self.navaid_name = to_nullable_string(navaid_name)
        self.state_code = to_nullable_string(state_code)
        self.city = to_nullable_string(city)
        self.latitude = to_nullable_string(latitude)
        self.lat_decimal = to_nullable_float(lat_decimal)
        self.longitude = to_nullable_string(longitude)
        self.long_decimal = to_nullable_float(long_decimal)
        self.arpt_id = to_nullable_string(arpt_id)
        self.site_no = to_nullable_string(site_no)
        self.site_type_code = SiteTypeCode.from_value(
            to_nullable_string(site_type_code)
        )
        self.drop_zone_name = to_nullable_string(drop_zone_name)
        self.max_altitude = to_nullable_string(max_altitude)
        self.max_altitude_type_code = AltitudeTypeCode.from_value(
            to_nullable_string(max_altitude_type_code)
        )
        self.pja_radius = to_nullable_float(pja_radius)
        self.chart_request_flag = to_nullable_bool(chart_request_flag)
        self.publish_criteria = to_nullable_bool(publish_criteria)
        self.description = to_nullable_string(description)
        self.time_of_use = to_nullable_string(time_of_use)
        self.fss_id = to_nullable_string(fss_id)
        self.fss_name = to_nullable_string(fss_name)
        self.pja_use = to_nullable_string(pja_use)
        self.volume = to_nullable_string(volume)
        self.pja_user = to_nullable_string(pja_user)
        self.remark = to_nullable_string(remark)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"NAV_ID={self.nav_id!r}, "
            f"NAV_TYPE={self.nav_type!r}, "
            f"RADIAL={self.radial!r}, "
            f"DISTANCE={self.distance!r}, "
            f"NAVAID_NAME={self.navaid_name!r}, "
            f"STATE_CODE={self.state_code!r}, "
            f"CITY={self.city!r}, "
            f"LATITUDE={self.latitude!r}, "
            f"LAT_DECIMAL={self.lat_decimal!r}, "
            f"LONGITUDE={self.longitude!r}, "
            f"LONG_DECIMAL={self.long_decimal!r}, "
            f"ARPT_ID={self.arpt_id!r}, "
            f"SITE_NO={self.site_no!r}, "
            f"SITE_TYPE_CODE={self.site_type_code!r}, "
            f"DROP_ZONE_NAME={self.drop_zone_name!r}, "
            f"MAX_ALTITUDE={self.max_altitude!r}, "
            f"MAX_ALTITUDE_TYPE_CODE={self.max_altitude_type_code!r}, "
            f"PJA_RADIUS={self.pja_radius!r}, "
            f"CHART_REQUEST_FLAG={self.chart_request_flag!r}, "
            f"PUBLISH_CRITERIA={self.publish_criteria!r}, "
            f"DESCRIPTION={self.description!r}, "
            f"TIME_OF_USE={self.time_of_use!r}, "
            f"FSS_ID={self.fss_id!r}, "
            f"FSS_NAME={self.fss_name!r}, "
            f"PJA_USE={self.pja_use!r}, "
            f"VOLUME={self.volume!r}, "
            f"PJA_USER={self.pja_user!r}, "
            f"REMARK={self.remark!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "nav_id",
                "nav_type",
                "radial",
                "distance",
                "navaid_name",
                "state_code",
                "city",
                "latitude",
                "lat_decimal",
                "longitude",
                "long_decimal",
                "arpt_id",
                "site_no",
                "site_type_code",
                "drop_zone_name",
                "max_altitude",
                "max_altitude_type_code",
                "pja_radius",
                "chart_request_flag",
                "publish_criteria",
                "description",
                "time_of_use",
                "fss_id",
                "fss_name",
                "pja_use",
                "volume",
                "pja_user",
                "remark",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "nav_id": self.nav_id,
            "nav_type": self.nav_type.value if self.nav_type else None,
            "radial": self.radial,
            "distance": self.distance,
            "navaid_name": self.navaid_name,
            "state_code": self.state_code,
            "city": self.city,
            "latitude": self.latitude,
            "lat_decimal": self.lat_decimal,
            "longitude": self.longitude,
            "long_decimal": self.long_decimal,
            "arpt_id": self.arpt_id,
            "site_no": self.site_no,
            "site_type_code": (
                self.site_type_code.value if self.site_type_code else None
            ),
            "drop_zone_name": self.drop_zone_name,
            "max_altitude": self.max_altitude,
            "max_altitude_type_code": (
                self.max_altitude_type_code.value
                if self.max_altitude_type_code
                else None
            ),
            "pja_radius": self.pja_radius,
            "chart_request_flag": self.chart_request_flag,
            "publish_criteria": self.publish_criteria,
            "description": self.description,
            "time_of_use": self.time_of_use,
            "fss_id": self.fss_id,
            "fss_name": self.fss_name,
            "pja_use": self.pja_use,
            "volume": self.volume,
            "pja_user": self.pja_user,
            "remark": self.remark,
        }
        return {**base_dict, **this_dict}
