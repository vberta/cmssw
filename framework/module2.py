import ROOT

class module2():
    def __init__(self):
        pass

    def beginJob(self, d):  
        
        self.d = d
        self.myObj = []
        
    def dosomething(self):

        d_new = self.d.Filter("Wrap_preFSR>0")

        self.myHisto = d_new.Histo1D("Wrap_preFSR")
        self.myHisto2 = d_new.Histo1D("Wrap_bare")
        
        self.myObj.append(self.myHisto)
        self.myObj.append(self.myHisto2)
        
        self.d = d_new

    def endJob(self):

        return (self.d,  self.myObj)
