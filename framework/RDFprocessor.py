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

        # modyfy RDF according to modules
        for m in self.modules: 

            print type(self.d)
            #self.d = m.doSomething(CastToRNode(self.d))
            tmp_obj = m.getObjects()

            for obj in tmp_obj:
                self.objs.append(obj)

        self.histoFile.cd()
        for obj in self.objs:
            obj.Write()

        #if self.snapshot: out = self.d.Snapshot("Events",self.outputFiles)
        if self.snapshot: out = self.d.Snapshot("Events","foo.root", "")

        #produce some kind of job report
