import ROOT

class module1:
    def __init__(self):
        pass
        
        self.myObj = []
        
    def doSomething(self,d):

        self.d = d

        entries1 = self.d.Filter("GenPart_pt[GenPart_bareMuonIdx]>20").Count()
        
        print("%s entries passed all filters" %entries1.GetValue())

        return self.d

    def getObjects(self):

        return self.myObj    