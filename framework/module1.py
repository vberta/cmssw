import ROOT
import math
from array import array


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

        yArr = [-3.5, -3.0, -2.5, -2.0, -1.6, -1.2, -0.8, -0.4, 0, 0.4, 0.8, 1.2 ,1.6, 2.0, 2.5, 3.0, 3.5]
        ptArr = [0, 4, 8, 12, 16, 20, 24, 32, 40, 60]

        self.d = d.Filter("GenPart_pdgId[GenPart_bareMuonIdx]<0") #select W+


        coeff = ['A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7']

        tmpCoeff = []
        
        normPt = []
        normY = []

        for c in coeff:
            self.myTH2.append(ROOT.TH2D("{c}".format(c=c), "{c}".format(c=c), len(yArr)-1, array('f',yArr), len(ptArr)-1, array('f',ptArr)))

        for i, h in enumerate(self.myTH2):
            
            tmpPt = []
            for j in range(1, h.GetNbinsY()+1):  # bins in W pt

                upPt = h.GetYaxis().GetBinUpEdge(j)
                lowPt = h.GetYaxis().GetBinLowEdge(j)
                
                tmpY = []
                for k in range(1, h.GetNbinsX()+1):  # bin in W y
                    
                    upY = h.GetXaxis().GetBinUpEdge(k)
                    lowY = h.GetXaxis().GetBinLowEdge(k)
                    
                    tmpY.append(ROOT.FilterAndSum(CastToRNode2(d), lowY, upY, lowPt, upPt, i))  

                    if i==0: 
                        normY.append(ROOT.FilterAndSumNorm(CastToRNode2(d), lowY, upY, lowPt, upPt))  
                
                if i==0: 
                    normPt.append(normY)   

                tmpPt.append(tmpY) 

            tmpCoeff.append(tmpPt)  

        print 'jitting'
        for i, h in enumerate(self.myTH2):
            for j in range(1, h.GetNbinsY()+1):  # bins in W pt
                for k in range(1, h.GetNbinsX()+1):  # bin in W y

                    mybin = h.GetBin(k,j)
                    h.SetBinContent(mybin, tmpCoeff[i][j-1][k-1].GetValue()/normPt[j-1][k-1].GetValue())
                    h.SetBinError(mybin, math.sqrt(1./normPt[j-1][k-1].GetValue()))

        print 'returning'    


        return self.d

    def getTH1(self):

        return self.myTH1

    def getTH2(self):

        return self.myTH2       
