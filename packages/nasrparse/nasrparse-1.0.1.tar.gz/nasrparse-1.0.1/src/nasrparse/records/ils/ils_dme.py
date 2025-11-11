from nasrparse.functions import (
    to_nullable_date,
    to_nullable_float,
    to_nullable_int,
    to_nullable_string,
)
from nasrparse.records.types import HemisCode, PositionSourceCode

from ._base import Base

from datetime import date


class ILS_DME(Base):
    component_status: str | None
    """Operational Status of DME"""
    component_status_date: date | None
    """Effective Date of DME Operational Status"""
    lat_deg: int | None
    """DME Transponder Antenna Latitude Degrees"""
    lat_min: int | None
    """DME Transponder Antenna Latitude Minutes"""
    lat_sec: float | None
    """DME Transponder Antenna Latitude Seconds"""
    lat_hemis: HemisCode
    """DME Transponder Antenna Latitude Hemisphere"""
    lat_decimal: float | None
    """DME Transponder Antenna Latitude in Decimal Format"""
    lon_deg: int | None
    """DME Transponder Antenna Longitude Degrees"""
    lon_min: int | None
    """DME Transponder Antenna Longitude Minutes"""
    lon_sec: float | None
    """DME Transponder Antenna Longitude Seconds"""
    lon_hemis: HemisCode
    """DME Transponder Antenna Longitude Hemisphere"""
    lon_decimal: float | None
    """DME Transponder Antenna Longitude in Decimal Format"""
    lat_lon_source_code: PositionSourceCode
    """Code Indication Source of Latitude/Longitude Information"""
    site_elevation: float | None
    """Site Elevation of DME Transponder Antenna in Tenth of a Foot (MSL)."""
    channel: str | None
    """NAS Channel on Which Distance Data is Transmitted"""

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
        channel: str,
    ) -> None:
        super().__init__(
            "ils_dmes",
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
        self.channel = to_nullable_string(channel)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
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
            f"CHANNEL={self.channel!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
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
                "channel",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
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
            "channel": self.channel,
        }
        return {**base_dict, **this_dict}
