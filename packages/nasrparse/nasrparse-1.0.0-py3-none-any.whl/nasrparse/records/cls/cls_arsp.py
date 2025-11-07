from nasrparse.functions import to_nullable_bool, to_nullable_string

from ._base import Base


class CLS_ARSP(Base):
    class_b_airspace: bool | None
    """Terminal Communication Facility containing Class B Airspace with be designated with 'Y' else null."""
    class_c_airspace: bool | None
    """Terminal Communication Facility containing Class C Airspace with be designated with 'Y' else null."""
    class_d_airspace: bool | None
    """Terminal Communication Facility containing Class D Airspace with be designated with 'Y' else null."""
    class_e_airspace: bool | None
    """Terminal Communication Facility containing Class E Airspace with be designated with 'Y' else null."""
    airspace_hrs: str | None
    """Airspace Hours of Terminal Communication Facility."""
    remark: str | None
    """Remark associated with Class Airspace."""

    def __init__(
        self,
        eff_date: str,
        site_no: str,
        site_type_code: str,
        state_code: str,
        arpt_id: str,
        city: str,
        country_code: str,
        class_b_airspace: str,
        class_c_airspace: str,
        class_d_airspace: str,
        class_e_airspace: str,
        airspace_hrs: str,
        remark: str,
    ) -> None:
        super().__init__(
            "classed_airspace",
            eff_date,
            site_no,
            site_type_code,
            state_code,
            arpt_id,
            city,
            country_code,
        )
        self.class_b_airspace = to_nullable_bool(class_b_airspace)
        self.class_c_airspace = to_nullable_bool(class_c_airspace)
        self.class_d_airspace = to_nullable_bool(class_d_airspace)
        self.class_e_airspace = to_nullable_bool(class_e_airspace)
        self.airspace_hrs = to_nullable_string(airspace_hrs)
        self.remark = to_nullable_string(remark)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"CLASS_B_AIRSPACE={self.class_b_airspace!r}, "
            f"CLASS_C_AIRSPACE={self.class_c_airspace!r}, "
            f"CLASS_D_AIRSPACE={self.class_d_airspace!r}, "
            f"CLASS_E_AIRSPACE={self.class_e_airspace!r}, "
            f"AIRSPACE_HRS={self.airspace_hrs!r}, "
            f"REMARK={self.remark!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "class_b_airspace",
                "class_c_airspace",
                "class_d_airspace",
                "class_e_airspace",
                "airspace_hrs",
                "remark",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "class_b_airspace": self.class_b_airspace,
            "class_c_airspace": self.class_c_airspace,
            "class_d_airspace": self.class_d_airspace,
            "class_e_airspace": self.class_e_airspace,
            "airspace_hrs": self.airspace_hrs,
            "remark": self.remark,
        }
        return {**base_dict, **this_dict}
