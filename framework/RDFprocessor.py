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
    def __init__(self, outputFile, inputFiles, histoFile, modules=[], snapshot = False):

        self.outputFile = outputFile
        self.inputFiles = inputFiles
        self.modules = modules
        self.histoFile = ROOT.TFile(histoFile, "recreate")
        self.snapshot = snapshot

        RDF = ROOT.ROOT.RDataFrame
        self.d = RDF("Events", inputFiles)
        self.entries = self.d.Count() 

        self.objs = [] # objects to be received from modules

    def run(self):

        #start analysis
        start = time.time()

        # modyfy RDF according to modules
        for m in self.modules: 

            self.d = m.doSomething(CastToRNode(self.d))
            tmp_th1 = m.getTH1()
            tmp_th2 = m.getTH2()

            for obj in tmp_th1:
                self.objs.append(obj)

            for obj in tmp_th2:
                self.objs.append(obj)

        if self.snapshot: 

            """ comment until we understand Snapshot bug
            ROOT.ROOT.RDataFrame("LuminosityBlocks", self.inputFiles).Snapshot("LuminosityBlocks",self.outputFile, "")
            print time.time()-t0, "first snapshot"
            
            opts = ROOT.ROOT.RDF.RSnapshotOptions()
            opts.fMode = "UPDATE"

            ROOT.ROOT.RDataFrame("Runs", self.inputFiles).Snapshot("Runs", self.outputFile, "", opts)
            print time.time()-start, "second snapshot"
            """
            
            # edm::Stuff cannot be written via Snapshot
            #ROOT.ROOT.RDataFrame("MetaData", self.inputFiles).Snapshot("MetaData",self.outputFile, "", opts)
            #print time.time()-t0, "third snapshot"
            
            #ROOT.ROOT.RDataFrame("ParameterSets", self.inputFiles).Snapshot("ParameterSets", self.outputFile, "", opts)
            #print time.time()-t0, "fourth loop"

            self.d.Snapshot("Events", self.outputFile)
            print time.time()-start, "events snapshot"
   
        self.histoFile.cd()
        for obj in self.objs:
            obj.Write()
        
        
        print time.time()-start, "histogram writing"
        print self.entries.GetValue(), " events processed in ", time.time()-start, " s"

        return time.time()-start
