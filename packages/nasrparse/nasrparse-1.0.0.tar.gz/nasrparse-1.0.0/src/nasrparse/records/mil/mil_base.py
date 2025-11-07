from nasrparse.functions import to_nullable_string
from nasrparse.records.types import FacilityOperatorCode

from ._base import Base


class MIL_BASE(Base):
    mil_ops_oper_code: FacilityOperatorCode
    """Military Agency Type Code that Operates the Control Facility."""
    mil_ops_call: str | None
    """Radio Call Name for Military Operations at this Control Facility."""
    mil_ops_hrs: str | None
    """Hours of Military Operations Conducted each Day."""
    amcp_hrs: str | None
    """Hours of Operation of the Military Aircraft Command Post (AMCP) Located At the Facility."""
    pmsv_hrs: str | None
    """Hours Of Operation Of The Military Pilot-To-Metro Service (PMSV) Located At The Facility."""
    remark: str | None
    """Remark associated with Military Operations."""

    def __init__(
        self,
        eff_date: str,
        site_no: str,
        site_type_code: str,
        state_code: str,
        arpt_id: str,
        city: str,
        country_code: str,
        mil_ops_oper_code: str,
        mil_ops_call: str,
        mil_ops_hrs: str,
        amcp_hrs: str,
        pmsv_hrs: str,
        remark: str,
    ) -> None:
        super().__init__(
            "military_operations",
            eff_date,
            site_no,
            site_type_code,
            state_code,
            arpt_id,
            city,
            country_code,
        )
        self.mil_ops_oper_code = FacilityOperatorCode.from_value(
            to_nullable_string(mil_ops_oper_code)
        )
        self.mil_ops_call = to_nullable_string(mil_ops_call)
        self.mil_ops_hrs = to_nullable_string(mil_ops_hrs)
        self.amcp_hrs = to_nullable_string(amcp_hrs)
        self.pmsv_hrs = to_nullable_string(pmsv_hrs)
        self.remark = to_nullable_string(remark)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"MIL_OPS_OPER_CODE={self.mil_ops_oper_code!r}, "
            f"MIL_OPS_CALL={self.mil_ops_call!r}, "
            f"MIL_OPS_HRS={self.mil_ops_hrs!r}, "
            f"AMCP_HRS={self.amcp_hrs!r}, "
            f"PMSV_HRS={self.pmsv_hrs!r}, "
            f"REMARK={self.remark!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "mil_ops_oper_code",
                "mil_ops_call",
                "mil_ops_hrs",
                "amcp_hrs",
                "pmsv_hrs",
                "remark",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "mil_ops_oper_code": (
                self.mil_ops_oper_code.value if self.mil_ops_oper_code else None
            ),
            "mil_ops_call": self.mil_ops_call,
            "mil_ops_hrs": self.mil_ops_hrs,
            "amcp_hrs": self.amcp_hrs,
            "pmsv_hrs": self.pmsv_hrs,
            "remark": self.remark,
        }
        return {**base_dict, **this_dict}
