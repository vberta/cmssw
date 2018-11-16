import ROOT

ROOT.gInterpreter.Declare("""ROOT::RDF::RResultPtr<float> FilterAndSum(ROOT::RDF::RNode df, double lowY, double upY, double lowPt, double upPt, int i)
{
    auto cut = [=] (float Wrap_preFSR, float Wpt_preFSR) {
        return Wrap_preFSR > lowY && Wrap_preFSR < upY && Wpt_preFSR > lowPt && Wpt_preFSR < upPt;
    };
    return df.Filter(cut, {"Wrap_preFSR", "Wpt_preFSR"}).Sum<float>("P" + std::to_string(i));
}

ROOT::RDF::RResultPtr<float> FilterAndSumNorm(ROOT::RDF::RNode df, double lowY, double upY, double lowPt, double upPt)
{
    auto cut = [=] (float Wrap_preFSR, float Wpt_preFSR) {
        return Wrap_preFSR > lowY && Wrap_preFSR < upY && Wpt_preFSR > lowPt && Wpt_preFSR < upPt;
    };
    return df.Filter(cut, {"Wrap_preFSR", "Wpt_preFSR"}).Sum<float>("Generator_weight");
}

""")

def CastToRNode2(node):
   return ROOT.NodeCaster(node.__cppname__).Cast(node)


class module1:
    def __init__(self):
        pass
        
        self.myTH1 = []
        self.myTH2 = []
        
    def doSomething(self,d):

        self.d = d.Filter("GenPart_pdgId[GenPart_bareMuonIdx]<0") #select W+


        coeff = ['A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7']

        tmpCoeff = []
        tmpPt = []
        tmpY = []

        normPt = []
        normY = []

        for c in coeff:
            self.myTH2.append(ROOT.TH2D("{c}".format(c=c), "{c}".format(c=c), 100, -5., 5., 100, 0, 100))

        for i, h in enumerate(self.myTH2):
            
            #print 'outer loop'
            for j in range(1, h.GetNbinsY()+1):  # bins in W pt
                #print '\tinner loop'
                
                upPt = h.GetYaxis().GetBinUpEdge(j)
                lowPt = h.GetYaxis().GetBinLowEdge(j)
                
                for k in range(1, h.GetNbinsX()+1):  # bin in W y
                    
                    upY = h.GetXaxis().GetBinUpEdge(k)
                    lowY = h.GetXaxis().GetBinLowEdge(k)
                     
                    tmpY.append(ROOT.FilterAndSum(CastToRNode2(d), lowY, upY, lowPt, upPt, i))  # one dimensional array

                    if i==0: 
                        normY.append(ROOT.FilterAndSumNorm(CastToRNode2(d), lowY, upY, lowPt, upPt))  # one dimensional array            
                
                if len(normY) >0: normPt.append(normY)   

                tmpPt.append(tmpY)  # bidimensional array
            
            tmpCoeff.append(tmpPt)  # tridimensional array

        print 'jitting'
        for i, h in enumerate(self.myTH2):
            for j in range(1, h.GetNbinsY()+1):  # bins in W pt
                for k in range(1, h.GetNbinsX()+1):  # bin in W y

                    print j,k   
                    h.SetBinContent(k, j, tmpCoeff[i][j][k].GetValue())

        print 'returning'    


        return self.d

    def getTH1(self):

        return self.myTH1

    def getTH2(self):

        return self.myTH2       
