import ROOT

class module2():
    def __init__(self):
        pass
        
        self.myObj = []
        
    def doSomething(self,d):

        self.d = d

        d_new = self.d.Filter("Wrap_preFSR>0")

        self.myHisto = d_new.Histo1D("Wrap_preFSR")
        self.myHisto2 = d_new.Histo1D("Wrap_bare")
        
        self.myObj.append(self.myHisto)
        self.myObj.append(self.myHisto2)
        
        self.d = d_new

        return self.d

    def getObjects(self):

        return self.myObj
