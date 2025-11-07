from nasrparse.records import (
    APTs,
    CLSs,
    AWYs,
    ATCs,
    AWOSs,
    ARBs,
    CDRs,
    COMs,
    DPs,
    FIXs,
    FRQs,
    FSSs,
    HPFs,
    ILSs,
    LIDs,
    MAAs,
    MILs,
    MTRs,
    NAVs,
    PFRs,
    PJAs,
    RDRs,
    STARs,
    WXLs,
)

from sqlite3 import connect

import json
import os


class NASR:
    __exists: bool
    __dir_path: str

    __APTs: APTs
    __CLSs: CLSs
    __AWYs: AWYs
    __ATCs: ATCs
    __AWOSs: AWOSs
    __ARBs: ARBs
    __CDRs: CDRs
    __COMs: COMs
    __DPs: DPs
    __FIXs: FIXs
    __FRQs: FRQs
    __FSSs: FSSs
    __HPFs: HPFs
    __ILSs: ILSs
    __LIDs: LIDs
    __MAAs: MAAs
    __MILs: MILs
    __MTRs: MTRs
    __NAVs: NAVs
    __PFRs: PFRs
    __PJAs: PJAs
    __RDRs: RDRs
    __STARs: STARs
    __WXLs: WXLs

    def __init__(self, path: str) -> None:
        self.__exists = False
        self.__dir_path = ""

        self.__set_path(path)

        self.__APTs = APTs(self.__dir_path)
        self.__CLSs = CLSs(self.__dir_path)
        self.__AWYs = AWYs(self.__dir_path)
        self.__ATCs = ATCs(self.__dir_path)
        self.__AWOSs = AWOSs(self.__dir_path)
        self.__ARBs = ARBs(self.__dir_path)
        self.__CDRs = CDRs(self.__dir_path)
        self.__COMs = COMs(self.__dir_path)
        self.__DPs = DPs(self.__dir_path)
        self.__FIXs = FIXs(self.__dir_path)
        self.__FRQs = FRQs(self.__dir_path)
        self.__FSSs = FSSs(self.__dir_path)
        self.__HPFs = HPFs(self.__dir_path)
        self.__ILSs = ILSs(self.__dir_path)
        self.__LIDs = LIDs(self.__dir_path)
        self.__MAAs = MAAs(self.__dir_path)
        self.__MILs = MILs(self.__dir_path)
        self.__MTRs = MTRs(self.__dir_path)
        self.__NAVs = NAVs(self.__dir_path)
        self.__PFRs = PFRs(self.__dir_path)
        self.__PJAs = PJAs(self.__dir_path)
        self.__RDRs = RDRs(self.__dir_path)
        self.__STARs = STARs(self.__dir_path)
        self.__WXLs = WXLs(self.__dir_path)

    def __set_path(self, path: str) -> None:
        self.__dir_path = path
        if os.path.exists(self.__dir_path):
            print(f"NASR Parser :: Found NASR dir at: {path}")
            self.__exists = True
        else:
            print(f"NASR Parser :: Unable to find NASR dir at: {path}")
            return

    def parse_apt_ars(self) -> None:
        if self.__exists:
            self.__APTs.parse_apt_ars()

    def parse_apt_att(self) -> None:
        if self.__exists:
            self.__APTs.parse_apt_att()

    def parse_apt_base(self) -> None:
        if self.__exists:
            self.__APTs.parse_apt_base()

    def parse_apt_con(self) -> None:
        if self.__exists:
            self.__APTs.parse_apt_con()

    def parse_apt_rmk(self) -> None:
        if self.__exists:
            self.__APTs.parse_apt_rmk()

    def parse_apt_rwy(self) -> None:
        if self.__exists:
            self.__APTs.parse_apt_rwy()

    def parse_apt_rwy_end(self) -> None:
        if self.__exists:
            self.__APTs.parse_apt_rwy_end()

    def parse_apt(self) -> None:
        if self.__exists:
            self.__APTs.parse()

    def parse_awy_alt(self) -> None:
        if self.__exists:
            self.__AWYs.parse_awy_alt()

    def parse_awy_base(self) -> None:
        if self.__exists:
            self.__AWYs.parse_awy_base()

    def parse_awy_seg(self) -> None:
        if self.__exists:
            self.__AWYs.parse_awy_seg()

    def parse_awy_seg_alt(self) -> None:
        if self.__exists:
            self.__AWYs.parse_awy_seg_alt()

    def parse_awy(self) -> None:
        if self.__exists:
            self.__AWYs.parse()

    def parse_arb_base(self) -> None:
        if self.__exists:
            self.__ARBs.parse_arb_base()

    def parse_arb_seg(self) -> None:
        if self.__exists:
            self.__ARBs.parse_arb_seg()

    def parse_arb(self) -> None:
        if self.__exists:
            self.__ARBs.parse()

    def parse_atc_atis(self) -> None:
        if self.__exists:
            self.__ATCs.parse_atc_atis()

    def parse_atc_base(self) -> None:
        if self.__exists:
            self.__ATCs.parse_atc_base()

    def parse_atc_rmk(self) -> None:
        if self.__exists:
            self.__ATCs.parse_atc_rmk()

    def parse_atc_svc(self) -> None:
        if self.__exists:
            self.__ATCs.parse_atc_svc()

    def parse_atc(self) -> None:
        if self.__exists:
            self.__ATCs.parse()

    def parse_awos_base(self) -> None:
        if self.__exists:
            self.__AWOSs.parse_awos_base()

    def parse_awos(self) -> None:
        if self.__exists:
            self.__AWOSs.parse()

    def parse_cdr_base(self) -> None:
        if self.__exists:
            self.__CDRs.parse_cdr_base()

    def parse_cdr(self) -> None:
        if self.__exists:
            self.__CDRs.parse()

    def parse_cls_arsp(self) -> None:
        if self.__exists:
            self.__CLSs.parse_cls_arsp()

    def parse_cls(self) -> None:
        if self.__exists:
            self.__CLSs.parse()

    def parse_com_base(self) -> None:
        if self.__exists:
            self.__COMs.parse_com_base()

    def parse_com(self) -> None:
        if self.__exists:
            self.__COMs.parse()

    def parse_dp_apt(self) -> None:
        if self.__exists:
            self.__DPs.parse_dp_apt()

    def parse_dp_base(self) -> None:
        if self.__exists:
            self.__DPs.parse_dp_base()

    def parse_dp_rte(self) -> None:
        if self.__exists:
            self.__DPs.parse_dp_rte()

    def parse_dp(self) -> None:
        if self.__exists:
            self.__DPs.parse()

    def parse_fix_base(self) -> None:
        if self.__exists:
            self.__FIXs.parse_fix_base()

    def parse_fix_chrt(self) -> None:
        if self.__exists:
            self.__FIXs.parse_fix_chrt()

    def parse_fix_nav(self) -> None:
        if self.__exists:
            self.__FIXs.parse_fix_nav()

    def parse_fix(self) -> None:
        if self.__exists:
            self.__FIXs.parse()

    def parse_frq_base(self) -> None:
        if self.__exists:
            self.__FRQs.parse_frq_base()

    def parse_frq(self) -> None:
        if self.__exists:
            self.__FRQs.parse()

    def parse_fss_base(self) -> None:
        if self.__exists:
            self.__FSSs.parse_fss_base()

    def parse_fss_rmk(self) -> None:
        if self.__exists:
            self.__FSSs.parse_fss_rmk()

    def parse_fss(self) -> None:
        if self.__exists:
            self.__FSSs.parse()

    def parse_hpf_base(self) -> None:
        if self.__exists:
            self.__HPFs.parse_hpf_base()

    def parse_hpf_chrt(self) -> None:
        if self.__exists:
            self.__HPFs.parse_hpf_chrt()

    def parse_hpf_rmk(self) -> None:
        if self.__exists:
            self.__HPFs.parse_hpf_rmk()

    def parse_hpf_spd_alt(self) -> None:
        if self.__exists:
            self.__HPFs.parse_hpf_spd_alt()

    def parse_hpf(self) -> None:
        if self.__exists:
            self.__HPFs.parse()

    def parse_ils_base(self) -> None:
        if self.__exists:
            self.__ILSs.parse_ils_base()

    def parse_ils_dme(self) -> None:
        if self.__exists:
            self.__ILSs.parse_ils_dme()

    def parse_ils_gs(self) -> None:
        if self.__exists:
            self.__ILSs.parse_ils_gs()

    def parse_ils_mkr(self) -> None:
        if self.__exists:
            self.__ILSs.parse_ils_mkr()

    def parse_ils_rmk(self) -> None:
        if self.__exists:
            self.__ILSs.parse_ils_rmk()

    def parse_ils(self) -> None:
        if self.__exists:
            self.__ILSs.parse()

    def parse_lid_base(self) -> None:
        if self.__exists:
            self.__LIDs.parse_lid_base()

    def parse_lid(self) -> None:
        if self.__exists:
            self.__LIDs.parse()

    def parse_maa_base(self) -> None:
        if self.__exists:
            self.__MAAs.parse_maa_base()

    def parse_maa_con(self) -> None:
        if self.__exists:
            self.__MAAs.parse_maa_con()

    def parse_maa_rmk(self) -> None:
        if self.__exists:
            self.__MAAs.parse_maa_rmk()

    def parse_maa_shp(self) -> None:
        if self.__exists:
            self.__MAAs.parse_maa_shp()

    def parse_maa(self) -> None:
        if self.__exists:
            self.__MAAs.parse()

    def parse_mil_base(self) -> None:
        if self.__exists:
            self.__MILs.parse_mil_base()

    def parse_mil(self) -> None:
        if self.__exists:
            self.__MILs.parse()

    def parse_mtr_agy(self) -> None:
        if self.__exists:
            self.__MTRs.parse_mtr_agy()

    def parse_mtr_base(self) -> None:
        if self.__exists:
            self.__MTRs.parse_mtr_base()

    def parse_mtr_pt(self) -> None:
        if self.__exists:
            self.__MTRs.parse_mtr_pt()

    def parse_mtr_sop(self) -> None:
        if self.__exists:
            self.__MTRs.parse_mtr_sop()

    def parse_mtr_terr(self) -> None:
        if self.__exists:
            self.__MTRs.parse_mtr_terr()

    def parse_mtr_wdth(self) -> None:
        if self.__exists:
            self.__MTRs.parse_mtr_wdth()

    def parse_mtr(self) -> None:
        if self.__exists:
            self.__MTRs.parse()

    def parse_nav_base(self) -> None:
        if self.__exists:
            self.__NAVs.parse_nav_base()

    def parse_nav_rmk(self) -> None:
        if self.__exists:
            self.__NAVs.parse_nav_rmk()

    def parse_nav_ckpt(self) -> None:
        if self.__exists:
            self.__NAVs.parse_nav_ckpt()

    def parse_nav(self) -> None:
        if self.__exists:
            self.__NAVs.parse()

    def parse_pfr_base(self) -> None:
        if self.__exists:
            self.__PFRs.parse_pfr_base()

    def parse_pfr_rmt_fmt(self) -> None:
        if self.__exists:
            self.__PFRs.parse_pfr_rmt_fmt()

    def parse_pfr_seg(self) -> None:
        if self.__exists:
            self.__PFRs.parse_pfr_seg()

    def parse_pfr(self) -> None:
        if self.__exists:
            self.__PFRs.parse()

    def parse_pja_base(self) -> None:
        if self.__exists:
            self.__PJAs.parse_pja_base()

    def parse_pja_con(self) -> None:
        if self.__exists:
            self.__PJAs.parse_pja_con()

    def parse_pja(self) -> None:
        if self.__exists:
            self.__PJAs.parse()

    def parse_rdr_base(self) -> None:
        if self.__exists:
            self.__RDRs.parse_rdr_base()

    def parse_rdr(self) -> None:
        if self.__exists:
            self.__RDRs.parse()

    def parse_star_apt(self) -> None:
        if self.__exists:
            self.__STARs.parse_star_apt()

    def parse_star_base(self) -> None:
        if self.__exists:
            self.__STARs.parse_star_base()

    def parse_star_rte(self) -> None:
        if self.__exists:
            self.__STARs.parse_star_rte()

    def parse_star(self) -> None:
        if self.__exists:
            self.__STARs.parse()

    def parse_wxl_base(self) -> None:
        if self.__exists:
            self.__WXLs.parse_wxl_base()

    def parse_wxl_svc(self) -> None:
        if self.__exists:
            self.__WXLs.parse_wxl_svc()

    def parse_wxl(self) -> None:
        if self.__exists:
            self.__WXLs.parse()

    def parse(self) -> None:
        self.parse_apt()
        self.parse_arb()
        self.parse_atc()
        self.parse_awy()
        self.parse_awos()
        self.parse_cdr()
        self.parse_cls()
        self.parse_com()
        self.parse_dp()
        self.parse_fix()
        self.parse_frq()
        self.parse_fss()
        self.parse_hpf()
        self.parse_ils()
        self.parse_lid()
        self.parse_maa()
        self.parse_mil()
        self.parse_mtr()
        self.parse_nav()
        self.parse_pfr()
        self.parse_pja()
        self.parse_rdr()
        self.parse_star()
        self.parse_wxl()

    def to_dict(self, json_file_path: str) -> None:
        if os.path.exists(json_file_path):
            os.remove(json_file_path)

        result = {
            **self.__APTs.to_dict(),
            **self.__CLSs.to_dict(),
            **self.__AWYs.to_dict(),
            **self.__ATCs.to_dict(),
            **self.__AWOSs.to_dict(),
            **self.__ARBs.to_dict(),
            **self.__CDRs.to_dict(),
            **self.__COMs.to_dict(),
            **self.__DPs.to_dict(),
            **self.__FIXs.to_dict(),
            **self.__FRQs.to_dict(),
            **self.__FSSs.to_dict(),
            **self.__HPFs.to_dict(),
            **self.__ILSs.to_dict(),
            **self.__LIDs.to_dict(),
            **self.__MAAs.to_dict(),
            **self.__MILs.to_dict(),
            **self.__MTRs.to_dict(),
            **self.__NAVs.to_dict(),
            **self.__PFRs.to_dict(),
            **self.__PJAs.to_dict(),
            **self.__RDRs.to_dict(),
            **self.__STARs.to_dict(),
            **self.__WXLs.to_dict(),
        }

        with open(json_file_path, "w") as jf:
            json.dump(result, jf, indent=4)

    def to_db(self, db_file_path: str) -> None:
        if os.path.exists(db_file_path):
            os.remove(db_file_path)

        connection = connect(db_file_path)
        db_cursor = connection.cursor()

        self.__APTs.to_db(db_cursor)
        self.__CLSs.to_db(db_cursor)
        self.__AWYs.to_db(db_cursor)
        self.__ATCs.to_db(db_cursor)
        self.__AWOSs.to_db(db_cursor)
        self.__ARBs.to_db(db_cursor)
        self.__CDRs.to_db(db_cursor)
        self.__COMs.to_db(db_cursor)
        self.__DPs.to_db(db_cursor)
        self.__FIXs.to_db(db_cursor)
        self.__FRQs.to_db(db_cursor)
        self.__FSSs.to_db(db_cursor)
        self.__HPFs.to_db(db_cursor)
        self.__ILSs.to_db(db_cursor)
        self.__LIDs.to_db(db_cursor)
        self.__MAAs.to_db(db_cursor)
        self.__MILs.to_db(db_cursor)
        self.__MTRs.to_db(db_cursor)
        self.__NAVs.to_db(db_cursor)
        self.__PFRs.to_db(db_cursor)
        self.__PJAs.to_db(db_cursor)
        self.__RDRs.to_db(db_cursor)
        self.__STARs.to_db(db_cursor)
        self.__WXLs.to_db(db_cursor)

        connection.commit()
        connection.close()
