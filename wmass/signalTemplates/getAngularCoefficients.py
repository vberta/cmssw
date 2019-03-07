from math import sqrt
import ROOT
import copy

class getAngularCoefficients:

    def __init__(self, string):

        pass
        
        self.myTH1 = []
        self.myTH2 = []
        self.myTH3 = []
        self.string = string

    def run(self,d):

        self.d = d

        fIn = ROOT.TFile.Open(self.string)

        hNum =[]
        hNum2 =[]
        hDen =[]


        for key in fIn.GetListOfKeys():

            hname = key.GetName()
            h = fIn.Get(hname)

            if "denom" in hname:
                hDen.append(h)
            elif "A" in hname:
                hNum.append(h)
            else: 
                hNum2.append(h)

        for p,h in enumerate(hNum):

            h.SetName('A{p}'.format(p=p))
            for n in range(1,h.GetNbinsY()+1):
                        
                for m in range(1, h.GetNbinsX()+1):


                    h.SetBinContent(m,n,h.GetBinContent(m,n)/hDen[0].GetBinContent(m,n))

                    # error propagation
                     
                    stdErr2 = hNum2[p].GetBinContent(m,n)/hDen[0].GetBinContent(m,n) - h.GetBinContent(m,n)*h.GetBinContent(m,n)
                    sqrtneff = hDen[0].GetBinContent(m,n)/hDen[0].GetBinError(m,n)

                    print stdErr2, sqrtneff
                    coefferr = sqrt(stdErr2)/sqrtneff

                    h.SetBinError(m,n,coefferr)

                    cont = h.GetBinContent(m,n)
                    err = h.GetBinError(m,n)

                    if p == 0:  
                        h.SetBinContent(m,n, 20./3.*cont + 2./3.)
                        h.SetBinError(m,n, 20./3.*err)

                    elif p == 1 or p == 5 or p == 6:        
                        h.SetBinContent(m,n, 5*cont)
                        h.SetBinError(m,n, 5*err)

                    elif p == 2:         
                        h.SetBinContent(m,n, 10*cont)
                        h.SetBinError(m,n, 10*err)

                    else:       
                        h.SetBinContent(m,n, 4*cont)
                        h.SetBinError(m,n, 4*err)

            self.myTH2.append(copy.deepcopy(h))

        return self.d

    def getTH1(self):

        return self.myTH1

    def getTH2(self):

        return self.myTH2  

    def getTH3(self):

        return self.myTH3

