from nasrparse.functions import to_nullable_float, to_nullable_int, to_nullable_string
from nasrparse.records.types import HemisCode, MethodCode

from ._base import Base


class WXL_BASE(Base):
    lat_deg: int | None
    """Weather Reporting Location Latitude Degrees"""
    lat_min: int | None
    """Weather Reporting Location Latitude Minutes"""
    lat_sec: float | None
    """Weather Reporting Location Latitude Seconds"""
    lat_hemis: HemisCode
    """Weather Reporting Location Latitude Hemisphere"""
    lat_decimal: float | None
    """Weather Reporting Location Latitude in Decimal Format"""
    lon_deg: int | None
    """Weather Reporting Location Longitude Degrees"""
    lon_min: int | None
    """Weather Reporting Location Longitude Minutes"""
    lon_sec: float | None
    """Weather Reporting Location Longitude Seconds"""
    lon_hemis: HemisCode
    """Weather Reporting Location Longitude Hemisphere"""
    lon_decimal: float | None
    """Weather Reporting Location Longitude in Decimal Format"""
    elev: int | None
    """Weather Reporting Location Elevation - Value (Whole Feet MSL)."""
    survey_method_code: MethodCode
    """Weather Reporting Location Elevation - Accuracy"""

    def __init__(
        self,
        eff_date: str,
        wea_id: str,
        city: str,
        state_code: str,
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
        elev: str,
        survey_method_code: str,
    ) -> None:
        super().__init__(
            "weather_locations",
            eff_date,
            wea_id,
            city,
            state_code,
            country_code,
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
        self.elev = to_nullable_int(elev)
        self.survey_method_code = MethodCode.from_value(
            to_nullable_string(survey_method_code)
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
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
            f"ELEV={self.elev!r}, "
            f"SURVEY_METHOD_CODE={self.survey_method_code!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
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
                "elev",
                "survey_method_code",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
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
            "elev": self.elev,
            "survey_method_code": (
                self.survey_method_code.value if self.survey_method_code else None
            ),
        }
        return {**base_dict, **this_dict}
