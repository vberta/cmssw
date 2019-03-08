import os
import copy
import argparse
import sys
sys.path.append('../../framework')
import ROOT
from RDFtreeV2 import RDFtree

from controlPlots import *
from plotter import *

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

parser = argparse.ArgumentParser("")
parser.add_argument('-tag', '--tag', type=str, default="TEST",      help="")
parser.add_argument('-dataYear', '--dataYear',type=int, default=2016, help="")
parser.add_argument('-hadd', '--hadd',type=int, default=False, help="")
parser.add_argument('-plot', '--plot',type=int, default=False, help="")
parser.add_argument('-tdf', '--tdf',type=int, default=True, help="")
args = parser.parse_args()
tag = args.tag
dataYear = args.dataYear
hadd = args.hadd
plot = args.plot
tdf = args.tdf
print "tag =", bcolors.OKGREEN, tag, bcolors.ENDC, \
    ", dataYear =", bcolors.OKGREEN, str(dataYear), bcolors.ENDC

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
myselections['SignalPlus'] = copy.deepcopy(selections['Signal'])
#myselections['SignalMinus'] = copy.deepcopy(selections['Signal'])
myselections['SignalPlus']['MC']['cut']  += ' && Muon_charge[Idx_mu1]>0'
#myselections['SignalMinus']['MC']['cut'] += ' && Muon_charge[Idx_mu1]<0'
#myselections['SidebandPlus'] = copy.deepcopy(selections['Sideband'])
#myselections['SidebandMinus'] = copy.deepcopy(selections['Sideband'])
#myselections['SidebandPlus']['MC']['cut']  += ' && Muon_charge[Idx_mu1]>0'
#myselections['SidebandMinus']['MC']['cut'] += ' && Muon_charge[Idx_mu1]<0'

# respect nanoAOD structure: Collection_modifiers_variable
variables =  {    
    'Muon': { 
        'newCollection': 'SelectedMuon', 'modifiers': '', 'index': 'Idx_mu1',
        'variables': { 
            'corrected_pt': ('muon pt',  100, 20, 100),
            'eta':          ('muon eta', 100, -2.5, 2.5),
            },
    },
}

inputDir, outDir = ('/gpfs/ddn/cms/user/bianchi/NanoAOD%s-%s/' % (str(dataYear), tag)), ('%s/' % tag)
if not os.path.isdir(outDir): os.system('mkdir '+outDir)

# full production
production_file = open('/home/users/bianchini/wmass/CMSSW_10_2_9/src/PhysicsTools/NanoAODTools/crab/mcsamples_%s.txt' % str(dataYear), 'r')
production_content = [x.strip() for x in production_file.readlines()]

restrict_to = ['QCD_Pt-300to470_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8', 'QCD_Pt-80to120_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8', 'SingleMuon_Run2016B_ver2' ]

# available filed
samples = os.listdir(inputDir)

samples_dict = {}
for sample in samples:    
    if '_ext' in sample: sample_stripped = sample[:-5]
    else: sample_stripped = sample        
    xsec = -1
    accept = len(restrict_to)==0 or sample_stripped in restrict_to
    if not accept: continue
    # add each Run period separately
    if 'Run' in sample:
        samples_dict[sample] = {'dir' : [sample], 'xsec' : xsec}
        continue
    # match for '_ext' to identify extensions of same process
    for prod in production_content:
        if sample_stripped in prod: xsec = float(prod.split(',')[-1])
    if sample_stripped not in samples_dict.keys():
        samples_dict[sample_stripped] = {'dir' : [sample], 'xsec' : xsec}
    else:
        samples_dict[sample_stripped]['dir'].append(sample)

for sample_key, sample in samples_dict.iteritems():
    dataType = 'MC' if 'Run' not in sample_key else 'DATA'
    print 'Analysing sample', bcolors.OKBLUE, sample_key, bcolors.ENDC
    print '\tdirectories =', bcolors.OKBLUE, sample['dir'] , bcolors.ENDC
    print '\txsec = '+'{:0.3f}'.format(sample['xsec'])+' pb', \
        ', (data type is', bcolors.OKBLUE, dataType, bcolors.ENDC, ')'
    if not tdf: continue
    inputFile = ROOT.std.vector("std::string")()
    for x in sample['dir']: inputFile.push_back(inputDir+x+"/tree.root")
    p = RDFtree(outputDir=outDir, inputFile=inputFile  )
    for sel_key, sel in myselections.iteritems():
        print '\tBranching:', bcolors.OKBLUE, sel_key, bcolors.ENDC
        p.branch(nodeToStart='input', 
                 nodeToEnd='controlPlots'+sel_key, 
                 outputFile="%s_%s.root" % (sample_key, sel_key), 
                 modules = [controlPlots(selections=sel, variables=variables, dataType=dataType, xsec=sample['xsec'], inputFile=inputFile)])    
    p.getOutput()

samples_merging = {
    'WJets'  : [x for x in samples_dict.keys() if 'WJetsToLNu' in x],
    'DYJets' : [x for x in samples_dict.keys() if 'DYJetsToLL' in x],
    'QCD' : [x for x in samples_dict.keys() if 'QCD_' in x],
    'Top' : [x for x in samples_dict.keys() if ('TTJets' in x or 'ST_' in x)],
    'Diboson' : [x for x in samples_dict.keys() if ('WW_' in x or 'WZ_' in x or 'ZZ_' in x)],
    'Data' : [x for x in samples_dict.keys() if 'Run' in x],
}

fileList = []
for sel_key, sel in myselections.iteritems():
    for sample_merging_key, sample_merging in samples_merging.iteritems():
        if len(sample_merging)>0:
            fileList.append( '%s_%s.root' % (sample_merging_key,sel_key))
            cmd = 'hadd -f %s/%s_%s.root' % (outDir,sample_merging_key,sel_key)
            for isample in sample_merging:
                cmd += ' %s/%s_%s.root' % (outDir,isample,sel_key)
            if hadd:
                print bcolors.OKGREEN, cmd, bcolors.ENDC
                os.system(cmd)

print fileList
#from plotter import plotter
if plot:
    plt = plotter(outdir=outDir, folder=outDir, fileList=fileList, norm = 2.7)
    plt.plotStack()
















































