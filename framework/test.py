from RDFprocessor import *

print "i am here!"

p = RDFprocessor(outputFiles = 'test.root', inputFiles ='/scratch/emanca/WMass/NanoDevelopment/CMSSW_10_2_6/src/PhysicsTools/NanoAODTools/python/postprocessing/wmass/test80X_NANO_Skim.root', modules=[module()], cores=20)
p.run()