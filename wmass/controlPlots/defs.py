import os
import copy
import math
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
parser.add_argument('-rdf', '--rdf',type=int, default=True, help="")
args = parser.parse_args()
tag = args.tag
dataYear = args.dataYear
hadd = args.hadd
plot = args.plot
rdf = args.rdf
print "tag =", bcolors.OKGREEN, tag, bcolors.ENDC, \
    ", dataYear =", bcolors.OKGREEN, str(dataYear), bcolors.ENDC

ROOT.ROOT.EnableImplicitMT()
ROOT.gInterpreter.ProcessLine('''
  gErrorIgnoreLevel = kWarning;
  ''')


def filterVariables(variables={}, selection='Signal', verbose=False):
    if verbose: print '>>', variables
    new_variables = copy.deepcopy(variables)
    delete_vars = []
    for ivar,var in new_variables.iteritems():
        match = False
        appliesTo = var['appliesTo']
        for applyTo in appliesTo:
            if applyTo[-1]=="*":
                if applyTo[0:-1] in selection: 
                    match = True
            else:
                if applyTo==selection:  match = True                
        if not match: 
            delete_vars.append(ivar)
    for ivar in delete_vars: 
        del new_variables[ivar]  
    if verbose: print '<<', new_variables
    return new_variables

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
                'Muon_ISO_SF[Idx_mu2]*Muon_ID_SF[Idx_mu2]',
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
for cut in ['Signal', 'Sideband', 'Dimuon']:
    if cut=='Dimuon':
        myselections['%s' % cut] = copy.deepcopy(selections['%s' % cut])
        continue
    myselections['%sPlus' % cut]  = copy.deepcopy(selections['%s' % cut])
    myselections['%sMinus' % cut] = copy.deepcopy(selections['%s' % cut])
    for d in ['MC','DATA']:
        myselections['%sPlus' % cut][d]['cut']    += ' && Muon_charge[Idx_mu1]>0'
        myselections['%sMinus' % cut][d]['cut']   += ' && Muon_charge[Idx_mu1]<0'

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
#del variables['Muon1']
#del variables['Muon2']


inputDir = ('/scratch/bertacch/NanoAOD%s-%s/' % (str(dataYear), tag))
outDir =  'NanoAOD%s-%s/' % (str(dataYear), tag)

if not os.path.isdir(outDir): os.system('mkdir '+outDir)

# full production
production_file = open('/scratch/bianchini/NanoAOD%s-%s/mcsamples_%s.txt' % (str(dataYear), tag, str(dataYear)), 'r')
production_content = [x.strip() for x in production_file.readlines()]

restrict_to = []
#restrict_to.extend(['QCD_Pt-30to50_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8'])
restrict_to = ['DYJetsToLL']

# available filed
samples = os.listdir(inputDir)

samples_dict = {}
for sample in samples:    
    if '_ext' in sample: sample_stripped = sample[:-5]
    else: sample_stripped = sample        
    xsec = -1
    accept = False
    for r in restrict_to: 
        if r in sample_stripped: accept = True
    accept |= (len(restrict_to)==0)
    if not accept: continue

    # add each Run period separately
    if 'Run' in sample:
        samples_dict[sample] = {'dir' : [sample], 'xsec' : xsec, 'subsel' : {'none' : ''}}
        continue
    # match for '_ext' to identify extensions of same process
    for prod in production_content:
        if sample_stripped in prod: xsec = float(prod.split(',')[-1])
    if sample_stripped not in samples_dict.keys():
        samples_dict[sample_stripped] = {'dir' : [sample], 'xsec' : xsec,  'subsel' : {'none' : ''} }
        if 'WJets' in sample_stripped:
            samples_dict[sample_stripped]['subsel']['WToMuNu']  = ' && genVtype == 14'
            samples_dict[sample_stripped]['subsel']['WToETauNu'] = ' && (genVtype == 12 || genVtype == 16)'        
    else:
        samples_dict[sample_stripped]['dir'].append(sample)

outputFiles = []
for sample_key, sample in samples_dict.iteritems():
    dataType = 'MC' if 'Run' not in sample_key else 'DATA'

    print 'Analysing sample', bcolors.OKBLUE, sample_key, bcolors.ENDC
    print '\tdirectories =', bcolors.OKBLUE, sample['dir'] , bcolors.ENDC
    print '\txsec = '+'{:0.3f}'.format(sample['xsec'])+' pb', \
        ', (data type is', bcolors.OKBLUE, dataType, bcolors.ENDC, ')'
    print '\tsubselections =', bcolors.OKBLUE, sample['subsel'] , bcolors.ENDC

    inputFile = ROOT.std.vector("std::string")()
    for x in sample['dir']: inputFile.push_back(inputDir+x+"/tree*.root")
    if rdf:
        p = RDFtree(outputDir=outDir, inputFile=inputFile  )
    
    # create branches
    for subsel_key, subsel in sample['subsel'].iteritems(): 
        outputFiles.append("%s%s" % (sample_key, ('_'+subsel_key if subsel_key!='none' else '')) )
        for sel_key, sel in myselections.iteritems():
            if len(sample['subsel'])>1 and subsel_key=='none': continue
            myvariables = filterVariables(variables, sel_key)
            print '\tBranching: subselection', bcolors.OKBLUE, subsel_key, bcolors.ENDC, 'with selection' , bcolors.OKBLUE, sel_key, bcolors.ENDC
            print '\tAdding variables for collections', bcolors.OKBLUE, myvariables.keys(), bcolors.ENDC
            if not rdf: continue
            outputFile = "%s%s_%s.root" % (sample_key, ('_'+subsel_key if subsel_key!='none' else ''), sel_key) 
            myselection = copy.deepcopy(sel)
            myselection[dataType]['cut'] += subsel if subsel_key!='none' else ''
            p.branch(nodeToStart='input',
                     nodeToEnd='controlPlots'+sel_key,
                     outputFile=outputFile,
                     modules = [controlPlots(selections=myselection, variables=myvariables, dataType=dataType, xsec=sample['xsec'], inputFile=inputFile)])
    if rdf:
        p.getOutput()

samples_merging = {
    'WToMuNu'  : [x for x in outputFiles if ('WJets' and 'WToMuNu') in x],
    'WToETauNu'  : [x for x in outputFiles if ('WJets' and 'WToETauNu') in x],
    'DYJets' : [x for x in outputFiles if 'DYJetsToLL' in x],
    'QCD' : [x for x in outputFiles if 'QCD_' in x],
    'Top' : [x for x in outputFiles if ('TTJets' in x or 'ST_' in x)],
    'Diboson' : [x for x in outputFiles if ('WW_' in x or 'WZ_' in x or 'ZZ_' in x)],
    'Data' : [x for x in outputFiles if 'Run' in x],
}

print 'Samples to be merged:'
print bcolors.OKBLUE, samples_merging, bcolors.ENDC

outputMergedFiles = []
for sel_key, sel in myselections.iteritems():
    for sample_merging_key, sample_merging in samples_merging.iteritems():
        if len(sample_merging)>0:
            outputMergedFiles.append( '%s_%s.root' % (sample_merging_key,sel_key))
            cmd = 'hadd -f %s/%s_%s.root' % (outDir,sample_merging_key,sel_key)
            for isample in sample_merging:
                cmd += ' %s/%s_%s.root' % (outDir,isample,sel_key)
            if hadd:
                print bcolors.OKGREEN, cmd, bcolors.ENDC
                os.system(cmd)

print 'Final samples:'
print bcolors.OKBLUE, outputMergedFiles, bcolors.ENDC

if plot:
    plt = plotter(outdir=outDir, folder=outDir, fileList=fileList, norm = 2.57)
    plt.plotStack()
















































