import ROOT

class module1:
    def __init__(self):
        pass
        
        self.myTH1 = []
        self.myTH2 = []
        
    def doSomething(self,d):

        self.d = d.Filter("GenPart_pdgId[GenPart_bareMuonIdx]<0") #select W+

        coeff=['A0','A1','A2','A3','A4','A5', 'A6', 'A7']

        tmpCoeff = []
        tmpPt = []
        tmpY = []

        normPt = []
        normY = []

        for c in coeff: 
            self.myTH2.append(ROOT.TH2D("{c}".format(c=c), "{c}".format(c=c), 100, -5., 5., 100, 0, 100))

        for i, h in enumerate(self.myTH2):
            for j in range(1, h.GetNbinsY()): #bins in W pt

                upPt = h.GetYaxis().GetBinUpEdge(j)
                lowPt = h.GetYaxis().GetBinLowEdge(j)

                for k in range(1, h.GetNbinsX()): #bin in W y

                    upY = h.GetXaxis().GetBinUpEdge(k)
                    lowY = h.GetXaxis().GetBinLowEdge(k)

                    dFilt = self.d.Filter('std::cout<< "i am looping" << std::endl; return true;').Filter("Wrap_preFSR > {lowY} && Wrap_preFSR < {upY} && Wpt_preFSR > {lowPt} && Wpt_preFSR < {upPt}"
                        .format(lowY=lowY, upY=upY, lowPt=lowPt, upPt=upPt))

                    tmpY.append(dFilt.Sum("P{i}".format(i=i))) #one dimensional array
                
                tmpPt.append(tmpY) # bidimensional array
            
            tmpCoeff.append(tmpPt) # tridimensional array

        print "qui"
        for j in range(1, self.myTH2[0].GetNbinsY()): #bins in W pt
            
            for k in range(1, self.myTH2[0].GetNbinsX()): #bin in W y

                normY.append(dFilt.Sum("Generator_weight"))

            normPt.append(normY)    
        

        for i, h in enumerate(self.myTH2):

            h.SetBinContent(k,j,tmpCoeff[i][j][k].GetValue()/normPt[j][k].GetValue())

        return self.d

    def getTH1(self):

        return self.myTH1

    def getTH2(self):

        return self.myTH2       