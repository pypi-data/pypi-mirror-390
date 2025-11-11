from nasrparse.functions import to_nullable_float, to_nullable_int, to_nullable_string
from nasrparse.records.types import HemisCode, LocationTypeCode

from ._base import Base


class ARB_BASE(Base):
    computer_id: str | None
    """Location Computer Identifier"""
    icao_id: str | None
    """ICAO Identifier"""
    location_type: LocationTypeCode
    """Location Type (ARTCC or CERAP)."""
    city: str | None
    """Location City Name"""
    state: str | None
    """Location State Post Office Code standard two letter abbreviation for US States and Territories."""
    country_code: str | None
    """Location Country Post Office Code"""
    lat_deg: int | None
    """Location Reference Point Latitude Degrees"""
    lat_min: int | None
    """Location Reference Point Latitude Minutes"""
    lat_sec: float | None
    """Location Reference Point Latitude Seconds"""
    lat_hemis: HemisCode
    """Location Reference Point Latitude Hemisphere"""
    lat_decimal: float | None
    """Location Reference Point Latitude in Decimal Format"""
    lon_deg: int | None
    """Location Reference Point Longitude Degrees"""
    lon_min: int | None
    """Location Reference Point Longitude Minutes"""
    lon_sec: float | None
    """Location Reference Point Longitude Seconds"""
    lon_hemis: HemisCode
    """Location Reference Point Longitude Hemisphere"""
    lon_decimal: float | None
    """Location Reference Point Longitude in Decimal Format"""
    cross_ref: str | None
    """Cross Reference Text (Free Form Text that further describes a specific Information Item.)"""

    def __init__(
        self,
        eff_date: str,
        location_id: str,
        location_name: str,
        computer_id: str,
        icao_id: str,
        location_type: str,
        city: str,
        state: str,
        country_code: str,
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
        cross_ref: str,
    ) -> None:
        super().__init__("boundaries", eff_date, location_id, location_name)
        self.computer_id = to_nullable_string(computer_id)
        self.icao_id = to_nullable_string(icao_id)
        self.location_type = LocationTypeCode.from_value(
            to_nullable_string(location_type)
        )
        self.city = to_nullable_string(city)
        self.state = to_nullable_string(state)
        self.country_code = to_nullable_string(country_code)
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
        self.cross_ref = to_nullable_string(cross_ref)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"COMPUTER_ID={self.computer_id!r}, "
            f"ICAO_ID={self.icao_id!r}, "
            f"LOCATION_TYPE={self.location_type!r}, "
            f"CITY={self.city!r}, "
            f"STATE={self.state!r}, "
            f"COUNTRY_CODE={self.country_code!r}, "
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
            f"CROSS_REF={self.cross_ref!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "computer_id",
                "icao_id",
                "location_type",
                "city",
                "state",
                "country_code",
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
                "cross_ref",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "computer_id": self.computer_id,
            "icao_id": self.icao_id,
            "location_type": self.location_type.value if self.location_type else None,
            "city": self.city,
            "state": self.state,
            "country_code": self.country_code,
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
            "cross_ref": self.cross_ref,
        }
        return {**base_dict, **this_dict}
