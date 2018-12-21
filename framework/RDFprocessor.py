from header import *

class RDFprocessor:
    def __init__(self, outputFile, inputFiles, histoFile, keepVars='', modules=[], snapshot = False):

        self.outputFile = outputFile
        self.inputFiles = inputFiles
        self.modules = modules
        self.histoFile = ROOT.TFile(histoFile, "recreate")
        self.snapshot = snapshot
        self.keepVars = keepVars

        RDF = ROOT.ROOT.RDataFrame
        self.d = RDF("Events", inputFiles)
        self.entries = self.d.Count() 

        self.objs = [] # objects to be received from modules

    def run(self):

        #start analysis
        start = time.time()

        # modyfy RDF according to modules
        for i, m in enumerate(self.modules): 

            print 'analysing module', i+1

            self.d = m.doSomething(CastToRNode(self.d))
            tmp_th1 = m.getTH1()
            tmp_th2 = m.getTH2()

            for obj in tmp_th1:
                self.objs.append(ROOT.RDF.RResultPtr('TH1D')(obj))

            for obj in tmp_th2:
                self.objs.append(ROOT.RDF.RResultPtr('TH2D')(obj))

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

            print self.keepVars
            if not self.keepVars == '':
                print "qui"
                Parser = parser(self.keepVars)
                self.d.Snapshot("Events", self.outputFile, Parser.parse())
            else:
                print "i'm snapshotting!"
                self.d.Snapshot("Events", self.outputFile)
                
            print time.time()-start, "events snapshot"
   
        self.histoFile.cd()
        for obj in self.objs:
            print type(obj), obj
            obj.Write()
        
        
        print time.time()-start, "histogram writing"
        print self.entries.GetValue(), " events processed in ", time.time()-start, " s"

        return time.time()-start
