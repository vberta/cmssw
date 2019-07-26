import math

bkg_variables = {
    'Muon1': {
        'appliesTo' : ['bkg_Signal*', 'bkg_Sideband*'],
        'inputCollection' : 'Muon',
        'newCollection': 'bkgSelMuon1',
        'index': 'Idx_mu1',
        'variables': {
            'corrected_pt':   ('muon p_{T} (Rochester corr.)',  100, 25, 65),
            'eta':            ('muon eta', 100, -2.5, 2.5),
            'corrected_MET_nom_mt':   ('M_{T} (Rochester corr./smear MET)',  120, 0, 120),
            'pfRelIso04_all': ('muon pfRelIso04', 400, 0., 0.5),
            'dxy':            ('muon dxy', 100, -0.01, 0.01),
            'dz':             ('muon dz', 100, -0.05, 0.05),
            },
        'newvariables':{
            'pfRelIso04_all_corrected_pt': ('muon pfAbsIso04',800, 0., 40,'Muon_pfRelIso04_all*Muon_corrected_pt'),
        },
        'D2variables':{
            'pfRelIso04_all_corrected_MET_nom_mt':   ('M_{T} (Rochester corr./smear MET) VS muon pfRelIso04', 400, 0., 0.5,120, 0, 120, "Muon_pfRelIso04_all[Idx_mu1]","Muon_corrected_MET_nom_mt[Idx_mu1]", "Muon_eta[Idx_mu1]"),
            # 'pfRelIso04_all_corrected_pt_corrected_MET_nom_mt':   ('M_{T} (Rochester corr./smear MET) VS muon pfIso04', 800, 0., 40,120, 0, 120, "bkgSelMuon1_pfRelIso04_all_corrected_pt[Idx_mu1]","Muon_corrected_MET_nom_mt[Idx_mu1]", "Muon_eta[Idx_mu1]"),   #out-of -ontrolplots implementation only          
            'pfRelIso04_all_corrected_pt_corrected_MET_nom_mt':   ('M_{T} (Rochester corr./smear MET) VS muon pfIso04', 800, 0., 40,120, 0, 120, "Muon_pfRelIso04_all_corrected_pt[Idx_mu1]","Muon_corrected_MET_nom_mt[Idx_mu1]", "Muon_eta[Idx_mu1]"), #INTEGRATED WITH CONTROL PLOTS IMPLEMENTATION

            # 'pfRelIso04_all_MET_pt':   ('MET p_{T} VS muon pfRelIso04', 400, 0., 0.5,120, 0, 120, "Muon_pfRelIso04_all[Idx_mu1]","MET_pt"),
            # 'pfRelIso04_all_corrected_pt_MET_pt':   ('MET p_{T} VS muon pfIso04', 800, 0., 40, 120, 0, 120,"Muon_pfRelIso04_all_corrected_pt[Idx_mu1]","MET_pt"),
        },
    },
    'MET' :{
        'appliesTo' : ['bkg_Signal*','bkg_Sideband*'],
        'inputCollection' : 'MET',
        # 'newCollection': 'bkgSelMET',#out-of -ontrolplots implementation only     
        'variables': {
            'pt':  ('MET P_{T}',  120, 0, 120),
        },
    },
        
    'PV' : {
        'appliesTo' : ['Signal*','Sideband*'],
        'inputCollection' : 'PV',
        # 'newCollection': 'bkgSelPV',#out-of -ontrolplots implementation only     
        'variables': {
            'npvsGood' :  ('Number of good primary vertices',  100, 0, 100),
            },
    }
}
