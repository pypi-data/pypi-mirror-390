from nasrparse.functions import (
    to_nullable_bool,
    to_nullable_float,
    to_nullable_int,
    to_nullable_string,
)
from nasrparse.records.types import (
    HemisCode,
    MonitoringCode,
    RegionCode,
    ServiceVolumeCode,
    SurveyAccuracyCode,
)

from ._base import Base


class NAV_BASE(Base):
    nav_status: str | None
    """Navigation Aid Status"""
    name: str | None
    """Name of NAVAID"""
    state_name: str | None
    """Associated State Name"""
    region_code: RegionCode
    """FAA Region responsible for NAVAID (code)"""
    country_name: str | None
    """Country Name NAVAID Located"""
    fan_marker: str | None
    """Name of FAN MARKER"""
    owner: str | None
    """A Concatenation of the NAVAID OWNER CODE - NAVAID OWNER NAME"""
    operator: str | None
    """A Concatenation of the NAVAID OPERATOR CODE - NAVAID OPERATOR NAME"""
    nas_use_flag: bool | None
    """Common System Usage (Y or N) Defines how the NAVAID is used."""
    public_use_flag: bool | None
    """NAVAID PUBLIC USE (Y or N) Defines by whom the NAVAID is used."""
    ndb_class_code: (
        str | None
    )  # Leaving as str because of odd FAA and Canadian encoding. See `NAV DATA LAYOUT.pdf` for details.
    """Class of NDB"""
    oper_hours: str | None
    """HOURS of Operation of NAVAID."""
    high_alt_artcc_id: str | None
    """Identifier of ARTCC with High Altitude Boundary That the NAVAID Falls Within."""
    high_artcc_name: str | None
    """Name of ARTCC with High Altitude Boundary That the NAVAID Falls Within."""
    low_alt_artcc_id: str | None
    """Identifier of ARTCC with Low Altitude Boundary That the NAVAID Falls Within."""
    low_artcc_name: str | None
    """Name of ARTCC with Low Altitude Boundary That the NAVAID Falls Within."""
    lat_deg: int | None
    """NAVAID Latitude Degrees"""
    lat_min: int | None
    """NAVAID Latitude Minutes"""
    lat_sec: float | None
    """NAVAID Latitude Seconds"""
    lat_hemis: HemisCode
    """NAVAID Latitude Hemisphere"""
    lat_decimal: float | None
    """NAVAID Latitude in Decimal Format"""
    lon_deg: int | None
    """NAVAID Longitude Degrees"""
    lon_min: int | None
    """NAVAID Longitude Minutes"""
    lon_sec: float | None
    """NAVAID Longitude Seconds"""
    lon_hemis: HemisCode
    """NAVAID Longitude Hemisphere"""
    lon_decimal: float | None
    """NAVAID Longitude in Decimal Format"""
    survey_accuracy_code: SurveyAccuracyCode
    """Latitude/Longitude Survey Accuracy (Code)"""
    tacan_dme_status: str | None
    """Status of TACAN or DME Equipment."""
    tacan_dme_lat_deg: int | None
    """Latitude Degrees of TACAN Portion of VORTAC when TACAN is not sited with VOR"""
    tacan_dme_lat_min: int | None
    """Latitude Minutes of TACAN Portion of VORTAC when TACAN is not sited with VOR"""
    tacan_dme_lat_sec: float | None
    """Latitude Seconds of TACAN Portion of VORTAC when TACAN is not sited with VOR"""
    tacan_dme_lat_hemis: HemisCode
    """Latitude Hemisphere of TACAN Portion of VORTAC when TACAN is not sited with VOR"""
    tacan_dme_lat_decimal: float | None
    """Latitude in Decimal Format of TACAN Portion of VORTAC when TACAN is not sited with VOR"""
    tacan_dme_lon_deg: int | None
    """Longitude Degrees of TACAN Portion of VORTAC when TACAN is not sited with VOR"""
    tacan_dme_lon_min: int | None
    """Longitude Minutes of TACAN Portion of VORTAC when TACAN is not sited with VOR"""
    tacan_dme_lon_sec: float | None
    """Longitude Seconds of TACAN Portion of VORTAC when TACAN is not sited with VOR"""
    tacan_dme_lon_hemis: HemisCode
    """Longitude Hemisphere of TACAN Portion of VORTAC when TACAN is not sited with VOR"""
    tacan_dme_lon_decimal: float | None
    """Longitude in Decimal Format of TACAN Portion of VORTAC when TACAN is not sited with VOR"""
    elev: float | None
    """Elevation in Tenth of a Foot (MSL)."""
    mag_varn: int | None
    """Magnetic Variation Degrees (DME, VOT and FM NAVAID Types do not have MAG VAR. Any value in this column for those NAVAID Types should be ignored.)"""
    mag_varn_hemis: HemisCode
    """Magnetic Variation Direction (DME, VOT and FM NAVAID Types do not have MAG HEMIS. Any value in this column for those NAVAID Types should be ignored.)"""
    mag_varn_year: str | None
    """Magnetic Variation Epoch Year (DME, VOT and FM NAVAID Types do not have MAG VAR YEAR. Any value in this column for those NAVAID Types should be ignored.)"""
    simul_voice_flag: bool | None
    """Simultaneous Voice Feature"""
    pwr_output: str | None
    """Power Output (In Watts)"""
    auto_voice_id_flag: bool | None
    """Automatic Voice Identification Feature"""
    mnt_cat_code: MonitoringCode
    """Monitoring Category"""
    voice_call: str | None
    """Radio Voice Call (Name) or Trans Signal"""
    chan: str | None
    """Channel (TACAN) NAVAID Transmits On"""
    freq: str | None
    """Frequency the NAVAID Transmits On (Except TACAN)"""
    mkr_ident: str | None
    """Transmitted Fan Marker/Marine Radio Beacon Identifier"""
    mkr_shape: str | None
    """fan marker type (e - ELLIPTICAL)"""
    mkr_brg: float | None
    """True Bearing of Major Axis of Fan Marker"""
    alt_code: ServiceVolumeCode
    """VOR Standard Service Volume"""
    dme_ssv: ServiceVolumeCode
    """DME Standard Service Volume"""
    low_nav_on_high_chart_flag: bool | None
    """Low Altitude Facility Used in High Structure"""
    z_mkr_flag: bool | None
    """NAVAID Z Marker Available"""
    fss_id: str | None
    """Associated/Controlling FSS (IDENT)"""
    fss_name: str | None
    """Associated/Controlling FSS (Name)"""
    fss_hours: str | None
    """Hours of Operation of Controlling FSS"""
    notam_id: str | None
    """NOTAM Accountability Code (IDENT)"""
    quad_ident: str | None
    """Quadrant Identification and Range Leg Bearing (LFR Only)"""
    pitch_flag: bool | None
    """Pitch Flag"""
    catch_flag: bool | None
    """Catch Flag"""
    sua_atcaa_flag: bool | None
    """SUA/ATCAA Flag"""
    restriction_flag: bool | None
    """NAVAID Restriction Flag"""
    hiwas_flag: bool | None
    """HIWAS Flag"""

    def __init__(
        self,
        eff_date: str,
        nav_id: str,
        nav_type: str,
        state_code: str,
        city: str,
        country_code: str,
        nav_status: str,
        name: str,
        state_name: str,
        region_code: str,
        country_name: str,
        fan_marker: str,
        owner: str,
        operator: str,
        nas_use_flag: str,
        public_use_flag: str,
        ndb_class_code: str,
        oper_hours: str,
        high_alt_artcc_id: str,
        high_artcc_name: str,
        low_alt_artcc_id: str,
        low_artcc_name: str,
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
        survey_accuracy_code: str,
        tacan_dme_status: str,
        tacan_dme_lat_deg: str,
        tacan_dme_lat_min: str,
        tacan_dme_lat_sec: str,
        tacan_dme_lat_hemis: str,
        tacan_dme_lat_decimal: str,
        tacan_dme_lon_deg: str,
        tacan_dme_lon_min: str,
        tacan_dme_lon_sec: str,
        tacan_dme_lon_hemis: str,
        tacan_dme_lon_decimal: str,
        elev: str,
        mag_varn: str,
        mag_varn_hemis: str,
        mag_varn_year: str,
        simul_voice_flag: str,
        pwr_output: str,
        auto_voice_id_flag: str,
        mnt_cat_code: str,
        voice_call: str,
        chan: str,
        freq: str,
        mkr_ident: str,
        mkr_shape: str,
        mkr_brg: str,
        alt_code: str,
        dme_ssv: str,
        low_nav_on_high_chart_flag: str,
        z_mkr_flag: str,
        fss_id: str,
        fss_name: str,
        fss_hours: str,
        notam_id: str,
        quad_ident: str,
        pitch_flag: str,
        catch_flag: str,
        sua_atcaa_flag: str,
        restriction_flag: str,
        hiwas_flag: str,
    ) -> None:
        super().__init__(
            "navaids",
            eff_date,
            nav_id,
            nav_type,
            state_code,
            city,
            country_code,
        )
        self.nav_status = to_nullable_string(nav_status)
        self.name = to_nullable_string(name)
        self.state_name = to_nullable_string(state_name)
        self.region_code = RegionCode.from_value(to_nullable_string(region_code))
        self.country_name = to_nullable_string(country_name)
        self.fan_marker = to_nullable_string(fan_marker)
        self.owner = to_nullable_string(owner)
        self.operator = to_nullable_string(operator)
        self.nas_use_flag = to_nullable_bool(nas_use_flag)
        self.public_use_flag = to_nullable_bool(public_use_flag)
        self.ndb_class_code = to_nullable_string(ndb_class_code)
        self.oper_hours = to_nullable_string(oper_hours)
        self.high_alt_artcc_id = to_nullable_string(high_alt_artcc_id)
        self.high_artcc_name = to_nullable_string(high_artcc_name)
        self.low_alt_artcc_id = to_nullable_string(low_alt_artcc_id)
        self.low_artcc_name = to_nullable_string(low_artcc_name)
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
        self.survey_accuracy_code = SurveyAccuracyCode.from_value(
            to_nullable_string(survey_accuracy_code)
        )
        self.tacan_dme_status = to_nullable_string(tacan_dme_status)
        self.tacan_dme_lat_deg = to_nullable_int(tacan_dme_lat_deg)
        self.tacan_dme_lat_min = to_nullable_int(tacan_dme_lat_min)
        self.tacan_dme_lat_sec = to_nullable_float(tacan_dme_lat_sec)
        self.tacan_dme_lat_hemis = HemisCode.from_value(
            to_nullable_string(tacan_dme_lat_hemis)
        )
        self.tacan_dme_lat_decimal = to_nullable_float(tacan_dme_lat_decimal)
        self.tacan_dme_lon_deg = to_nullable_int(tacan_dme_lon_deg)
        self.tacan_dme_lon_min = to_nullable_int(tacan_dme_lon_min)
        self.tacan_dme_lon_sec = to_nullable_float(tacan_dme_lon_sec)
        self.tacan_dme_lon_hemis = HemisCode.from_value(
            to_nullable_string(tacan_dme_lon_hemis)
        )
        self.tacan_dme_lon_decimal = to_nullable_float(tacan_dme_lon_decimal)
        self.elev = to_nullable_float(elev)
        self.mag_varn = to_nullable_int(mag_varn)
        self.mag_varn_hemis = HemisCode.from_value(to_nullable_string(mag_varn_hemis))
        self.mag_varn_year = to_nullable_string(mag_varn_year)
        self.simul_voice_flag = to_nullable_bool(simul_voice_flag)
        self.pwr_output = to_nullable_string(pwr_output)
        self.auto_voice_id_flag = to_nullable_bool(auto_voice_id_flag)
        self.mnt_cat_code = MonitoringCode.from_value(to_nullable_string(mnt_cat_code))
        self.voice_call = to_nullable_string(voice_call)
        self.chan = to_nullable_string(chan)
        self.freq = to_nullable_string(freq)
        self.mkr_ident = to_nullable_string(mkr_ident)
        self.mkr_shape = to_nullable_string(mkr_shape)
        self.mkr_brg = to_nullable_float(mkr_brg)
        self.alt_code = ServiceVolumeCode.from_value(to_nullable_string(alt_code))
        self.dme_ssv = ServiceVolumeCode.from_value(to_nullable_string(dme_ssv))
        self.low_nav_on_high_chart_flag = to_nullable_bool(low_nav_on_high_chart_flag)
        self.z_mkr_flag = to_nullable_bool(z_mkr_flag)
        self.fss_id = to_nullable_string(fss_id)
        self.fss_name = to_nullable_string(fss_name)
        self.fss_hours = to_nullable_string(fss_hours)
        self.notam_id = to_nullable_string(notam_id)
        self.quad_ident = to_nullable_string(quad_ident)
        self.pitch_flag = to_nullable_bool(pitch_flag)
        self.catch_flag = to_nullable_bool(catch_flag)
        self.sua_atcaa_flag = to_nullable_bool(sua_atcaa_flag)
        self.restriction_flag = to_nullable_bool(restriction_flag)
        self.hiwas_flag = to_nullable_bool(hiwas_flag)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"NAV_STATUS={self.nav_status!r}, "
            f"NAME={self.name!r}, "
            f"STATE_NAME={self.state_name!r}, "
            f"REGION_CODE={self.region_code!r}, "
            f"COUNTRY_NAME={self.country_name!r}, "
            f"FAN_MARKER={self.fan_marker!r}, "
            f"OWNER={self.owner!r}, "
            f"OPERATOR={self.operator!r}, "
            f"NAS_USE_FLAG={self.nas_use_flag!r}, "
            f"PUBLIC_USE_FLAG={self.public_use_flag!r}, "
            f"NDB_CLASS_CODE={self.ndb_class_code!r}, "
            f"OPER_HOURS={self.oper_hours!r}, "
            f"HIGH_ALT_ARTCC_ID={self.high_alt_artcc_id!r}, "
            f"HIGH_ARTCC_NAME={self.high_artcc_name!r}, "
            f"LOW_ALT_ARTCC_ID={self.low_alt_artcc_id!r}, "
            f"LOW_ARTCC_NAME={self.low_artcc_name!r}, "
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
            f"SURVEY_ACCURACY_CODE={self.survey_accuracy_code!r}, "
            f"TACAN_DME_STATUS={self.tacan_dme_status!r}, "
            f"TACAN_DME_LAT_DEG={self.tacan_dme_lat_deg!r}, "
            f"TACAN_DME_LAT_MIN={self.tacan_dme_lat_min!r}, "
            f"TACAN_DME_LAT_SEC={self.tacan_dme_lat_sec!r}, "
            f"TACAN_DME_LAT_HEMIS={self.tacan_dme_lat_hemis!r}, "
            f"TACAN_DME_LAT_DECIMAL={self.tacan_dme_lat_decimal!r}, "
            f"TACAN_DME_LON_DEG={self.tacan_dme_lon_deg!r}, "
            f"TACAN_DME_LON_MIN={self.tacan_dme_lon_min!r}, "
            f"TACAN_DME_LON_SEC={self.tacan_dme_lon_sec!r}, "
            f"TACAN_DME_LON_HEMIS={self.tacan_dme_lon_hemis!r}, "
            f"TACAN_DME_LON_DECIMAL={self.tacan_dme_lon_decimal!r}, "
            f"ELEV={self.elev!r}, "
            f"MAG_VARN={self.mag_varn!r}, "
            f"MAG_VARN_HEMIS={self.mag_varn_hemis!r}, "
            f"MAG_VARN_YEAR={self.mag_varn_year!r}, "
            f"SIMUL_VOICE_FLAG={self.simul_voice_flag!r}, "
            f"PWR_OUTPUT={self.pwr_output!r}, "
            f"AUTO_VOICE_ID_FLAG={self.auto_voice_id_flag!r}, "
            f"MNT_CAT_CODE={self.mnt_cat_code!r}, "
            f"VOICE_CALL={self.voice_call!r}, "
            f"CHAN={self.chan!r}, "
            f"FREQ={self.freq!r}, "
            f"MKR_IDENT={self.mkr_ident!r}, "
            f"MKR_SHAPE={self.mkr_shape!r}, "
            f"MKR_BRG={self.mkr_brg!r}, "
            f"ALT_CODE={self.alt_code!r}, "
            f"DME_SSV={self.dme_ssv!r}, "
            f"LOW_NAV_ON_HIGH_CHART_FLAG={self.low_nav_on_high_chart_flag!r}, "
            f"Z_MKR_FLAG={self.z_mkr_flag!r}, "
            f"FSS_ID={self.fss_id!r}, "
            f"FSS_NAME={self.fss_name!r}, "
            f"FSS_HOURS={self.fss_hours!r}, "
            f"NOTAM_ID={self.notam_id!r}, "
            f"QUAD_IDENT={self.quad_ident!r}, "
            f"PITCH_FLAG={self.pitch_flag!r}, "
            f"CATCH_FLAG={self.catch_flag!r}, "
            f"SUA_ATCAA_FLAG={self.sua_atcaa_flag!r}, "
            f"RESTRICTION_FLAG={self.restriction_flag!r}, "
            f"HIWAS_FLAG={self.hiwas_flag!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "nav_status",
                "name",
                "state_name",
                "region_code",
                "country_name",
                "fan_marker",
                "owner",
                "operator",
                "nas_use_flag",
                "public_use_flag",
                "ndb_class_code",
                "oper_hours",
                "high_alt_artcc_id",
                "high_artcc_name",
                "low_alt_artcc_id",
                "low_artcc_name",
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
                "survey_accuracy_code",
                "tacan_dme_status",
                "tacan_dme_lat_deg",
                "tacan_dme_lat_min",
                "tacan_dme_lat_sec",
                "tacan_dme_lat_hemis",
                "tacan_dme_lat_decimal",
                "tacan_dme_lon_deg",
                "tacan_dme_lon_min",
                "tacan_dme_lon_sec",
                "tacan_dme_lon_hemis",
                "tacan_dme_lon_decimal",
                "elev",
                "mag_varn",
                "mag_varn_hemis",
                "mag_varn_year",
                "simul_voice_flag",
                "pwr_output",
                "auto_voice_id_flag",
                "mnt_cat_code",
                "voice_call",
                "chan",
                "freq",
                "mkr_ident",
                "mkr_shape",
                "mkr_brg",
                "alt_code",
                "dme_ssv",
                "low_nav_on_high_chart_flag",
                "z_mkr_flag",
                "fss_id",
                "fss_name",
                "fss_hours",
                "notam_id",
                "quad_ident",
                "pitch_flag",
                "catch_flag",
                "sua_atcaa_flag",
                "restriction_flag",
                "hiwas_flag",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "nav_status": self.nav_status,
            "name": self.name,
            "state_name": self.state_name,
            "region_code": self.region_code.value if self.region_code else None,
            "country_name": self.country_name,
            "fan_marker": self.fan_marker,
            "owner": self.owner,
            "operator": self.operator,
            "nas_use_flag": self.nas_use_flag,
            "public_use_flag": self.public_use_flag,
            "ndb_class_code": self.ndb_class_code,
            "oper_hours": self.oper_hours,
            "high_alt_artcc_id": self.high_alt_artcc_id,
            "high_artcc_name": self.high_artcc_name,
            "low_alt_artcc_id": self.low_alt_artcc_id,
            "low_artcc_name": self.low_artcc_name,
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
            "survey_accuracy_code": (
                self.survey_accuracy_code.value if self.survey_accuracy_code else None
            ),
            "tacan_dme_status": self.tacan_dme_status,
            "tacan_dme_lat_deg": self.tacan_dme_lat_deg,
            "tacan_dme_lat_min": self.tacan_dme_lat_min,
            "tacan_dme_lat_sec": self.tacan_dme_lat_sec,
            "tacan_dme_lat_hemis": (
                self.tacan_dme_lat_hemis.value if self.tacan_dme_lat_hemis else None
            ),
            "tacan_dme_lat_decimal": self.tacan_dme_lat_decimal,
            "tacan_dme_lon_deg": self.tacan_dme_lon_deg,
            "tacan_dme_lon_min": self.tacan_dme_lon_min,
            "tacan_dme_lon_sec": self.tacan_dme_lon_sec,
            "tacan_dme_lon_hemis": (
                self.tacan_dme_lon_hemis.value if self.tacan_dme_lon_hemis else None
            ),
            "tacan_dme_lon_decimal": self.tacan_dme_lon_decimal,
            "elev": self.elev,
            "mag_varn": self.mag_varn,
            "mag_varn_hemis": (
                self.mag_varn_hemis.value if self.mag_varn_hemis else None
            ),
            "mag_varn_year": self.mag_varn_year,
            "simul_voice_flag": self.simul_voice_flag,
            "pwr_output": self.pwr_output,
            "auto_voice_id_flag": self.auto_voice_id_flag,
            "mnt_cat_code": self.mnt_cat_code.value if self.mnt_cat_code else None,
            "voice_call": self.voice_call,
            "chan": self.chan,
            "freq": self.freq,
            "mkr_ident": self.mkr_ident,
            "mkr_shape": self.mkr_shape,
            "mkr_brg": self.mkr_brg,
            "alt_code": self.alt_code.value if self.alt_code else None,
            "dme_ssv": self.dme_ssv.value if self.dme_ssv else None,
            "low_nav_on_high_chart_flag": self.low_nav_on_high_chart_flag,
            "z_mkr_flag": self.z_mkr_flag,
            "fss_id": self.fss_id,
            "fss_name": self.fss_name,
            "fss_hours": self.fss_hours,
            "notam_id": self.notam_id,
            "quad_ident": self.quad_ident,
            "pitch_flag": self.pitch_flag,
            "catch_flag": self.catch_flag,
            "sua_atcaa_flag": self.sua_atcaa_flag,
            "restriction_flag": self.restriction_flag,
            "hiwas_flag": self.hiwas_flag,
        }
        return {**base_dict, **this_dict}
