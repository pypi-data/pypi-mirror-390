from nasrparse.functions import (
    to_nullable_date,
    to_nullable_float,
    to_nullable_int,
    to_nullable_string,
)
from nasrparse.records.types import CommunicationStatusCode, HemisCode

from ._base import Base

from datetime import date


class COM_BASE(Base):
    comm_outlet_name: str | None
    """Communications Outlet Name. The Communications Outlet Name is also used as the Communications Outlet Call."""
    lat_deg: int | None
    """Communications Outlet Latitude Degrees"""
    lat_min: int | None
    """Communications Outlet Latitude Minutes"""
    lat_sec: float | None
    """Communications Outlet Latitude Seconds"""
    lat_hemis: HemisCode
    """Communications Outlet Latitude Hemisphere"""
    lat_decimal: float | None
    """Communications Outlet Latitude in Decimal Format"""
    lon_deg: int | None
    """Communications Outlet Longitude Degrees"""
    lon_min: int | None
    """Communications Outlet Longitude Minutes"""
    lon_sec: float | None
    """Communications Outlet Longitude Seconds"""
    lon_hemis: HemisCode
    """Communications Outlet Longitude Hemisphere"""
    lon_decimal: float | None
    """Communications Outlet Longitude in Decimal Format"""
    facility_id: str | None
    """For RCO and RCO1, the Facility ID is the Associated Flight Service Station Ident. For RCAG, the Facility ID is the Associated ARTCC. FACILITY_NAME - For RCO and RCO1, the Facility Name is the Associated Flight Service Station Name. For RCAG, the Facility Name is the Associated ARTCC Name."""
    alt_fss_id: str | None
    """Associated Alternate Flight Service Station Ident - Applies to RCO/RCO1 types only."""
    alt_fss_name: str | None
    """Associated Alternate Flight Service Station Name - Applies to RCO/RCO1 types only."""
    opr_hrs: str | None
    """Standard Time Zone - Applies to RCO/RCO1 types only."""
    comm_status_code: CommunicationStatusCode
    """Communication Outlet Status - Applies to RCO/RCO1 types only."""
    comm_status_date: date | None
    """STATUS Date of Communications Outlet - Applies to RCO/RCO1 types only."""
    remark: str | None
    """Remark associated with Communications Outlet."""

    def __init__(
        self,
        eff_date: str,
        comm_loc_id: str,
        comm_type: str,
        nav_id: str,
        nav_type: str,
        city: str,
        state_code: str,
        region_code: str,
        country_code: str,
        comm_outlet_name: str,
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
        facility_id: str,
        alt_fss_id: str,
        alt_fss_name: str,
        opr_hrs: str,
        comm_status_code: str,
        comm_status_date: str,
        remark: str,
    ) -> None:
        super().__init__(
            "communication_outlets",
            eff_date,
            comm_loc_id,
            comm_type,
            nav_id,
            nav_type,
            city,
            state_code,
            region_code,
            country_code,
        )
        self.comm_outlet_name = to_nullable_string(comm_outlet_name)
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
        self.facility_id = to_nullable_string(facility_id)
        self.alt_fss_id = to_nullable_string(alt_fss_id)
        self.alt_fss_name = to_nullable_string(alt_fss_name)
        self.opr_hrs = to_nullable_string(opr_hrs)
        self.comm_status_code = CommunicationStatusCode.from_value(
            to_nullable_string(comm_status_code)
        )
        self.comm_status_date = to_nullable_date(comm_status_date, "YYYY/MM/DD")
        self.remark = to_nullable_string(remark)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"COMM_OUTLET_NAME={self.comm_outlet_name!r}, "
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
            f"FACILITY_ID={self.facility_id!r}, "
            f"ALT_FSS_ID={self.alt_fss_id!r}, "
            f"ALT_FSS_NAME={self.alt_fss_name!r}, "
            f"OPR_HRS={self.opr_hrs!r}, "
            f"COMM_STATUS_CODE={self.comm_status_code!r}, "
            f"COMM_STATUS_DATE={self.comm_status_date!r}, "
            f"REMARK={self.remark!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "comm_outlet_name",
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
                "facility_id",
                "alt_fss_id",
                "alt_fss_name",
                "opr_hrs",
                "comm_status_code",
                "comm_status_date",
                "remark",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "comm_outlet_name": self.comm_outlet_name,
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
            "facility_id": self.facility_id,
            "alt_fss_id": self.alt_fss_id,
            "alt_fss_name": self.alt_fss_name,
            "opr_hrs": self.opr_hrs,
            "comm_status_code": (
                self.comm_status_code.value if self.comm_status_code else None
            ),
            "comm_status_date": (
                self.comm_status_date.strftime("%Y-%m-%d")
                if self.comm_status_date
                else None
            ),
            "remark": self.remark,
        }
        return {**base_dict, **this_dict}
