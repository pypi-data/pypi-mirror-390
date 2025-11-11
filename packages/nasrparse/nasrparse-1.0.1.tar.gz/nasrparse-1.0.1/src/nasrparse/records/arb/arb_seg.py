from nasrparse.functions.record import (
    to_nullable_float,
    to_nullable_int,
    to_nullable_string,
)
from nasrparse.records.types import AltitudeStructureCode, BoundaryTypeCode, HemisCode

from ._base import Base


class ARB_SEG(Base):
    rec_id: str | None
    """Concatenation of the LOCATION_ID * BNDRY_CODE * 5 Character Point Designator."""
    altitude: AltitudeStructureCode
    """Boundary Altitude Structure"""
    type: BoundaryTypeCode
    """Boundary Type (ARTCC, FIR, CTA, CTA/FIR, UTA)."""
    point_seq: int | None
    """Sequencing number in multiples of ten. Points are in order adapted for given Boundary."""
    lat_deg: int | None
    """Boundary Point Latitude Degrees"""
    lat_min: int | None
    """Boundary Point Latitude Minutes"""
    lat_sec: float | None
    """Boundary Point Latitude Seconds"""
    lat_hemis: HemisCode
    """Boundary Point Latitude Hemisphere"""
    lat_decimal: float | None
    """Boundary Point Latitude in Decimal Format"""
    lon_deg: int | None
    """Boundary Point Longitude Degrees"""
    lon_min: int | None
    """Boundary Point Longitude Minutes"""
    lon_sec: float | None
    """Boundary Point Longitude Seconds"""
    lon_hemis: HemisCode
    """Boundary Point Longitude Hemisphere"""
    lon_decimal: float | None
    """Boundary Point Longitude in Decimal Format"""
    bndry_pt_descrip: str | None
    """Description of Boundary Line Connecting Points on The Boundary."""
    nas_descrip_flag: str | None
    """An 'X' In This Field Indicates This Point Is Used Only in The NAS Description and Not the Legal Description."""

    def __init__(
        self,
        eff_date: str,
        location_id: str,
        location_name: str,
        rec_id: str,
        altitude: str,
        type: str,
        point_seq: str,
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
        bndry_pt_descrip: str,
        nas_descrip_flag: str,
    ) -> None:
        super().__init__("boundary_segment", eff_date, location_id, location_name)
        self.rec_id = to_nullable_string(rec_id)
        self.altitude = AltitudeStructureCode.from_value(to_nullable_string(altitude))
        self.type = BoundaryTypeCode.from_value(to_nullable_string(type))
        self.point_seq = to_nullable_int(point_seq)
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
        self.bndry_pt_descrip = to_nullable_string(bndry_pt_descrip)
        self.nas_descrip_flag = to_nullable_string(nas_descrip_flag)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"REC_ID={self.rec_id!r}, "
            f"ALTITUDE={self.altitude!r}, "
            f"TYPE={self.type!r}, "
            f"POINT_SEQ={self.point_seq!r}, "
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
            f"BNDRY_PT_DESCRIP={self.bndry_pt_descrip!r}, "
            f"NAS_DESCRIP_FLAG={self.nas_descrip_flag!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "rec_id",
                "altitude",
                "type",
                "point_seq",
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
                "bndry_pt_descrip",
                "nas_descrip_flag",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "rec_id": self.rec_id,
            "altitude": self.altitude.value if self.altitude else None,
            "type": self.type.value if self.type else None,
            "point_seq": self.point_seq,
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
            "bndry_pt_descrip": self.bndry_pt_descrip,
            "nas_descrip_flag": self.nas_descrip_flag,
        }
        return {**base_dict, **this_dict}
