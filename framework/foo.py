import ROOT 

class parser:
    
    def __init__(self, file):

    	self.file = file
	
        self.f = open(self.file)                      

    def parse(self):

        list = [x.strip() for x in self.f.readlines()] 
        branchList = ROOT.vector('string')()

        for l in list:
        	branchList.push_back(l)

        return branchList 

