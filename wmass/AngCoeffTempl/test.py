import os
import sys
import ROOT

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

sys.path.append('../../framework')

from RDFprocessor import *


ROOT.ROOT.EnableImplicitMT(20)
p = RDFprocessor(outputFile = "test.root", inputFiles ='/scratch/emanca/WMass/NanoDevelopment/CMSSW_10_2_6/src/PhysicsTools/NanoAODTools/scripts/nanoPost.root', modules=[ROOT.AngCoeff()], histoFile = 'histo.root', snapshot=True)
time = p.run()

print "elapsed world time", time, "s"

"""
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