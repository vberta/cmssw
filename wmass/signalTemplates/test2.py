import os
import sys
import ROOT

sys.path.append('../RDFprocessor/framework')
sys.path.append('../RDFprocessor/wmass/muonCalibration')

from RDFtreeV2 import RDFtree
from plotter import plotter

from basicPlots import *
from prepareSample import *
from prepareSampleAfter import *
'''
os.system("g++ -fPIC -Wall -O3 ../RDFprocessor/framework/module.cpp ../RDFprocessor/wmass/muonCalibration/reweightSample.cpp $(root-config --libs --cflags) -shared -o ../RDFprocessor/wmass/muonCalibration/reweightSample.so")
ROOT.gInterpreter.Declare('#include "../RDFprocessor/framework/module.h"')
ROOT.gInterpreter.Declare('#include "../RDFprocessor/wmass/muonCalibration/reweightSample.h"')
ROOT.gSystem.Load('../RDFprocessor/wmass/muonCalibration/reweightSample.so')

os.system("g++ -fPIC -Wall -O3 ../RDFprocessor/framework/module.cpp ../RDFprocessor/wmass/muonCalibration/applyCalibration.cpp /scratch/emanca/WMass/MuonCalibration/KaMuCaSLC7/CMSSW_8_0_20/src/KaMuCa/Calibration/src/KalmanMuonCalibrator.cc $(root-config --libs --cflags) -shared -o ../RDFprocessor/wmass/muonCalibration/applyCalibration.so")
ROOT.gInterpreter.Declare('#include "../RDFprocessor/framework/module.h"')
ROOT.gInterpreter.Declare('#include "../RDFprocessor/wmass/muonCalibration/applyCalibration.h"')
ROOT.gSystem.Load('../RDFprocessor/wmass/muonCalibration/applyCalibration.so')

ROOT.ROOT.EnableImplicitMT(64)

cut = 'pt1>22.0&&pt2>20.0&&abs(eta1)<1&&abs(eta2)<1&&mass>75&&mass<115'
inputFileMC ='/scratch/emanca/WMass/MuonCalibration/KaMuCaSLC7/CMSSW_8_0_20/src/KaMuCa/Derivation/run/Scale/muonTreeMCZ.root'

inputFileD ='/scratch/emanca/WMass/MuonCalibration/KaMuCaSLC7/CMSSW_8_0_20/src/KaMuCa/Derivation/run/Scale/muonTreeDataZ.root'

calibData = ROOT.string('DATA_80X_13TeV')
calibMC = ROOT.string('MC_80X_13TeV')

# data

pD = RDFtree(outputDir = 'TESTBarr', outputFile = "beforeCalibData.root", inputFile = inputFileD, \
	modules=[prepareSample(cut=cut, target=90.851,isMC=False),basicPlots(res='J')], treeName = 'tree')
pD.run()
pD.branch([ROOT.applyCalibration(calibData),basicPlots(res='Z', calib=True),prepareSampleAfter(cut,res='Z')],outputFile="afterCalibData.root")
pD.getOutput()


# mc reco

pMC = RDFtree(outputDir = 'TESTBarr', outputFile = "beforeCalibMC.root", inputFile = inputFileMC, \
	modules=[prepareSample(cut=cut, target=90.851,isMC=True),basicPlots(res='Z')], treeName = 'tree')
pMC.run()
pMC.branch([ROOT.applyCalibration(calibMC),basicPlots(res='Z', calib=True),prepareSampleAfter(cut,res='Z')],outputFile=("afterCalibMC.root"))
pMC.getOutput()

# gen to match data and MC

p = RDFtree(outputDir = 'TESTBarr', outputFile = "gen.root", inputFile = inputFileMC, \
	modules=[prepareSample(cut=cut, target=90.851, gen=True),basicPlots(res='Z', gen = True)],treeName = 'tree')
p.run()
p.getOutput()
p.branch([ROOT.reweightSample(),basicPlots(res='Z', gen = True, weight = True),prepareSampleAfter(cut,res='Z', gen = True, weight = True)],outputFile = "genAfterRew.root")
p.branch([basicPlots(res='Z', gen = True, weight = False),prepareSampleAfter(cut,res='Z', gen = True, weight = False)],outputFile = "genAfter.root")
p.getOutput()

plt = plotter(outdir= 'PlotsZDATAMC', folder = 'TESTBarr', fileList = ['beforeCalibData.root', 'beforeCalibMC.root'])
plt.plotDataMC()

plt = plotter(outdir= 'PlotsZDATAGENUNW', folder = 'TESTBarr', fileList = ['beforeCalibData.root', 'genAfter.root'])
plt.plotDataMC()

plt = plotter(outdir= 'PlotsZDATAGENW', folder = 'TESTBarr', fileList = ['beforeCalibData.root', 'genAfterRew.root'])
plt.plotDataMC()
'''

ROOT.gSystem.Load("/scratch/emanca/WMass/MuonCalibration/KaMuCaSLC7/CMSSW_8_0_20/src/KaMuCa/Derivation/bin/libChargedHiggs.so")

from fittingTools import *

runFits1D('TESTBarr/afterCalibData.root','TESTBarr/genAfterRew.root','resultsZDataBarr.root')
runFits1D('TESTBarr/afterCalibMC.root','TESTBarr/genAfter.root','resultsZMCBarr.root')






























