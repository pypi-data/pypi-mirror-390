from nasrparse.functions import to_nullable_string

from ._base import Base


class ATC_SVC(Base):
    ctl_svc: str | None
    """Services Provided to Satellite Airport."""

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
        ctl_svc: str,
    ) -> None:
        super().__init__(
            "atc_services",
            eff_date,
            site_no,
            site_type_code,
            facility_type,
            state_code,
            facility_id,
            city,
            country_code,
        )
        self.ctl_svc = to_nullable_string(ctl_svc)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"CTL_SVC={self.ctl_svc!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "ctl_svc",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "ctl_svc": self.ctl_svc,
        }
        return {**base_dict, **this_dict}
