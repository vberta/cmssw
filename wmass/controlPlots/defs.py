import os
import copy
import sys
sys.path.append('../../framework')
import ROOT
from RDFtreeV2 import RDFtree

from controlPlots import *

ROOT.ROOT.EnableImplicitMT(48)

# corrected = Rochester
muon = '_corrected'

# nom = MET w/ jet smearing
met = '_nom'

selections = {
    'Signal' : {
        'MC' : {
            'cut': \
                'Vtype==0 && ' + \
                'HLT_SingleMu24 && '+ \
                ('Muon%s_pt[Idx_mu1]>25. && ' % muon) + \
                ('Muon%s_MET%s_mt[Idx_mu1]>0. && ' % (muon, met) ) + \
                'MET_filters==1 && ' + \
                'nVetoElectrons==0 && ' + \
                '1',            
            'weight' : \
                'puWeight*' + \
                'Muon_Trigger_SF[Idx_mu1]*' + \
                'Muon_ID_SF[Idx_mu1]*' + \
                'Muon_ISO_SF[Idx_mu1]',
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

    'Sideband' : {
        'MC' : {
            'cut': \
                'Vtype==1 && ' +\
                'HLT_SingleMu24 && ' +\
                ('Muon%s_pt[Idx_mu1]>25. && ' % muon) + \
                ('Muon%s_MET%s_mt[Idx_mu1]>0. && ' % (muon, met)) + \
                'MET_filters==1 && ' +\
                'nVetoElectrons==0 && ' +\
                '1',
            'weight' : \
                'puWeight*' + \
                'Muon_Trigger_SF[Idx_mu1]*' + \
                'Muon_ID_SF[Idx_mu1]*' + \
                'Muon_ISO_SF[Idx_mu1]',
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

    'Dimuon' : {
        'MC' : {
            'cut': \
                'Vtype==2 && '+ \
                'HLT_SingleMu24 && '+ \
                ('Muon%s_pt[Idx_mu1]>25. && Muon%s_pt[Idx_mu2]>20. && ' % (muon, muon) ) + \
                'MET_filters==1 && '+ \
                'nVetoElectrons==0 && '+ \
                '1',
            'weight' : \
                'puWeight*' +\
                'Muon_Trigger_SF[Idx_mu1]*Muon_ISO_SF[Idx_mu1]*Muon_ID_SF[Idx_mu1]*' +\
                'Muon_Trigger_SF[Idx_mu2]*Muon_ISO_SF[Idx_mu2]*Muon_ID_SF[Idx_mu2]',
            },
        'DATA' : {
            'cut': \
                'Vtype==2 && '+ \
                'HLT_SingleMu24 && '+ \
                ('Muon%s_pt[Idx_mu1]>25. && Muon%s_pt[Idx_mu2]>20. && ' % (muon, muon))+ \
                'MET_filters==1 && '+ \
                'nVetoElectrons==0 && '+ \
                '1',
            'weight' : '',
            },
        },
    }

myselections = {}
myselections['Signal_Plus'] = copy.deepcopy(selections['Signal'])
#myselections['Signal_Minus'] = copy.deepcopy(selections['Signal'])
myselections['Signal_Plus']['MC']['cut']  += ' && Muon_charge[Idx_mu1]>0'
#myselections['Signal_Minus']['MC']['cut'] += ' && Muon_charge[Idx_mu1]<0'
#myselections['Sideband_Plus'] = copy.deepcopy(selections['Sideband'])
#myselections['Sideband_Minus'] = copy.deepcopy(selections['Sideband'])
#myselections['Sideband_Plus']['MC']['cut']  += ' && Muon_charge[Idx_mu1]>0'
#myselections['Sideband_Minus']['MC']['cut'] += ' && Muon_charge[Idx_mu1]<0'

# respect nanoAOD structure: Collection_modifiers_variable

variables =  {    

    'Muon': { 
        'newCollection': 'SelectedMuon', 
        'modifiers': '', 
        'index': 'Idx_mu1',
        'variables': { 
            'corrected_pt': ('muon pt',  100, 20, 100),
            'eta':          ('muon eta', 100, -2.5, 2.5),
            },
    },
            
}

inputDir = '/gpfs/ddn/cms/user/bianchi/NanoAOD2016-V0/'
outdir = 'V0'

production_file = open('/home/users/bianchini/wmass/CMSSW_10_2_9/src/PhysicsTools/NanoAODTools/crab/mcsamples_2016.txt', 'r')
production_content = [x.strip() for x in production_file.readlines()]
samples = os.listdir(inputDir)
samples_dict = {}
for sample in samples:
    xsec = -1
    for prod in production_content:
        if sample[:-5] in prod:
            xsec = float(prod.split(',')[-1])
            break
    samples_dict[sample] = {'dir' : sample, 'xsec' : xsec}

for sample_key, sample in samples_dict.iteritems():
    dataType = 'MC' if 'Run' not in sample_key else 'DATA'
    print 'Analysing sample '+sample_key+' with xsec '+'{:0.3f}'.format(sample['xsec'])+' pb, (data type: '+dataType+')'
    continue
    p = RDFtree(outputDir=outdir, inputFile=(inputDir+sample['dir']+'/tree.root') )
    for sel_key, sel in myselections.iteritems():
        print '\tBranching: '+sel_key
        p.branch(nodeToStart='input', 
                 nodeToEnd='controlPlots'+sel_key, 
                 outputFile="%s_%s.root" % (sample_key, sel_key), 
                 modules = [controlPlots(selections=sel, variables=variables, dataType=dataType, xsec=sample['xsec'], file=inputDir+sample['dir']+'/tree.root')])    
    p.getOutput()

samples_merging = {
    'WJets'  : [x for x in samples if 'WJetsToLNu' in x],
    'DYJets' : [x for x in samples if 'DYJetsToLL' in x],
    'QCD' : [x for x in samples if 'QCD_' in x],
    'Top' : [x for x in samples if ('TTJets' in x or 'ST_' in x)],
    'Diboson' : [x for x in samples if ('WW_' in x or 'WZ_' in x or 'ZZ_' in x)],
    'Data' : [x for x in samples if 'Run' in x],
}

for sel_key, sel in myselections.iteritems():
    for sample_merging_key, sample_merging in samples_merging.iteritems():
        cmd = 'hadd -f %s/%s_%s.root' % (outdir,sample_merging_key,sel_key)
        for isample in sample_merging:
            cmd += ' %s/%s_%s.root' % (outdir,isample,sel_key)
        print cmd
        #os.system(cmd)

#from plotter import plotter
#plt = plotter(outdir= 'TESTstack', folder = 'TEST', fileList = ['DY_plus.root', 'ttbar_plus.root', 'diboson_plus.root','W_plus.root','QCD_plus.root', 'data_plus.root'], norm = 2.7)
#plt.plotStack()


























































