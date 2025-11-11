from nasrparse.functions import (
    to_nullable_date,
    to_nullable_float,
    to_nullable_int,
    to_nullable_string,
)
from nasrparse.records.types import (
    HemisCode,
    ILSCompTypeCode,
    MarkerTypeCode,
    PositionSourceCode,
)

from ._base import Base

from datetime import date


class ILS_MKR(Base):
    ils_comp_type_code: ILSCompTypeCode
    """Marker Type (IM - Inner Marker, MM - Middle Marker, OM - Outer Marker)"""
    component_status: str | None
    """Operational Status of Marker Beacon"""
    component_status_date: date | None
    """Effective Date of Marker Beacon Operational Status"""
    lat_deg: int | None
    """Marker Beacon Latitude Degrees"""
    lat_min: int | None
    """Marker Beacon Latitude Minutes"""
    lat_sec: float | None
    """Marker Beacon Latitude Seconds"""
    lat_hemis: HemisCode
    """Marker Beacon Latitude Hemisphere"""
    lat_decimal: float | None
    """Marker Beacon Latitude in Decimal Format"""
    lon_deg: int | None
    """Marker Beacon Longitude Degrees"""
    lon_min: int | None
    """Marker Beacon Longitude Minutes"""
    lon_sec: float | None
    """Marker Beacon Longitude Seconds"""
    lon_hemis: HemisCode
    """Marker Beacon Longitude Hemisphere"""
    lon_decimal: float | None
    """Marker Beacon Longitude in Decimal Format"""
    lat_lon_source_code: PositionSourceCode
    """Code Indication Source of Latitude/Longitude Information"""
    site_elevation: float | None
    """Site Elevation of Marker Beacon in Tenth of a Foot (MSL)."""
    mkr_fac_type_code: MarkerTypeCode
    """Facility/Type of Marker/Locator"""
    marker_id_beacon: str | None
    """Location Identifier of Beacon at Marker"""
    compass_locator_name: str | None
    """Name of the Marker Locator Beacon"""
    freq: str | None
    """NAVAID Frequency when Marker is collocated else Locator Frequency (in KHZ)"""
    nav_id: str | None
    """Location Identifier of Navigation Aid Collocated With Marker (Blank Indicates Marker Is Not Collocated With A NAVAID)"""
    nav_type: str | None
    """Collocated NAVAID Type"""
    low_powered_ndb_status: str | None
    """Low Powered NDB Status of Marker Beacon"""

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
        ils_comp_type_code: str,
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
        mkr_fac_type_code: str,
        marker_id_beacon: str,
        compass_locator_name: str,
        freq: str,
        nav_id: str,
        nav_type: str,
        low_powered_ndb_status: str,
    ) -> None:
        super().__init__(
            "ils_markers",
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
        self.ils_comp_type_code = ILSCompTypeCode.from_value(
            to_nullable_string(ils_comp_type_code)
        )
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
        self.mkr_fac_type_code = MarkerTypeCode.from_value(
            to_nullable_string(mkr_fac_type_code)
        )
        self.marker_id_beacon = to_nullable_string(marker_id_beacon)
        self.compass_locator_name = to_nullable_string(compass_locator_name)
        self.freq = to_nullable_string(freq)
        self.nav_id = to_nullable_string(nav_id)
        self.nav_type = to_nullable_string(nav_type)
        self.low_powered_ndb_status = to_nullable_string(low_powered_ndb_status)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"ILS_COMP_TYPE_CODE={self.ils_comp_type_code!r}, "
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
            f"MKR_FAC_TYPE_CODE={self.mkr_fac_type_code!r}, "
            f"MARKER_ID_BEACON={self.marker_id_beacon!r}, "
            f"COMPASS_LOCATOR_NAME={self.compass_locator_name!r}, "
            f"FREQ={self.freq!r}, "
            f"NAV_ID={self.nav_id!r}, "
            f"NAV_TYPE={self.nav_type!r}, "
            f"LOW_POWERED_NDB_STATUS={self.low_powered_ndb_status!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "ils_comp_type_code",
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
                "mkr_fac_type_code",
                "marker_id_beacon",
                "compass_locator_name",
                "freq",
                "nav_id",
                "nav_type",
                "low_powered_ndb_status",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "ils_comp_type_code": (
                self.ils_comp_type_code.value if self.ils_comp_type_code else None
            ),
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
            "mkr_fac_type_code": (
                self.mkr_fac_type_code.value if self.mkr_fac_type_code else None
            ),
            "marker_id_beacon": self.marker_id_beacon,
            "compass_locator_name": self.compass_locator_name,
            "freq": self.freq,
            "nav_id": self.nav_id,
            "nav_type": self.nav_type,
            "low_powered_ndb_status": self.low_powered_ndb_status,
        }
        return {**base_dict, **this_dict}
