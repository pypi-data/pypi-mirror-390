from nasrparse.functions import to_nullable_bool, to_nullable_int, to_nullable_string

from ._base import Base


class MAA_CON(Base):
    freq_seq: int | None
    """Unique Sequence number for Frequency Contact entries"""
    fac_id: str | None
    """Contact Facility Identifier"""
    fac_name: str | None
    """Contact Facility Name"""
    commercial_freq: str | None
    """Commercial Frequency"""
    commercial_chart_flag: bool | None
    """Commercial Chart Flag"""
    mil_freq: str | None
    """Military Frequency"""
    mil_chart_flag: bool | None
    """Military Chart Flag"""

    def __init__(
        self,
        eff_date: str,
        maa_id: str,
        freq_seq: str,
        fac_id: str,
        fac_name: str,
        commercial_freq: str,
        commercial_chart_flag: str,
        mil_freq: str,
        mil_chart_flag: str,
    ) -> None:
        super().__init__(
            "misc_activity_contacts",
            eff_date,
            maa_id,
        )
        self.freq_seq = to_nullable_int(freq_seq)
        self.fac_id = to_nullable_string(fac_id)
        self.fac_name = to_nullable_string(fac_name)
        self.commercial_freq = to_nullable_string(commercial_freq)
        self.commercial_chart_flag = to_nullable_bool(commercial_chart_flag)
        self.mil_freq = to_nullable_string(mil_freq)
        self.mil_chart_flag = to_nullable_bool(mil_chart_flag)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"FREQ_SEQ={self.freq_seq!r}, "
            f"FAC_ID={self.fac_id!r}, "
            f"FAC_NAME={self.fac_name!r}, "
            f"COMMERCIAL_FREQ={self.commercial_freq!r}, "
            f"COMMERCIAL_CHART_FLAG={self.commercial_chart_flag!r}, "
            f"MIL_FREQ={self.mil_freq!r}, "
            f"MIL_CHART_FLAG={self.mil_chart_flag!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "freq_seq",
                "fac_id",
                "fac_name",
                "commercial_freq",
                "commercial_chart_flag",
                "mil_freq",
                "mil_chart_flag",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "freq_seq": self.freq_seq,
            "fac_id": self.fac_id,
            "fac_name": self.fac_name,
            "commercial_freq": self.commercial_freq,
            "commercial_chart_flag": self.commercial_chart_flag,
            "mil_freq": self.mil_freq,
            "mil_chart_flag": self.mil_chart_flag,
        }
        return {**base_dict, **this_dict}
