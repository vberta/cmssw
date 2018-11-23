import ROOT
import math
from array import array


ROOT.gInterpreter.Declare(

    """
    // numerator of weighted average
    ROOT::RDF::RResultPtr<float> FilterAndSum(ROOT::RDF::RNode df, double lowY, double upY, double lowPt, double upPt, int i)
{
    auto cut = [=] (float Wrap_preFSR, float Wpt_preFSR) {
        return Wrap_preFSR > lowY && Wrap_preFSR < upY && Wpt_preFSR > lowPt && Wpt_preFSR < upPt;
    };
    return df.Filter(cut, {"Wrap_preFSR", "Wpt_preFSR"}).Sum<float>("P" + std::to_string(i)+ "w");
}

    // sum of generator weights
ROOT::RDF::RResultPtr<float> FilterAndSumNorm(ROOT::RDF::RNode df, double lowY, double upY, double lowPt, double upPt)
{
    auto cut = [=] (float Wrap_preFSR, float Wpt_preFSR) {
        return Wrap_preFSR > lowY && Wrap_preFSR < upY && Wpt_preFSR > lowPt && Wpt_preFSR < upPt;
    };
    return df.Filter(cut, {"Wrap_preFSR", "Wpt_preFSR"}).Sum<float>("Generator_weight_norm");
}

    // sum of generator weights squared
ROOT::RDF::RResultPtr<float> FilterAndSumNorm2(ROOT::RDF::RNode df, double lowY, double upY, double lowPt, double upPt)
{
    auto cut = [=] (float Wrap_preFSR, float Wpt_preFSR) {
        return Wrap_preFSR > lowY && Wrap_preFSR < upY && Wpt_preFSR > lowPt && Wpt_preFSR < upPt;
    };
    return df.Filter(cut, {"Wrap_preFSR", "Wpt_preFSR"}).Sum<float>("Generator_weight_norm");
}

    // std deviation of armonics
ROOT::RDF::RResultPtr<double> FilterAndStdDev(ROOT::RDF::RNode df, double lowY, double upY, double lowPt, double upPt, int i)
{
    auto cut = [=] (float Wrap_preFSR, float Wpt_preFSR) {
        return Wrap_preFSR > lowY && Wrap_preFSR < upY && Wpt_preFSR > lowPt && Wpt_preFSR < upPt;
    };
    return df.Filter(cut, {"Wrap_preFSR", "Wpt_preFSR"}).StdDev<float>("P" + std::to_string(i)+ "w");
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
        stdCoeff = []

        linPt = []
        linY = []

        sqPt = []
        sqY = []

        for c in coeff:
            self.myTH2.append(ROOT.TH2D("{c}".format(c=c), "{c}".format(c=c), len(yArr)-1, array('f',yArr), len(ptArr)-1, array('f',ptArr)))

        for i, h in enumerate(self.myTH2):
            
            tmpPt = []
            stdPt = []
            for j in range(1, h.GetNbinsY()+1):  # bins in W pt

                upPt = h.GetYaxis().GetBinUpEdge(j)
                lowPt = h.GetYaxis().GetBinLowEdge(j)
                
                tmpY = []
                stdY = []
                for k in range(1, h.GetNbinsX()+1):  # bin in W y
                    
                    upY = h.GetXaxis().GetBinUpEdge(k)
                    lowY = h.GetXaxis().GetBinLowEdge(k)
                    
                    tmpY.append(ROOT.FilterAndSum(CastToRNode2(d), lowY, upY, lowPt, upPt, i))  
                    stdY.append(ROOT.FilterAndStdDev(CastToRNode2(d), lowY, upY, lowPt, upPt, i))  

                    # stupid way to avoid reelooping
                    if i==0: 
                        linY.append(ROOT.FilterAndSumNorm(CastToRNode2(d), lowY, upY, lowPt, upPt)) 
                        sqY.append(ROOT.FilterAndSumNorm2(CastToRNode2(d), lowY, upY, lowPt, upPt))  
                        

                if i==0: 
                    linPt.append(linY)   
                    sqPt.append(sqY)  

                tmpPt.append(tmpY) 
                stdPt.append(stdY) 

            tmpCoeff.append(tmpPt) 
            stdCoeff.append(stdPt) 

        for i, h in enumerate(self.myTH2):
            for j in range(1, h.GetNbinsY()+1):  # bins in W pt
                for k in range(1, h.GetNbinsX()+1):  # bin in W y

                    mybin = h.GetBin(k,j)
                    h.SetBinContent(mybin, tmpCoeff[i][j-1][k-1].GetValue()/linPt[j-1][k-1].GetValue())
                    h.SetBinError(mybin, stdCoeff[i][j-1][k-1].GetValue()*math.sqrt(sqPt[j-1][k-1].GetValue()/linPt[j-1][k-1].GetValue()/linPt[j-1][k-1].GetValue())) #according to uncertainty propagation

            for j in range(1, h.GetNbinsY()+1):  # bins in W pt
                for k in range(1, h.GetNbinsX()+1):  # bin in W y

                    mybin = h.GetBin(k,j)
                    # now get the right angular coefficient
                    cont = h.GetBinContent(mybin)
                    err = h.GetBinError(mybin)
                    if i == 0:        
                        h.SetBinContent(mybin, 20./3.*cont + 2./3.)
                        h.SetBinError(mybin, 20./3.*err)
                    if i == 1 or i == 5 or i == 6:        
                        h.SetBinContent(mybin, 5*cont)
                        h.SetBinError(mybin, 5*err)
                    if i == 2:        
                        h.SetBinContent(mybin, 10*cont)
                        h.SetBinError(mybin, 10*err) 
                    if i == 3 or i == 4 or i ==7:        
                        h.SetBinContent(mybin, 4*cont)
                        h.SetBinError(mybin, 4*err)        



        return self.d

    def getTH1(self):

        return self.myTH1

    def getTH2(self):

        return self.myTH2       
