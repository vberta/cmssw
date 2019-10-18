import ROOT
from array import array
import math
import sys
import copy as copy
sys.path.append('../../framework')
from module import *
from header import *
from bkg_variables_standalone import *
from bkg_selections import *
from bkg_systematics import *

class bkg_WptReweighter:
    def __init__(self, ptBinning, etaBinning, outdir='./bkg', folder='./', norm = 1, varPt = 'RecoZ_Muon_corrected_pt',systKind='nom',systName='nom',interpol=True)  :
        
        self.outdir = outdir
        self.folder = folder
        self.norm = norm
        self.ptBinning = ptBinning
        self.etaBinning = etaBinning
        self.varPt = varPt
        self.systKind = systKind
        self.systName = systName
        self.interpol = interpol

        self.fileDict = {}
        self.sampleList = ['DY','Data']

        self.ptBinningS = ['{:.2g}'.format(x) for x in self.ptBinning[:-1]]
        self.etaBinningS = ['{:.2g}'.format(x) for x in self.etaBinning[:-1]]

        for f in range(len(self.sampleList)) :
            self.fileDict[self.sampleList[f]] = (ROOT.TFile.Open(self.folder+'/'+self.sampleList[f]+'.root'))
        
    def ratio_fitter(self, differential=False, mLow=70,mUp=110,integrated=False) :        
        self.differential = differential
        self.mLow=mLow
        self.mUp=mUp
        self.integrated=integrated
        

        
        #getting histos and doing the ratio
        histoDict = {}
        if integrated :
            histoDict['WptMC'] = self.fileDict['DY'].Get('Dimuon/nom/bkgSel_'+self.varPt+'_'+self.systName)
            histoDict['WptData'] = self.fileDict['Data'].Get('Dimuon/nom/bkgSel_'+self.varPt+'_'+self.systName)
        else :
            histoDict['WptMC_2D'] = self.fileDict['DY'].Get('Dimuon/nom/bkgSel_RecoZ_Muon_mass'+'_'+self.systName+'_VS_Wpt')
            histoDict['WptData_2D'] = self.fileDict['Data'].Get('Dimuon/nom/bkgSel_RecoZ_Muon_mass'+'_'+self.systName+'_VS_Wpt')
            
            mMin= histoDict['WptMC_2D'].GetXaxis().GetBinCenter(1)-histoDict['WptMC_2D'].GetXaxis().GetBinWidth(1)/2
            binsize = histoDict['WptMC_2D'].GetXaxis().GetBinWidth(1)
            Nlow=int((self.mLow-mMin)/binsize)
            Nup=int((self.mUp-mMin)/binsize)
            print "bin limits", Nlow, Nup, binsize, mMin
            
            histoDict['WptMC'] = histoDict['WptMC_2D'].ProjectionY("Wpt_MC",Nlow,Nup)
            histoDict['WptData'] = histoDict['WptData_2D'].ProjectionY("Wpt_Data",Nlow,Nup)

            
        histoDict['WptMC'].Scale(self.norm)
        histoDict['WptData'].Scale(1/histoDict['WptData'].Integral())
        histoDict['WptMC'].Scale(1/histoDict['WptMC'].Integral())
        histoDict['WptRatio'] = histoDict['WptData'].Clone()
        histoDict['WptRatio'].Divide(histoDict['WptMC'])
        
        #histo features
        histoDict['WptMC'].SetLineColor(2)
        histoDict['WptData'].SetLineColor(3)
        histoDict['WptData'].GetXaxis().SetTitle("Reco Z p_{T}")
        histoDict['WptMC'].GetXaxis().SetTitle("Reco Z p_{T}")
        histoDict['WptData'].GetYaxis().SetTitle("Events")
        histoDict['WptMC'].GetYaxis().SetTitle("Events")
        histoDict['WptData'].GetYaxis().SetTitleOffset(1.2)
        histoDict['WptMC'].GetYaxis().SetTitleOffset(1.2)          
        histoDict['WptMC'].SetLineWidth(3)
        histoDict['WptData'].SetLineWidth(3)
        histoDict['WptRatio'].GetXaxis().SetTitle("Reco Z p_{T}")
        histoDict['WptRatio'].GetYaxis().SetTitle("DATA/MC")
        histoDict['WptRatio'].GetYaxis().SetTitleOffset(1.2)            
        histoDict['WptRatio'].SetLineWidth(3)
        
        
        if self.interpol :
            # pt_arr = ROOT.Double(0)
            # ptVal_arr = ROOT.Double(0)
            graph_spline = ROOT.TGraph()
            # pt_arr = []
            # ptVal_arr = []
            graph_spline.SetPoint(0,0,histoDict['WptRatio'].GetBinContent(1))
            for b in range(1,histoDict['WptRatio'].GetNbinsX()) :
                # pt_arr.append(histoDict['WptRatio'].GetBinCenter(b))
                # ptVal_arr.append(histoDict['WptRatio'].GetBinContent(b))
                # print b-1,histoDict['WptRatio'].GetBinCenter(b),histoDict['WptRatio'].GetBinContent(b)
                if histoDict['WptRatio'].GetBinCenter(b)<80  :
                    graph_spline.SetPoint(b,histoDict['WptRatio'].GetBinCenter(b),histoDict['WptRatio'].GetBinContent(b))
                else :
                    graph_spline.SetPoint(b,histoDict['WptRatio'].GetBinCenter(b),1) #weight =1 above Wpt=80
            graph_spline.SetPoint(b+1,histoDict['WptRatio'].GetBinCenter(b)*10,1)
            
            # pt_arr = histoDict['WptRatio'].GetXaxis().GetXbins()
            # ptVal_arr = histoDict['WptRatio'].GetArray()
            # for i in range(0,pt_arr.Size()) :
            #     print pt_arr[i]
            # for i in range(0,ptVal_arr.Size()) :
            #     print ptVal_arr[i]
            
            # splineRatio = ROOT.TSpline3("splineRatio",pt_arr, ptVal_arr,histoDict['WptRatio'].GetNbinsX())
            splineRatio = ROOT.TSpline3("splineRatio",graph_spline,"",0,0)
            splineRatio.SetName("splineRatio")
            splineRatio.SetTitle("splineRatio")

        else :    
            fitZpt = ROOT.TF1("fitZpt", 'pol5',0,200,6)
            fitZpt.SetParameters(1.08,-0.01,0.005,0.0004,0.0000084,0)
            histoDict['WptRatio'].Fit(fitZpt,"","",0,200)
        
        
        
        #plotting integrated version of the ratio-fit
        c_integrated = ROOT.TCanvas("c_integrated","c_integrated",800,700)
        c_integrated.cd()
        c_integrated.SetGridx()
        c_integrated.SetGridy()
        p_integrated_histo = ROOT.TPad("p_integrated_histo", "c_integrated",0,0.4,1,1)
        p_integrated_ratio = ROOT.TPad("p_integrated_ratio", "c_integrated",0,0,1,0.4)
        p_integrated_histo.SetBottomMargin(0.02)
        p_integrated_histo.Draw()
        p_integrated_ratio.SetTopMargin(0)
        p_integrated_ratio.SetBottomMargin(0.25)
        p_integrated_ratio.Draw()
        
        leg_integrated = ROOT.TLegend(0.30,0.10,0.80,0.4)
        leg_integrated.AddEntry(histoDict['WptMC'], "DY MC")
        leg_integrated.AddEntry(histoDict['WptData'], "Data")
        
        p_integrated_histo.cd()
        histoDict['WptData'].Draw()
        histoDict['WptMC'].Draw("Same")
        leg_integrated.Draw("SAME")        
        p_integrated_ratio.cd()
        histoDict['WptRatio'].Draw()
        splineRatio.Draw("SAME")
        
        if self.differential :
            for e in self.etaBinningS :
                for p in self.ptBinningS :
                    if self.etaBinningS.index(e)==len(self.etaBinningS)+1 or self.ptBinningS.index(p)==len(self.ptBinningS)+1 : continue
                    histoDict['WptMC'+e+p] = self.fileDict['DY'].Get('Dimuon/nom/bkgSel_'+self.varPt+'_'+self.systName+'_VS_eta_VS_pt').ProjectionX('Wpt_MC_'+p+'_'+e, self.etaBinningS.index(e)+1, self.etaBinningS.index(e)+1,self.ptBinningS.index(p)+1, self.ptBinningS.index(p)+1)
                    histoDict['WptData'+e+p] = self.fileDict['Data'].Get('Dimuon/nom/bkgSel_'+self.varPt+'_'+self.systName+'_VS_eta_VS_pt').ProjectionX('Wpt_Data_'+p+'_'+e,self.etaBinningS.index(e)+1, self.etaBinningS.index(e)+1,self.ptBinningS.index(p)+1, self.ptBinningS.index(p)+1)
                    histoDict['WptMC'+e+p].Scale(self.norm)
                    print e, p, "Entries", histoDict['WptMC'+e+p].GetEntries(), histoDict['WptData'+e+p].GetEntries()
                    histoDict['WptRatio'+e+p] = histoDict['WptData'+e+p].Clone('WptRatio'+e+p)
                    histoDict['WptRatio'+e+p].Divide(histoDict['WptMC'+e+p])
                
                    histoDict['WptMC'+e+p].SetLineColor(2)
                    histoDict['WptData'+e+p].SetLineColor(3)
                    histoDict['WptData'+e+p].GetXaxis().SetTitle("Reco Z p_{T}")
                    histoDict['WptMC'+e+p].GetXaxis().SetTitle("Reco Z p_{T}")
                    histoDict['WptData'+e+p].GetYaxis().SetTitle("Events")
                    histoDict['WptMC'+e+p].GetYaxis().SetTitle("Events")
                    histoDict['WptData'+e+p].GetYaxis().SetTitleOffset(1.2)
                    histoDict['WptMC'+e+p].GetYaxis().SetTitleOffset(1.2)          
                    histoDict['WptMC'+e+p].SetLineWidth(3)
                    histoDict['WptData'+e+p].SetLineWidth(3)
                    histoDict['WptRatio'+e+p].GetXaxis().SetTitle("Reco Z p_{T}")
                    histoDict['WptRatio'+e+p].GetYaxis().SetTitle("DATA/MC")
                    histoDict['WptRatio'+e+p].GetYaxis().SetTitleOffset(1.2)            
                    histoDict['WptRatio'+e+p].SetLineWidth(3)
            
        
        
        
        #write output
        output= ROOT.TFile(self.outdir+"WptReweight.root","recreate")
        output.cd()
        c_integrated.Write()
        splineRatio.Write()
        
        if self.differential :
            for e in self.etaBinningS :
                for p in self.ptBinningS :
                    if self.etaBinningS.index(e)==len(self.etaBinningS) or self.ptBinningS.index(p)==len(self.ptBinningS) : continue
                    histoDict['WptData'+e+p].Write()
                    histoDict['WptRatio'+e+p].Write()
        

        
        
        

        
        
        
