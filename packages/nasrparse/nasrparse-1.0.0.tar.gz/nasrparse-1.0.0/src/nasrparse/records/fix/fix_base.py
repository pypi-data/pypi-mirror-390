from nasrparse.functions import (
    to_nullable_bool,
    to_nullable_float,
    to_nullable_int,
    to_nullable_string,
)
from nasrparse.records.types import HemisCode, PointCode

from ._base import Base


class FIX_BASE(Base):
    lat_deg: int | None
    """FIX Latitude Degrees"""
    lat_min: int | None
    """FIX Latitude Minutes"""
    lat_sec: float | None
    """FIX Latitude Seconds"""
    lat_hemis: HemisCode | None
    """FIX Latitude Hemisphere"""
    lat_decimal: float | None
    """FIX Latitude in Decimal Format"""
    lon_deg: int | None
    """FIX Longitude Degrees"""
    lon_min: int | None
    """FIX Longitude Minutes"""
    lon_sec: float | None
    """FIX Longitude Seconds"""
    lon_hemis: HemisCode | None
    """FIX Longitude Hemisphere"""
    lon_decimal: float | None
    """FIX Longitude in Decimal Format"""
    fix_id_old: str | None
    """Previous Name(s) of the Fix before It was Renamed."""
    charting_remark: str | None
    """Charting Information."""
    fix_use_code: PointCode
    """FIX Type."""
    artcc_id_high: str | None
    """Denotes High ARTCC Area Of Jurisdiction."""
    artcc_id_low: str | None
    """Denotes Low ARTCC Area Of Jurisdiction."""
    pitch_flag: bool | None
    """Pitch (Y = YES or N = NO)"""
    catch_flag: bool | None
    """Catch (Y = YES or N = NO)"""
    sua_atcaa_flag: bool | None
    """SUA/ATCAA (Y = YES or N = NO)"""
    min_recep_alt: int | None
    """Fix Minimum Reception Altitude (MRA)"""
    compulsory: str | None
    """Compulsory FIX identified as HIGH or LOW or LOW/HIGH. Null in this field identifies Non-Compulsory FIX."""
    charts: str | None
    """Concatenated list of the information found in the FIX_CHRT file separated by a comma."""

    def __init__(
        self,
        eff_date: str,
        fix_id: str,
        icao_region_code: str,
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
        fix_id_old: str,
        charting_remark: str,
        fix_use_code: str,
        artcc_id_high: str,
        artcc_id_low: str,
        pitch_flag: str,
        catch_flag: str,
        sua_atcaa_flag: str,
        min_recep_alt: str,
        compulsory: str,
        charts: str,
    ) -> None:
        super().__init__(
            "fixes",
            eff_date,
            fix_id,
            icao_region_code,
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
        self.fix_id_old = to_nullable_string(fix_id_old)
        self.charting_remark = to_nullable_string(charting_remark)
        self.fix_use_code = PointCode.from_value(to_nullable_string(fix_use_code))
        self.artcc_id_high = to_nullable_string(artcc_id_high)
        self.artcc_id_low = to_nullable_string(artcc_id_low)
        self.pitch_flag = to_nullable_bool(pitch_flag)
        self.catch_flag = to_nullable_bool(catch_flag)
        self.sua_atcaa_flag = to_nullable_bool(sua_atcaa_flag)
        self.min_recep_alt = to_nullable_int(min_recep_alt)
        self.compulsory = to_nullable_string(compulsory)
        self.charts = to_nullable_string(charts)

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
            f"FIX_ID_OLD={self.fix_id_old!r}, "
            f"CHARTING_REMARK={self.charting_remark!r}, "
            f"FIX_USE_CODE={self.fix_use_code!r}, "
            f"ARTCC_ID_HIGH={self.artcc_id_high!r}, "
            f"ARTCC_ID_LOW={self.artcc_id_low!r}, "
            f"PITCH_FLAG={self.pitch_flag!r}, "
            f"CATCH_FLAG={self.catch_flag!r}, "
            f"SUA_ATCAA_FLAG={self.sua_atcaa_flag!r}, "
            f"MIN_RECEP_ALT={self.min_recep_alt!r}, "
            f"COMPULSORY={self.compulsory!r}, "
            f"CHARTS={self.charts!r}"
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
                "fix_id_old",
                "charting_remark",
                "fix_use_code",
                "artcc_id_high",
                "artcc_id_low",
                "pitch_flag",
                "catch_flag",
                "sua_atcaa_flag",
                "min_recep_alt",
                "compulsory",
                "charts",
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
            "fix_id_old": self.fix_id_old,
            "charting_remark": self.charting_remark,
            "fix_use_code": self.fix_use_code.value if self.fix_use_code else None,
            "artcc_id_high": self.artcc_id_high,
            "artcc_id_low": self.artcc_id_low,
            "pitch_flag": self.pitch_flag,
            "catch_flag": self.catch_flag,
            "sua_atcaa_flag": self.sua_atcaa_flag,
            "min_recep_alt": self.min_recep_alt,
            "compulsory": self.compulsory,
            "charts": self.charts,
        }
        return {**base_dict, **this_dict}
