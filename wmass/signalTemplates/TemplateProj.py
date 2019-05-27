import ROOT
from array import array
import copy

import sys
sys.path.append('../../framework')
from module import *

class TemplateProj(module):
    def __init__(self, string):

        pass
        
        self.myTH1 = []
        self.myTH2 = []
        self.myTH3 = []
        self.string = string
        
    def run(self,d):

        self.d = d

        ROOT.TH3.SetDefaultSumw2(True)
        ROOT.gROOT.SetBatch()

        ROOT.gStyle.SetPalette(ROOT.kRainBow)

        fIn = ROOT.TFile.Open(self.string)
        myf = fIn.Get("Templates/nom")

        for key in myf.GetListOfKeys():
            
            name = key.GetName()

            if "pseudodata" in name:

                th2=ROOT.TH2D

                th2 = myf.Get(key.GetName())
                self.myTH2.append(copy.deepcopy(th2))
            
            else:
                th3=ROOT.TH3D

                th3 = myf.Get(key.GetName())

            
                """
                if not 'UL' in name:

                    nameUL = name.replace(name.split('_')[0], 'AUL')

                    th3UL = myf.Get(nameUL)

                    th3.Add(th3, th3UL)
                """
                for i in range(1, th3.GetNbinsZ()+1): #for each y bin
                
                    lowEdgeY = th3.GetZaxis().GetBinLowEdge(i)
                    upEdgeY = th3.GetZaxis().GetBinUpEdge(i);

                    th3.GetZaxis().SetRange(i, i);
                
                    #proj = th3.Project3D("_y_{:0.1f}_to_{:0.1f}_yxe".format(lowEdgeY, upEdgeY))
                    proj = th3.Project3D("y_{i}_yxe".format(i=i))

                    self.myTH2.append(copy.deepcopy(proj))

        return self.d


