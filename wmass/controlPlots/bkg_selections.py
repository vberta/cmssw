# corrected = Rochester
muon = '_corrected'

v0 = False 
if(v0) : version = ''
else :version = 'BCDEF_'

# nom = MET w/ jet smearing
met = '_nom'

bkg_selections = {
    'bkg_Signal' : {
        'MC' : {
            'cut': \
                'Vtype==0 && ' + \
                'HLT_SingleMu24 && '+ \
                ('Muon%s_pt[Idx_mu1]>25. && ' % muon) + \
                ('Muon%s_MET%s_mt[Idx_mu1]>0. && ' % (muon, met) ) + \
                'MET_filters==1 && ' + \
                'nVetoElectrons==0 && ' + \
                '1',
            'weight' : 'Generator_weight*' +\
                'puWeight*' + \
                ('Muon_Trigger_%sSF[Idx_mu1]*'% version) + \
                ('Muon_ID_%sSF[Idx_mu1]*'% version) + \
                ('Muon_ISO_%sSF[Idx_mu1]'% version),
            },
        'DATA' : {
            'cut': \
                'Vtype==0 && ' + \
                'HLT_SingleMu24 && ' + \
                ('Muon%s_pt[Idx_mu1]>25. && ' % muon) + \
                ('Muon%s_MET%s_mt[Idx_mu1]>0. && ' % (muon, met)) +\
                'MET_filters==1 && ' + \
                'nVetoElectrons==0 && ' + \
                '1',
            'weight' : '',
            },
        },
    'bkg_Sideband' : {
        'MC' : {
            'cut': \
                'Vtype==1 && ' +\
                'HLT_SingleMu24 && ' +\
                ('Muon%s_pt[Idx_mu1]>25. && ' % muon) + \
                ('Muon%s_MET%s_mt[Idx_mu1]>0. && ' % (muon, met)) + \
                'MET_filters==1 && ' +\
                'nVetoElectrons==0 && ' +\
                '1',
            'weight' : 'Generator_weight*' +\
                'puWeight*' + \
                ('Muon_Trigger_%sSF[Idx_mu1]*'% version) + \
                ('Muon_ID_%sSF[Idx_mu1]*'% version) + \
                ('Muon_ISO_%sSF[Idx_mu1]'% version),
            },
        'DATA' : {
            'cut': \
                'Vtype==1 && ' +\
                'HLT_SingleMu24 && '+ \
                ('Muon%s_pt[Idx_mu1]>25. && ' % muon) + \
                ('Muon%s_MET%s_mt[Idx_mu1]>0. && ' % (muon, met)) + \
                'MET_filters==1 && ' +\
                'nVetoElectrons==0 && ' + \
                '1',
            'weight' : '',
            },
        },
}

ptBinning = [30,31,32,33,34,35,36,37,38,40,42,44,46,48,50,52,54,57,60,65]
etaBinning = [-2.4,-2.3,-2.2,-2.1,-2.0,-1.9,-1.8,-1.7,-1.6,-1.5,-1.4,-1.3,-1.2,-1.1,-1.0,-0.9,-0.8,-0.7,-0.6,-0.5,-0.4,-0.3,-0.2,-0.1,0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4]
# ptBinning = [30,32,34,36,38,41,45,50,65]
# etaBinning = [0.0,0.2,0.4,0.8,1.2,1.6,2.0,2.4]

