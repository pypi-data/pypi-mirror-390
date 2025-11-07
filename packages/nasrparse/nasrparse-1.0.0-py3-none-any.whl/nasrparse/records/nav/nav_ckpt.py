from nasrparse.functions import to_nullable_int, to_nullable_string
from nasrparse.records.types import AirGroundCode

from ._base import Base


class NAV_CKPT(Base):
    altitude: str | None
    """Altitude Only When Checkpoint is in Air"""
    brg: int | None
    """Bearing of Checkpoint"""
    air_gnd_code: AirGroundCode
    """Air/Ground code - A=AIR, G=GROUND, G1=GROUND ONE"""
    chk_desc: str | None
    """Narrative Description Associated with the Checkpoint in AIR/Ground"""
    arpt_id: str | None
    """Airport ID"""
    state_chk_code: str | None
    """State Code in Which Associated City is Located"""

    def __init__(
        self,
        eff_date: str,
        nav_id: str,
        nav_type: str,
        state_code: str,
        city: str,
        country_code: str,
        altitude: str,
        brg: str,
        air_gnd_code: str,
        chk_desc: str,
        arpt_id: str,
        state_chk_code: str,
    ) -> None:
        super().__init__(
            "navaid_checkpoints",
            eff_date,
            nav_id,
            nav_type,
            state_code,
            city,
            country_code,
        )
        self.altitude = to_nullable_string(altitude)
        self.brg = to_nullable_int(brg)
        self.air_gnd_code = AirGroundCode.from_value(to_nullable_string(air_gnd_code))
        self.chk_desc = to_nullable_string(chk_desc)
        self.arpt_id = to_nullable_string(arpt_id)
        self.state_chk_code = to_nullable_string(state_chk_code)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"ALTITUDE={self.altitude!r}, "
            f"BRG={self.brg!r}, "
            f"AIR_GND_CODE={self.air_gnd_code!r}, "
            f"CHK_DESC={self.chk_desc!r}, "
            f"ARPT_ID={self.arpt_id!r}, "
            f"STATE_CHK_CODE={self.state_chk_code!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "altitude",
                "brg",
                "air_gnd_code",
                "chk_desc",
                "arpt_id",
                "state_chk_code",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "altitude": self.altitude,
            "brg": self.brg,
            "air_gnd_code": self.air_gnd_code.value if self.air_gnd_code else None,
            "chk_desc": self.chk_desc,
            "arpt_id": self.arpt_id,
            "state_chk_code": self.state_chk_code,
        }
        return {**base_dict, **this_dict}
