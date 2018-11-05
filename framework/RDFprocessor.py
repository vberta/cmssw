import ROOT
import os
import time

class RDFprocessor:
    def __init__(self, outputFiles, inputFiles, cores, histoFile, modules=[], snapshot = False):

        self.outputFiles = outputFiles
        self.inputFiles = inputFiles
        self.cores = cores
        self.modules = modules
        self.histoFile = ROOT.TFile(histoFile, "recreate")
        self.snapshot = snapshot

        ROOT.ROOT.EnableImplicitMT(self.cores)

        RDF = ROOT.ROOT.RDataFrame
        self.d = RDF("Events", inputFiles)
        self.objs = [] # objects to be received from modules

    def run(self):

        # modyfy RDF according to modules
        for m in self.modules: 

            m.beginJob(self.d)
            m.dosomething()
            (self.d, tmp_obj) = m.endJob()

            for obj in tmp_obj:
                self.objs.append(obj)

        self.histoFile.cd()
        for obj in self.objs:
            obj.Write()

        if self.snapshot: out = self.d.Snapshot("Events",self.outputFiles)

        #produce some kind of job report
