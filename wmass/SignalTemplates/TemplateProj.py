import ROOT
from array import array

import sys
sys.path.append('../../framework')

from header import *

class TemplateProj:
    def __init__(self):
        pass
        
        self.myTH1 = []
        self.myTH2 = []
        
    def doSomething(self,d):

        ROOT.TH3.SetDefaultSumw2(True)
        ROOT.gROOT.SetBatch()

        ROOT.gStyle.SetPalette(ROOT.kRainBow)

        self.fIn = ROOT.TFile.Open("templates.root")

        for key in self.fIn.GetListOfKeys():
            
            th3=ROOT.TH3D

            th3 = self.fIn.Get(key.GetName())

            name = key.GetName()

            if not 'UL' in name:

                nameUL = name.replace(name.split('_')[0], 'AUL')

                th3UL = self.fIn.Get(nameUL)

                th3.Add(th3, th3UL)

            for i in range(1, th3.GetNbinsZ()+1): #for each y bin
                
                lowEdgeY = th3.GetZaxis().GetBinLowEdge(i)
                upEdgeY = th3.GetZaxis().GetBinUpEdge(i);

                th3.GetZaxis().SetRange(i, i);
                
                proj = th3.Project3D("_y_{:0.1f}_to_{:0.1f}_yxe".format(lowEdgeY, upEdgeY))


                c = ROOT.TCanvas(proj.GetName())
                c.cd()

                proj.Draw("colz")

                c.SaveAs('./Templ_png/{c}.png'.format(c=proj.GetName()))
                

        return d
     

    def getTH1(self):

        return self.myTH1

    def getTH2(self):

        return self.myTH2     



