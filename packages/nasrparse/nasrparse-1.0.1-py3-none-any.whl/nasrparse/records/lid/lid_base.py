from nasrparse.functions import to_nullable_string
from nasrparse.records.types._base_enum import BaseEnum
from nasrparse.records.types import (
    CommunicationOutletCode,
    ControlFacilityCode,
    FSSTypeCode,
    ILSCode,
    LIDGroupCode,
    PointCode,
    SiteTypeCode,
    SpecialUseCode,
    WeatherSensorCode,
    WeatherStationCode,
)

from ._base import Base

from enum import Enum


class LID_BASE(Base):
    lid_group: LIDGroupCode
    """Logical grouping of LID entries."""
    fac_type: Enum
    """Facility Type of Location Identifier Record"""
    fac_name: str | None
    """Official Facility Name. Instrument Landing System Facility Name is a concatenation of the Associated Landing Facility Name, ID and Runway End ID (e.g. ATLANTIC CITY INTL(ACY) ILS RWY 31) LID"""
    resp_artcc_id: str | None
    """Responsible FAA Air Route Traffic Control Center (ARTCC) Identifier"""
    artcc_computer_id: str | None
    """Responsible ARTCC Computer Identifier"""
    fss_id: str | None
    """Tie-In Flight Service Station (FSS) Identifier"""

    def __init__(
        self,
        eff_date: str,
        country_code: str,
        loc_id: str,
        region_code: str,
        state_code: str,
        city: str,
        lid_group: str,
        fac_type: str,
        fac_name: str,
        resp_artcc_id: str,
        artcc_computer_id: str,
        fss_id: str,
    ) -> None:
        super().__init__(
            "location_identifiers",
            eff_date,
            country_code,
            loc_id,
            region_code,
            state_code,
            city,
        )
        self.lid_group = LIDGroupCode.from_value(to_nullable_string(lid_group))
        self.fac_type = self.__find_matching_enum(to_nullable_string(fac_type))
        self.fac_name = to_nullable_string(fac_name)
        self.resp_artcc_id = to_nullable_string(resp_artcc_id)
        self.artcc_computer_id = to_nullable_string(artcc_computer_id)
        self.fss_id = to_nullable_string(fss_id)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"LID_GROUP={self.lid_group!r}, "
            f"FAC_TYPE={self.fac_type!r}, "
            f"FAC_NAME={self.fac_name!r}, "
            f"RESP_ARTCC_ID={self.resp_artcc_id!r}, "
            f"ARTCC_COMPUTER_ID={self.artcc_computer_id!r}, "
            f"FSS_ID={self.fss_id!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "lid_group",
                "fac_type",
                "fac_name",
                "resp_artcc_id",
                "artcc_computer_id",
                "fss_id",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "lid_group": self.lid_group.value if self.lid_group else None,
            "fac_type": self.fac_type.value if self.fac_type else None,
            "fac_name": self.fac_name,
            "resp_artcc_id": self.resp_artcc_id,
            "artcc_computer_id": self.artcc_computer_id,
            "fss_id": self.fss_id,
        }
        return {**base_dict, **this_dict}

    def __find_matching_enum(self, str_value: str | None) -> Enum:
        if str_value is None:
            return WeatherSensorCode.NULL  # Generic "NULL" from smallest Enum

        possible_enums: list[type[BaseEnum]] = [
            CommunicationOutletCode,
            ControlFacilityCode,
            FSSTypeCode,
            ILSCode,
            LIDGroupCode,
            PointCode,
            SiteTypeCode,
            SpecialUseCode,
            WeatherSensorCode,
            WeatherStationCode,
        ]

        for item in possible_enums:
            result = item.from_value(str_value)
            if result.value != None:
                return result

        return WeatherSensorCode.NULL  # Generic "NULL" from smallest Enum
