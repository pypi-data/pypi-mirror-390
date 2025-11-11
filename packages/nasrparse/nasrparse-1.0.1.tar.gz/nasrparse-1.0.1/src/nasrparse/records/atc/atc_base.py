from nasrparse.functions import to_nullable_string
from nasrparse.records.types import AgencyTypeCode, FacilityOperatorCode, RegionCode

from ._base import Base


class ATC_BASE(Base):
    icao_id: str | None
    """ICAO Identifier"""
    facility_name: str | None
    """Official Facility Name"""
    region_code: RegionCode
    """FAA Region Code."""
    twr_operator_code: FacilityOperatorCode
    """Operator Code of the Agency that Operates the Tower."""
    twr_call: str | None
    """Radio Call used by Pilot to Contact Tower."""
    twr_hrs: str | None
    """Hours of Tower Operation in Local Time."""
    primary_apch_radio_call: str | None
    """Radio Call of Facility That Furnishes Primary Approach Control."""
    apch_p_provider: str | None
    """Facility ID (or Provider Description when Provider Type equals 'S') of the Agency That Operates the Primary Approach Control Facility/Functions"""
    apch_p_prov_type_cd: AgencyTypeCode
    """Provider Agency Type Code for Agency that Operates the Primary Approach Control Facility/Functions."""
    secondary_apch_radio_call: str | None
    """Radio Call of Facility That Furnishes Secondary Approach Control."""
    apch_s_provider: str | None
    """Facility ID (or Provider Description when Provider Type equals 'S') of the Agency That Operates the Secondary Approach Control Facility/Functions"""
    apch_s_prov_type_cd: AgencyTypeCode
    """Provider Agency Type Code for Agency that Operates the Secondary Approach Control Facility/Functions."""
    primary_dep_radio_call: str | None
    """Radio Call of Facility That Furnishes Primary Departure Control."""
    dep_p_provider: str | None
    """Facility ID (or Provider Description when Provider Type equals 'S') of the Agency That Operates the Primary Departure Control Facility/Functions"""
    dep_p_prov_type_cd: AgencyTypeCode
    """Provider Agency Type Code for Agency that Operates the Primary Departure Control Facility/Functions."""
    secondary_dep_radio_call: str | None
    """Radio Call of Facility That Furnishes Secondary Departure Control."""
    dep_s_provider: str | None
    """Facility ID (or Provider Description when Provider Type equals 'S') of the Agency That Operates the Secondary Departure Control Facility/Functions"""
    dep_s_prov_type_cd: AgencyTypeCode
    """Provider Agency Type Code for Agency that Operates the Secondary Departure Control Facility/Functions."""
    ctl_fac_apch_dep_calls: str | None
    """Approach Departure Call associated with a Control Facility."""
    apch_dep_oper_code: FacilityOperatorCode
    """Agency Type Code that Operates the Control Facility"""
    ctl_prvding_hrs: str | None
    """Hours of Operation of the Primary Control Facility."""
    secondary_ctl_prvding_hrs: str | None
    """Hours of Operation of the Secondary Control Facility."""

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
        icao_id: str,
        facility_name: str,
        region_code: str,
        twr_operator_code: str,
        twr_call: str,
        twr_hrs: str,
        primary_apch_radio_call: str,
        apch_p_provider: str,
        apch_p_prov_type_cd: str,
        secondary_apch_radio_call: str,
        apch_s_provider: str,
        apch_s_prov_type_cd: str,
        primary_dep_radio_call: str,
        dep_p_provider: str,
        dep_p_prov_type_cd: str,
        secondary_dep_radio_call: str,
        dep_s_provider: str,
        dep_s_prov_type_cd: str,
        ctl_fac_apch_dep_calls: str,
        apch_dep_oper_code: str,
        ctl_prvding_hrs: str,
        secondary_ctl_prvding_hrs: str,
    ) -> None:
        super().__init__(
            "atc_comms",
            eff_date,
            site_no,
            site_type_code,
            facility_type,
            state_code,
            facility_id,
            city,
            country_code,
        )
        self.icao_id = to_nullable_string(icao_id)
        self.facility_name = to_nullable_string(facility_name)
        self.region_code = RegionCode.from_value(to_nullable_string(region_code))
        self.twr_operator_code = FacilityOperatorCode(
            to_nullable_string(twr_operator_code)
        )
        self.twr_call = to_nullable_string(twr_call)
        self.twr_hrs = to_nullable_string(twr_hrs)
        self.primary_apch_radio_call = to_nullable_string(primary_apch_radio_call)
        self.apch_p_provider = to_nullable_string(apch_p_provider)
        self.apch_p_prov_type_cd = AgencyTypeCode.from_value(
            to_nullable_string(apch_p_prov_type_cd)
        )
        self.secondary_apch_radio_call = to_nullable_string(secondary_apch_radio_call)
        self.apch_s_provider = to_nullable_string(apch_s_provider)
        self.apch_s_prov_type_cd = AgencyTypeCode.from_value(
            to_nullable_string(apch_s_prov_type_cd)
        )
        self.primary_dep_radio_call = to_nullable_string(primary_dep_radio_call)
        self.dep_p_provider = to_nullable_string(dep_p_provider)
        self.dep_p_prov_type_cd = AgencyTypeCode.from_value(
            to_nullable_string(dep_p_prov_type_cd)
        )
        self.secondary_dep_radio_call = to_nullable_string(secondary_dep_radio_call)
        self.dep_s_provider = to_nullable_string(dep_s_provider)
        self.dep_s_prov_type_cd = AgencyTypeCode.from_value(
            to_nullable_string(dep_s_prov_type_cd)
        )
        self.ctl_fac_apch_dep_calls = to_nullable_string(ctl_fac_apch_dep_calls)
        self.apch_dep_oper_code = FacilityOperatorCode.from_value(
            to_nullable_string(apch_dep_oper_code)
        )
        self.ctl_prvding_hrs = to_nullable_string(ctl_prvding_hrs)
        self.secondary_ctl_prvding_hrs = to_nullable_string(secondary_ctl_prvding_hrs)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"ICAO_ID={self.icao_id!r}, "
            f"FACILITY_NAME={self.facility_name!r}, "
            f"REGION_CODE={self.region_code!r}, "
            f"TWR_OPERATOR_CODE={self.twr_operator_code!r}, "
            f"TWR_CALL={self.twr_call!r}, "
            f"TWR_HRS={self.twr_hrs!r}, "
            f"PRIMARY_APCH_RADIO_CALL={self.primary_apch_radio_call!r}, "
            f"APCH_P_PROVIDER={self.apch_p_provider!r}, "
            f"APCH_P_PROV_TYPE_CD={self.apch_p_prov_type_cd!r}, "
            f"SECONDARY_APCH_RADIO_CALL={self.secondary_apch_radio_call!r}, "
            f"APCH_S_PROVIDER={self.apch_s_provider!r}, "
            f"APCH_S_PROV_TYPE_CD={self.apch_s_prov_type_cd!r}, "
            f"PRIMARY_DEP_RADIO_CALL={self.primary_dep_radio_call!r}, "
            f"DEP_P_PROVIDER={self.dep_p_provider!r}, "
            f"DEP_P_PROV_TYPE_CD={self.dep_p_prov_type_cd!r}, "
            f"SECONDARY_DEP_RADIO_CALL={self.secondary_dep_radio_call!r}, "
            f"DEP_S_PROVIDER={self.dep_s_provider!r}, "
            f"DEP_S_PROV_TYPE_CD={self.dep_s_prov_type_cd!r}, "
            f"CTL_FAC_APCH_DEP_CALLS={self.ctl_fac_apch_dep_calls!r}, "
            f"APCH_DEP_OPER_CODE={self.apch_dep_oper_code!r}, "
            f"CTL_PRVDING_HRS={self.ctl_prvding_hrs!r}, "
            f"SECONDARY_CTL_PRVDING_HRS={self.secondary_ctl_prvding_hrs!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "icao_id",
                "facility_name",
                "region_code",
                "twr_operator_code",
                "twr_call",
                "twr_hrs",
                "primary_apch_radio_call",
                "apch_p_provider",
                "apch_p_prov_type_cd",
                "secondary_apch_radio_call",
                "apch_s_provider",
                "apch_s_prov_type_cd",
                "primary_dep_radio_call",
                "dep_p_provider",
                "dep_p_prov_type_cd",
                "secondary_dep_radio_call",
                "dep_s_provider",
                "dep_s_prov_type_cd",
                "ctl_fac_apch_dep_calls",
                "apch_dep_oper_code",
                "ctl_prvding_hrs",
                "secondary_ctl_prvding_hrs",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "icao_id": self.icao_id,
            "facility_name": self.facility_name,
            "region_code": self.region_code.value if self.region_code else None,
            "twr_operator_code": (
                self.twr_operator_code.value if self.twr_operator_code else None
            ),
            "twr_call": self.twr_call,
            "twr_hrs": self.twr_hrs,
            "primary_apch_radio_call": self.primary_apch_radio_call,
            "apch_p_provider": self.apch_p_provider,
            "apch_p_prov_type_cd": (
                self.apch_p_prov_type_cd.value if self.apch_p_prov_type_cd else None
            ),
            "secondary_apch_radio_call": self.secondary_apch_radio_call,
            "apch_s_provider": self.apch_s_provider,
            "apch_s_prov_type_cd": (
                self.apch_s_prov_type_cd.value if self.dep_s_prov_type_cd else None
            ),
            "primary_dep_radio_call": self.primary_dep_radio_call,
            "dep_p_provider": self.dep_p_provider,
            "dep_p_prov_type_cd": (
                self.dep_p_prov_type_cd.value if self.dep_p_prov_type_cd else None
            ),
            "secondary_dep_radio_call": self.secondary_dep_radio_call,
            "dep_s_provider": self.dep_s_provider,
            "dep_s_prov_type_cd": (
                self.dep_s_prov_type_cd.value if self.dep_s_prov_type_cd else None
            ),
            "ctl_fac_apch_dep_calls": self.ctl_fac_apch_dep_calls,
            "apch_dep_oper_code": (
                self.apch_dep_oper_code.value if self.apch_dep_oper_code else None
            ),
            "ctl_prvding_hrs": self.ctl_prvding_hrs,
            "secondary_ctl_prvding_hrs": self.secondary_ctl_prvding_hrs,
        }
        return {**base_dict, **this_dict}
