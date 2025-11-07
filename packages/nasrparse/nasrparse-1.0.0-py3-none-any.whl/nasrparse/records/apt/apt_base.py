from nasrparse.functions import (
    to_nullable_bool,
    to_nullable_date,
    to_nullable_float,
    to_nullable_int,
    to_nullable_string,
)
from nasrparse.records.types import (
    ASPCode,
    BeaconColorCode,
    DirectionCode,
    FuelCode,
    HemisCode,
    InspectionMethodCode,
    InspectorCode,
    LightScheduleCode,
    MagVarCode,
    MethodCode,
    NASPCode,
    OwnershipCode,
    OxygenCode,
    RegionCode,
    SegmentedCircleCode,
    SERCode,
    ServiceCode,
    StatusCode,
    TowerCode,
    UseCode,
    WindIndicatorCode,
)

from ._base import Base

from datetime import date


class APT_BASE(Base):
    region_code: RegionCode
    """FAA Region Code"""
    ado_code: str | None
    """FAA District or Field Office Code"""
    state_name: str | None
    """Associated State Name"""
    county_name: str | None
    """Associated County or Parish Name (For Non-Us Aerodromes This May Be Territory Or Province Name.)"""
    county_assoc_state: str | None
    """Associated County's State (Post Office Code) State where the Associated County is located; may not be the same as the Associated City's State Code. For non-US Aerodrome Facilities, these "State" Codes are internal to this system and may not correspond to standard State or Country Codes in use elsewhere."""
    arpt_name: str | None
    """Official Facility Name"""
    ownership_type_code: OwnershipCode
    """Airport Ownership Type"""
    facility_use_code: UseCode
    """Facility Use"""
    lat_deg: int | None
    """Airport Reference Point Latitude Degrees"""
    lat_min: int | None
    """Airport Reference Point Latitude Minutes"""
    lat_sec: float | None
    """Airport Reference Point Latitude Seconds"""
    lat_hemis: HemisCode
    """Airport Reference Point Latitude Hemisphere"""
    lat_decimal: float | None
    """Airport Reference Point Latitude in Decimal Format"""
    lon_deg: int | None
    """Airport Reference Point Longitude Degrees"""
    lon_min: int | None
    """Airport Reference Point Longitude Minutes"""
    lon_sec: float | None
    """Airport Reference Point Longitude Seconds"""
    lon_hemis: HemisCode
    """Airport Reference Point Longitude Hemisphere"""
    lon_decimal: float | None
    """Airport Reference Point Longitude in Decimal Format"""
    survey_method_code: MethodCode
    """Airport Reference Point Determination Method"""
    elev: float | None
    """Airport Elevation (Nearest Tenth of a Foot MSL) Elevation is measured at the highest point on the centerline of the usable landing surface."""
    elev_method_code: MethodCode
    """Airport Elevation Determination Method"""
    mag_varn: int | None
    """Magnetic Variation"""
    mag_hemis: MagVarCode
    """Magnetic Variation Direction"""
    mag_varn_year: int | None
    """Magnetic Variation Epoch Year"""
    tpa: int | None
    """Traffic Pattern Altitude (Whole Feet AGL)"""
    chart_name: str | None
    """Aeronautical Sectional Chart on Which Facility Appears"""
    dist_city_to_airport: int | None
    """Distance from Central Business District of the Associated City to the Airport"""
    direction_code: DirectionCode
    """Direction of Airport from Central Business District of Associated City (Nearest 1/8 Compass Point)"""
    acreage: int | None
    """Land Area Covered by Airport (Acres)"""
    resp_artcc_id: str | None
    """Responsible ARTCC Identifier (The Responsible ARTCC Is The FAA Air Route Traffic Control Center Who Has Control Over The Airport.)"""
    computer_id: str | None
    """Responsible ARTCC (FAA) Computer Identifier"""
    artcc_name: str | None
    """Responsible ARTCC Name"""
    fss_on_arpt_flag: bool | None
    """Tie-In FSS Physically Located On Facility"""
    fss_id: str | None
    """Tie-In Flight Service Station (FSS) Identifier"""
    fss_name: str | None
    """Tie-In FSS Name"""
    phone_no: str | None
    """Local Phone Number from Airport to FSS for Administrative Services"""
    toll_free_no: str | None
    """Toll Free Phone Number from Airport to FSS for Pilot Briefing Services"""
    alt_fss_id: str | None
    """Alternate FSS Identifier provides the identifier of a full-time Flight Service Station that assumes responsibility for the Airport during the off hours of a part-time primary FSS."""
    alt_fss_name: str | None
    """Alternate FSS Name"""
    alt_toll_free_no: str | None
    """Toll Free Phone Number from Airport to Alternate FSS for Pilot Briefing Services"""
    notam_id: str | None
    """Identifier of the Facility responsible for issuing Notices to Airmen (NOTAMS) and Weather information for the Airport"""
    notam_flag: bool | None
    """Availability of NOTAM 'D' Service at Airport"""
    activation_date: date | None
    """Airport Activation Date (YYYY/MM) provides the YEAR and MONTH that the Facility was added to the NFDC airport database. Note: this information is only available for those Facilities opened since 1981."""
    arpt_status: StatusCode
    """Airport Status Code"""
    far_139_type_code: str | None
    """Airport ARFF Certification Type Code. Format is the class code ('I', 'II', 'III', or 'IV') followed by a one character code A, B, C, D, E, or L. Codes A, B, C, D, E are for Airports having a full certificate under CFR PART 139, and identifies the Aircraft Rescue and Firefighting index for the Airport. Code L is for Airports having limited certification under CFR PART 139. Blank indicates the Facility is not certificated."""
    far_139_carrier_ser_code: str | None
    """Airport ARFF Certification Carrier Service Code. Code S is for Airports receiving scheduled Air Carrier Service from carriers certificated by the Civil Aeronautics Board. Code U is for Airports not receiving this scheduled service."""
    arff_cert_type_date: date | None
    """Airport ARFF Certification Date (YYYY/MM)"""
    nasp_code: NASPCode
    """NPIAS/Federal Agreements Code. A Combination of 1 to 7 Codes that Indicate the Type of Federal Agreements existing at the Airport."""
    asp_anlys_dtrm_code: ASPCode
    """Airport Airspace Analysis Determination"""
    cust_flag: bool | None
    """Facility has been designated by the U.S. Department of Homeland Security as an International Airport of Entry for Customs"""
    lndg_rights_flag: bool | None
    """Facility has been designated by the U.S. Department of Homeland Security as a Customs Landing Rights Airport. (Customs User Fee Airports will be designated with an E80, E80A, or E80C referenced remark "US CUSTOMS USER FEE ARPT.")"""
    joint_use_flag: bool | None
    """Facility has Military/Civil Joint Use Agreement that allows Civil Operations at a Military Airport."""
    mil_lndg_flag: bool | None
    """Airport has entered into an Agreement that Grants Landing Rights to the Military"""
    inspect_method_code: InspectionMethodCode
    """Airport Inspection Method"""
    inspector_code: InspectorCode
    """Agency/Group Performing Physical Inspection"""
    last_inspection: date | None
    """Last Physical Inspection Date (YYYY/MM/DD)"""
    last_info_response: date | None
    """ Last Date Information Request was completed by Facility Owner or Manager (YYYY/MM/DD)"""
    fuel_types: list[FuelCode]
    """Fuel Types available for public use at the Airport."""
    airframe_repair_ser_code: SERCode
    """Airframe Repair Service Availability/Type"""
    pwr_plant_repair_ser: SERCode
    """Power Plant (Engine) Repair Availability/Type"""
    bottled_oxy_type: OxygenCode
    """Type of Bottled Oxygen Available (Value represents High and/or Low Pressure Replacement Bottle)"""
    bulk_oxy_type: OxygenCode
    """Type of Bulk Oxygen Available (Value represents High and/or Low Pressure Cylinders)"""
    lgt_sked: LightScheduleCode
    """Airport Lighting Schedule value is the beginning-ending times (local time) that the Standard Airport Lights are operated. Value can be "SS-SR" (indicating sunset-sunrise), blank, or "SEE RMK", indicating that the details are in a facility remark data entry."""
    bcn_lgt_sked: LightScheduleCode
    """Beacon Lighting Schedule value is the beginning-ending times (local time) that the Rotating Airport Beacon Light is operated. Value can be "SS-SR" (indicating sunset-sunrise), blank, or "SEE RMK", indicating that the details are in a facility remark data entry."""
    twr_type_code: TowerCode
    """Air Traffic Control Tower Facility Type (ATCT, NON-ATCT, ATCT-A/C, ATCT-RAPCON, ATCT-RATCF, ATCT-TRACON, TRACON). NON-ATCT is equivalent to “N” ATC TOWER at Airport. All Other are equivalent to “Y” ATC TOWER at AIRPORT."""
    seg_circle_mkr_flag: SegmentedCircleCode
    """Segmented Circle Airport Marker System on the Airport"""
    bcn_lens_color: BeaconColorCode
    """Lens Color of Operable Beacon located on the Airport."""
    lndg_fee_flag: bool | None
    """Landing Fee charged to Non-Commercial Users of Airport"""
    medical_use_flag: bool | None
    """Landing Facility Is used for Medical Purposes"""
    arpt_psn_source: str | None
    """Airport Position Source"""
    position_src_date: date | None
    """Airport Position Source Date (YYYY/MM/DD)"""
    arpt_elev_source: str | None
    """Airport Elevation Source"""
    elevation_src_date: date | None
    """Airport Elevation Source Date (YYYY/MM/DD)"""
    contr_fuel_avbl: bool | None
    """Contract Fuel Available"""
    trns_strg_buoy_flag: bool | None
    """Buoy Transient Storage Facilities"""
    trns_strg_hgr_flag: bool | None
    """Hangar Transient Storage Facilities"""
    trns_strg_tie_flag: bool | None
    """Tie-Down Transient Storage Facilities"""
    other_services: list[ServiceCode]
    """Other Airport Services Available. A Comma-Separated List of Other Airport Services Available at the Airport"""
    wind_indcr_flag: WindIndicatorCode
    """Wind Indicator shows whether a Wind Indicator exists at the Airport"""
    icao_id: str | None
    """ICAO Identifier"""
    min_op_network: bool | None
    """ Minimum Operational Network (MON)"""
    user_fee_flag: str | None
    """If Flag is checked in NASR, User Fee Airports Will Be Designated With Text "US CUSTOMS USER FEE ARPT."""
    cta: str | None
    """Cold Temperature Airport. Altitude Correction Required At or Below Temperature Given in Celsius."""

    def __init__(
        self,
        eff_date: str,
        site_no: str,
        site_type_code: str,
        state_code: str,
        arpt_id: str,
        city: str,
        country_code: str,
        region_code: str,
        ado_code: str,
        state_name: str,
        county_name: str,
        county_assoc_state: str,
        arpt_name: str,
        ownership_type_code: str,
        facility_use_code: str,
        lat_deg: str,
        lat_min: str,
        lat_sec: str,
        lat_hemis: str,
        lat_decimal: str,
        lon_deg: str,
        lon_min: str,
        lon_sec: str,
        lon_hemis: str,
        lon_decimal: str,
        survey_method_code: str,
        elev: str,
        elev_method_code: str,
        mag_varn: str,
        mag_hemis: str,
        mag_varn_year: str,
        tpa: str,
        chart_name: str,
        dist_city_to_airport: str,
        direction_code: str,
        acreage: str,
        resp_artcc_id: str,
        computer_id: str,
        artcc_name: str,
        fss_on_arpt_flag: str,
        fss_id: str,
        fss_name: str,
        phone_no: str,
        toll_free_no: str,
        alt_fss_id: str,
        alt_fss_name: str,
        alt_toll_free_no: str,
        notam_id: str,
        notam_flag: str,
        activation_date: str,
        arpt_status: str,
        far_139_type_code: str,
        far_139_carrier_ser_code: str,
        arff_cert_type_date: str,
        nasp_code: str,
        asp_anlys_dtrm_code: str,
        cust_flag: str,
        lndg_rights_flag: str,
        joint_use_flag: str,
        mil_lndg_flag: str,
        inspect_method_code: str,
        inspector_code: str,
        last_inspection: str,
        last_info_response: str,
        fuel_types: str,
        airframe_repair_ser_code: str,
        pwr_plant_repair_ser: str,
        bottled_oxy_type: str,
        bulk_oxy_type: str,
        lgt_sked: str,
        bcn_lgt_sked: str,
        twr_type_code: str,
        seg_circle_mkr_flag: str,
        bcn_lens_color: str,
        lndg_fee_flag: str,
        medical_use_flag: str,
        arpt_psn_source: str,
        position_src_date: str,
        arpt_elev_source: str,
        elevation_src_date: str,
        contr_fuel_avbl: str,
        trns_strg_buoy_flag: str,
        trns_strg_hgr_flag: str,
        trns_strg_tie_flag: str,
        other_services: str,
        wind_indcr_flag: str,
        icao_id: str,
        min_op_network: str,
        user_fee_flag: str,
        cta: str,
    ) -> None:
        super().__init__(
            "airports",
            eff_date,
            site_no,
            site_type_code,
            state_code,
            arpt_id,
            city,
            country_code,
        )
        self.region_code = RegionCode.from_value(to_nullable_string(region_code))
        self.ado_code = to_nullable_string(ado_code)
        self.state_name = to_nullable_string(state_name)
        self.county_name = to_nullable_string(county_name)
        self.county_assoc_state = to_nullable_string(county_assoc_state)
        self.arpt_name = to_nullable_string(arpt_name)
        self.ownership_type_code = OwnershipCode.from_value(
            to_nullable_string(ownership_type_code)
        )
        self.facility_use_code = UseCode.from_value(
            to_nullable_string(facility_use_code)
        )
        self.lat_deg = to_nullable_int(lat_deg)
        self.lat_min = to_nullable_int(lat_min)
        self.lat_sec = to_nullable_float(lat_sec)
        self.lat_hemis = HemisCode.from_value(to_nullable_string(lat_hemis))
        self.lat_decimal = to_nullable_float(lat_decimal)
        self.lon_deg = to_nullable_int(lon_deg)
        self.lon_min = to_nullable_int(lon_min)
        self.lon_sec = to_nullable_float(lon_sec)
        self.lon_hemis = HemisCode.from_value(to_nullable_string(lon_hemis))
        self.lon_decimal = to_nullable_float(lon_decimal)
        self.survey_method_code = MethodCode.from_value(
            to_nullable_string(survey_method_code)
        )
        self.elev = to_nullable_float(elev)
        self.elev_method_code = MethodCode.from_value(
            to_nullable_string(elev_method_code)
        )
        self.mag_varn = to_nullable_int(mag_varn)
        self.mag_hemis = MagVarCode.from_value(to_nullable_string(mag_hemis))
        self.mag_varn_year = to_nullable_int(mag_varn_year)
        self.tpa = to_nullable_int(tpa)
        self.chart_name = to_nullable_string(chart_name)
        self.dist_city_to_airport = to_nullable_int(dist_city_to_airport)
        self.direction_code = DirectionCode.from_value(
            to_nullable_string(direction_code)
        )
        self.acreage = to_nullable_int(acreage)
        self.resp_artcc_id = to_nullable_string(resp_artcc_id)
        self.computer_id = to_nullable_string(computer_id)
        self.artcc_name = to_nullable_string(artcc_name)
        self.fss_on_arpt_flag = to_nullable_bool(fss_on_arpt_flag)
        self.fss_id = to_nullable_string(fss_id)
        self.fss_name = to_nullable_string(fss_name)
        self.phone_no = to_nullable_string(phone_no)
        self.toll_free_no = to_nullable_string(toll_free_no)
        self.alt_fss_id = to_nullable_string(alt_fss_id)
        self.alt_fss_name = to_nullable_string(alt_fss_name)
        self.alt_toll_free_no = to_nullable_string(alt_toll_free_no)
        self.notam_id = to_nullable_string(notam_id)
        self.notam_flag = to_nullable_bool(notam_flag)
        self.activation_date = to_nullable_date(activation_date, "YYYY/MM")
        self.arpt_status = StatusCode.from_value(to_nullable_string(arpt_status))
        self.far_139_type_code = to_nullable_string(far_139_type_code)
        self.far_139_carrier_ser_code = to_nullable_string(far_139_carrier_ser_code)
        self.arff_cert_type_date = to_nullable_date(arff_cert_type_date, "YYYY/MM")
        self.nasp_code = NASPCode.from_value(to_nullable_string(nasp_code))
        self.asp_anlys_dtrm_code = ASPCode.from_value(
            to_nullable_string(asp_anlys_dtrm_code)
        )
        self.cust_flag = to_nullable_bool(cust_flag)
        self.lndg_rights_flag = to_nullable_bool(lndg_rights_flag)
        self.joint_use_flag = to_nullable_bool(joint_use_flag)
        self.mil_lndg_flag = to_nullable_bool(mil_lndg_flag)
        self.inspect_method_code = InspectionMethodCode.from_value(
            to_nullable_string(inspect_method_code)
        )
        self.inspector_code = InspectorCode.from_value(
            to_nullable_string(inspector_code)
        )
        self.last_inspection = to_nullable_date(last_inspection, "YYYY/MM/DD")
        self.last_info_response = to_nullable_date(last_info_response, "YYYY/MM/DD")
        self.fuel_types = [
            fc
            for item in (fuel_types or "").split(",")
            if (fc := FuelCode.from_value(to_nullable_string(item))) is not fc.NULL
        ]
        self.airframe_repair_ser_code = SERCode.from_value(
            to_nullable_string(airframe_repair_ser_code)
        )
        self.pwr_plant_repair_ser = SERCode.from_value(
            to_nullable_string(pwr_plant_repair_ser)
        )
        self.bottled_oxy_type = OxygenCode.from_value(
            to_nullable_string(bottled_oxy_type)
        )
        self.bulk_oxy_type = OxygenCode.from_value(to_nullable_string(bulk_oxy_type))
        self.lgt_sked = LightScheduleCode.from_value(to_nullable_string(lgt_sked))
        self.bcn_lgt_sked = LightScheduleCode.from_value(
            to_nullable_string(bcn_lgt_sked)
        )
        self.twr_type_code = TowerCode.from_value(to_nullable_string(twr_type_code))
        self.seg_circle_mkr_flag = SegmentedCircleCode.from_value(
            to_nullable_string(seg_circle_mkr_flag)
        )
        self.bcn_lens_color = BeaconColorCode.from_value(
            to_nullable_string(bcn_lens_color)
        )
        self.lndg_fee_flag = to_nullable_bool(lndg_fee_flag)
        self.medical_use_flag = to_nullable_bool(medical_use_flag)
        self.arpt_psn_source = to_nullable_string(arpt_psn_source)
        self.position_src_date = to_nullable_date(position_src_date, "YYYY/MM/DD")
        self.arpt_elev_source = to_nullable_string(arpt_elev_source)
        self.elevation_src_date = to_nullable_date(elevation_src_date, "YYYY/MM/DD")
        self.contr_fuel_avbl = to_nullable_bool(contr_fuel_avbl)
        self.trns_strg_buoy_flag = to_nullable_bool(trns_strg_buoy_flag)
        self.trns_strg_hgr_flag = to_nullable_bool(trns_strg_hgr_flag)
        self.trns_strg_tie_flag = to_nullable_bool(trns_strg_tie_flag)
        self.other_services = [
            sc
            for item in (other_services or "").split(",")
            if (sc := ServiceCode.from_value(to_nullable_string(item))) is not sc.NULL
        ]
        self.wind_indcr_flag = WindIndicatorCode.from_value(
            to_nullable_string(wind_indcr_flag)
        )
        self.icao_id = to_nullable_string(icao_id)
        self.min_op_network = to_nullable_bool(min_op_network)
        self.user_fee_flag = to_nullable_string(user_fee_flag)
        self.cta = to_nullable_string(cta)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"REGION_CODE={self.region_code!r}, "
            f"ADO_CODE={self.ado_code!r}, "
            f"STATE_NAME={self.state_name!r}, "
            f"COUNTY_NAME={self.county_name!r}, "
            f"COUNTY_ASSOC_STATE={self.county_assoc_state!r}, "
            f"ARPT_NAME={self.arpt_name!r}, "
            f"OWNERSHIP_TYPE_CODE={self.ownership_type_code!r}, "
            f"FACILITY_USE_CODE={self.facility_use_code!r}, "
            f"LAT_DEG={self.lat_deg!r}, "
            f"LAT_MIN={self.lat_min!r}, "
            f"LAT_SEC={self.lat_sec!r}, "
            f"LAT_HEMIS={self.lat_hemis!r}, "
            f"LAT_DECIMAL={self.lat_decimal!r}, "
            f"LON_DEG={self.lon_deg!r}, "
            f"LON_MIN={self.lon_min!r}, "
            f"LON_SEC={self.lon_sec!r}, "
            f"LON_HEMIS={self.lon_hemis!r}, "
            f"LON_DECIMAL={self.lon_decimal!r}, "
            f"SURVEY_METHOD_CODE={self.survey_method_code!r}, "
            f"ELEV={self.elev!r}, "
            f"ELEV_METHOD_CODE={self.elev_method_code!r}, "
            f"MAG_VARN={self.mag_varn!r}, "
            f"MAG_HEMIS={self.mag_hemis!r}, "
            f"MAG_VARN_YEAR={self.mag_varn_year!r}, "
            f"TPA={self.tpa!r}, "
            f"CHART_NAME={self.chart_name!r}, "
            f"DIST_CITY_TO_AIRPORT={self.dist_city_to_airport!r}, "
            f"DIRECTION_CODE={self.direction_code!r}, "
            f"ACREAGE={self.acreage!r}, "
            f"RESP_ARTCC_ID={self.resp_artcc_id!r}, "
            f"COMPUTER_ID={self.computer_id!r}, "
            f"ARTCC_NAME={self.artcc_name!r}, "
            f"FSS_ON_ARPT_FLAG={self.fss_on_arpt_flag!r}, "
            f"FSS_ID={self.fss_id!r}, "
            f"FSS_NAME={self.fss_name!r}, "
            f"PHONE_NO={self.phone_no!r}, "
            f"TOLL_FREE_NO={self.toll_free_no!r}, "
            f"ALT_FSS_ID={self.alt_fss_id!r}, "
            f"ALT_FSS_NAME={self.alt_fss_name!r}, "
            f"ALT_TOLL_FREE_NO={self.alt_toll_free_no!r}, "
            f"NOTAM_ID={self.notam_id!r}, "
            f"NOTAM_FLAG={self.notam_flag!r}, "
            f"ACTIVATION_DATE={self.activation_date!r}, "
            f"ARPT_STATUS={self.arpt_status!r}, "
            f"FAR_139_TYPE_CODE={self.far_139_type_code!r}, "
            f"FAR_139_CARRIER_SER_CODE={self.far_139_carrier_ser_code!r}, "
            f"ARFF_CERT_TYPE_DATE={self.arff_cert_type_date!r}, "
            f"NASP_CODE={self.nasp_code!r}, "
            f"ASP_ANLYS_DTRM_CODE={self.asp_anlys_dtrm_code!r}, "
            f"CUST_FLAG={self.cust_flag!r}, "
            f"LNDG_RIGHTS_FLAG={self.lndg_rights_flag!r}, "
            f"JOINT_USE_FLAG={self.joint_use_flag!r}, "
            f"MIL_LNDG_FLAG={self.mil_lndg_flag!r}, "
            f"INSPECT_METHOD_CODE={self.inspect_method_code!r}, "
            f"INSPECTOR_CODE={self.inspector_code!r}, "
            f"LAST_INSPECTION={self.last_inspection!r}, "
            f"LAST_INFO_RESPONSE={self.last_info_response!r}, "
            f"FUEL_TYPES={self.fuel_types!r}, "
            f"AIRFRAME_REPAIR_SER_CODE={self.airframe_repair_ser_code!r}, "
            f"PWR_PLANT_REPAIR_SER={self.pwr_plant_repair_ser!r}, "
            f"BOTTLED_OXY_TYPE={self.bottled_oxy_type!r}, "
            f"BULK_OXY_TYPE={self.bulk_oxy_type!r}, "
            f"LGT_SKED={self.lgt_sked!r}, "
            f"BCN_LGT_SKED={self.bcn_lgt_sked!r}, "
            f"TWR_TYPE_CODE={self.twr_type_code!r}, "
            f"SEG_CIRCLE_MKR_FLAG={self.seg_circle_mkr_flag!r}, "
            f"BCN_LENS_COLOR={self.bcn_lens_color!r}, "
            f"LNDG_FEE_FLAG={self.lndg_fee_flag!r}, "
            f"MEDICAL_USE_FLAG={self.medical_use_flag!r}, "
            f"ARPT_PSN_SOURCE={self.arpt_psn_source!r}, "
            f"POSITION_SRC_DATE={self.position_src_date!r}, "
            f"ARPT_ELEV_SOURCE={self.arpt_elev_source!r}, "
            f"ELEVATION_SRC_DATE={self.elevation_src_date!r}, "
            f"CONTR_FUEL_AVBL={self.contr_fuel_avbl!r}, "
            f"TRNS_STRG_BUOY_FLAG={self.trns_strg_buoy_flag!r}, "
            f"TRNS_STRG_HGR_FLAG={self.trns_strg_hgr_flag!r}, "
            f"TRNS_STRG_TIE_FLAG={self.trns_strg_tie_flag!r}, "
            f"OTHER_SERVICES={self.other_services!r}, "
            f"WIND_INDCR_FLAG={self.wind_indcr_flag!r}, "
            f"ICAO_ID={self.icao_id!r}, "
            f"MIN_OP_NETWORK={self.min_op_network!r}, "
            f"USER_FEE_FLAG={self.user_fee_flag!r}, "
            f"CTA={self.cta!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "region_code",
                "ado_code",
                "state_name",
                "county_name",
                "county_assoc_state",
                "arpt_name",
                "ownership_type_code",
                "facility_use_code",
                "lat_deg",
                "lat_min",
                "lat_sec",
                "lat_hemis",
                "lat_decimal",
                "lon_deg",
                "lon_min",
                "lon_sec",
                "lon_hemis",
                "lon_decimal",
                "survey_method_code",
                "elev",
                "elev_method_code",
                "mag_varn",
                "mag_hemis",
                "mag_varn_year",
                "tpa",
                "chart_name",
                "dist_city_to_airport",
                "direction_code",
                "acreage",
                "resp_artcc_id",
                "computer_id",
                "artcc_name",
                "fss_on_arpt_flag",
                "fss_id",
                "fss_name",
                "phone_no",
                "toll_free_no",
                "alt_fss_id",
                "alt_fss_name",
                "alt_toll_free_no",
                "notam_id",
                "notam_flag",
                "activation_date",
                "arpt_status",
                "far_139_type_code",
                "far_139_carrier_ser_code",
                "arff_cert_type_date",
                "nasp_code",
                "asp_anlys_dtrm_code",
                "cust_flag",
                "lndg_rights_flag",
                "joint_use_flag",
                "mil_lndg_flag",
                "inspect_method_code",
                "inspector_code",
                "last_inspection",
                "last_info_response",
                "fuel_types",
                "airframe_repair_ser_code",
                "pwr_plant_repair_ser",
                "bottled_oxy_type",
                "bulk_oxy_type",
                "lgt_sked",
                "bcn_lgt_sked",
                "twr_type_code",
                "seg_circle_mkr_flag",
                "bcn_lens_color",
                "lndg_fee_flag",
                "medical_use_flag",
                "arpt_psn_source",
                "position_src_date",
                "arpt_elev_source",
                "elevation_src_date",
                "contr_fuel_avbl",
                "trns_strg_buoy_flag",
                "trns_strg_hgr_flag",
                "trns_strg_tie_flag",
                "other_services",
                "wind_indcr_flag",
                "icao_id",
                "min_op_network",
                "user_fee_flag",
                "cta",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "region_code": self.region_code.value if self.region_code else None,
            "ado_code": self.ado_code,
            "state_name": self.state_name,
            "county_name": self.county_name,
            "county_assoc_state": self.county_assoc_state,
            "arpt_name": self.arpt_name,
            "ownership_type_code": (
                self.ownership_type_code.value if self.ownership_type_code else None
            ),
            "facility_use_code": (
                self.facility_use_code.value if self.facility_use_code else None
            ),
            "lat_deg": self.lat_deg,
            "lat_min": self.lat_min,
            "lat_sec": self.lat_sec,
            "lat_hemis": self.lat_hemis.value if self.lat_hemis else None,
            "lat_decimal": self.lat_decimal,
            "lon_deg": self.lon_deg,
            "lon_min": self.lon_min,
            "lon_sec": self.lon_sec,
            "lon_hemis": self.lon_hemis.value if self.lon_hemis else None,
            "lon_decimal": self.lon_decimal,
            "survey_method_code": (
                self.survey_method_code.value if self.survey_method_code else None
            ),
            "elev": self.elev,
            "elev_method_code": (
                self.elev_method_code.value if self.elev_method_code else None
            ),
            "mag_varn": self.mag_varn,
            "mag_hemis": self.mag_hemis.value if self.mag_hemis else None,
            "mag_varn_year": self.mag_varn_year,
            "tpa": self.tpa,
            "chart_name": self.chart_name,
            "dist_city_to_airport": self.dist_city_to_airport,
            "direction_code": (
                self.direction_code.value if self.direction_code else None
            ),
            "acreage": self.acreage,
            "resp_artcc_id": self.resp_artcc_id,
            "computer_id": self.computer_id,
            "artcc_name": self.artcc_name,
            "fss_on_arpt_flag": self.fss_on_arpt_flag,
            "fss_id": self.fss_id,
            "fss_name": self.fss_name,
            "phone_no": self.phone_no,
            "toll_free_no": self.toll_free_no,
            "alt_fss_id": self.alt_fss_id,
            "alt_fss_name": self.alt_fss_name,
            "alt_toll_free_no": self.alt_toll_free_no,
            "notam_id": self.notam_id,
            "notam_flag": self.notam_flag,
            "activation_date": (
                self.activation_date.strftime("%Y-%m-%d")
                if self.activation_date
                else None
            ),
            "arpt_status": self.arpt_status.value if self.arpt_status else None,
            "far_139_type_code": self.far_139_type_code,
            "far_139_carrier_ser_code": self.far_139_carrier_ser_code,
            "arff_cert_type_date": (
                self.arff_cert_type_date.strftime("%Y-%m-%d")
                if self.arff_cert_type_date
                else None
            ),
            "nasp_code": self.nasp_code.value if self.nasp_code else None,
            "asp_anlys_dtrm_code": (
                self.asp_anlys_dtrm_code.value if self.asp_anlys_dtrm_code else None
            ),
            "cust_flag": self.cust_flag,
            "lndg_rights_flag": self.lndg_rights_flag,
            "joint_use_flag": self.joint_use_flag,
            "mil_lndg_flag": self.mil_lndg_flag,
            "inspect_method_code": (
                self.inspect_method_code.value if self.inspect_method_code else None
            ),
            "inspector_code": (
                self.inspector_code.value if self.inspector_code else None
            ),
            "last_inspection": (
                self.last_inspection.strftime("%Y-%m-%d")
                if self.last_inspection
                else None
            ),
            "last_info_response": (
                self.last_info_response.strftime("%Y-%m-%d")
                if self.last_info_response
                else None
            ),
            "fuel_types": (
                ", ".join(
                    member.value
                    for member in self.fuel_types
                    if member.value is not None
                )
                if self.fuel_types
                else None
            ),
            "airframe_repair_ser_code": (
                self.airframe_repair_ser_code.value
                if self.airframe_repair_ser_code
                else None
            ),
            "pwr_plant_repair_ser": (
                self.pwr_plant_repair_ser.value if self.pwr_plant_repair_ser else None
            ),
            "bottled_oxy_type": (
                self.bottled_oxy_type.value if self.bottled_oxy_type else None
            ),
            "bulk_oxy_type": self.bulk_oxy_type.value if self.bulk_oxy_type else None,
            "lgt_sked": self.lgt_sked.value if self.lgt_sked else None,
            "bcn_lgt_sked": self.bcn_lgt_sked.value if self.bcn_lgt_sked else None,
            "twr_type_code": self.twr_type_code.value if self.twr_type_code else None,
            "seg_circle_mkr_flag": (
                self.seg_circle_mkr_flag.value if self.seg_circle_mkr_flag else None
            ),
            "bcn_lens_color": (
                self.bcn_lens_color.value if self.bcn_lens_color else None
            ),
            "lndg_fee_flag": self.lndg_fee_flag,
            "medical_use_flag": self.medical_use_flag,
            "arpt_psn_source": self.arpt_psn_source,
            "position_src_date": (
                self.position_src_date.strftime("%Y-%m-%d")
                if self.position_src_date
                else None
            ),
            "arpt_elev_source": self.arpt_elev_source,
            "elevation_src_date": (
                self.elevation_src_date.strftime("%Y-%m-%d")
                if self.elevation_src_date
                else None
            ),
            "contr_fuel_avbl": self.contr_fuel_avbl,
            "trns_strg_buoy_flag": self.trns_strg_buoy_flag,
            "trns_strg_hgr_flag": self.trns_strg_hgr_flag,
            "trns_strg_tie_flag": self.trns_strg_tie_flag,
            "other_services": (
                ", ".join(
                    member.value
                    for member in self.other_services
                    if member.value is not None
                )
                if self.other_services
                else None
            ),
            "wind_indcr_flag": (
                self.wind_indcr_flag.value if self.wind_indcr_flag else None
            ),
            "icao_id": self.icao_id,
            "min_op_network": self.min_op_network,
            "user_fee_flag": self.user_fee_flag,
            "cta": self.cta,
        }
        return {**base_dict, **this_dict}
