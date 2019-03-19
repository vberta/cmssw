import math

# respect nanoAOD structure: Collection_modifiers_variable
variables =  {        
    'PV' : {
        'appliesTo' : ['Signal*','Sideband*','Dimuon'],
        'inputCollection' : 'PV',
        'modifiers': '',
        'variables': {
            'npvsGood' :  ('Number of good primary vertexes',  100, 0, 100),
            },
        },
    'RecoZ' : {
        'appliesTo' : ['Dimuon'],
        'inputCollection' : 'RecoZ',
        'modifiers': '',
         'variables': {
            'Muon_corrected_mass' :  ('Dimuon mass (Rochester corr.)',  100, 50, 150),
            'Muon_corrected_pt' :  ('Dimuon pT (Rochester corr.)',  100, 00, 100),
            'Muon_corrected_y' :  ('Dimuon y (Rochester corr.)',  100, -3, 3),
            'Muon_corrected_CStheta' :  ('Dimuon CS cosTheta (Rochester corr.)',  100, -1, 1),
            'Muon_corrected_CSphi' :  ('Dimuon CS phi (Rochester corr.)',  100, -math.pi, math.pi),
            'Muon_corrected_MET_nom_uPar' :  ('uPar on Z (Rochester corr./smear MET)',  100, -100, 100),
            'Muon_corrected_MET_nom_uPer' :  ('uPer on Z (Rochester corr./smear MET)',  100, -100, 100),
            },
        },
    'Muon1': { 
        'appliesTo' : ['Signal*','Sideband*','Dimuon'],
        'inputCollection' : 'Muon',
        'newCollection': 'SelectedMuon1', 
        'modifiers': '', 
        'index': 'Idx_mu1',
        'variables': { 
            'corrected_pt':   ('muon pt (Rochester corr.)',  100, 20, 100),
            'corrected_MET_uPar':   ('uPar (Rochester corr./smear MET)',  100, -100, 100),
            'corrected_MET_uPer':   ('uPer (Rochester corr./smear MET)',  100, -100, 100),
            'corrected_MET_nom_Wlikemt':   ('W-like Mt (Rochester corr./smear MET)',  100, 0, 200),
            'pfRelIso04_all': ('muon pfRelIso04', 100, 0., 0.5),
            'eta':            ('muon eta', 100, -2.5, 2.5),
            'dxy':            ('muon dxy', 100, -0.04, 0.04),
            'dz':             ('muon dz', 100, -0.2, 0.2),
            },
    },
    'Muon2': { 
        'appliesTo' : ['Dimuon'],
        'inputCollection' : 'Muon',
        'newCollection': 'SelectedMuon2', 
        'modifiers': '', 
        'index': 'Idx_mu2',
        'variables': { 
            'corrected_pt':   ('muon pt (Rochester corr.)',  100, 20, 100),
            'corrected_MET_nom_Wlikemt':   ('W-like Mt (Rochester corr./smear MET)',  100, 0, 200),
            'corrected_MET_uPar':   ('uPar (Rochester corr./smear MET)',  100, -100, 100),
            'corrected_MET_uPer':   ('uPer (Rochester corr./smear MET)',  100, -100, 100),
            'eta':            ('muon eta', 100, -2.5, 2.5),
            'dxy':            ('muon dxy', 100, -0.04, 0.04),
            'dz':             ('muon dz', 100, -0.2, 0.2),
            'pfRelIso04_all': ('muon pfRelIso04', 100, 0., 0.5),
            },
    },    
}