from nasrparse.functions import to_nullable_bool, to_nullable_string

from ._base import Base


class PJA_CON(Base):
    fac_id: str | None
    """Contact Facility Identifier"""
    fac_name: str | None
    """Contact Facility Name"""
    loc_id: str | None
    """Related Location Identifier"""
    commercial_freq: str | None
    """Commercial Frequency"""
    commercial_chart_flag: bool | None
    """Commercial Chart Flag"""
    mil_freq: str | None
    """Military Frequency"""
    mil_chart_flag: str | None
    """Military Chart Flag"""
    sector: str | None
    """Sector Description Text"""
    contact_freq_altitude: str | None
    """Altitude Description Text"""

    def __init__(
        self,
        eff_date: str,
        pja_id: str,
        fac_id: str,
        fac_name: str,
        loc_id: str,
        commercial_freq: str,
        commercial_chart_flag: str,
        mil_freq: str,
        mil_chart_flag: str,
        sector: str,
        contact_freq_altitude: str,
    ) -> None:
        super().__init__("parachute_jump_area_contacts", eff_date, pja_id)
        self.fac_id = to_nullable_string(fac_id)
        self.fac_name = to_nullable_string(fac_name)
        self.loc_id = to_nullable_string(loc_id)
        self.commercial_freq = to_nullable_string(commercial_freq)
        self.commercial_chart_flag = to_nullable_bool(commercial_chart_flag)
        self.mil_freq = to_nullable_string(mil_freq)
        self.mil_chart_flag = to_nullable_string(mil_chart_flag)
        self.sector = to_nullable_string(sector)
        self.contact_freq_altitude = to_nullable_string(contact_freq_altitude)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"FAC_ID={self.fac_id!r}, "
            f"FAC_NAME={self.fac_name!r}, "
            f"LOC_ID={self.loc_id!r}, "
            f"COMMERCIAL_FREQ={self.commercial_freq!r}, "
            f"COMMERCIAL_CHART_FLAG={self.commercial_chart_flag!r}, "
            f"MIL_FREQ={self.mil_freq!r}, "
            f"MIL_CHART_FLAG={self.mil_chart_flag!r}, "
            f"SECTOR={self.sector!r}, "
            f"CONTACT_FREQ_ALTITUDE={self.contact_freq_altitude!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "fac_id",
                "fac_name",
                "loc_id",
                "commercial_freq",
                "commercial_chart_flag",
                "mil_freq",
                "mil_chart_flag",
                "sector",
                "contact_freq_altitude",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "fac_id": self.fac_id,
            "fac_name": self.fac_name,
            "loc_id": self.loc_id,
            "commercial_freq": self.commercial_freq,
            "commercial_chart_flag": self.commercial_chart_flag,
            "mil_freq": self.mil_freq,
            "mil_chart_flag": self.mil_chart_flag,
            "sector": self.sector,
            "contact_freq_altitude": self.contact_freq_altitude,
        }
        return {**base_dict, **this_dict}
