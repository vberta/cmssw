import ROOT
import os
import time

# Begin code for casting

# this injection can be replaced by properly having this in a header
# included in the interpreter at framework startup
ROOT.gInterpreter.Declare('''
template <typename T>
class NodeCaster {
   public:
   static ROOT::RDF::RNode Cast(T rdf)
   {
      return ROOT::RDF::RNode(rdf);
   }
};
''')

def CastToRNode(node):
   return ROOT.NodeCaster(node.__cppname__).Cast(node)

# end code for casting

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

        #start analysis
        t0 = time.clock()

        # modyfy RDF according to modules
        for m in self.modules: 

            self.d = m.doSomething(CastToRNode(self.d))
            tmp_th1 = m.getTH1()
            tmp_th2 = m.getTH2()

            for obj in tmp_th1:
                self.objs.append(obj)

            for obj in tmp_th2:
                self.objs.append(obj)

        self.histoFile.cd()
        for obj in self.objs:
            #obj.Write()
            print "obj"

        if self.snapshot: 

            opts = ROOT.ROOT.RDF.RSnapshotOptions()
            opts.fLazy = True

            out = self.d.Snapshot("Events",self.outputFiles, "", opts)
            print time.clock()-t0, "first snapshot"
            """
            out = self.d.Snapshot("LuminosityBlocks",self.outputFiles, "", opts)
            print time.clock()-t0, "second snapshot"
            out = self.d.Snapshot("Runs",self.outputFiles, "", opts)
            print time.clock()-t0, "third snapshot"
            out = self.d.Snapshot("MetaData",self.outputFiles, "", opts)
            print time.clock()-t0, "forth snapshot"

            opts.fLazy = False
            out = self.d.Snapshot("ParameterSets",self.outputFiles, "", opts)
            print time.clock()-t0, "last snapshot"
            """
        
