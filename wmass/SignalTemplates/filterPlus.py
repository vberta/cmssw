class filterPlus:
   
    def __init__(self):
        
        pass
        
        self.myTH1 = []
        self.myTH2 = []
        self.myTH3 = []

    def run(self,d):

        self.d = d.Filter("GenPart_pdgId[GenPart_preFSRMuonIdx]<0") # selects W+
        
        return self.d

    def getTH1(self):

        return self.myTH1

    def getTH2(self):

        return self.myTH2  

    def getTH3(self):

        return self.myTH3    


