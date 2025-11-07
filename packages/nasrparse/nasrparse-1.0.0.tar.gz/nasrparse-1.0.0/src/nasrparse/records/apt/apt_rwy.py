from nasrparse.functions.record import (
    to_nullable_date,
    to_nullable_float,
    to_nullable_int,
    to_nullable_string,
)
from nasrparse.records.types import (
    ConditionCode,
    DeterminationCode,
    PavementCode,
    RunwayLightCode,
    SurfaceCode,
    TreatmentCode,
)

from ._base import Base

from datetime import date


class APT_RWY(Base):
    rwy_id: str | None
    """Runway Identification"""
    rwy_len: int | None
    """Physical Runway Length (Nearest Foot)"""
    rwy_width: int | None
    """Physical Runway Width (Nearest Foot)"""
    surface_type_code: list[SurfaceCode]
    """Runway Surface Type (The value will usually be one of those described below or a combination of two types when the runway is composed of distinct sections.)"""
    cond: ConditionCode
    """Runway Surface Condition"""
    treatment_code: TreatmentCode
    """Runway Surface Treatment"""
    pcn: int | None
    """Pavement Classification Number (PCN) See FAA Advisory Circular 150/5335-5 for Code Definitions and PCN Determination Formula."""
    pavement_type_code: PavementCode
    """Pavement Type"""
    subgrade_strength_code: str | None
    """Subgrade Strength (Letters A-F)"""
    tire_pres_code: str | None
    """Tire Pressure Code (Letters W-Z)"""
    dtrm_method_code: DeterminationCode
    """Determination Method"""
    rwy_lgt_code: RunwayLightCode
    """Runway Lights Edge Intensity"""
    rwy_len_source: str | None
    """Runway Length Source"""
    length_source_date: date | None
    """Runway Length Source Date (YYYY/MM/DD)"""
    gross_wt_sw: float | None
    """Runway Weight-Bearing Capacity for Single Wheel type Landing Gear"""
    gross_wt_dw: float | None
    """Runway Weight-Bearing Capacity for Dual Wheel type Landing Gear"""
    gross_wt_dtw: float | None
    """Runway Weight-Bearing Capacity for Two Dual Wheels in tandem type Landing Gear"""
    gross_wt_ddtw: float | None
    """Runway Weight-Bearing Capacity for Two Dual Wheels in tandem/two dual wheels in double tandem body gear type Landing Gear"""

    def __init__(
        self,
        eff_date: str,
        site_no: str,
        site_type_code: str,
        state_code: str,
        arpt_id: str,
        city: str,
        country_code: str,
        rwy_id: str,
        rwy_len: str,
        rwy_width: str,
        surface_type_code: str,
        cond: str,
        treatment_code: str,
        pcn: str,
        pavement_type_code: str,
        subgrade_strength_code: str,
        tire_pres_code: str,
        dtrm_method_code: str,
        rwy_lgt_code: str,
        rwy_len_source: str,
        length_source_date: str,
        gross_wt_sw: str,
        gross_wt_dw: str,
        gross_wt_dtw: str,
        gross_wt_ddtw: str,
    ) -> None:
        super().__init__(
            "airport_runway",
            eff_date,
            site_no,
            site_type_code,
            state_code,
            arpt_id,
            city,
            country_code,
        )
        self.rwy_id = to_nullable_string(rwy_id)
        self.rwy_len = to_nullable_int(rwy_len)
        self.rwy_width = to_nullable_int(rwy_width)
        self.surface_type_code = [
            st
            for item in (surface_type_code or "").split(",")
            if (st := SurfaceCode.from_value(to_nullable_string(item))) is not st.NULL
        ]
        self.cond = ConditionCode.from_value(to_nullable_string(cond))
        self.treatment_code = TreatmentCode.from_value(
            to_nullable_string(treatment_code)
        )
        self.pcn = to_nullable_int(pcn)
        self.pavement_type_code = PavementCode.from_value(
            to_nullable_string(pavement_type_code)
        )
        self.subgrade_strength_code = to_nullable_string(subgrade_strength_code)
        self.tire_pres_code = to_nullable_string(tire_pres_code)
        self.dtrm_method_code = DeterminationCode.from_value(
            to_nullable_string(dtrm_method_code)
        )
        self.rwy_lgt_code = RunwayLightCode.from_value(to_nullable_string(rwy_lgt_code))
        self.rwy_len_source = to_nullable_string(rwy_len_source)
        self.length_source_date = to_nullable_date(length_source_date, "YYYY/MM/DD")
        self.gross_wt_sw = to_nullable_float(gross_wt_sw)
        self.gross_wt_dw = to_nullable_float(gross_wt_dw)
        self.gross_wt_dtw = to_nullable_float(gross_wt_dtw)
        self.gross_wt_ddtw = to_nullable_float(gross_wt_ddtw)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"RWY_ID={self.rwy_id!r}, "
            f"RWY_LEN={self.rwy_len!r}, "
            f"RWY_WIDTH={self.rwy_width!r}, "
            f"SURFACE_TYPE_CODE={self.surface_type_code!r}, "
            f"COND={self.cond!r}, "
            f"TREATMENT_CODE={self.treatment_code!r}, "
            f"PCN={self.pcn!r}, "
            f"PAVEMENT_TYPE_CODE={self.pavement_type_code!r}, "
            f"SUBGRADE_STRENGTH_CODE={self.subgrade_strength_code!r}, "
            f"TIRE_PRES_CODE={self.tire_pres_code!r}, "
            f"DTRM_METHOD_CODE={self.dtrm_method_code!r}, "
            f"RWY_LGT_CODE={self.rwy_lgt_code!r}, "
            f"RWY_LEN_SOURCE={self.rwy_len_source!r}, "
            f"LENGTH_SOURCE_DATE={self.length_source_date!r}, "
            f"GROSS_WT_SW={self.gross_wt_sw!r}, "
            f"GROSS_WT_DW={self.gross_wt_dw!r}, "
            f"GROSS_WT_DTW={self.gross_wt_dtw!r}, "
            f"GROSS_WT_DDTW={self.gross_wt_ddtw!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "rwy_id",
                "rwy_len",
                "rwy_width",
                "surface_type_code",
                "cond",
                "treatment_code",
                "pcn",
                "pavement_type_code",
                "subgrade_strength_code",
                "tire_pres_code",
                "dtrm_method_code",
                "rwy_lgt_code",
                "rwy_len_source",
                "length_source_date",
                "gross_wt_sw",
                "gross_wt_dw",
                "gross_wt_dtw",
                "gross_wt_ddtw",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "rwy_id": self.rwy_id,
            "rwy_len": self.rwy_len,
            "rwy_width": self.rwy_width,
            "surface_type_code": (
                ", ".join(
                    member.value
                    for member in self.surface_type_code
                    if member.value is not None
                )
                if self.surface_type_code
                else None
            ),
            "cond": self.cond.value,
            "treatment_code": self.treatment_code.value,
            "pcn": self.pcn,
            "pavement_type_code": self.pavement_type_code.value,
            "subgrade_strength_code": self.subgrade_strength_code,
            "tire_pres_code": self.tire_pres_code,
            "dtrm_method_code": self.dtrm_method_code.value,
            "rwy_lgt_code": self.rwy_lgt_code.value,
            "rwy_len_source": self.rwy_len_source,
            "length_source_date": self.length_source_date,
            "gross_wt_sw": self.gross_wt_sw,
            "gross_wt_dw": self.gross_wt_dw,
            "gross_wt_dtw": self.gross_wt_dtw,
            "gross_wt_ddtw": self.gross_wt_ddtw,
        }
        return {**base_dict, **this_dict}
