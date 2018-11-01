import ROOT
import os
import time

from module import *
from module2 import *

class RDFprocessor:
    def __init__(self, outputFiles, inputFiles, cores, modules=[]):

        self.outputFiles = outputFiles
        self.inputFiles = inputFiles
        self.modules = modules
        self.cores = cores

        ROOT.ROOT.EnableImplicitMT(self.cores)

        RDF = ROOT.ROOT.RDataFrame
        self.d = RDF("Events", inputFiles)

        print "successful constructor", "len modules:", len(self.modules)
    def run(self):

        # modyfy RDF according to modules
        for m in self.modules: 

            m.beginJob(self.d)
            m.dosomething()

        # this line crashes
        #out = self.d.Snapshot("Events", self.outputFiles)

        #produce some kind of job report
