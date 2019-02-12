from header import *

class RDFtree:
    def __init__(self, outputDir, outputFile, inputFile, modules=[],treeName='Events'):

        self.outputDir = outputDir # output directory
        self.outputFile = outputFile
        self.inputFile = inputFile
        self.modules = modules
        self.treeName = treeName

        RDF = ROOT.ROOT.RDataFrame
        self.d = RDF(self.treeName, self.inputFile)
        self.entries = self.d.Count() #stores lazily the number of events

        self.objs = [] # objects to be received from modules

    def run(self):

        #start analysis
        self.start = time.time()

        # modify RDF according to modules
        for i, m in enumerate(self.modules): 

            print 'analysing module', i+1

            self.d = m.run(CastToRNode(self.d))
            tmp_th1 = m.getTH1()
            tmp_th2 = m.getTH2()
            tmp_th3 = m.getTH3()

            for obj in tmp_th1:
                print obj.GetName()
                self.objs.append(ROOT.RDF.RResultPtr('TH1D')(obj))

            for obj in tmp_th2:
                self.objs.append(ROOT.RDF.RResultPtr('TH2D')(obj))

            for obj in tmp_th3:
                self.objs.append(ROOT.RDF.RResultPtr('TH3D')(obj))

    def branch(self, mlist):

        self.start = time.time()

        self.d1 = self.d

        for m in mlist:

            self.d1 = m.run(CastToRNode(self.d1))
            tmp_th1 = m.getTH1()
            tmp_th2 = m.getTH2()
            tmp_th3 = m.getTH3()

            for obj in tmp_th1:
                self.objs.append(ROOT.RDF.RResultPtr('TH1D')(obj))

            for obj in tmp_th2:
                self.objs.append(ROOT.RDF.RResultPtr('TH2D')(obj))

            for obj in tmp_th3:
                self.objs.append(ROOT.RDF.RResultPtr('TH3D')(obj))


    def takeSnapshot(self):

        opts = ROOT.ROOT.RDF.RSnapshotOptions()
        opts.fLazy = True

        print time.time()-self.start, "before snapshot"
        out = self.d.Snapshot(self.treeName,self.outputFiles[i], "", opts)

        # dummy histogram to trigger snapshot

        h = self.d.Define("foo", "1").Histo1D("foo")    
        self.objs.append(ROOT.RDF.RResultPtr('TH1D')(h))
                    

    def getOutput(self, outputFile=''):

        if not  outputFile=='':
            self.outputFile = outputFile

        # now write all the outputs together

        print "writing output files in "+ self.outputDir
   
        if not os.path.exists(self.outputDir):
            os.system("mkdir -p " + self.outputDir)
   
        os.chdir(self.outputDir) 

        fout = ROOT.TFile(self.outputFile, "recreate")
        fout.cd()
        
        for obj in self.objs:

            obj.Write()
        
        os.chdir('..')
        self.objs = [] # re-initialise object list

        print self.entries.GetValue(), " events processed in ", time.time()-self.start, " s"

    def saveGraph(self):

        from graphviz import Source

        RDF = ROOT.ROOT.RDataFrame(1000)
        Source(ROOT.ROOT.RDF.SaveGraph(CastToRNode(self.d))).render()
