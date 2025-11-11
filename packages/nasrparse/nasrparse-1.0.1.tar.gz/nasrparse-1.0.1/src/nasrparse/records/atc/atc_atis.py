from nasrparse.functions import to_nullable_string

from ._base import Base


class ATC_ATIS(Base):
    atis_no: str | None
    """ATIS Serial Number."""
    description: str | None
    """Optional Description of Purpose, Fulfilled by ATIS."""
    atis_hrs: str | None
    """ATIS Hours of Operation in Local Time."""
    atis_phone_no: str | None
    """ATIS Phone Number."""

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
        atis_no: str,
        description: str,
        atis_hrs: str,
        atis_phone_no: str,
    ) -> None:
        super().__init__(
            "atc_atis",
            eff_date,
            site_no,
            site_type_code,
            facility_type,
            state_code,
            facility_id,
            city,
            country_code,
        )
        self.atis_no = to_nullable_string(atis_no)
        self.description = to_nullable_string(description)
        self.atis_hrs = to_nullable_string(atis_hrs)
        self.atis_phone_no = to_nullable_string(atis_phone_no)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"ATIS_NO={self.atis_no!r}, "
            f"DESCRIPTION={self.description!r}, "
            f"ATIS_HRS={self.atis_hrs!r}, "
            f"ATIS_PHONE_NO={self.atis_phone_no!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "atis_no",
                "description",
                "atis_hrs",
                "atis_phone_no",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "atis_no": self.atis_no,
            "description": self.description,
            "atis_hrs": self.atis_hrs,
            "atis_phone_no": self.atis_phone_no,
        }
        return {**base_dict, **this_dict}
