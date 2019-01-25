from header import *
from importlib import import_module

class RDFtree:

    def __init__(self, inputFiles, outputDir, outputFiles, graphList=[]):

        self.inputFiles = inputFiles # list of input files
        self.outputFiles = outputFiles # list of output files - one for each path
        self.outputDir = outputDir # output directory
        self.graphList = graphList
        self.objList = [] # list of dictionaries containing objects to write


    def allNodesFrom(self, node, graph):
        # returns a list of all the possible paths from a given node

        paths = []
        if node not in graph:
            return [[node]]
        else: 
            res = []
            for child in graph[node]:
                res.extend(self.allNodesFrom(child, graph))
            for r in res:
                paths.append([node]+r)
        
            return paths 


    def run(self):

        #start analysis
        start = time.time()

        for j, graph in enumerate(self.graphList):
            
            self.paths = self.allNodesFrom('input',graph) # get a list of all the paths from root

            # this is the dictionary to be filled with the output objects

            objs = {} # key: filename and value: list of objects to write

            for i, path in enumerate(self.paths): # selects one of the paths

                # this is the starting RDF to be recreated at the beginning of each path
                    
                RDF = ROOT.ROOT.RDataFrame
                self.d = RDF("Events", self.inputFiles[j])

                print 'analysing path:', path

                for name in path: # modifies RDF using modules in a sequential way    

                    if not 'snapshot' in name:

                        module = import_module(name)

                        if 'ROOT' in name:
                            name = name.split(".")[1]
                        action = getattr(module, name)
                        run = action()
                    
                        self.d = run.run(CastToRNode(self.d))

                        # collect the outputs

                        tmp_th1 = run.getTH1()
                        tmp_th2 = run.getTH2()
                        tmp_th3 = run.getTH3()

                        objs[self.outputFiles[i]] = []

                        for obj in tmp_th1:
                            print obj
                            objs[self.outputFiles[i]].append(ROOT.RDF.RResultPtr('TH1D')(obj))

                        for obj in tmp_th2:
                            objs[self.outputFiles[i]].append(ROOT.RDF.RResultPtr('TH2D')(obj))

                        for obj in tmp_th3:
                            objs[self.outputFiles[i]].append(ROOT.RDF.RResultPtr('TH3D')(obj))

                        self.objList.append(objs)

                    else: # save a lazy snapshot    

                        opts = ROOT.ROOT.RDF.RSnapshotOptions()
                        opts.fLazy = True

                        print time.time()-start, "before snapshot"
                        out = self.d.Snapshot("Events",self.outputFiles[i], "", opts)

                        # dummy histogram to trigger snapshot

                        h = self.d.Histo1D("event")    
                        objs[self.outputFiles[i]].append(ROOT.RDF.RResultPtr('TH1D')(h))


        # now write all the outputs together

        print "writing output files in "+ self.outputDir
   
        if not os.path.exists(self.outputDir):
            os.system("mkdir -p " + self.outputDir)

        os.chdir(self.outputDir) 

        print time.time()-start, "before writing objects"
        for obj in self.objList:

            for outfile, hList in obj.iteritems():

                fout = ROOT.TFile(outfile, "recreate")
                fout.cd()
                for h in hList:
                    print h.GetName()
                    h.Write()
        
        
        print time.time()-start, "histogram written"
