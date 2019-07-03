import os
import copy
import math
import argparse
import sys
sys.path.append('../../framework')
import ROOT
from RDFtreeV2 import RDFtree

from bkg_histos import *
from plotter import *

from sampleParser import *
from bkg_selections import *
from bkg_variables import *
from systematics import *
from bkg_fakerateAnalyzer import *

ROOT.gROOT.Reset()
ROOT.gROOT.SetBatch(True);

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
parser.add_argument('-fakerate', '--fakerate',type=int, default=False, help="")
parser.add_argument('-rdf', '--rdf',type=int, default=True, help="")
parser.add_argument('-pretend', '--pretend',type=bool, default=False, help="")
args = parser.parse_args()
tag = args.tag
dataYear = args.dataYear
hadd = args.hadd
plot = args.plot
fakerate = args.fakerate
rdf = args.rdf
pretend = args.pretend
print "tag =", bcolors.OKGREEN, tag, bcolors.ENDC, \
    ", dataYear =", bcolors.OKGREEN, str(dataYear), bcolors.ENDC


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

def RDFprocess(outDir, inputFile, selections, sample):

    outDir = outDir
    inputFile = inputFile
    myselections = selections
    sample = sample

    outputFile = "%s.root" % (sample_key) 

    p = RDFtree(outputDir=outDir, outputFile = outputFile,inputFile=inputFile,pretend = pretend, syst = systematics)

      # create branches
    for subsel_key, subsel in sample['subsel'].iteritems(): 
        outputFiles.append("%s" % (sample_key))
        for sel_key, sel in myselections.iteritems():
            if len(sample['subsel'])>1 and subsel_key=='none': continue
            myvariables = filterVariables(bkg_variables, sel_key)
            print '\tBranching: subselection', bcolors.OKBLUE, subsel_key, bcolors.ENDC, 'with selection' , bcolors.OKBLUE, sel_key, bcolors.ENDC
            print '\tAdding variables for collections', bcolors.OKBLUE, myvariables.keys(), bcolors.ENDC
           
            myselection = copy.deepcopy(sel)
            myselection[dataType]['cut'] += subsel if subsel_key!='none' else ''
            subsel_str= subsel if subsel_key!='none' else ''
            p.branch(nodeToStart='input',
                        nodeToEnd='controlPlots'+sel_key,
                        outputFile=outputFile,
                        modules = [bkg_histos(selections=myselection, variables=myvariables, dataType=dataType, xsec=sample['xsec'], inputFile=inputFile,ptBins=ptBinning, etaBins=etaBinning)])
    
    p.getOutput()


myselections = {}

for cut in ['bkg_Signal', 'bkg_Sideband']:
    myselections['%sPlus' % cut]  = copy.deepcopy(bkg_selections['%s' % cut])
    myselections['%sMinus' % cut] = copy.deepcopy(bkg_selections['%s' % cut])
    for d in ['MC','DATA']:
        myselections['%sPlus' % cut][d]['cut']    += ' && Muon_charge[Idx_mu1]>0'
        myselections['%sMinus' % cut][d]['cut']   += ' && Muon_charge[Idx_mu1]<0'


# inputDir = ('/scratch/bertacch/NanoAOD%s-%s/' % (str(dataYear), tag))
inputDir = ('/scratch/sroychow/NanoAOD%s-%s/' % (str(dataYear), tag))


outDir =  'NanoAOD%s-%s/' % (str(dataYear), tag) 
if not os.path.isdir(outDir): os.system('mkdir '+outDir) 

outputFiles = []

# parser = sampleParser(restrict= ['QCD_Pt-300to470_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8'],tag=tag, inputDir=inputDir, production_file ='/scratch/sroychow/mcsamples_'+str(dataYear)+'-'+str(tag)+'.txt')
parser = sampleParser(tag=tag, inputDir=inputDir, production_file ='/scratch/sroychow/mcsamples_'+str(dataYear)+'-'+str(tag)+'.txt')
# parser = sampleParser(restrict= ['WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8'], tag=tag, inputDir=inputDir, production_file ='/scratch/sroychow/mcsamples_'+str(dataYear)+'-'+str(tag)+'.txt')
#WJ+QCD
# parser = sampleParser(restrict= ['WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8','QCD_Pt-1000toInf_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8','QCD_Pt-1000toInf_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8_ext1','QCD_Pt-120to170_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8','QCD_Pt-15to20_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8','QCD_Pt-170to300_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8','QCD_Pt-170to300_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8_ext1','QCD_Pt-20to30_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8','QCD_Pt-300to470_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8','QCD_Pt-300to470_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8_ext1','QCD_Pt-300to470_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8_ext2','QCD_Pt-30to50_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8','QCD_Pt-470to600_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8','QCD_Pt-470to600_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8_ext1','QCD_Pt-470to600_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8_ext2','QCD_Pt-50to80_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8','QCD_Pt-600to800_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8','QCD_Pt-600to800_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8_ext1','QCD_Pt-800to1000_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8','QCD_Pt-800to1000_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8_ext1','QCD_Pt-800to1000_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8_ext2','QCD_Pt-80to120_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8', 'QCD_Pt-80to120_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8_ext1'])

#data only
# parser = sampleParser(restrict= ['SingleMuon_Run2016B_ver2', 'SingleMuon_Run2016C', 'SingleMuon_Run2016D', 'SingleMuon_Run2016E', 'SingleMuon_Run2016F', 'SingleMuon_Run2016G', 'SingleMuon_Run2016H'])

#data example
# parser = sampleParser(restrict= ['SingleMuon_Run2016B_ver2'])

# WJ+QCD+EWK+DY (w/o  data)
# parser = sampleParser(restrict= ['WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8','DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8', 'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_ext1','DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_ext2','ST_s-channel_4f_leptonDecays_13TeV-amcatnlo-pythia8_TuneCUETP8M1', 'ST_t-channel_antitop_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1', 'ST_t-channel_top_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1', 'ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1_ext1', 'ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1_ext1', 'TTJets_DiLept_TuneCUETP8M1_13TeV-madgraphMLM-pythia8', 'TTJets_DiLept_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_ext1', 'TTJets_SingleLeptFromTbar_TuneCUETP8M1_13TeV-madgraphMLM-pythia8', 'TTJets_SingleLeptFromTbar_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_ext1', 'TTJets_SingleLeptFromT_TuneCUETP8M1_13TeV-madgraphMLM-pythia8', 'TTJets_SingleLeptFromT_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_ext1', 'WW_TuneCUETP8M1_13TeV-pythia8', 'WW_TuneCUETP8M1_13TeV-pythia8_ext1', 'WZ_TuneCUETP8M1_13TeV-pythia8', 'ZZ_TuneCUETP8M1_13TeV-pythia8','QCD_Pt-1000toInf_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8','QCD_Pt-1000toInf_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8_ext1','QCD_Pt-120to170_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8','QCD_Pt-15to20_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8','QCD_Pt-170to300_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8','QCD_Pt-170to300_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8_ext1','QCD_Pt-20to30_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8','QCD_Pt-300to470_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8','QCD_Pt-300to470_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8_ext1','QCD_Pt-300to470_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8_ext2','QCD_Pt-30to50_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8','QCD_Pt-470to600_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8','QCD_Pt-470to600_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8_ext1','QCD_Pt-470to600_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8_ext2','QCD_Pt-50to80_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8','QCD_Pt-600to800_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8','QCD_Pt-600to800_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8_ext1','QCD_Pt-800to1000_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8','QCD_Pt-800to1000_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8_ext1','QCD_Pt-800to1000_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8_ext2','QCD_Pt-80to120_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8', 'QCD_Pt-80to120_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8_ext1'])


samples_dict = parser.getSampleDict()

for sample_key, sample in samples_dict.iteritems():
    for subsel_key, subsel in sample['subsel'].iteritems(): 
        outputFiles.append("%s" % (sample_key))

if rdf:

    from multiprocessing import Process

    procs = []

    for sample_key, sample in samples_dict.iteritems():

        print 'doing multiprocessing'

        if not sample['multiprocessing']: continue
    
        dataType = 'MC' if 'Run' not in sample_key else 'DATA'

        print 'Analysing sample', bcolors.OKBLUE, sample_key, bcolors.ENDC
        print '\tdirectories =', bcolors.OKBLUE, sample['dir'] , bcolors.ENDC
        print '\txsec = '+'{:0.3f}'.format(sample['xsec'])+' pb', \
        ', (data type is', bcolors.OKBLUE, dataType, bcolors.ENDC, ')'
        print '\tsubselections =', bcolors.OKBLUE, sample['subsel'] , bcolors.ENDC

        inputFile = ROOT.std.vector("std::string")()
        for x in sample['dir']: inputFile.push_back(inputDir+x+"/tree*.root")
            
        p = Process(target=RDFprocess, args=(outDir, inputFile, myselections,sample))

        p.start()
        
        procs.append(p)

    for p in procs:  
        p.join()
    
    
    ROOT.ROOT.EnableImplicitMT(30)#24

    for sample_key, sample in samples_dict.iteritems():

        print 'doing multithreading'

        if sample['multiprocessing']: continue

        dataType = 'MC' if 'Run' not in sample_key else 'DATA'

        print 'Analysing sample', bcolors.OKBLUE, sample_key, bcolors.ENDC
        print '\tdirectories =', bcolors.OKBLUE, sample['dir'] , bcolors.ENDC
        print '\txsec = '+'{:0.3f}'.format(sample['xsec'])+' pb', \
        ', (data type is', bcolors.OKBLUE, dataType, bcolors.ENDC, ')'
        print '\tsubselections =', bcolors.OKBLUE, sample['subsel'] , bcolors.ENDC

        inputFile = ROOT.std.vector("std::string")()
        for x in sample['dir']: inputFile.push_back(inputDir+x+"/tree*.root")
            
        RDFprocess(outDir, inputFile, myselections, sample)
        


samples_merging = {
    'WToMuNu'  : [x for x in outputFiles if ('WJets' and 'WToMuNu') in x],###
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
for sample_merging_key, sample_merging_value in samples_merging.iteritems():
        if len(sample_merging_value)>0:
            outputMergedFiles.append( '%s.root' % (sample_merging_key))
            cmd = 'hadd -f -k %s/%s.root' % (outDir,sample_merging_key)
            for isample in sample_merging_value:
                cmd += ' %s/%s.root' % (outDir,isample)
            if hadd:
                print bcolors.OKGREEN, cmd, bcolors.ENDC
                os.system(cmd)

print 'Final samples:'
print bcolors.OKBLUE, outputMergedFiles, bcolors.ENDC

if fakerate :
    print "----> FakeRate analyzer:"
    selected = [s for s in outputMergedFiles]
    if not rdf : #if rdf=false --->expected already created the rootfiles with proper histos (done previously by rdf)
        skipHisto = True
    if not os.path.isdir(outDir+'/bkg'): os.system('mkdir '+outDir+'/bkg') 
    if not os.path.isdir(outDir+'/bkg/bkg_plot'): os.system('mkdir '+outDir+'/bkg/bkg_plot')
    # fake = fakerateAnalyzer(outdir=outDir+'/bkg', folder=outDir, fileList=selected, norm = 35.922, skipHisto = skipHisto)
    fake = bkg_fakerateAnalyzer(outdir=outDir+'/bkg', folder=outDir,norm = 35.922, fitOnTemplate=True, ptBinning=ptBinning, etaBinning=etaBinning, onData=True)#, tightCut = 5, varFake='pfRelIso04_all_corrected_pt_corrected_MET_nom_mt')
    fake.integrated_preliminary()
    fake.differential_preliminary(fakerate=True)
    tightCutList = [0.02, 0.05, 0.10, 0.15, 0.2, 0.3, 0.5]
    looseCutList = [10,20,30,35,40,45,50,60,70,80]
    print "starting variation"
    # for lcut in looseCutList :
    #         for tcut in tightCutList :
    #             print "---variation (l, t)",lcut, tcut
    #             fake_i = bkg_fakerateAnalyzer(outdir=outDir+'/bkg', folder=outDir,norm = 35.922, fitOnTemplate=False, ptBinning=ptBinning, etaBinning=etaBinning, onData=True, tightCut = tcut, looseCut=lcut, nameSuff="_"+str(lcut)+"_"+str(tcut))
    #             fake_i.differential_preliminary(fakerate=True)
    print "plotting"    
    fake.fakerate_plots(variations=False,tightCutList=tightCutList,looseCutList=looseCutList )


if (plot and 0):

    for sel_key, sel in myselections.iteritems():

        print sel_key
        selected = [s for s in outputMergedFiles]

        plt = plotter(outdir=outDir+'/'+sel_key, folder=outDir, tag = sel_key, syst=systematics , fileList=selected, norm = 35.922)
        plt.plotStack()


