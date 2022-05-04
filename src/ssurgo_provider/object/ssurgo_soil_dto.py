class SsurgoSoilDto:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
        self.horizon_0 = None
        self.horizon_1 = None
        self.horizon_2 = None

    def to_dict(self):
        horizon_0_dict = None
        horizon_1_dict = None
        horizon_2_dict = None
        if self.horizon_0 is not None:
            horizon_0_dict = self.horizon_0.__dict__
        if self.horizon_1 is not None:
            horizon_1_dict = self.horizon_1.__dict__
        if self.horizon_2 is not None:
            horizon_2_dict = self.horizon_2.__dict__
        return {'latitude': self.latitude,
                'longitude': self.longitude,
                'horizon_0': horizon_0_dict,
                'horizon_1': horizon_1_dict,
                'horizon_2': horizon_2_dict}


class SoilHorizon(object):
    def __init__(self, comppct_r, feature):
        self.comppct_r = comppct_r
        self.hzname = feature.GetField("hzname")
        self.desgndisc = feature.GetField("desgndisc")
        self.desgnmaster = feature.GetField("desgnmaster")
        self.desgnmasterprime = feature.GetField("desgnmasterprime")
        self.desgnvert = feature.GetField("desgnvert")
        self.hzdept_r = feature.GetField("hzdept_r")
        self.hzdepb_r = feature.GetField("hzdepb_r")
        self.hzthk_r = feature.GetField("hzthk_r")
        self.fraggt10_r = feature.GetField("fraggt10_r")
        self.frag3to10_r = feature.GetField("frag3to10_r")
        self.sieveno4_r = feature.GetField("sieveno4_r")
        self.sieveno10_r = feature.GetField("sieveno10_r")
        self.sieveno40_r = feature.GetField("sieveno40_r")
        self.sieveno200_r = feature.GetField("sieveno200_r")
        self.sandtotal_r = feature.GetField("sandtotal_r")
        self.sandvc_r = feature.GetField("sandvc_r")
        self.sandco_r = feature.GetField("sandco_r")
        self.sandmed_r = feature.GetField("sandmed_r")
        self.sandfine_r = feature.GetField("sandfine_r")
        self.sandvf_r = feature.GetField("sandvf_r")
        self.silttotal_r = feature.GetField("silttotal_r")
        self.siltco_r = feature.GetField("siltco_r")
        self.siltfine_r = feature.GetField("siltfine_r")
        self.claytotal_r = feature.GetField("claytotal_r")
        self.claysizedcarb_r = feature.GetField("claysizedcarb_r")
        self.om_r = feature.GetField("om_r")
        self.dbtenthbar_r = feature.GetField("dbtenthbar_r")
        self.dbthirdbar_r = feature.GetField("dbthirdbar_r")
        self.dbfifteenbar_r = feature.GetField("dbfifteenbar_r")
        self.dbovendry_r = feature.GetField("dbovendry_r")
        self.partdensity = feature.GetField("partdensity")
        self.ksat_r = feature.GetField("ksat_r")
        self.awc_r = feature.GetField("awc_r")
        self.wtenthbar_r = feature.GetField("wtenthbar_r")
        self.wthirdbar_r = feature.GetField("wthirdbar_r")
        self.wfifteenbar_r = feature.GetField("wfifteenbar_r")
        self.wsatiated_r = feature.GetField("wsatiated_r")
        self.lep_r = feature.GetField("lep_r")
        self.ll_r = feature.GetField("ll_r")
        self.pi_r = feature.GetField("pi_r")
        self.aashind_r = feature.GetField("aashind_r")
        self.kwfact = feature.GetField("kwfact")
        self.kffact = feature.GetField("kffact")
        self.caco3_r = feature.GetField("caco3_r")
        self.gypsum_r = feature.GetField("gypsum_r")
        self.sar_r = feature.GetField("sar_r")
        self.ec_r = feature.GetField("ec_r")
        self.cec7_r = feature.GetField("cec7_r")
        self.ecec_r = feature.GetField("ecec_r")
        self.sumbases_r = feature.GetField("sumbases_r")
        self.ph1to1h2o_r = feature.GetField("ph1to1h2o_r")
        self.ph01mcacl2_r = feature.GetField("ph01mcacl2_r")
        self.freeiron_r = feature.GetField("freeiron_r")
        self.feoxalate_r = feature.GetField("feoxalate_r")
        self.extracid_r = feature.GetField("extracid_r")
        self.extral_r = feature.GetField("extral_r")
        self.pbray1_r = feature.GetField("pbray1_r")
        self.poxalate_r = feature.GetField("poxalate_r")
        self.ph2o_soluble_r = feature.GetField("ph2osoluble_r")
        self.ptotal_r = feature.GetField("ptotal_r")
        self.excavdifcl = feature.GetField("excavdifcl")
        self.excavdifms = feature.GetField("excavdifms")
        self.chkey = feature.GetField("chkey")
        self.cokey = feature.GetField("cokey")
