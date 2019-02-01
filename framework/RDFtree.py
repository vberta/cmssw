from header import *
from importlib import import_module

class RDFtree:

    def __init__(self, inputFiles, outputDir, outputFiles, graphList=[]):

        self.inputFiles = inputFiles # list of input files
        self.outputFiles = outputFiles # list of output files - one for each path
        self.outputDir = outputDir # output directory
        self.graphList = graphList
        self.objList = [] # list of dictionaries containing objects to write
        self.rdfOut = []
        self.nodesToRestart = []
        self.start = time.time()


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

    def getOutput(self):

        # now write all the outputs together

        print "writing output files in "+ self.outputDir
   
        if not os.path.exists(self.outputDir):
            os.system("mkdir -p " + self.outputDir)

        cwd = os.getcwd()    
        os.chdir(self.outputDir) 

        print time.time()-self.start, "before writing objects"
        
        for obj in self.objList:

            for outfile, hList in obj.iteritems():

                fout = ROOT.TFile(outfile+'_{f}'.format(f=self.nIter)+'.root', "recreate")
                fout.cd()
                for h in hList:
                    h.Write()

        os.chdir('..')
        self.objList = [] # re-initialise object list            


    def run(self):


        for j, graph in enumerate(self.graphList):
            
            self.paths = self.allNodesFrom('input',graph) # get a list of all the paths from root

            # this is the dictionary to be filled with the output objects

            objs = {} # key: filename and value: list of objects to write

            self.nIter = 0

            for k in range(len(self.paths)):
                aux = ROOT.ROOT.RDataFrame
                self.rdfOut.append(aux)
                self.nodesToRestart.append(0)

            stop = True 

            while stop:

                check = 0

                for i, path in enumerate(self.paths): # selects one of the paths
 

                    # this is the starting RDF to be recreated at the beginning of each path
                    
                    RDF = ROOT.ROOT.RDataFrame
                    self.d = RDF("Events", self.inputFiles[j])

                    print 'analysing path:', path
                    print self.nIter, 'iteration number:'

                    if self.nIter == 0: #first iteration
                        subpath = path

                    else: #n iteration
                        subpath = path[self.nodesToRestart[i]:]

                    #if subpath is empty it doesn't loop
                    print subpath, 'subpath' 

                    for idx, name in enumerate(subpath): # modifies RDF using modules in a sequential way

                        print 'analysing module', name

                        if not 'snapshot' in name:

                            string = ''

                            if ',' in name:
                                name,string = name.split(",")

                            module = import_module(name)

                            if 'ROOT' in name:
                                name = name.split(".")[1]

                            action = getattr(module, name)
                            if string == '': run = action()
                            else: run = action(string) #call a constructor with a string

                            if self.nIter == 0:
                        
                                self.d = run.run(CastToRNode(self.d))

                            else: self.d = run.run(CastToRNode(self.rdfOut[i]))

                            # collect the outputs

                            tmp_th1 = run.getTH1()
                            tmp_th2 = run.getTH2()
                            tmp_th3 = run.getTH3()

                            objs[self.outputFiles[i]] = []

                            for obj in tmp_th1:
                                if isinstance(obj, ROOT.TH1D):  
                                   
                                    objs[self.outputFiles[i]].append(ROOT.TH1D(obj)) 
                                else:
                                    objs[self.outputFiles[i]].append(ROOT.RDF.RResultPtr('TH1D')(obj)) 

                            for obj in tmp_th2:
                                if isinstance(obj, ROOT.TH2D):  
                                   
                                    objs[self.outputFiles[i]].append(ROOT.TH2D(obj)) 
                                else:
                                    objs[self.outputFiles[i]].append(ROOT.RDF.RResultPtr('TH2D')(obj))
                                
                                     
                            for obj in tmp_th3:
                                if isinstance(obj, ROOT.TH3D):  
                                   
                                    objs[self.outputFiles[i]].append(ROOT.TH2D(obj)) 
                                else:
                                    objs[self.outputFiles[i]].append(ROOT.RDF.RResultPtr('TH3D')(obj))

                            self.objList.append(objs)

                            triggerLoop = run.triggerLoop()

                            self.rdfOut[i]=self.d

                            if triggerLoop == True:
                                self.nodesToRestart[i]=self.nodesToRestart[i]+idx+1 # restart from that module
                                print self.nodesToRestart[i], 'index for path', i, 'idx', idx
                                
                                check = check -1
                                break #exit from path loop
 

                        else: # save a lazy snapshot    

                            opts = ROOT.ROOT.RDF.RSnapshotOptions()
                            opts.fLazy = True

                            print time.time()-self.start, "before snapshot"
                            out = self.d.Snapshot("Events",self.outputFiles[i], "", opts)

                            # dummy histogram to trigger snapshot

                            h = self.d.Histo1D("event")    
                            objs[self.outputFiles[i]].append(ROOT.RDF.RResultPtr('TH1D')(h))

                    check = check +1        

                self.nIter = self.nIter+1  
                print 'triggered loop!'
                self.getOutput() # this triggers loop
                if check == len(self.paths): stop = False #there is nothing to do so exit

                         

        print time.time()-self.start, "finish job"
