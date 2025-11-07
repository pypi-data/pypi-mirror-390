from nasrparse.functions import (
    to_nullable_date,
    to_nullable_float,
    to_nullable_int,
    to_nullable_string,
)
from nasrparse.records.types import (
    BackCourseStatusCode,
    HemisCode,
    RegionCode,
    PositionSourceCode,
)

from ._base import Base

from datetime import date


class ILS_BASE(Base):
    state_name: str | None
    """Associated State Name"""
    region_code: RegionCode
    """FAA Region responsible for NAVAID (code)"""
    rwy_len: int | None
    """ILS Runway Length in Whole Feet"""
    rwy_width: int | None
    """ILS Runway Width in Whole Feet"""
    category: str | None
    """Category of the ILS"""
    owner: str | None
    """A Concatenation of the ILS OWNER CODE - ILS OWNER NAME"""
    operator: str | None
    """A Concatenation of the ILS OPERATOR CODE - ILS OPERATOR NAME"""
    apch_bear: float | None
    """ILS Approach Bearing in Degrees Magnetic"""
    mag_var: int | None
    """Magnetic Variation Degrees"""
    mag_var_hemis: HemisCode
    """Magnetic Variation Direction"""
    component_status: str | None
    """Operational Status of Localizer"""
    component_status_date: date | None
    """Effective Date of Localizer Operational Status"""
    lat_deg: int | None
    """Localizer Antenna Latitude Degrees"""
    lat_min: int | None
    """Localizer Antenna Latitude Minutes"""
    lat_sec: float | None
    """Localizer Antenna Latitude Seconds"""
    lat_hemis: HemisCode
    """Localizer Antenna Latitude Hemisphere"""
    lat_decimal: float | None
    """Localizer Antenna Latitude in Decimal Format"""
    lon_deg: int | None
    """Localizer Antenna Longitude Degrees"""
    lon_min: int | None
    """Localizer Antenna Longitude Minutes"""
    lon_sec: float | None
    """Localizer Antenna Longitude Seconds"""
    lon_hemis: HemisCode
    """Localizer Antenna Longitude Hemisphere"""
    lon_decimal: float | None
    """Localizer Antenna Longitude in Decimal Format"""
    lat_lon_source_code: PositionSourceCode
    """Code Indication Source of Latitude/Longitude Information"""
    site_elevation: float | None
    """Site Elevation of Localizer Antenna in Tenth of a Foot (MSL)."""
    loc_freq: str | None
    """Localizer Frequency (MHZ)"""
    bk_course_status_code: BackCourseStatusCode
    """Localizer Back Course Status"""

    def __init__(
        self,
        eff_date: str,
        site_no: str,
        site_type_code: str,
        state_code: str,
        arpt_id: str,
        city: str,
        country_code: str,
        rwy_end_id: str,
        ils_loc_id: str,
        system_type_code: str,
        state_name: str,
        region_code: str,
        rwy_len: str,
        rwy_width: str,
        category: str,
        owner: str,
        operator: str,
        apch_bear: str,
        mag_var: str,
        mag_var_hemis: str,
        component_status: str,
        component_status_date: str,
        lat_deg: str,
        lat_min: str,
        lat_sec: str,
        lat_hemis: str,
        lat_decimal: str,
        lon_deg: str,
        lon_min: str,
        lon_sec: str,
        lon_hemis: str,
        lon_decimal: str,
        lat_lon_source_code: str,
        site_elevation: str,
        loc_freq: str,
        bk_course_status_code: str,
    ) -> None:
        super().__init__(
            "ils_installations",
            eff_date,
            site_no,
            site_type_code,
            state_code,
            arpt_id,
            city,
            country_code,
            rwy_end_id,
            ils_loc_id,
            system_type_code,
        )
        self.state_name = to_nullable_string(state_name)
        self.region_code = RegionCode.from_value(to_nullable_string(region_code))
        self.rwy_len = to_nullable_int(rwy_len)
        self.rwy_width = to_nullable_int(rwy_width)
        self.category = to_nullable_string(category)
        self.owner = to_nullable_string(owner)
        self.operator = to_nullable_string(operator)
        self.apch_bear = to_nullable_float(apch_bear)
        self.mag_var = to_nullable_int(mag_var)
        self.mag_var_hemis = HemisCode.from_value(to_nullable_string(mag_var_hemis))
        self.component_status = to_nullable_string(component_status)
        self.component_status_date = to_nullable_date(
            component_status_date, "YYYY/MM/DD"
        )
        self.lat_deg = to_nullable_int(lat_deg)
        self.lat_min = to_nullable_int(lat_min)
        self.lat_sec = to_nullable_float(lat_sec)
        self.lat_hemis = HemisCode.from_value(to_nullable_string(lat_hemis))
        self.lat_decimal = to_nullable_float(lat_decimal)
        self.lon_deg = to_nullable_int(lon_deg)
        self.lon_min = to_nullable_int(lon_min)
        self.lon_sec = to_nullable_float(lon_sec)
        self.lon_hemis = HemisCode.from_value(to_nullable_string(lon_hemis))
        self.lon_decimal = to_nullable_float(lon_decimal)
        self.lat_lon_source_code = PositionSourceCode.from_value(
            to_nullable_string(lat_lon_source_code)
        )
        self.site_elevation = to_nullable_float(site_elevation)
        self.loc_freq = to_nullable_string(loc_freq)
        self.bk_course_status_code = BackCourseStatusCode.from_value(
            to_nullable_string(bk_course_status_code)
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"STATE_NAME={self.state_name!r}, "
            f"REGION_CODE={self.region_code!r}, "
            f"RWY_LEN={self.rwy_len!r}, "
            f"RWY_WIDTH={self.rwy_width!r}, "
            f"CATEGORY={self.category!r}, "
            f"OWNER={self.owner!r}, "
            f"OPERATOR={self.operator!r}, "
            f"APCH_BEAR={self.apch_bear!r}, "
            f"MAG_VAR={self.mag_var!r}, "
            f"MAG_VAR_HEMIS={self.mag_var_hemis!r}, "
            f"COMPONENT_STATUS={self.component_status!r}, "
            f"COMPONENT_STATUS_DATE={self.component_status_date!r}, "
            f"LAT_DEG={self.lat_deg!r}, "
            f"LAT_MIN={self.lat_min!r}, "
            f"LAT_SEC={self.lat_sec!r}, "
            f"LAT_HEMIS={self.lat_hemis!r}, "
            f"LAT_DECIMAL={self.lat_decimal!r}, "
            f"LON_DEG={self.lon_deg!r}, "
            f"LON_MIN={self.lon_min!r}, "
            f"LON_SEC={self.lon_sec!r}, "
            f"LON_HEMIS={self.lon_hemis!r}, "
            f"LON_DECIMAL={self.lon_decimal!r}, "
            f"LAT_LON_SOURCE_CODE={self.lat_lon_source_code!r}, "
            f"SITE_ELEVATION={self.site_elevation!r}, "
            f"LOC_FREQ={self.loc_freq!r}, "
            f"BK_COURSE_STATUS_CODE={self.bk_course_status_code!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "state_name",
                "region_code",
                "rwy_len",
                "rwy_width",
                "category",
                "owner",
                "operator",
                "apch_bear",
                "mag_var",
                "mag_var_hemis",
                "component_status",
                "component_status_date",
                "lat_deg",
                "lat_min",
                "lat_sec",
                "lat_hemis",
                "lat_decimal",
                "lon_deg",
                "lon_min",
                "lon_sec",
                "lon_hemis",
                "lon_decimal",
                "lat_lon_source_code",
                "site_elevation",
                "loc_freq",
                "bk_course_status_code",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "state_name": self.state_name,
            "region_code": self.region_code.value if self.region_code else None,
            "rwy_len": self.rwy_len,
            "rwy_width": self.rwy_width,
            "category": self.category,
            "owner": self.owner,
            "operator": self.operator,
            "apch_bear": self.apch_bear,
            "mag_var": self.mag_var,
            "mag_var_hemis": self.mag_var_hemis.value if self.mag_var_hemis else None,
            "component_status": self.component_status,
            "component_status_date": (
                self.component_status_date.strftime("%Y-%m-%d")
                if self.component_status_date
                else None
            ),
            "lat_deg": self.lat_deg,
            "lat_min": self.lat_min,
            "lat_sec": self.lat_sec,
            "lat_hemis": self.lat_hemis.value if self.lat_hemis else None,
            "lat_decimal": self.lat_decimal,
            "lon_deg": self.lon_deg,
            "lon_min": self.lon_min,
            "lon_sec": self.lon_sec,
            "lon_hemis": self.lon_hemis.value if self.lon_hemis else None,
            "lon_decimal": self.lon_decimal,
            "lat_lon_source_code": (
                self.lat_lon_source_code.value if self.lat_lon_source_code else None
            ),
            "site_elevation": self.site_elevation,
            "loc_freq": self.loc_freq,
            "bk_course_status_code": (
                self.bk_course_status_code.value if self.bk_course_status_code else None
            ),
        }
        return {**base_dict, **this_dict}
