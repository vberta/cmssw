import os
import sys
import ROOT
"""
os.system("g++ -fPIC -Wall -O3 ../../framework/module.cpp AngCoeff.cpp $(root-config --libs --cflags) -shared -o AngCoeff.so")
os.system("g++ -fPIC -Wall -O3 ../../framework/module.cpp TemplateBuilder.cpp $(root-config --libs --cflags) -shared -o TemplateBuilder.so")
#os.system("g++ -fPIC -Wall -O3 ../../framework/module.cpp GetWeights.cpp $(root-config --libs --cflags) -shared -o GetWeights.so")

ROOT.gInterpreter.Declare('#include "../../framework/module.h"')
ROOT.gInterpreter.Declare('#include "AngCoeff.h"')
ROOT.gInterpreter.Declare('#include "TemplateBuilder.h"')
#ROOT.gInterpreter.Declare('#include "GetWeights.h"')


ROOT.gSystem.Load('AngCoeff.so')
ROOT.gSystem.Load('TemplateBuilder.so')
#ROOT.gSystem.Load('GetWeights.so')

#from TemplateBuilderPy import *
from TemplateProj import *

#sys.path.append('../../framework')

from RDFProcessor import RDFProcessor


ROOT.ROOT.EnableImplicitMT(20)
#p = RDFprocessor(outputFile = "test.root", inputFiles ='/scratch/emanca/WMass/NanoDevelopment/CMSSW_10_2_6/src/PhysicsTools/NanoAODTools/scripts/nanoPost.root', modules=[ROOT.AngCoeff()], histoFile = 'histo.root', snapshot=True)
#time = p.run()

#print "elapsed world time", time, "s"


cores =[1, 4, 8, 12, 20, 40, 64]

time = []


for c in cores:

	print "performing test with {c} cores".format(c=c)
	ROOT.ROOT.DisableImplicitMT()
	ROOT.ROOT.EnableImplicitMT(c)
	p = RDFprocessor(outputFile = "test.root", inputFiles ='/scratch/emanca/WMass/NanoDevelopment/CMSSW_10_2_6/src/PhysicsTools/NanoAODTools/scripts/inputTree.root', modules=[ROOT.AngCoeff()], histoFile = 'histo.root', snapshot=False)
	time.append(7798042./p.run())

	print "elapsed world time", time, "s"

perf = ROOT.TGraph()

for i, c in enumerate(cores):
	perf.SetPoint(i, c, time[i])

canv = ROOT.TCanvas()
canv.cd()
perf.Draw()
canv.SaveAs('perf.pdf')
"""
# append location of the framework and of the modules to use

sys.path.append('../RDFprocessor/framework')
sys.path.append('../RDFprocessor/wmass/signalTemplates')


os.system("g++ -fPIC -Wall -O3 ../RDFprocessor/framework/module.cpp ../RDFprocessor/wmass/signalTemplates/AngCoeff.cpp $(root-config --libs --cflags) -shared -o ../RDFprocessor/wmass/signalTemplates/AngCoeff.so")
ROOT.gInterpreter.Declare('#include "../RDFprocessor/framework/module.h"')
ROOT.gInterpreter.Declare('#include "../RDFprocessor/wmass/signalTemplates/AngCoeff.h"')
ROOT.gSystem.Load('../RDFprocessor/wmass/signalTemplates/AngCoeff.so')

os.system("g++ -fPIC -Wall -O3 ../RDFprocessor/framework/module.cpp ../RDFprocessor/wmass/signalTemplates/GetWeights.cpp $(root-config --libs --cflags) -shared -o ../RDFprocessor/wmass/signalTemplates/GetWeights.so")
ROOT.gInterpreter.Declare('#include "../RDFprocessor/framework/module.h"')
ROOT.gInterpreter.Declare('#include "../RDFprocessor/wmass/signalTemplates/GetWeights.h"')
ROOT.gSystem.Load('../RDFprocessor/wmass/signalTemplates/GetWeights.so')

os.system("g++ -fPIC -Wall -O3 ../RDFprocessor/framework/module.cpp ../RDFprocessor/wmass/signalTemplates/TemplateBuilder.cpp $(root-config --libs --cflags) -shared -o ../RDFprocessor/wmass/signalTemplates/TemplateBuilder.so")
ROOT.gInterpreter.Declare('#include "../RDFprocessor/framework/module.h"')
ROOT.gInterpreter.Declare('#include "../RDFprocessor/wmass/signalTemplates/TemplateBuilder.h"')
ROOT.gSystem.Load('../RDFprocessor/wmass/signalTemplates/TemplateBuilder.so')

from RDFtree import RDFtree

# declare a dictionary containing your analysis

mygraph = {}

mygraph['input'] = ['defineHarmonics']
mygraph['defineHarmonics'] = ['filter,GenPart_pdgId[GenPart_preFSRMuonIdx]>0', 'filter,GenPart_pdgId[GenPart_preFSRMuonIdx]<0']
mygraph['filter,GenPart_pdgId[GenPart_preFSRMuonIdx]>0'] = ['ROOT.AngCoeff,WMinus']
mygraph['filter,GenPart_pdgId[GenPart_preFSRMuonIdx]<0'] = ['ROOT.AngCoeff,WPlus']
mygraph['ROOT.AngCoeff,WPlus'] = ['getAngularCoefficients,PLOTS/histosWPlus_1.root']
mygraph['getAngularCoefficients,PLOTS/histosWPlus_1.root'] = ['ROOT.GetWeights,PLOTS/histosWPlus_2.root']
mygraph['ROOT.GetWeights,PLOTS/histosWPlus_2.root'] = ['ROOT.TemplateBuilder, WPlus']
mygraph['ROOT.TemplateBuilder, WPlus'] = ['TemplateProj, PLOTS/histosWPlus_3.root']
mygraph['ROOT.AngCoeff,WMinus'] = ['getAngularCoefficients,PLOTS/histosWMinus_1.root']
mygraph['getAngularCoefficients,PLOTS/histosWMinus_1.root'] = ['ROOT.GetWeights,PLOTS/histosWMinus_2.root']
mygraph['ROOT.GetWeights,PLOTS/histosWMinus_2.root'] = ['ROOT.TemplateBuilder, WMinus']
mygraph['ROOT.TemplateBuilder, WMinus'] = ['TemplateProj, PLOTS/histosWMinus_3.root']


ROOT.ROOT.EnableImplicitMT(20)

p = RDFtree(inputFiles=["/scratch/emanca/WMass/NanoDevelopment/CMSSW_10_2_6/src/PhysicsTools/NanoAODTools/scripts/nanoPost.root"], outputDir = "PLOTS", outputFiles = ["histosWMinus", "histosWPlus"], graphList = [mygraph])
p.run()
