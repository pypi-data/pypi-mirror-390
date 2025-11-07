from nasrparse.functions import to_nullable_int, to_nullable_string

from ._base import Base


class ATC_RMK(Base):
    legacy_element_number: str | None
    """Legacy Remark Element."""
    tab_name: str | None
    """NASR Table name associated with Remark."""
    ref_col_name: str | None
    """NASR Column name associated with Remark. ARPT_CTL_REMARKs are identified as ATC_REMARK. All other Non-specific remarks are identified as GENERAL_REMARK."""
    remark_no: int | None
    """Sequence number assigned to Reference Column Remark."""
    remark: str | None
    """Remark Text (Free Form Text that further describes a specific Information Item.)"""

    def __init__(
        self,
        eff_date: str,
        site_no: str,
        site_type_code: str,
        facility_type: str,
        state_code: str,
        facility_id: str,
        city: str,
        country_code: str,
        legacy_element_number: str,
        tab_name: str,
        ref_col_name: str,
        remark_no: str,
        remark: str,
    ) -> None:
        super().__init__(
            "atc_remarks",
            eff_date,
            site_no,
            site_type_code,
            facility_type,
            state_code,
            facility_id,
            city,
            country_code,
        )
        self.legacy_element_number = to_nullable_string(legacy_element_number)
        self.tab_name = to_nullable_string(tab_name)
        self.ref_col_name = to_nullable_string(ref_col_name)
        self.remark_no = to_nullable_int(remark_no)
        self.remark = to_nullable_string(remark)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"LEGACY_ELEMENT_NUMBER={self.legacy_element_number!r}, "
            f"TAB_NAME={self.tab_name!r}, "
            f"REF_COL_NAME={self.ref_col_name!r}, "
            f"REMARK_NO={self.remark_no!r}, "
            f"REMARK={self.remark!r}"
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
                "remark_no",
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
            "remark_no": self.remark_no,
            "remark": self.remark,
        }
        return {**base_dict, **this_dict}
