import os
import copy


selections = {

    'signal' : {
        'mc' : {
            'cut': 'Vtype==0 && ' \
                #'Muon_HLT && ' \
                #('Muon_pt%s[Idx_mu1]>25. && ' % muon) \
                #('Muon%s_MET%s_mt[Idx_mu1]>40.' % (muon, met)) \
                #'MET_filters==1 && ' \
                #'nVetoElectrons==0 && ', \
                '1',            
            'weight' : \
                'puWeight*' \
                'Muon_effSF[Idx_mu1]',
            },
        'data' : {
            'cut': 'Vtype==0 && ' \
                #'Muon_HLT && ' \
                #('Muon_pt%s[Idx_mu1]>25. && ' % muon_pt) \
                #('Muon%s_MET%s_mt[Idx_mu1]>40. ' % (muon, met)) \
                #'MET_filters==1 && ' \
                #'nVetoElectrons==0 && ', \
                '1',
            'weight' : '',
            },
        },

    'control' : {
        'mc' : {
            'cut': 'Vtype==1 && ' \
                #'Muon_HLT && ' \
                #('Muon_pt%s[Idx_mu1]>25. && ' % muon_pt) \
                #('Muon%s_MET%s_mt[Idx_mu1]<40. ' % (muon, met)) \
                #'MET_filters==1 && ' \
                #'nVetoElectrons==0 && ', \
                '1',
            'weight' : \
                'puWeight*' \
                'Muon_effSF[Idx_mu1]',
            },
        'data' : {
            'cut': 'Vtype==1 && ' \
                #'Muon_HLT && ' \
                #('Muon_pt%s[Idx_mu1]>25. && ' % muon_pt) \
                #('Muon%s_MET%s_mt[Idx_mu1]<40.' % (muon, met)) \
                #'MET_filters==1 && ' \
                #'nVetoElectrons==0 && ', \
                '1',
            'weight' : '',
            },
        },

    'dimuon' : {
        'mc' : {
            'cut': 'Vtype==2 && ' \
                #'Muon_HLT && ' \
                #('Muon_pt%s[Idx_mu1]>25. && Muon_pt%s[Muon_idx2]>20.' % (muon_pt, muon_pt)) \
                #'MET_filters==1 && ' \
                #'nVetoElectrons==0 && ', \
                '1',
            'weight' : \
                'puWeight*' \
                'Muon_effSF[Idx_mu1]*Muon_effSF[Muon_idx2]',
            },
        'data' : {
            'cut': 'Vtype==2 && ' \
                #'Muon_HLT && ' \
                #('Muon_pt%s[Idx_mu1]>25. && Muon_pt%s[Muon_idx2]>20.' % (muon_pt, muon_pt)) \
                #'MET_filters==1 && ' \
                #'nVetoElectrons==0 && ', \
                '1',
            'weight' : '',
            },
        },
    }

selections['signalplus'] = copy.deepcopy(selections['signal'])
selections['signalminus'] = copy.deepcopy(selections['signal'])
selections['signalplus']['mc']['cut']  += ' && Muon_charge[Idx_mu1]>0'
selections['signalminus']['mc']['cut'] += ' && Muon_charge[Idx_mu1]<0'

selections['controlplus'] = copy.deepcopy(selections['control'])
selections['controlminus'] = copy.deepcopy(selections['control'])
selections['controlplus']['mc']['cut']  += ' && Muon_charge[Idx_mu1]>0'
selections['controlminus']['mc']['cut'] += ' && Muon_charge[Idx_mu1]<0'


# respect nanoAOD structure: Collection_modifiers_variable

# modifiers:

# corrected = Rochester
muon = '_corrected'

# nom = MET w/ jet smearing
met = '_nom'


variables =  {
    

        'Muon': { # collection we want to take

                'newCollection': 'SelectedMuon', # if we want to define a new subcollection, what is it called?
                'modifiers': '', # modifiers we have added to the original collection
                'index': 'Idx_mu1', # cuts or idx for defining the new collection
                'variables': { 
                                'corrected_pt': ('muon pt', 100, 20, 100), # variable to plot: (title of x axis, number of bins, xLow, xUp)
                                'eta': ('muon eta', 100, -2.5, 2.5),
                                #'corrected_MET_nom_mt':('mt',100, 30, 100), #not working in this version of samples

        },

    },
            
}


import sys
sys.path.append('../../framework')

import ROOT

from RDFtreeV2 import RDFtree

ROOT.ROOT.EnableImplicitMT(48)

from controlPlots import *

inputDir = '/gpfs/ddn/cms/user/bianchi/NanoAOD2016-TEST/'

# mc samples

samples = {
    
    'W' : ['WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8', 61526.7],
    'DY' : ['DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_ext2', 6025.2],
    'ttbar': ['TTJets_SingleLeptFromT_TuneCUETP8M1_13TeV-madgraphMLM-pythia8', 182.0],
    'diboson': ['WW_TuneCUETP8M1_13TeV-pythia8', 115.0],
    'QCD' : ['QCD_Pt-30to50_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8', 1655000.0],

}

for sample, mylist in samples.iteritems():

    print 'analysing', sample

    p = RDFtree(outputDir = 'TEST', inputFile = inputDir+mylist[0]+'/tree.root')
    p.branch(nodeToStart = 'input', nodeToEnd = 'controlPlotsPlus',outputFile="{}_plus.root".format(sample), modules = [controlPlots(selections = selections['signalplus'], variables = variables, dataType = 'mc', xsec = mylist[1], file = inputDir+mylist[0]+'/tree.root')])
    p.branch(nodeToStart = 'input', nodeToEnd = 'controlPlotsMinus',outputFile="{}_minus.root".format(sample), modules = [controlPlots(selections = selections['signalminus'], variables = variables, dataType = 'mc', xsec = mylist[1], file = inputDir+mylist[0]+'/tree.root')])
    p.getOutput()

# data
print 'analysing data'

p = RDFtree(outputDir = 'TEST', inputFile = inputDir+'SingleMuon'+'/tree.root')
p.branch(nodeToStart = 'input', nodeToEnd = 'controlPlotsPlus',outputFile="data_plus.root", modules = [controlPlots(selections = selections['signalplus'], variables = variables, dataType = 'data', xsec = 1, file = inputDir+'SingleMuon'+'/tree.root')])
p.branch(nodeToStart = 'input', nodeToEnd = 'controlPlotsMinus',outputFile="data_minus.root", modules = [controlPlots(selections = selections['signalminus'], variables = variables, dataType = 'data', xsec = 1, file = inputDir+'SingleMuon'+'/tree.root')])
p.getOutput()

from plotter import plotter

plt = plotter(outdir= 'TESTstack', folder = 'TEST', fileList = ['DY_plus.root', 'ttbar_plus.root', 'diboson_plus.root','W_plus.root','QCD_plus.root', 'data_plus.root'], norm = 2.7)
plt.plotStack()


























































