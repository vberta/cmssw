import ROOT

class module1:
    def __init__(self):
        pass

    def beginJob(self, d):  
        
        self.d = d
        self.myObj = []

    def dosomething(self):

        entries1 = self.d.Filter("GenPart_pt[GenPart_bareMuonIdx]>20").Count()
        
        print("%s entries passed all filters" %entries1.GetValue())

    def endJob(self):

        return (self.d,  self.myObj)    