import ROOT
from array import array

import sys
sys.path.append('../../framework')

from header import *
import numpy as np

class TemplateBuilder:
    def __init__(self):
        pass
        
        self.myTH1 = []
        self.myTH2 = []
        
    def doSomething(self,d):

        yArr = [-6.0, -3.0, -2.5, -2.0, -1.6, -1.2, -0.8, -0.4, 0, 0.4, 0.8, 1.2 ,1.6, 2.0, 2.5, 3.0, 6.0]
        ptArr = [0., 4., 8., 12., 16., 20., 24., 32., 40., 60., 100., 200.]

        getVector_code ='''

        float getFromIdx(rvec_f v, int idx){ return v[idx];}

        '''

        ROOT.gInterpreter.Declare(getVector_code)

        d1 = d.Define("Mupt_preFSR", "getFromIdx(GenPart_pt, GenPart_preFSRMuonIdx)").Define("Mueta_preFSR", "getFromIdx(GenPart_eta, GenPart_preFSRMuonIdx)")

        ROOT.TH3.SetDefaultSumw2(True)

        coeff = ["0", "1", "2", "3", "4", "5", "6", "7", "UL"]
        templList = []

        # fake histogram just to define filters
    
        h = ROOT.TH2F("h", "h", len(yArr)-1, array('f',yArr), len(ptArr)-1, array('f',ptArr))

        sel_code = '''

        ROOT::RDF::RNode sel(ROOT::RDF::RNode df, float lowEdgePt, float upEdgePt, std::string c){

            auto sel = [=](float Wpt_preFSR) { return (Wpt_preFSR >lowEdgePt && Wpt_preFSR < upEdgePt);};

            return df.Filter(sel, {"Wpt_preFSR"});

        }

        '''

        ROOT.gInterpreter.Declare(sel_code)

        ptBins  = np.linspace( 25.0, 65.0, 81  )
        etaBins = np.linspace( -2.5, 2.5,  101 )

        for i in range(1, h.GetNbinsY()+1): #for each pt bin

            lowEdgePt = h.GetYaxis().GetBinLowEdge(i)
            upEdgePt = h.GetYaxis().GetBinUpEdge(i);

            for c in coeff:
                
                dtmp = ROOT.sel(CastToRNode(d1), lowEdgePt, upEdgePt, c)
                htmp = dtmp.Histo3D(("A{}_pt_{:0.1f}_to_{:0.1f}".format(c, lowEdgePt, upEdgePt), "A{}_pt_{:0.1f}_to_{:0.1f}".format(c, lowEdgePt, upEdgePt), len(etaBins)-1, array('f',etaBins), len(ptBins)-1, array('f',ptBins), len(yArr)-1, array('f', yArr)), "Mueta_preFSR" ,"Mupt_preFSR", "Wrap_preFSR", "Pweight"+"{c}".format(c=c))

                templList.append(htmp)

        ftempl = ROOT.TFile("templates.root", "recreate")

        ftempl.cd()

        for h in templList:
        
            h.Write()
        
        
        return d1
     

    def getTH1(self):

        return self.myTH1

    def getTH2(self):

        return self.myTH2     



