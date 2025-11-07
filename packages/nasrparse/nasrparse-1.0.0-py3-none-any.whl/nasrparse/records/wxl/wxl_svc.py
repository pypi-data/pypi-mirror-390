from nasrparse.functions import to_nullable_string
from nasrparse.records.types import WeatherServiceCode

from ._base import Base


class WXL_SVC(Base):
    wea_svc_type_code: WeatherServiceCode
    """Weather Services Available at Location"""
    wea_affect_area: str | None
    """Affected State/Area. An Alphabetically Ordered Series of Two Character US State Post Office Abbreviations Separated by Commas. Values May Also Include LE, LH, LM, LO, LS for the Great Lakes (Erie, Huron, Michigan, Ontario, Superior)"""

    def __init__(
        self,
        eff_date: str,
        wea_id: str,
        city: str,
        state_code: str,
        country_code: str,
        wea_svc_type_code: str,
        wea_affect_area: str,
    ) -> None:
        super().__init__(
            "weather_services",
            eff_date,
            wea_id,
            city,
            state_code,
            country_code,
        )
        self.wea_svc_type_code = WeatherServiceCode.from_value(
            to_nullable_string(wea_svc_type_code)
        )
        self.wea_affect_area = to_nullable_string(wea_affect_area)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"WEA_SVC_TYPE_CODE={self.wea_svc_type_code!r}, "
            f"WEA_AFFECT_AREA={self.wea_affect_area!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "wea_svc_type_code",
                "wea_affect_area",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "wea_svc_type_code": (
                self.wea_svc_type_code.value if self.wea_svc_type_code else None
            ),
            "wea_affect_area": self.wea_affect_area,
        }
        return {**base_dict, **this_dict}
