from RDFprocessor import *
from module1 import *
from module2 import *
ROOT.gSystem.Load('module3_cpp')


p = RDFprocessor(outputFiles = "test.root", inputFiles ='/scratch/emanca/WMass/NanoDevelopment/CMSSW_10_2_6/src/PhysicsTools//NanoAOD/test/test80X_NANO.root', modules=[ROOT.leptonSelection()], cores=20, histoFile = 'histo.root', snapshot = True)
p.run()