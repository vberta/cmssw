from RDFprocessor import *
from module1 import *
from module2 import *

p = RDFprocessor(outputFiles = "test.root", inputFiles ='/scratch/emanca/WMass/NanoDevelopment/CMSSW_10_2_6/src/PhysicsTools/NanoAODTools/python/postprocessing/wmass/test80X_NANO_Skim.root', modules=[module1(),module2()], cores=20, histoFile = 'histo.root')
p.run()