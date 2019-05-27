import sys
sys.path.append('../../framework')
from module import *

class ACoeff(module):
   
    def __init__(self, hmap):
        
        self.myTH1 = []
        self.myTH2 = []
        self.myTH3 = []

        self.hmap = hmap

    def defineHarmonicsFunc(self, d, s):

        d = d.Define("P{s}sq".format(s=s), "P{s}*P{s}*Generator_weight_norm".format(s=s)).Define("P{s}w".format(s=s),"P{s}*Generator_weight_norm".format(s=s))

        return d

    def run(self,d):

        self.d = d.Define("Generator_weight_norm","Generator_weight/fabs(Generator_weight)")

        coeff = ["0", "1", "2", "3", "4", "5", "6", "7"]

        charge = ["Plus", "Minus"]

        for ch in charge:

            if "Plus" in ch:
                dch = self.d.Filter('GenPart_pdgId[GenPart_preFSRMuonIdx]<0')
            else:
                dch = self.d.Filter('GenPart_pdgId[GenPart_preFSRMuonIdx]>0')

            hDenominator = dch.Histo2D(("hdenom_{}".format(ch), " ; W rapidity; W p_{T}",\
            self.hmap.GetXaxis().GetNbins(),self.hmap.GetXaxis().GetXbins().GetArray(), \
            self.hmap.GetYaxis().GetNbins(),self.hmap.GetYaxis().GetXbins().GetArray()), \
            "Wrap_preFSR", "Wpt_preFSR", "Generator_weight_norm")

            self.myTH2.append(hDenominator)

            for c in coeff:

                dch = self.defineHarmonicsFunc(dch,c)
            
                hNumerator = dch.Histo2D(('A_{c}_{ch}'.format(c=c, ch=ch), " ; W rapidity; W p_{T}",\
                self.hmap.GetXaxis().GetNbins(),self.hmap.GetXaxis().GetXbins().GetArray(), \
                self.hmap.GetYaxis().GetNbins(),self.hmap.GetYaxis().GetXbins().GetArray()),\
                "Wrap_preFSR", "Wpt_preFSR", "P{c}w".format(c=c))

                hP2 = dch.Histo2D(('hnum2_{c}_{ch}'.format(c=c, ch=ch), " ; W rapidity; W p_{T}",\
                self.hmap.GetXaxis().GetNbins(),self.hmap.GetXaxis().GetXbins().GetArray(), \
                self.hmap.GetYaxis().GetNbins(),self.hmap.GetYaxis().GetXbins().GetArray()),\
                "Wrap_preFSR", "Wpt_preFSR", "P{c}sq".format(c=c))

                self.myTH2.append(hNumerator)
                self.myTH2.append(hP2)

        return dch

    def getTH1(self):

        return self.myTH1

    def getTH2(self):

        return self.myTH2  

    def getTH3(self):

        return self.myTH3

    

