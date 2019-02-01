import ROOT
from array import array
import copy

class TemplateProj:
    def __init__(self, string):

        pass
        
        self.myTH1 = []
        self.myTH2 = []
        self.myTH3 = []
        self.trigLoop = False
        self.string = string
        
    def run(self,d):

        self.d = d

        ROOT.TH3.SetDefaultSumw2(True)
        ROOT.gROOT.SetBatch()

        ROOT.gStyle.SetPalette(ROOT.kRainBow)

        fIn = ROOT.TFile.Open(self.string)

        for key in fIn.GetListOfKeys():
            
            th3=ROOT.TH3D

            th3 = fIn.Get(key.GetName())

            name = key.GetName()

            if not 'UL' in name:

                nameUL = name.replace(name.split('_')[0], 'AUL')

                th3UL = fIn.Get(nameUL)

                th3.Add(th3, th3UL)

            for i in range(1, th3.GetNbinsZ()+1): #for each y bin
                
                lowEdgeY = th3.GetZaxis().GetBinLowEdge(i)
                upEdgeY = th3.GetZaxis().GetBinUpEdge(i);

                th3.GetZaxis().SetRange(i, i);
                
                proj = th3.Project3D("_y_{:0.1f}_to_{:0.1f}_yxe".format(lowEdgeY, upEdgeY))

                self.myTH2.append(copy.deepcopy(proj))

        return self.d
     

    def getTH1(self):

        return self.myTH1

    def getTH2(self):

        return self.myTH2

    def getTH3(self):

        return self.myTH3

    def triggerLoop(self):

        return self.trigLoop              



