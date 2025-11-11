from nasrparse.functions import (
    to_nullable_bool,
    to_nullable_date,
    to_nullable_float,
    to_nullable_int,
    to_nullable_string,
)
from nasrparse.records.types import FSSTypeCode, HemisCode

from ._base import Base

from datetime import date


class FSS_BASE(Base):
    update_date: date | None
    """Last Date on which the Record was updated."""
    fss_fac_type: FSSTypeCode
    """facility type: Flight Service Station (FSS), FS21 HUB Station (HUB) or FS21 Radio Service Area (RADIO)."""
    voice_call: str | None
    """FSS Voice Call"""
    lat_deg: int | None
    """Flight Service Station Latitude Degrees"""
    lat_min: int | None
    """Flight Service Station Latitude Minutes"""
    lat_sec: float | None
    """Flight Service Station Latitude Seconds"""
    lat_hemis: HemisCode
    """Flight Service Station Latitude Hemisphere"""
    lat_decimal: float | None
    """Flight Service Station Latitude in Decimal Format"""
    lon_deg: int | None
    """Flight Service Station Longitude Degrees"""
    lon_min: int | None
    """Flight Service Station Longitude Minutes"""
    lon_sec: float | None
    """Flight Service Station Longitude Seconds"""
    lon_hemis: HemisCode
    """Flight Service Station Longitude Hemisphere"""
    lon_decimal: float | None
    """Flight Service Station Longitude in Decimal Format"""
    opr_hours: str | None
    """FSS Hours of Operation"""
    fac_status: str | None
    """Status of Facility"""
    alternate_fss: str | None
    """If the Record Facility does not have Circuit B Teletype Capable of Transmitting/Receiving Flight Plan Messages then Alternate FSS with this Capability listed."""
    wea_radar_flag: bool | None
    """Availability of Weather Radar"""
    phone_no: str | None
    """Telephone Number used to reach FSS."""
    toll_free_no: str | None
    """Toll Free Telephone Number used to reach FSS."""

    def __init__(
        self,
        eff_date: str,
        fss_id: str,
        name: str,
        city: str,
        state_code: str,
        country_code: str,
        update_date: str,
        fss_fac_type: str,
        voice_call: str,
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
        opr_hours: str,
        fac_status: str,
        alternate_fss: str,
        wea_radar_flag: str,
        phone_no: str,
        toll_free_no: str,
    ) -> None:
        super().__init__(
            "flight_services",
            eff_date,
            fss_id,
            name,
            city,
            state_code,
            country_code,
        )
        self.update_date = to_nullable_date(update_date, "YYYY/MM/DD")
        self.fss_fac_type = FSSTypeCode.from_value(to_nullable_string(fss_fac_type))
        self.voice_call = to_nullable_string(voice_call)
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
        self.opr_hours = to_nullable_string(opr_hours)
        self.fac_status = to_nullable_string(fac_status)
        self.alternate_fss = to_nullable_string(alternate_fss)
        self.wea_radar_flag = to_nullable_bool(wea_radar_flag)
        self.phone_no = to_nullable_string(phone_no)
        self.toll_free_no = to_nullable_string(toll_free_no)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"UPDATE_DATE={self.update_date!r}, "
            f"FSS_FAC_TYPE={self.fss_fac_type!r}, "
            f"VOICE_CALL={self.voice_call!r}, "
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
            f"OPR_HOURS={self.opr_hours!r}, "
            f"FAC_STATUS={self.fac_status!r}, "
            f"ALTERNATE_FSS={self.alternate_fss!r}, "
            f"WEA_RADAR_FLAG={self.wea_radar_flag!r}, "
            f"PHONE_NO={self.phone_no!r}, "
            f"TOLL_FREE_NO={self.toll_free_no!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "update_date",
                "fss_fac_type",
                "voice_call",
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
                "opr_hours",
                "fac_status",
                "alternate_fss",
                "wea_radar_flag",
                "phone_no",
                "toll_free_no",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "update_date": (
                self.update_date.strftime("%Y-%m-%d") if self.update_date else None
            ),
            "fss_fac_type": self.fss_fac_type.value if self.fss_fac_type else None,
            "voice_call": self.voice_call,
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
            "opr_hours": self.opr_hours,
            "fac_status": self.fac_status,
            "alternate_fss": self.alternate_fss,
            "wea_radar_flag": self.wea_radar_flag,
            "phone_no": self.phone_no,
            "toll_free_no": self.toll_free_no,
        }
        return {**base_dict, **this_dict}
