from nasrparse.functions.record import to_nullable_int, to_nullable_string

from ._base import Base


class APT_RMK(Base):
    legacy_element_number: str | None
    """Legacy Remark Element Number. The Legacy element number field is equivalent to the LEGACY_ELEMENT_NAME field referenced in the TXT APT.txt NASR Subscriber File."""
    tab_name: str | None
    """NASR Table name associated with Remark."""
    ref_col_name: str | None
    """NASR Column name associated with Remark. Non-specific remarks are identified as GENERAL_REMARK."""
    element: str | None
    """Specific Element that Remark Text Pertains to. Not all Tables require Element to be Unique."""
    ref_col_seq_no: int | None
    """Sequence number assigned to Reference Column Remark."""
    remark: str | None
    """Remark Text (Free Form Text that further describes a specific Information Item.)"""

    def __init__(
        self,
        eff_date: str,
        site_no: str,
        site_type_code: str,
        state_code: str,
        arpt_id: str,
        city: str,
        country_code: str,
        legacy_element_number: str,
        tab_name: str,
        ref_col_name: str,
        element: str,
        ref_col_seq_no: str,
        remark: str,
    ) -> None:
        super().__init__(
            "airport_remark",
            eff_date,
            site_no,
            site_type_code,
            state_code,
            arpt_id,
            city,
            country_code,
        )
        self.legacy_element_number = to_nullable_string(legacy_element_number)
        self.tab_name = to_nullable_string(tab_name)
        self.ref_col_name = to_nullable_string(ref_col_name)
        self.element = to_nullable_string(element)
        self.ref_col_seq_no = to_nullable_int(ref_col_seq_no)
        self.remark = to_nullable_string(remark)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"LEGACY_ELEMENT_NUMBER={self.legacy_element_number!r}, "
            f"TAB_NAME={self.tab_name!r}, "
            f"REF_COL_NAME={self.ref_col_name!r}, "
            f"ELEMENT={self.element!r}, "
            f"REF_COL_SEQ_NO={self.ref_col_seq_no!r}, "
            f"REMARK={self.remark!r}, "
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "legacy_element_number",
                "tab_name",
                "ref_col_name",
                "element",
                "ref_col_seq_no",
                "remark",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "legacy_element_number": self.legacy_element_number,
            "tab_name": self.tab_name,
            "ref_col_name": self.ref_col_name,
            "element": self.element,
            "ref_col_seq_no": self.ref_col_seq_no,
            "remark": self.remark,
        }
        return {**base_dict, **this_dict}
