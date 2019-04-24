from header import *
import copy

class RDFtree:
    def __init__(self, outputDir, outputFile, inputFile,treeName='Events',syst = {}, pretend=False):

        self.outputDir = outputDir # output directory
        self.outputFile = outputFile
        self.inputFile = inputFile
        
        self.treeName = treeName

        RDF = ROOT.ROOT.RDataFrame
        self.d = RDF(self.treeName, self.inputFile)

        self.pretend = pretend
        if self.pretend:

            ROOT.ROOT.DisableImplicitMT()
            self.d=self.d.Range(10)

        self.entries = self.d.Count() #stores lazily the number of events
        
        self.modules = []

        self.objs = {} # objects to be received from modules
        
        self.node = {} # dictionary branchName - RDF
        self.node['input'] = self.d # assign input RDF to a branch called 'input'

        self.graph = {} # save the graph to write it in the end 
        self.syst = syst


        #start analysis
        self.start = time.time()
        
    def branch(self,nodeToStart, nodeToEnd, outputFile, modules=[]):

        self.branchDir = nodeToEnd
        self.objs[self.branchDir] = {}

        for syst_type, variations in self.syst.iteritems():

            for var in variations:

                mysyst = {syst_type: var}

                if len(var)==2: # check if this is an Up/Down variation
                    systDir = var[0].replace("Up", "")
                else: systDir = "nom"

                self.objs[self.branchDir][systDir] = []
               
                if nodeToStart in self.graph:
                    self.graph[nodeToStart].append(nodeToEnd)
                else: 
                    self.graph[nodeToStart]=[nodeToEnd]

                branchRDF = self.node[nodeToStart]

                lenght = len(self.modules)

                self.modules.extend(modules)

                # modify RDF according to modules
                for i, m in enumerate(self.modules[lenght:]): 

                    if hasattr( m, 'getSyst' ) and callable( m.getSyst ):
                        m.getSyst(mysyst) #get the syst dictionary to run the module doing the variations

                    branchRDF = m.run(CastToRNode(branchRDF))
                    tmp_th1 = m.getTH1()
                    tmp_th2 = m.getTH2()
                    tmp_th3 = m.getTH3()

                    for obj in tmp_th1:
                        self.objs[self.branchDir][systDir].append(ROOT.RDF.RResultPtr('TH1D')(obj))

                    for obj in tmp_th2:
                        self.objs[self.branchDir][systDir].append(ROOT.RDF.RResultPtr('TH2D')(obj))

                    for obj in tmp_th3:
                        self.objs[self.branchDir][systDir].append(ROOT.RDF.RResultPtr('TH3D')(obj))

                    m.reset()

                self.node[nodeToEnd] = branchRDF


    def takeSnapshot(self):

        opts = ROOT.ROOT.RDF.RSnapshotOptions()
        opts.fLazy = True

        print time.time()-self.start, "before snapshot"
        out = self.d.Snapshot(self.treeName,self.outputFile[i], "", opts)

        # dummy histogram to trigger snapshot

        h = self.d.Define("foo", "1").Histo1D("foo")    
        self.objs.append(ROOT.RDF.RResultPtr('TH1D')(h))
                    

    def getOutput(self):

        # now write all the outputs together

        print "Writing output files in "+ self.outputDir
   
        if not os.path.exists(self.outputDir):
            os.system("mkdir -p " + self.outputDir)
   
        os.chdir(self.outputDir) 

        fout = ROOT.TFile(self.outputFile, "recreate")
        fout.cd()
    
        for branchDir, systDic in self.objs.iteritems():

            fout.mkdir(branchDir)
            
            for syst, hList in systDic.iteritems():

                fout.mkdir(branchDir+'/'+syst)
            
                fout.cd(branchDir+'/'+syst)
                for h in hList:
                    print h.GetName()
                    h.Write()

        
        os.chdir('..')
        self.objs = {} # re-initialise object list

        print self.entries.GetValue(), "events processed in "+"{:0.1f}".format(time.time()-self.start), "s", "rate", self.entries.GetValue()/(time.time()-self.start)

    def saveGraph(self):

        from graphviz import Digraph

        dot = Digraph(name='my analysis', filename = 'graph.pdf')

        for node, nodelist in self.graph.iteritems():
            for n in nodelist:
                
                dot.node(node, n)


        print(dot.source)  

        #dot.render(view=True)  

