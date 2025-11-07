from nasrparse.functions import (
    to_nullable_bool,
    to_nullable_date,
    to_nullable_float,
    to_nullable_int,
    to_nullable_string,
)
from nasrparse.records.types import HemisCode, MethodCode, SiteTypeCode

from ._base import Base

from datetime import date


class AWOS_BASE(Base):
    commissioned_date: date | None
    """Decommissioned Weather systems are not included so Dates given are for Commissioning Dates."""
    navaid_flag: bool | None
    """Weather associated with NAVAID"""
    lat_deg: int | None
    """Weather System Latitude Degrees"""
    lat_min: int | None
    """Weather System Latitude Minutes"""
    lat_sec: float | None
    """Weather System Latitude Seconds"""
    lat_hemis: HemisCode
    """Weather System Latitude Hemisphere"""
    lat_decimal: float | None
    """Weather System Latitude in Decimal Format"""
    lon_deg: int | None
    """Weather System Longitude Degrees"""
    lon_min: int | None
    """Weather System Longitude Minutes"""
    lon_sec: float | None
    """Weather System Longitude Seconds"""
    lon_hemis: HemisCode
    """Weather System Longitude Hemisphere"""
    lon_decimal: float | None
    """Weather System Longitude in Decimal Format"""
    elev: float | None
    """Weather System Elevation (Nearest Tenth of a Foot)"""
    survey_method_code: MethodCode
    """Weather System Location Determination Method"""
    phone_no: str | None
    """Weather System Telephone Number"""
    second_phone_no: str | None
    """Weather System Second Telephone Number"""
    site_no: str | None
    """Landing Facility Site Number when Weather System Located at Airport."""
    site_type_code: SiteTypeCode
    """Landing Facility Type Code when Weather System Located at Airport."""
    remark: str | None
    """Remark associated with Weather System."""

    def __init__(
        self,
        eff_date: str,
        asos_awos_id: str,
        asos_awos_type: str,
        state_code: str,
        city: str,
        country_code: str,
        commissioned_date: str,
        navaid_flag: str,
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
        phone_no: str,
        second_phone_no: str,
        site_no: str,
        site_type_code: str,
        remark: str,
    ) -> None:
        super().__init__(
            "awos",
            eff_date,
            asos_awos_id,
            asos_awos_type,
            state_code,
            city,
            country_code,
        )
        self.commissioned_date = to_nullable_date(commissioned_date, "YYYY/MM/DD")
        self.navaid_flag = to_nullable_bool(navaid_flag)
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
        self.elev = to_nullable_float(elev)
        self.survey_method_code = MethodCode.from_value(
            to_nullable_string(survey_method_code)
        )
        self.phone_no = to_nullable_string(phone_no)
        self.second_phone_no = to_nullable_string(second_phone_no)
        self.site_no = to_nullable_string(site_no)
        self.site_type_code = SiteTypeCode.from_value(
            to_nullable_string(site_type_code)
        )
        self.remark = to_nullable_string(remark)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"COMMISSIONED_DATE={self.commissioned_date!r}, "
            f"NAVAID_FLAG={self.navaid_flag!r}, "
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
            f"SURVEY_METHOD_CODE={self.survey_method_code!r}, "
            f"PHONE_NO={self.phone_no!r}, "
            f"SECOND_PHONE_NO={self.second_phone_no!r}, "
            f"SITE_NO={self.site_no!r}, "
            f"SITE_TYPE_CODE={self.site_type_code!r}, "
            f"REMARK={self.remark!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "commissioned_date",
                "navaid_flag",
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
                "phone_no",
                "second_phone_no",
                "site_no",
                "site_type_code",
                "remark",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "commissioned_date": (
                self.commissioned_date.strftime("%Y-%m-%d")
                if self.commissioned_date
                else None
            ),
            "navaid_flag": self.navaid_flag,
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
            "phone_no": self.phone_no,
            "second_phone_no": self.second_phone_no,
            "site_no": self.site_no,
            "site_type_code": (
                self.site_type_code.value if self.site_type_code else None
            ),
            "remark": self.remark,
        }
        return {**base_dict, **this_dict}
