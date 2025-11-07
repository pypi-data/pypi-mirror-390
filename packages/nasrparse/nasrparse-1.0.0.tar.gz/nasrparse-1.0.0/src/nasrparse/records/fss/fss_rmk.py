from nasrparse.functions import to_nullable_int, to_nullable_string

from ._base import Base


class FSS_RMK(Base):
    ref_col_name: str | None
    """NASR Column name associated with Remark. Non-specific remarks identified as GENERAL_REMARK."""
    ref_col_seq_no: int | None
    """Sequence number assigned to Reference Column Remark"""
    remark: str | None
    """Remark Text (Free Form Text that further describes a specific Information Item.)"""

    def __init__(
        self,
        eff_date: str,
        fss_id: str,
        name: str,
        city: str,
        state_code: str,
        country_code: str,
        ref_col_name: str,
        ref_col_seq_no: str,
        remark: str,
    ) -> None:
        super().__init__(
            "flight_service_remarks",
            eff_date,
            fss_id,
            name,
            city,
            state_code,
            country_code,
        )
        self.ref_col_name = to_nullable_string(ref_col_name)
        self.ref_col_seq_no = to_nullable_int(ref_col_seq_no)
        self.remark = to_nullable_string(remark)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"REF_COL_NAME={self.ref_col_name!r}, "
            f"REF_COL_SEQ_NO={self.ref_col_seq_no!r}, "
            f"REMARK={self.remark!r}, "
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "ref_col_name",
                "ref_col_seq_no",
                "remark",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "ref_col_name": self.ref_col_name,
            "ref_col_seq_no": self.ref_col_seq_no,
            "remark": self.remark,
        }
        return {**base_dict, **this_dict}
