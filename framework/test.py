from RDFprocessor import *
from module1 import *
from module2 import *
ROOT.gSystem.Load('module3_cpp')


cores =[1, 4, 8, 12, 20, 40, 64]

time = []

"""
for c in cores:

	print "performing test with {c} cores".format(c=c)
	ROOT.ROOT.DisableImplicitMT()
	ROOT.ROOT.EnableImplicitMT(c)
	# local file	
	#p = RDFprocessor(outputFile = "test.root", inputFiles ='/scratch/emanca/WMass/NanoDevelopment/CMSSW_10_2_6/src/PhysicsTools/NanoAODTools/scripts/inputTree.root', modules=[ROOT.Test()], histoFile = 'histo.root', snapshot=False)
	# T2 files
	#p = RDFprocessor(outputFile = "test.root", inputFiles ='/gpfs/ddn/srm/cms/store/user/emanca/NanoPost/WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/NanoTestPost/181109_132641/0000/tree_*.root', modules=[ROOT.Test()], histoFile = 'histo.root', snapshot=False)
	p = RDFprocessor(outputFile = "test2.root", inputFiles ='test.root', modules=[module1()], histoFile = 'histo.root', snapshot=False)
	time.append(p.run())

import matplotlib.pyplot as plt

plot = plt.plot(cores, time, 'ro')	
plt.show()

"""

ROOT.ROOT.EnableImplicitMT(60)
#p = RDFprocessor(outputFile = "test.root", inputFiles ='/scratch/emanca/WMass/NanoDevelopment/CMSSW_10_2_6/src/PhysicsTools/NanoAODTools/scripts/inputTree.root', modules=[ROOT.AngCoeff()], histoFile = 'histo.root', snapshot=True)
p = RDFprocessor(outputFile = "test2.root", inputFiles ='test.root', modules=[module1()], histoFile = 'histo.root', snapshot=False)
time = p.run()
print "elapsed world time", time, "s"
