import os
import sys
import ROOT

os.system("g++ -fPIC -Wall -O3 ../framework/module.cpp AngCoeff.cpp $(root-config --libs --cflags) -shared -o AngCoeff.so")

ROOT.gInterpreter.Declare('#include "../framework/module.h"')
ROOT.gInterpreter.Declare('#include "AngCoeff.h"')
ROOT.gSystem.Load('AngCoeff.so')

sys.path.append('../framework')

from RDFprocessor import *

ROOT.ROOT.EnableImplicitMT(8)
p = RDFprocessor(outputFile = "test.root", inputFiles ='/scratch/emanca/WMass/NanoDevelopment/CMSSW_10_2_6/src/PhysicsTools/NanoAODTools/scripts/inputTree.root', modules=[ROOT.AngCoeff()], histoFile = 'histo.root', snapshot=False)
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

import matplotlib.pyplot as plt

plot = plt.plot(cores, time, 'ro')	
plt.xlabel('number of cores')
plt.ylabel('rate (Hz)')
plt.show()
"""
