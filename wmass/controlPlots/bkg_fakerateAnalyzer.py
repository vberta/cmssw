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
from scipy.special import erf
import mpmath
import numpy as np


rej_line_code = '''
                    Double_t rejline(Double_t *x, Double_t *par)
                            {
                                if (x[0] > 34 && x[0] < 46)
                                {
                                    TF1::RejectPoint();
                                    return 0;
                                }
                            return par[0] + par[1]*x[0];
                            }
                '''
ROOT.gInterpreter.Declare(rej_line_code)





# class bkg_fakerateAnalyzer(module):
class bkg_fakerateAnalyzer:
    def __init__(self, ptBinning, etaBinning, outdir='./bkg', folder='./', norm = 1, varFake = 'Muon_pfRelIso04_all_corrected_MET_nom_mt', tightCut = 0.15, looseCut=40, fitOnTemplate=False, onData=True, nameSuff = '',slicing=True,systKind='nom',systName='nom',parabolaFit=False, EWSF='Fit',fastHistos=False,extraValidationPlots=False,correlatedFit=False)  :

        self.outdir = outdir
        self.folder = folder
        self.norm = norm
        self.ptBinning = ptBinning
        self.etaBinning = etaBinning
        self.varFake = varFake
        self.tightCut = tightCut
        self.looseCut = looseCut
        self.nameSuff = nameSuff
        self.systKind = systKind
        self.systName = systName
        self.parabolaFit = parabolaFit
        self.EWSF =EWSF
        self.correlatedFit = correlatedFit
        if self.correlatedFit :
            # self.corrFitSuff = '_correlatedFit' #OPTION DISABLED
            self.corrFitSuff = ''
        else :
            self.corrFitSuff = ''

        self.fitOnTemplate = fitOnTemplate
        self.onData = onData
        self.slicing = slicing
        self.fastHistos = fastHistos
        self.extraValidationPlots=extraValidationPlots

        self.hardcodeLooseCut = 30

        self.rootFilesRaw = []
        # self.rootFiles = []
        # self.relisoCUT = 0.15
        self.isoCUT = 5 # used for ratios VS Mt in preliminary studies only
        self.QCDmult = 1. #multiplication factor to QCD bkg, not implemented

        self.sampleList = ['WToMuNu','QCD','EWKbkg','Data','DataLike']
        # self.sampleList = ['WToMuNu','QCD','EWKbkg','DataLike']
        # self.sampleList = ['WToMuNu','QCD','Data','DataLike']

        self.signList = ['Plus','Minus']
        self.regionList = ['Signal','Sideband', 'Tot']
        self.varList = []
        for var in bkg_variables_standalone['D2variables'] : self.varList.append(var)
        # self.varList = ["pfRelIso04_all_VS_corrected_MET_nom_mt","pfRelIso04_all_TIMES_corrected_pt_VS_corrected_MET_nom_mt","pfRelIso04_all_VS_MET_pt","pfRelIso04_all_TIMES_corrected_pt_VS_MET_pt"]
        # self.varName = ["relIso_vs_Mt", "absIso_vs_Mt","relIso_vs_MET", "absIso_vs_MET"]
        # self.varName = ["relIso_vs_Mt", "absIso_vs_Mt"]
        self.varName = ["relIso_vs_Mt"]

        # self.ptBinningS = ['{:.2g}'.format(x) for x in self.ptBinning[1:]]
        # self.etaBinningS = ['{:.2g}'.format(x) for x in self.etaBinning[1:]]
        self.ptBinningS = ['{:.2g}'.format(x) for x in self.ptBinning[:-1]]
        self.etaBinningS = ['{:.2g}'.format(x) for x in self.etaBinning[:-1]]

        self.dataOpt = 'fake'
        if not self.onData : self.dataOpt = 'fakeMC'
        
        self.MarcFit = False
        if self.MarcFit :
            maxPt_linearFit = 45
            print "ATTENTION: FIT RANGE 25-45, MARC-LIKE TEST!!!"
        else :
            maxPt_linearFit = 65

        #open all the useful rootfile
        # for f in fileList
        #     rootFiles.append(ROOT.TFile.Open(self.folder+'/'+f))
        for f in range(len(self.sampleList)-1) :
            if (self.sampleList[f]!='DataLike') : self.rootFilesRaw.append(ROOT.TFile.Open(self.folder+'/'+self.sampleList[f]+'.root'))

        if self.slicing  :
            if self.fastHistos :
                self.fast_slicer()
            else :
                self.slicer()

        self.rootFiles = []
        for f in range(len(self.sampleList)-1) :
                if (self.sampleList[f]!='DataLike') : self.rootFiles.append(ROOT.TFile.Open(self.outdir+"/"+self.sampleList[f]+"_sliced"+".root"))
        


    def slicer(self) :
        print "-->Slincing:"
        # outlist = []
        print "files raw", self.rootFilesRaw
        for f in range(len(self.rootFilesRaw)) :

            var1DList = []
            for var,tools in bkg_variables_standalone['variables'].iteritems() :
                if not tools[5] : continue
                var1DList.append(var)

            output = ROOT.TFile(self.outdir+"/"+self.sampleList[f]+"_sliced"+".root","recreate")
            dirOutDict = {}
            histo1DDict ={}
            histo2DDict ={}
            histo3DDict = {}
            for s in self.signList :
                for r in self.regionList :
                    # print "filename, region,sign", self.rootFilesRaw[f], r, s
                    if r== 'Tot': continue
                    dirOutDict[s+r] = output.mkdir('bkg_'+r+s+'/nom')
                    dirOutDict[s+r+'nom'] = dirOutDict[s+r].GetDirectory("nom")
                    dirOutDict[s+r+'nom'].cd()

                    #COPY 1D
                    for v in var1DList :
                        v_var = v
                        if "nom" in self.systKind or "corrected" in self.systKind :
                            if  not "Data.root" in self.rootFilesRaw[f].GetName() : v_var = v.replace(self.systKind,self.systName)
                        histo1DDict[s+r+v] = self.rootFilesRaw[f].Get('bkg_'+r+s+'/nom/bkgSel_'+v_var+'_'+self.systName)
                        # print "histo name", 'bkgSel_'+v_var+'_'+self.systName
                        histo1DDict[s+r+v].SetName('bkgSel_'+v)
                        histo1DDict[s+r+v].Write()

                    #SLICE 2D
                    name2D = 'Muon_corrected_MET_nom_mt_VS_eta'
                    # name2D = 'MET_pt_VS_eta'
                    name2D_var = name2D
                    if "nom" in self.systKind or "corrected" in self.systKind :
                        if not "Data.root" in self.rootFilesRaw[f].GetName() : name2D_var = name2D.replace(self.systKind,self.systName)
                    histo2DDict[s+r] = self.rootFilesRaw[f].Get('bkg_'+r+s+'/nom/bkgSel_'+name2D_var+'_'+self.systName)
                    for eta in range(1, histo2DDict[s+r].GetNbinsY()+1) :
                        histo2DDict[s+r+str(eta)] = histo2DDict[s+r].ProjectionX("bkgSel_Muon_corrected_MET_nom_mt_"+self.etaBinningS[eta-1],eta,eta+1,"e")
                        histo2DDict[s+r+str(eta)].Write()
                    histo2DDict[s+r+"int"] = histo2DDict[s+r].ProjectionX("bkgSel_Muon_corrected_MET_nom_mt",1,histo2DDict[s+r].GetNbinsY(),"e")
                    histo2DDict[s+r+"int"].Write()

                    #SLICE 3D
                    for v in self.varList :
                        v_var = v
                        if "nom" in self.systKind or "corrected" in self.systKind :
                            if not "Data.root" in self.rootFilesRaw[f].GetName() : v_var = v.replace(self.systKind,self.systName)
                        histo3DDict[s+r+v+"int"] =  self.rootFilesRaw[f].Get('bkg_'+r+s+'/nom/bkgSel_'+v_var+'_VS_eta_'+self.ptBinningS[0]+'_'+self.systName).Project3D("yxe")
                        for p in self.ptBinningS :
                            histo3DDict[s+r+v] = self.rootFilesRaw[f].Get('bkg_'+r+s+'/nom/bkgSel_'+v_var+'_VS_eta_'+p+'_'+self.systName)
                            for eta in range(0, histo3DDict[s+r+v].GetNbinsZ()+1) :
                                histo3DDict[s+r+v].GetZaxis().SetRange(eta,eta+1)
                                histo3DDict[s+r+v+str(eta)] = histo3DDict[s+r+v].Project3D("yxe")
                                histo3DDict[s+r+v+str(eta)].SetName('bkgSel_'+v+'_'+self.etaBinningS[eta-1]+'_'+p)
                                histo3DDict[s+r+v+str(eta)].Write()
                                if(p!=self.ptBinningS[0]) :
                                    histo3DDict[s+r+v+"int"].Add(histo3DDict[s+r+v+str(eta)])
                        histo3DDict[s+r+v+"int"].SetName('bkgSel_'+v)
                        histo3DDict[s+r+v+"int"].Write()

            output.Close()
            # outlist.append(output)
        # return outlist
        
    def binNumb_calculator(self,histo, axis, lowEdge) : #axis can be X,Y,Z
        binout = 0
        
        if axis =='X' :
            for i in range(1,histo.GetNbinsX()+1) :
                if abs(histo.GetXaxis().GetBinLowEdge(i)-lowEdge)<0.00001 :
                    binout = i
        if axis =='Y' :
            for i in range(1,histo.GetNbinsY()+1) :
                if abs(histo.GetYaxis().GetBinLowEdge(i)-lowEdge)<0.00001 :
                    binout = i
        if axis =='Z' :
            for i in range(1,histo.GetNbinsZ()+1) :
                if abs(histo.GetYaxis().GetBinLowEdge(i)-lowEdge)<0.00001 :
                    binout = i
        
        return binout 
        
    
        
    
    

        
    def fast_slicer(self) : #for output of histo_fast
        
        #in this function several empty histograms are filled to avoid to change thigs in the script when the fast RDF is used
        #the relevant histos are filled bin-by-bin
        print "-->Slincing fast:"
        # outlist = []
        print "files raw", self.rootFilesRaw
        for f in range(len(self.rootFilesRaw)) :
            var1DList = []
            for var,tools in bkg_variables_standalone['variables'].iteritems() :
                if not tools[5] : continue
                var1DList.append(var)

            output = ROOT.TFile(self.outdir+"/"+self.sampleList[f]+"_sliced"+".root","recreate")
            dirOutDict = {}
            histo1DDict ={}
            histo2DDict ={}
            histo3DDict = {}
            for s in self.signList :
                # print s
                for r in self.regionList :
                    # print r
                    # print "filename, region,sign", self.rootFilesRaw[f], r, s
                    if r== 'Tot': continue
                    dirOutDict[s+r] = output.mkdir('bkg_'+r+s+'/nom')
                    dirOutDict[s+r+'nom'] = dirOutDict[s+r].GetDirectory("nom")
                    dirOutDict[s+r+'nom'].cd()

                    #1D completely skipped
                    for v in var1DList :
                        v_var = v
                        if "nom" in self.systKind or "corrected" in self.systKind :
                            if  not "Data.root" in self.rootFilesRaw[f].GetName() : v_var = v.replace(self.systKind,self.systName)
                        histo1DDict[s+r+v] =  ROOT.TH1F()#self.rootFilesRaw[f].Get('bkg_'+r+s+'/nom/bkgSel_'+v_var+'_'+self.systName)                      
                        histo1DDict[s+r+v].SetName('bkgSel_'+v)
                        histo1DDict[s+r+v].Write()

                    #SLICE 2D completely skipped
                    name2D = 'ptVSetaVSmt'
                    # name2D = 'MET_pt_VS_eta'
                    name2D_var = name2D
                    if "nom" in self.systKind or "corrected" in self.systKind :
                        if not "Data.root" in self.rootFilesRaw[f].GetName() : name2D_var = name2D.replace(self.systKind,self.systName)
                    histo2DDict[s+r] = ROOT.TH2F()#self.rootFilesRaw[f].Get('bkg_'+r+s+'/nom/bkgSel_'+name2D_var+'_'+self.systName)
                    for eta in range(0, len(self.etaBinningS)) :
                        histo2DDict[s+r+str(eta)] = ROOT.TH1F()#histo2DDict[s+r].ProjectionX("bkgSel_Muon_corrected_MET_nom_mt_"+self.etaBinningS[eta-1],eta,eta+1,"e")
                        histo2DDict[s+r+str(eta)].SetName("bkgSel_Muon_corrected_MET_nom_mt_"+self.etaBinningS[eta-1]) 
                        histo2DDict[s+r+str(eta)].Write()
                    histo2DDict[s+r+"int"] = ROOT.TH1F()#histo2DDict[s+r].ProjectionX("bkgSel_Muon_corrected_MET_nom_mt",1,histo2DDict[s+r].GetNbinsY(),"e")
                    histo2DDict[s+r+"int"].SetName("bkgSel_Muon_corrected_MET_nom_mt")
                    histo2DDict[s+r+"int"].Write()

                    #SLICE 3D
                    for v in self.varList :
                        # print v
                        v_var = v
                        # print "GET", 'bkg_'+r+s+'/nom/'+name2D_var+self.systName
                        # print "file", self.rootFilesRaw[f], f
                        mainHisto = self.rootFilesRaw[f].Get('bkg_'+r+s+'/nom/'+name2D_var+'_'+self.systName)
                        EWSFHisto = self.rootFilesRaw[f].Get('bkg_'+r+s+'/nom/ptVSeta_IsoEWKSF_'+self.systName) 
                        if "nom" in self.systKind or "corrected" in self.systKind :
                            if not "Data.root" in self.rootFilesRaw[f].GetName() : v_var = v.replace(self.systKind,self.systName)
                        histo3DDict[s+r+v+"int"] =  ROOT.TH3F()#self.rootFilesRaw[f].Get('bkg_'+r+s+'/nom/bkgSel_'+v_var+'_VS_eta_'+self.ptBinningS[0]+'_'+self.systName).Project3D("yxe")
                        for p in self.ptBinningS:
                            histo3DDict[s+r+v] = ROOT.TH3F()#self.rootFilesRaw[f].Get('bkg_'+r+s+'/nom/bkgSel_'+v_var+'_VS_eta_'+p+'_'+self.systName)
                            # print "p=", p
                            for eta in self.etaBinningS :    
                                # print "e=", eta
                                histo3DDict[s+r+v+eta] = ROOT.TH2F('bkgSel_'+v+'_'+eta+'_'+p,'bkgSel_'+v+'_'+eta+'_'+p,len(mtBinning)-1, array('f',mtBinning),2,array('f',[0,0.15,0.5]))
                                histo3DDict[s+r+v+eta+'IsoEWKSF'] = ROOT.TH2F('bkgSel_'+v+'_'+eta+'_'+p+'IsoEWKSF','bkgSel_'+v+'_'+eta+'_'+p+'IsoEWKSF',len(mtBinning)-1, array('f',mtBinning),2,array('f',[0,0.15,0.5]))
                                if r=='Signal' :
                                    isoBin = 1
                                else :
                                    isoBin = 2
                                for mtbin in range(1,3) :
                                    binPt =  self.binNumb_calculator(mainHisto,'X',self.ptBinning[self.ptBinningS.index(p)])
                                    binEta = self.binNumb_calculator(mainHisto,'Y',self.etaBinning[self.etaBinningS.index(eta)])
                                    
                                    histo3DDict[s+r+v+eta].SetBinContent(mtbin,isoBin,mainHisto.GetBinContent(binPt,binEta,mtbin))
                                    # print "start DEBUG:", p, eta, r, v, s, "binn=",binPt,binEta, "info bin calc=", self.ptBinning[self.ptBinningS.index(p)], self.etaBinning[self.etaBinningS.index(eta)]
                                    # print  "lowEdgeX=",mainHisto.GetXaxis().GetBinLowEdge(binPt), ", center X=",mainHisto.GetXaxis().GetBinCenter(binPt) 
                                    # print  "lowEdgeY=",mainHisto.GetYaxis().GetBinLowEdge(binEta), ", center Y=",mainHisto.GetYaxis().GetBinCenter(binEta)
                                    # print  "lowEdgeZ=",mainHisto.GetZaxis().GetBinLowEdge(mtbin), ", center Z=",mainHisto.GetZaxis().GetBinCenter(mtbin)
                                histo3DDict[s+r+v+eta+'IsoEWKSF'].SetBinContent(2,isoBin,EWSFHisto.GetBinContent(binPt,binEta))
                                histo3DDict[s+r+v+eta].SetName('bkgSel_'+v+'_'+eta+'_'+p)
                                histo3DDict[s+r+v+eta+'IsoEWKSF'].SetName('bkgSel_'+v+'_'+eta+'_'+p+'IsoEWKSF')
                                histo3DDict[s+r+v+eta].Write()
                                histo3DDict[s+r+v+eta+'IsoEWKSF'].Write()
                        histo3DDict[s+r+v+"int"].SetName('bkgSel_'+v)
                        histo3DDict[s+r+v+"int"].Write()

            output.Close()
            
            # outlist.append(output)
        # return outlist


    def ratio_2Dto1D(self,histo,isocut =0.15,name = "histoRate") : #histo = 2D isto iso:Mt, isocut=tight def., name=output histo name
        #this func. produce an histogram of fake or prompt rate in fuction of Mt (to verify ABCD assumption)

        # self.histo = histo
        # self.isocut = isocut
        # self.name = name

        isoMin= histo.GetYaxis().GetBinCenter(1)-histo.GetYaxis().GetBinWidth(1)/2
        binsize = histo.GetYaxis().GetBinWidth(1)
        Ncut=(isocut-isoMin)/binsize
        # print "DEBUG RATIO", isoMin, binsize, Ncut
        Ncut = int(Ncut)
        # print isocut, Ncut, isoMin
        # histoDen = histo.ProjectionX("histoDen",Ncut,-1)
        
        if self.fastHistos :
            Ncut = 2

        histoDen = histo.ProjectionX("histoDen")
        histoNum = histo.ProjectionX("histoNum",0,Ncut-1)
        histoRate = histoNum.Clone(name)
        histoRate.Divide(histoNum,histoDen,1,1)
        # print "preliminary, NUM, DEN", histoNum.GetEntries(),histoDen.GetEntries()
        return histoRate

    def Fit4ScaleFactorEW(self,mtDict, sign, eta,datakind,pt='') :
        # self.mtDict = mtDict
        # self.sign = sign
        # self.datakind = datakind
        # self.eta = eta
        # self.pt = pt

        outlist =[] #sig,bkg, chi2,chi2err

        class linearHistoFit:
            def __call__(self, x, parameters):
                s = parameters[0] # weight signal
                b = parameters[1] # weight bkg
                # c = parameters[2]
                x = x[0]
                ysig = hsig.GetBinContent(hsig.GetXaxis().FindFixBin(x));
                ybkg = hbkg.GetBinContent(hbkg.GetXaxis().FindFixBin(x));
                y = s*ysig+b*ybkg
                # print "value y",y
                return y

        hsig = mtDict[pt+eta+sign+'WToMuNuTot'].Clone()
        hsig.Add(mtDict[pt+eta+sign+'EWKbkgTot'])
        hbkg = mtDict[pt+eta+sign+'QCDTot'].Clone()
        hsig.Rebin(4)
        hbkg.Rebin(4)
        fitFunc = ROOT.TF1("fitFunc", linearHistoFit(),0,120,2)
        # fitFunc = ROOT.TF1("fitFunc", linearHistoFit,0,120,2)
        fitFunc.SetParameters(1,1,0)
        fitFunc.SetParNames("sig","bkg","const")
        hdata = mtDict[pt+eta+sign+datakind+'Tot'].Clone()
        hdata.Rebin(4)
        hdata.Fit(fitFunc,"Q","",0,120)

        sumDiffPre = 0
        sumDiffPost = 0
        for x in range(0,120) :
            btot = mtDict[pt+eta+sign+datakind+'Tot'].GetBinContent(hsig.GetXaxis().FindFixBin(x))
            bsig = hsig.GetBinContent(hsig.GetXaxis().FindFixBin(x));
            bbkg = hbkg.GetBinContent(hbkg.GetXaxis().FindFixBin(x));
            ss = fitFunc.GetParameter(0)
            bb = fitFunc.GetParameter(1)
            sumDiffPre = sumDiffPre+ (bsig+bbkg-btot)**2
            sumDiffPost = sumDiffPost+ (ss*bsig+bb*bbkg-btot)**2

        # print "FIT RESULTS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Post fit, values:", fitFunc.GetParameter(0), fitFunc.GetParameter(1), fitFunc.GetChisquare()/fitFunc.GetNDF(), "residual prefit/postfit =",sumDiffPre/sumDiffPost #PRINT THIS ONE
        # print "Pre fit values: (tot,w,QCD)   ", mtDict[sign+datakind+'Tot'].GetBinContent(10), mtDict[sign+'WToMuNuTot'].GetBinContent(10)+mtDict[sign+'QCDTot'].GetBinContent(10)+mtDict[sign+'EWKbkgTot'].GetBinContent(10)

        outlist = [fitFunc.GetParameter(0), fitFunc.GetParError(0),fitFunc.GetParameter(1), fitFunc.GetParError(1),fitFunc.GetChisquare()/fitFunc.GetNDF(),math.sqrt(2*fitFunc.GetNDF())/fitFunc.GetNDF() ]
        # return fitFunc.GetParameter(1)
        return outlist


    def isolationAna(self, hdict,  loosecut=40, varname = 'Muon_pfRelIso04_all_corrected_MET_nom_mt', kind = 'fake') :
        # self.loosecut = loosecut
        # self.varname = varname
        # self.kind = kind # fake = calculate the fakerate (measurement ABCD), prompt = the promptrate (from MC), validation = the fakerate on MC QCD, fakeMC = fakerate from dataLike (MC) SEE DICT BELOW
        # self.hdict = hdict

        # print "loosecut iso ana", loosecut
        kindDict = {
            'fake' : 'Data',
            'validation' : 'QCD',
            'fakeMC' : 'DataLike' ,
            'prompt' : 'WToMuNu',
            'EWKbkg' : 'EWKbkg',
        }
        datakind = kindDict[kind]

        hIsos = {}

        for s in self.signList :
            for e in self.etaBinningS :
                for p in self.ptBinningS :
                    # hIso = ROOT.TH1F("hIso_{kind}_{sign}_{eta}_{pt}".format(kind=kind,sign=s,eta=e, pt=p),"hIso_{kind}_{sign}_{eta}_{pt}".format(kind=kind,sign=s,eta=e, pt=p),400,0,0.5)
                    mtMin= hdict[p+e+s+varname+datakind+'Tot'].GetXaxis().GetBinCenter(1)-hdict[p+e+s+varname+datakind+'Tot'].GetXaxis().GetBinWidth(1)/2
                    binsizeLoose = hdict[p+e+s+varname+datakind+'Tot'].GetXaxis().GetBinWidth(1)
                    NcutLoose=(loosecut-mtMin)/binsizeLoose
                    NcutLoose = int(NcutLoose)
                    
                    if self.fastHistos :
                        NcutLoose = 2

                    hIso = hdict[p+e+s+varname+datakind+'Tot'].ProjectionY("Iso_{kind}_{sign}_{eta}_{pt}".format(kind=kind,sign=s,eta=e, pt=p),0,NcutLoose-1)

                    hIsos[p+e+s] = (hIso)
        return hIsos

    def asymmetryEW(self, p,e,hdict, NcutLoose, varname, NcutTight,ratio_differential=True,EWsubtraction=False) :
        # self.p = p
        # self.e = e
        # self.hdict = hdict
        # self.ratio_differential = ratio_differential
        # self.EWsubtraction = EWsubtraction
        # self.varname = varname

        hAsym = {}
        nAsym = {}
        rAsym = {}
        ewkAsym = {}
        for s in self.signList :
            for kind in ['Data','WToMuNu', 'EWKbkg'] :
                hAsym[kind+s] =  hdict[p+e+s+varname+kind+'Tot'].Clone(p+'_'+e+'_'+kind+s+'_'+varname)
                if kind=='EWKbkg' : #merge W and EWKbkg
                    hAsym['EWKbkg'+s].Add(hAsym['WToMuNu'+s])
                nAsym[kind+s+'denErr'] = ROOT.Double(0)
                nAsym[kind+s+'numErr'] = ROOT.Double(0)
                nAsym[kind+s+'den'] = hAsym[kind+s].ProjectionX("den_"+p+'_'+e+'_'+kind+s+'_'+varname,NcutTight-1,-1,"e").IntegralAndError(0,NcutLoose-1,nAsym[kind+s+'denErr'])
                nAsym[kind+s+'num'] = hAsym[kind+s].ProjectionX("num_"+p+'_'+e+'_'+kind+s+'_'+varname,0,NcutTight-1, "e").IntegralAndError(0,NcutLoose-1,nAsym[kind+s+'numErr'])
            for reg in ['num', 'den'] : #EWsubtraction
                if EWsubtraction :
                    nAsym['QCD'+s+reg] = nAsym['Data'+s+reg]-nAsym['EWKbkg'+s+reg]
                    nAsym['QCD'+s+reg+'Err'] = math.sqrt(nAsym['Data'+s+reg+'Err']**2+nAsym['EWKbkg'+s+reg+'Err']**2)
                else :
                    nAsym['QCD'+s+reg] = nAsym['Data'+s+reg]
                    nAsym['QCD'+s+reg+'Err'] = nAsym['Data'+s+reg+'Err']

        for kind in ['QCD','EWKbkg'] : #building or asymmetry ratios
            for reg in ['num', 'den'] :
                rAsym[kind+reg] = nAsym[kind+'Plus'+reg]/nAsym[kind+'Minus'+reg]
                # print "ratios",  kind, reg,  rAsym[kind+reg]
                rAsym[kind+reg+'Err'] = 1/(nAsym[kind+'Minus'+reg]**2)*math.sqrt((nAsym[kind+'Plus'+reg]**2)*(nAsym[kind+'Minus'+reg+'Err']**2)+(nAsym[kind+'Plus'+reg]**2)*(nAsym[kind+'Minus'+reg+'Err']**2))

        deltaQCD = nAsym['QCD'+'Plus'+'den']*(1-1/rAsym['QCD'+'den'])
        for reg in ['num', 'den'] :
                # print reg, "+,-,q=", nAsym['Data'+'Plus'+reg], nAsym['Data'+'Minus'+reg], deltaQCD, 1/rAsym['EWKbkg'+reg], nAsym['Data'+'Plus'+reg]-nAsym['Data'+'Minus'+reg]-deltaQCD, 1-1/rAsym['EWKbkg'+reg]
                ewkAsym[reg+'Plus'] = (nAsym['Data'+'Plus'+reg]-nAsym['Data'+'Minus'+reg]-deltaQCD)/(1-1/rAsym['EWKbkg'+reg])
                ewkAsym[reg+'Minus'] = (nAsym['Data'+'Plus'+reg]-nAsym['Data'+'Minus'+reg]-deltaQCD)/(rAsym['EWKbkg'+reg]-1)
                # print reg, ewkAsym[reg+'Plus'], ewkAsym[reg+'Minus']
        return ewkAsym

    def MinuitLinearFit(self, yy, xx, invCov, p0, q0,p0Err,q0Err,s,e) :
        # self.yy = yy
        # self.xx = xx
        # self.invCov = invCov
        # self.p0 = p0
        # self.q0 = q0
        # self.p0Err = p0Err
        # self.q0Err = q0Err
        # self.s = s
        # self.e = e
        # print "INITIAL VALUE=", q0,p0

        def linearChi2(npar, gin, f, par, istatus ):
            vec = yy-(par[0]+par[1]*xx)
            chi2 = np.linalg.multi_dot( [vec.T, invCov, vec] )
            f[0] = chi2
            return

        # minuit = ROOT.TVirtualFitter.Fitter(0, 2)
        # minuit.Clear()
        # minuit.SetFCN(linearChi2)
        # minuit.SetParameter(0, 'offset',q0,0.001,-2,2)
        # minuit.SetParameter(1, 'slope',p0,0.001,-0.1,0.1)
        # arglist = array.array('d',2*[0])
        # arglist[0] = 50000 #call limit
        # arglist[1] = 0.01 #tolerance
        # minuit.ExecuteCommand("MIGRAD", arglist, 2)
        # outdict['offset'] = minuit.GetParameter(0)
        # outdict['slope'] = minuit.GetParameter(1)
        # outdict['offsetErr'] = minuit.GetParError(0)
        # outdict['slopeErr'] = minuit.GetParError(1)
        # outdict['offset*slope'] = minuit.GetCovarianceMatrixElement(1,1)

        minuit = ROOT.TMinuit(2)#.Fitter(0, 2)
        minuit.SetFCN(linearChi2)
        arglist = array('d',2*[0])
        arglist[0] =1.0
        ierflg = ROOT.Long(0)
        # ierflag=0
        # q0 = 0.5
        # p0=0
        minuit.mnexcm("SET ERR",arglist,1,ierflg)
        minuit.mnparm(0, 'offset',q0,p0Err,-1,1,ierflg)
        minuit.mnparm(1, 'slope',p0,q0Err,-0.3,0.3,ierflg)
        # minuit.mnparm(0, 'offset',q0,0.001,-40,40,ierflg)
        # minuit.mnparm(1, 'slope',p0,0.001,-10,10,ierflg)
        arglist[0] = 500000 #call limit
        # arglist[1] = 0.01 #tolerance
        minuit.mnexcm("MIGRAD", arglist, 2,ierflg)
        # minuit.mnexcm("SEEk", arglist, 2,ierflg)


        out_cov = ROOT.TMatrixDSym(2)
        minuit.mnemat(out_cov.GetMatrixArray(),2)
        # out_cov = ROOT.TMatrixD(2,2)
        # minuit.mnemat(out_cov,2)
        val0 = ROOT.Double(0.)
        err0 = ROOT.Double(0.)
        val1 = ROOT.Double(0.)
        err1 = ROOT.Double(0.)
        minuit.GetParameter(0,val0,err0)
        minuit.GetParameter(1,val1,err1)


        outdict = {}
        outdict[s+e+'offset'+'Minuit'] = val0
        outdict[s+e+'slope'+'Minuit'] = val1
        outdict[s+e+'offset'+'Minuit'+'Err'] = err0
        outdict[s+e+'slope'+'Minuit'+'Err'] = err1

        outdict[s+e+'offset*slope'+'Minuit'] = ROOT.TMatrixDRow(out_cov,0)(1)
        # print "DEBUGGG>>>>", outdict
        # print "DEBU2:" , out_cov, ROOT.TMatrixDRow(out_cov,0)(0), ROOT.TMatrixDRow(out_cov,0)(1), ROOT.TMatrixDRow(out_cov,1)(0), ROOT.TMatrixDRow(out_cov,1)(1)
        # print "DEBUG>>>", "value at pt=30", val0+30*val1, ", value at pt=60", val0+60*val1
        return outdict


    def correlatedFitter(self, fakedict) :
        # self.fakedict = fakedict

        #load the histos
        file_dict = {}
        histo_fake_dict = {}
        systList = []
        systDict = bkg_systematics
    #    bin4corFit = [30,33,35,37,39,41,43,45,47,50,53,56,59,62,65]
        bin4corFit = [30,32,34,36,38,40,42,44,47,50,53,56,59,62,65] #good one
        bin4corFit = [26,28,30,32,34,36,38,40,42,44,47,50,53,56,59,62,65]
        binChange = 7 # bin 1-8: merge 2 pt bins, bin 8-end: merge 3 bins.
        binChange = 9

        bin4corFitS = ['{:.2g}'.format(x) for x in bin4corFit[:-1]]

        for sKind, sList in systDict.iteritems():
            for sName in sList :
                systList.append(sName)
                systdir = self.outdir.replace("bkg_nom","bkg_"+sName+'/')
                file_dict[sName]=ROOT.TFile.Open(systdir+'bkg_plots'+self.nameSuff+".root")

                for s in self.signList :
                    for e in self.etaBinningS :
                        histo_fake_dict[sName+s+e] = file_dict[sName].Get('c_comparison_'+s+'_'+e).GetPrimitive('hFakes_pt_fake_'+s+'_'+e)

                        temp_histREB = ROOT.TH1F(histo_fake_dict[sName+s+e].GetName()+'_reb',histo_fake_dict[sName+s+e].GetName()+'_reb',len(bin4corFit)-1,array('d',bin4corFit))
                        for r in range(1,len(bin4corFit)) :
                            if r<binChange :
                                valueBinRebinned = (histo_fake_dict[sName+s+e].GetBinContent(2*r)+histo_fake_dict[sName+s+e].GetBinContent(2*r-1))/2
                                valueBinRebinnedErr = (histo_fake_dict[sName+s+e].GetBinError(2*r)+histo_fake_dict[sName+s+e].GetBinError(2*r-1))/2
                            else :
                                valueBinRebinned = (histo_fake_dict[sName+s+e].GetBinContent(3*r-binChange)+histo_fake_dict[sName+s+e].GetBinContent(3*r-binChange-1)+histo_fake_dict[sName+s+e].GetBinContent(3*r-binChange-2))/3 #the not-simplified value of the bin number is: 2*N+3*(r-N), -1, -2.
                                valueBinRebinnedErr = (histo_fake_dict[sName+s+e].GetBinError(3*r-binChange)+histo_fake_dict[sName+s+e].GetBinError(3*r-binChange-1)+histo_fake_dict[sName+s+e].GetBinError(3*r-binChange-2))/3 #the not-simplified value of the bin number is: 2*N+3*(r-N), -1, -2.

                            temp_histREB.SetBinContent(r,valueBinRebinned)
                            temp_histREB.SetBinError(r,valueBinRebinnedErr)
                        temp_histREB.AddDirectory(False)
                        histo_fake_dict[sName+s+e+'reb'] = temp_histREB.Clone()
                file_dict[sName].Close()

        #prepare the fit
        correlatedFitterDict = {}
        for s in self.signList :
            for e in self.etaBinningS :
                np.set_printoptions(threshold=np.inf)

                err_multiplier=1
                dimFit = len(bin4corFitS)
                # print "fit dimension=",dimFit

                #debuglineREB
                # dimFit = 15#len(bin4corFitS) #17#len(self.ptBinning)-1

                xx_ = np.zeros(dimFit)
                yy_ = np.zeros(dimFit)
                cov_ = np.zeros(( len(systList)+1,dimFit,dimFit))

                #debug lines -----------------------
                # covdict = {}
                # for syst in  systList :
                #     covdict[syst] = np.zeros((dimFit,dimFit))
                # covdict['nom'] = np.zeros((dimFit,dimFit))

                # histo_fake_dict['nom'+s+e+'reb'] = fakedict[s+e].Rebin(len(bin4corFit)-1,fakedict[s+e].GetName()+'_reb', array('d',bin4corFit))
                # histo_fake_dict['nom'+s+e+'reb'] =fakedict[s+e].GetName()+'_reb'

                histo_fake_dict['nom'+s+e+'reb'] = ROOT.TH1F(fakedict[s+e].GetName()+'_reb',fakedict[s+e].GetName()+'_reb',len(bin4corFit)-1,array('d',bin4corFit))
                for r in range(1,len(bin4corFit)) :
                    if r<binChange :
                        valueBinRebinned = (fakedict[s+e].GetBinContent(2*r)+fakedict[s+e].GetBinContent(2*r-1))/2
                        valueBinRebinnedErr = (fakedict[s+e].GetBinError(2*r)+fakedict[s+e].GetBinError(2*r-1))/2
                    else :
                        valueBinRebinned = (fakedict[s+e].GetBinContent(3*r-binChange)+fakedict[s+e].GetBinContent(3*r-binChange-1)+fakedict[s+e].GetBinContent(3*r-binChange-2))/3 #the not-simplified value of the bin number is: 2*N+3*(r-N), -1, -2.
                        valueBinRebinnedErr = (fakedict[s+e].GetBinError(3*r-binChange)+fakedict[s+e].GetBinError(3*r-binChange-1)+fakedict[s+e].GetBinError(3*r-binChange-2))/3 #the not-simplified value of the bin number is: 2*N+3*(r-N), -1, -2.

                    histo_fake_dict['nom'+s+e+'reb'].SetBinContent(r,valueBinRebinned)
                    histo_fake_dict['nom'+s+e+'reb'].SetBinError(r,valueBinRebinnedErr)
                    # print r, valueBinRebinned

                #debuglineREB
                # histo_fake_dict['nom'+s+e+'reb'] =  fakedict[s+e]


                for pp in range(xx_.size) :
                    # if fakedict[s+e].GetBinCenter(pp+1)>35 and fakedict[s+e].GetBinCenter(pp+1)<45 :
                    #     print "centro skipped", fakedict[s+e].GetBinCenter(pp+1)
                    #     continue
                    jump = 0
                    # if pp==16 :jump = 16

                    xx_[pp] = histo_fake_dict['nom'+s+e+'reb'].GetBinCenter(pp+1+jump)
                    # print "bin center=",pp, xx_[pp]
                    # yy_[pp] = fakedict[s+e+'offset']+xx_[pp]*fakedict[s+e+'slope']
                    yy_[pp] = histo_fake_dict['nom'+s+e+'reb'].GetBinContent(pp+1+jump)

                    #debug
                    # print "FIT,",s,e,pp,", centro=", fakedict[s+e].GetBinCenter(pp+1), ",  fake=", yy_[pp], "variation=", histo_fake_dict["puWeightUp"+s+e].GetBinContent(pp+1) #, histo_fake_dict['nom'+s+e].GetBinContent(pp+1)

                for pp in range(xx_.size) : #separate loop because needed xx,yy fully filled
                    # print "()()()()()()()() entro in pp", pp
                    jump1=0
                    # if pp == 16 : jump1 = 16
                    for p2 in range(xx_.size) :
                        jump2 = 0
                        # if p2 == 16 : jump2 = 16
                        # print "--->>>>>>>>>>--->_>_>_entro in p2", p2
                        for syst in range(len(systList)+1) :
                            # print "entro in syst", syst
                            if pp==p2 and syst==len(systList):

                                dx_f = (histo_fake_dict['nom'+s+e+'reb'].GetBinWidth(pp+1+jump1))/2
                                # erv = fakedict[s+e+'offsetErr']**2+(dx_f**2)*(fakedict[s+e+'slope']**2)+(xx_[pp]**2)*(fakedict[s+e+'slopeErr']**2)+2*xx_[pp]*fakedict[s+e+'offset*slope']
                                erv = err_multiplier*histo_fake_dict['nom'+s+e+'reb'].GetBinError(pp+1+jump1)**2
                                cov_[syst][pp][p2] = erv
                                # covdict['nom'][pp][p2] = erv
                            elif syst<len(systList):
                                if 'Up' in systList[syst] :#do not use down syst, will be symmetrized with up later
                                    # if 'puWeight' in systList[syst]:
                                        systUp =systList[syst]
                                        systDown =  systUp.replace("Up","Down")

                                        #debuglineREB
                                        # histo_fake_dict[systUp+s+e+'reb'] = histo_fake_dict[systUp+s+e]
                                        # histo_fake_dict[systDown+s+e+'reb'] = histo_fake_dict[systDown+s+e]
                                        #EODREB

                                        deltaPP = (abs(yy_[pp]-histo_fake_dict[systUp+s+e+'reb'].GetBinContent(pp+1+jump1))+ abs(yy_[pp]-histo_fake_dict[systDown+s+e+'reb'].GetBinContent(pp+1+jump1)))/2
                                        deltaP2 = (abs(yy_[p2]-histo_fake_dict[systUp+s+e+'reb'].GetBinContent(p2+1+jump2))+ abs(yy_[p2]-histo_fake_dict[systDown+s+e+'reb'].GetBinContent(p2+1+jump2)))/2
                                        # erv = (yy_[pp]-histo_fake_dict[systList[syst]+s+e].GetBinContent(pp+1))*(yy_[p2]-histo_fake_dict[systList[syst]+s+e].GetBinContent(p2+1))
                                        erv = err_multiplier*deltaPP*deltaP2
                                        # print "riempo, syst, pp, p2", systList[syst], pp, p2, systUp,systDown
                                        # if 'ID' in systList[syst] : erv = 0
                                        cov_[syst][pp][p2] = erv
                                        # covdict[systList[syst]][pp][p2] = erv
                                        if pp==p2:
                                            # print "sign=",s," fake=", yy_[pp], " varied=", systUp, histo_fake_dict[systUp+s+e].GetBinContent(pp+1)
                                            debug_notsym = (yy_[pp]-histo_fake_dict[systUp+s+e+'reb'].GetBinContent(pp+1+jump1))**2
                                            # debug_erv = fakedict[s+e+'offsetErr']**2+(((fakedict[s+e].GetBinWidth(pp+1))/2)**2)*(fakedict[s+e+'slope']**2)+(xx_[pp]**2)*(fakedict[s+e+'slopeErr']**2)+2*xx_[pp]*fakedict[s+e+'offset*slope']
                                            debug_erv=histo_fake_dict['nom'+s+e+'reb'].GetBinError(pp+1+jump1)**2
                                            # print "FIT:",p2+35,pp+35,"sig=",s,", err(syst)=", erv, ", err(stat)=", debug_erv,  " ratio(sym) syst/stat=",erv/debug_erv, systList[syst]# " not_sym_erv= ",debug_notsym," ratio(nsy)=", debug_notsym/debug_erv

                q0_ = fakedict[s+e+'offset']
                p0_ = fakedict[s+e+'slope']
                q0Err_ = fakedict[s+e+'offsetErr']
                p0Err_ = fakedict[s+e+'slopeErr']
                # print "PREPROJJJ---------------------------", cov_.shape
                # print cov_
                cov_proj = cov_.sum(axis=0) #square sum of syst
                # print "MATRIX---------------------------", cov_proj.shape
                # print cov_proj
                # for pp in range(xx_.size) :

                #     xx_[pp] = xx_[pp]-(fakedict[s+e].GetBinCenter(1)-fakedict[s+e].GetBinWidth(1)/2)
                    # xx_[pp] = xx_[pp]-30
                    # print "post", xx_[pp]

                #uncomment here -----------------------------------
                # matt = np.zeros((dimFit,dimFit))
                # for syst in  systList :
                #     print "rank of", syst,  np.linalg.matrix_rank(covdict[syst])
                #     matt = matt+covdict[syst]
                # matt = matt + covdict['nom']
                # print "rank of all",  np.linalg.matrix_rank(cov_proj), np.linalg.slogdet(cov_proj)
                # print "rank of matt", np.linalg.matrix_rank(matt), np.linalg.slogdet(matt)
                # # print "eigval and egvec of matt=", np.linalg.eig(matt)
                # matt = matt- cov_proj
                # # print "debugg", matt
                #end of good debug ----------------------------

                invCov_ = np.linalg.inv(cov_proj)

                #do the fit
                minuitDict = self.MinuitLinearFit( yy=yy_, xx=xx_, invCov=invCov_, p0=p0_, q0=q0_,p0Err=p0Err_, q0Err=q0Err_,s=s,e=e)
                correlatedFitterDict.update(minuitDict)
        return correlatedFitterDict





    def differential_fakerate(self, hdict, mtDict, tightcut = 0.15, loosecut=40, varname = 'pfRelIso04_all_corrected_MET_nom_mt', kind = 'fake', EWSF='Fit', highMtCut=90,parabolaFit=False, asymmetry_EW=False, correlatedFit=False) :
        # self.loosecut = loosecut
        # self.tightcut = tightcut
        # self.varname = varname
        # self.kind = kind # fake = calculate the fakerate (measurement ABCD), prompt = the promptrate (from MC), validation = the fakerate on MC QCD, fakeMC = fakerate from dataLike (MC) SEE DICT BELOW
        # self.hdct = hdict
        # self.mtDict =mtDict
        # self.EWSF = EWSF
        # self.highMtCut = highMtCut
        # self.parabolaFit = parabolaFit
        # self.asymmetry_EW = asymmetry_EW
        # self.correlatedFit = correlatedFit



        # print "loosecut diff fakerate",loosecut

        kindDict = {
            'fake' : 'Data',
            'validation' : 'QCD',
            'fakeMC' : 'DataLike' ,
            'prompt' : 'WToMuNu',
            'validationSigReg' : 'QCD',
            'promptSideband' : 'WToMuNu',
        }
        datakind = kindDict[kind]

        hFakes = {}
        h2Fakes = {}
        hEWSF_Fit = {}
        hTempl_Fit = {}
        # TH2F h2Fakes = TH2F("h2Fakes","h2Fakes",len(self.etaBinning)-1, array('f',self.etaBinning), len(self.ptBinning)-1, array('f',self.ptBinning) )
        # h2Fakes[0] = TH2F("h2Fakes_plus","h2Fakes_plus",len(self.etaBinning)-1, array('f',self.etaBinning), len(self.ptBinning)-1, array('f',self.ptBinning) )
        # h2Fakes[1] = TH2F("h2Fakes_minus","h2Fakes_minus",len(self.etaBinning)-1, array('f',self.etaBinning), len(self.ptBinning)-1, array('f',self.ptBinning) )
        for s in self.signList :
            h2Fakes_sign = ROOT.TH2F("h2Fakes_{kind}_{sign}".format(kind=kind,sign=s),"h2Fakes_{kind}_{sign}".format(kind=kind,sign=s),len(self.etaBinning)-1, array('f',self.etaBinning), len(self.ptBinning)-1, array('f',self.ptBinning) )
            if kind == 'fake' or kind == 'fakeMC' :
                hEWSF_chi2 = ROOT.TH1F("hEWSF_chi2_{kind}_{sign}".format(kind=kind,sign=s),"hEWSF_chi2_{kind}_{sign}".format(kind=kind,sign=s), len(self.etaBinning)-1, array('f',self.etaBinning), )
                hEWSF_bkg = ROOT.TH1F("hEWSF_bkg_{kind}_{sign}".format(kind=kind,sign=s),"hEWSF_bkg_{kind}_{sign}".format(kind=kind,sign=s), len(self.etaBinning)-1, array('f',self.etaBinning), )
                hEWSF_sig = ROOT.TH1F("hEWSF_sig_{kind}_{sign}".format(kind=kind,sign=s),"hEWSF_sig_{kind}_{sign}".format(kind=kind,sign=s), len(self.etaBinning)-1, array('f',self.etaBinning), )
            hTempl_chi2 = ROOT.TH1F("hTempl_chi2_{kind}_{sign}".format(kind=kind,sign=s),"hTempl_chi2_{kind}_{sign}".format(kind=kind,sign=s), len(self.etaBinning)-1, array('f',self.etaBinning), )
            hTempl_slope = ROOT.TH1F("hTempl_slope_{kind}_{sign}".format(kind=kind,sign=s),"hTempl_slope_{kind}_{sign}".format(kind=kind,sign=s), len(self.etaBinning)-1, array('f',self.etaBinning), )
            hTempl_offset = ROOT.TH1F("hTempl_offset_{kind}_{sign}".format(kind=kind,sign=s),"hTempl_offset_{kind}_{sign}".format(kind=kind,sign=s), len(self.etaBinning)-1, array('f',self.etaBinning), )
            hTempl_2deg = ROOT.TH1F("hTempl_2deg_{kind}_{sign}".format(kind=kind,sign=s),"hTempl_2deg_{kind}_{sign}".format(kind=kind,sign=s), len(self.etaBinning)-1, array('f',self.etaBinning), )


            for e in self.etaBinningS :
                hFakes_pt = ROOT.TH1F("hFakes_pt_{kind}_{sign}_{eta}".format(kind=kind,sign=s,eta=e),"hFakes_pt_{kind}_{sign}_{eta}".format(kind=kind,sign=s,eta=e), len(self.ptBinning)-1, array('f',self.ptBinning) )

                #debug histo
                hFakes_pt_Cdata = ROOT.TH1F("hFakes_pt_Cdata_{kind}_{sign}_{eta}".format(kind=kind,sign=s,eta=e),"hFakes_pt_Cdata_{kind}_{sign}_{eta}".format(kind=kind,sign=s,eta=e), len(self.ptBinning)-1, array('f',self.ptBinning) )
                hFakes_pt_Adata = ROOT.TH1F("hFakes_pt_Adata_{kind}_{sign}_{eta}".format(kind=kind,sign=s,eta=e),"hFakes_pt_Adata_{kind}_{sign}_{eta}".format(kind=kind,sign=s,eta=e), len(self.ptBinning)-1, array('f',self.ptBinning) )
                hFakes_pt_Cweak = ROOT.TH1F("hFakes_pt_Cweak_{kind}_{sign}_{eta}".format(kind=kind,sign=s,eta=e),"hFakes_pt_Cweak_{kind}_{sign}_{eta}".format(kind=kind,sign=s,eta=e), len(self.ptBinning)-1, array('f',self.ptBinning) )
                hFakes_pt_Aweak = ROOT.TH1F("hFakes_pt_Aweak_{kind}_{sign}_{eta}".format(kind=kind,sign=s,eta=e),"hFakes_pt_Aweak_{kind}_{sign}_{eta}".format(kind=kind,sign=s,eta=e), len(self.ptBinning)-1, array('f',self.ptBinning) )
                hFakes_pt_ratioCA = ROOT.TH1F("hFakes_pt_ratioCA_{kind}_{sign}_{eta}".format(kind=kind,sign=s,eta=e),"hFakes_pt_ratioCA_{kind}_{sign}_{eta}".format(kind=kind,sign=s,eta=e), len(self.ptBinning)-1, array('f',self.ptBinning) )


                scaleFactorEW = {}
                scaleFactorEWErr = {}
                scaleFactorEW['1'] = 1
                scaleFactorEWErr['1'] = 0
                scaleFactorEW['0'] = 0
                scaleFactorEWErr['0'] = 0

                if kind == 'fake' or kind == 'fakeMC' :
                    # print "PRE FIT (sign, eta, kind))", s, e, datakind
                    # scaleFactorEW=self.Fit4ScaleFactorEW(mtDict=mtDict,sign=s,eta=e,datakind=datakind)
                    if not self.fastHistos :
                        scaleFactorEWPars = self.Fit4ScaleFactorEW(mtDict=mtDict,sign=s,eta=e,datakind=datakind)
                    else : 
                        scaleFactorEWPars = [0,0,0,0,0,0]

                    #Fit EWSF
                    scaleFactorEW['Fit']=scaleFactorEWPars[0]
                    scaleFactorEWErr['Fit']=scaleFactorEWPars[1]
                        # scaleFactorEW = scaleFactorEW-0.1*scaleFactorEW #variation of EWSF

                    #Mt EWSF
                    if not self.fastHistos :
                        EWKIntErr = ROOT.Double(0)
                        EWKbIntErr = ROOT.Double(0)
                        dataIntErr = ROOT.Double(0)
                        QCDIntErr = ROOT.Double(0)
                        minBin = mtDict[e+s+'WToMuNuTot'].GetXaxis().FindBin(highMtCut)
                        maxBin = mtDict[e+s+'WToMuNuTot'].GetSize()-1 #number of bins (overflow included, -1 is to the underflow)
                        EWKInt = mtDict[e+s+'WToMuNuTot'].IntegralAndError(minBin,maxBin,EWKIntErr)
                        EWKInt = EWKInt + mtDict[e+s+'EWKbkgTot'].IntegralAndError(minBin,maxBin,EWKbIntErr)
                        dataInt = mtDict[e+s+datakind+'Tot'].IntegralAndError(minBin,maxBin,dataIntErr)
                        QCDInt = mtDict[e+s+'QCDTot'].IntegralAndError(minBin,maxBin,QCDIntErr)            
                        scaleFactorEW['Mt'] = (EWKInt-QCDInt)/dataInt
                        sfnumErr2 = EWKIntErr**2+EWKbIntErr**2+QCDIntErr**2
                        scaleFactorEWErr['Mt'] = 1/(dataInt**2)*math.sqrt(sfnumErr2*(dataInt**2)+(dataIntErr**2)*((EWKInt-QCDInt)**2))
                    else :
                         scaleFactorEW['Mt']  = 0
                         scaleFactorEWErr['Mt'] = 0

                        # print "SCALE FACTOR (eta,sign)",e, s, ",   VALUE=", scaleFactorEW, "  fit one=",scaleFactorEWPars[0], "   ratio (int/fit)=",scaleFactorEW/scaleFactorEWPars[0] #PRINT THIS ONE
                    hEWSF_bkg.SetBinContent(self.etaBinningS.index(e)+1,scaleFactorEWPars[2])
                    hEWSF_bkg.SetBinError(self.etaBinningS.index(e)+1,scaleFactorEWPars[3])
                    hEWSF_sig.SetBinContent(self.etaBinningS.index(e)+1,scaleFactorEWPars[0])
                    hEWSF_sig.SetBinError(self.etaBinningS.index(e)+1,scaleFactorEWPars[1])
                    hEWSF_chi2.SetBinContent(self.etaBinningS.index(e)+1,scaleFactorEWPars[4])
                    hEWSF_chi2.SetBinError(self.etaBinningS.index(e)+1,scaleFactorEWPars[5])


                    hEWSF_chi2_pt = ROOT.TH1F("hEWSF_chi2_{kind}_{sign}_{eta}".format(kind=kind,sign=s,eta=e),"hEWSF_chi2_{kind}_{sign}_{eta}".format(kind=kind,sign=s,eta=e), len(self.ptBinning)-1, array('f',self.ptBinning), )
                    hEWSF_bkg_pt = ROOT.TH1F("hEWSF_bkg_{kind}_{sign}_{eta}".format(kind=kind,sign=s,eta=e),"hEWSF_bkg_{kind}_{sign}_{eta}".format(kind=kind,sign=s,eta=e), len(self.ptBinning)-1, array('f',self.ptBinning), )
                    hEWSF_sig_pt = ROOT.TH1F("hEWSF_sig_{kind}_{sign}_{eta}".format(kind=kind,sign=s,eta=e),"hEWSF_sig_{kind}_{sign}_{eta}".format(kind=kind,sign=s,eta=e), len(self.ptBinning)-1, array('f',self.ptBinning), )
                    hEWSF_iso_pt = ROOT.TH1F("hEWSF_iso_{kind}_{sign}_{eta}".format(kind=kind,sign=s,eta=e),"hEWSF_iso_{kind}_{sign}_{eta}".format(kind=kind,sign=s,eta=e), len(self.ptBinning)-1, array('f',self.ptBinning), )
                    hEWSF_Mt_pt = ROOT.TH1F("hEWSF_Mt_{kind}_{sign}_{eta}".format(kind=kind,sign=s,eta=e),"hEWSF_Mt_{kind}_{sign}_{eta}".format(kind=kind,sign=s,eta=e), len(self.ptBinning)-1, array('f',self.ptBinning), )

                for p in self.ptBinningS :
                    # print ">>>>>>>>>>>>>>>>>DEBUG......",kind, "s,e,p=", s,e,p
                    if kind == 'fake' or kind == 'fakeMC' :
                        if not self.fastHistos :
                            scaleFactorEWPars_p = self.Fit4ScaleFactorEW(mtDict=mtDict,sign=s,eta=e,datakind=datakind,pt=p)
                        else :
                            scaleFactorEWPars_p = [0,0,0,0,0,0]

                        #Fit_pt EWSF
                        scaleFactorEW['Fit_pt']=scaleFactorEWPars_p[0]
                        scaleFactorEWErr['Fit_pt']=scaleFactorEWPars_p[1]

                        #Mt_pt EWSF
                        if not self.fastHistos :
                            EWKIntErr = ROOT.Double(0)
                            EWKbIntErr = ROOT.Double(0)
                            dataIntErr = ROOT.Double(0)
                            QCDIntErr = ROOT.Double(0)
                            minBin = mtDict[p+e+s+'WToMuNuTot'].GetXaxis().FindBin(highMtCut)
                            maxBin = mtDict[p+e+s+'WToMuNuTot'].GetSize()-1 #number of bins (overflow included, -1 is to the underflow)
                            EWKInt = mtDict[p+e+s+'WToMuNuTot'].IntegralAndError(minBin,maxBin,EWKIntErr)
                            EWKInt = EWKInt + mtDict[p+e+s+'EWKbkgTot'].IntegralAndError(minBin,maxBin,EWKbIntErr)
                            dataInt = mtDict[p+e+s+datakind+'Tot'].IntegralAndError(minBin,maxBin,dataIntErr)
                            QCDInt = mtDict[p+e+s+'QCDTot'].IntegralAndError(minBin,maxBin,QCDIntErr)                           
                            scaleFactorEW['Mt_pt'] = dataInt/(EWKInt-QCDInt)
                            sfdenErr = EWKIntErr**2+EWKbIntErr**2+QCDIntErr**2
                            scaleFactorEWErr['Mt_pt'] = 1/((EWKInt-QCDInt)**2)*math.sqrt(sfdenErr*(dataInt**2)+(dataIntErr**2)*((EWKInt-QCDInt)**2))
                        else :
                            scaleFactorEW['Mt_pt'] = 0
                            scaleFactorEWErr['Mt_pt'] = 0

                    if not self.fastHistos :
                        if kind == 'fake' or kind == 'fakeMC' :
                            hEWSF_bkg_pt.SetBinContent(self.ptBinningS.index(p)+1,scaleFactorEWPars_p[0])
                            hEWSF_bkg_pt.SetBinError(self.ptBinningS.index(p)+1,scaleFactorEWPars_p[1])
                            hEWSF_sig_pt.SetBinContent(self.ptBinningS.index(p)+1,scaleFactorEWPars_p[2])
                            hEWSF_sig_pt.SetBinError(self.ptBinningS.index(p)+1,scaleFactorEWPars_p[3])
                            hEWSF_chi2_pt.SetBinContent(self.ptBinningS.index(p)+1,scaleFactorEWPars_p[4])
                            hEWSF_chi2_pt.SetBinError(self.ptBinningS.index(p)+1,scaleFactorEWPars_p[5])
                            # print "e,p, s=", e,p,s, ", value=", scaleFactorEWPars_p[0]
                            hEWSF_Mt_pt.SetBinContent(self.ptBinningS.index(p)+1,scaleFactorEW['Mt_pt'])
                            hEWSF_Mt_pt.SetBinError(self.ptBinningS.index(p)+1,scaleFactorEWErr['Mt_pt'])


                    hsubtract= hdict[p+e+s+varname+datakind+'Tot'].Clone(p+'_'+e+'_'+'datakind'+s+'_'+varname)
                    # if kind == 'fake' or kind == 'fakeMC' :
                    #     hsubtract.Add(hdict[p+e+s+varname+'EWKbkg'+'Tot'],-1)
                    #     hsubtract.Add(hdict[p+e+s+varname+'WToMuNu'+'Tot'],-1)

                    isoMin= hsubtract.GetYaxis().GetBinCenter(1)-hsubtract.GetYaxis().GetBinWidth(1)/2
                    binsizeTight = hsubtract.GetYaxis().GetBinWidth(1)
                    NcutTight=(tightcut-isoMin)/binsizeTight
                    NcutTight = int(NcutTight)
                    
                    mtMin= hsubtract.GetXaxis().GetBinCenter(1)-hsubtract.GetXaxis().GetBinWidth(1)/2
                    binsizeLoose = hsubtract.GetXaxis().GetBinWidth(1)
                    NcutLoose=(loosecut-mtMin)/binsizeLoose
                    NcutLoose = int(NcutLoose)
                    
                    if self.fastHistos :
                        NcutTight=2
                        NcutLoose=2

                    numErr = ROOT.Double(0)
                    denErr = ROOT.Double(0)
                    antiNumErr = ROOT.Double(0) #antinum = b region (not tight)
                    fake_err =0
                    if (kind=='fake' or kind=='validation' or kind=='fakeMC' or kind=='promptSideband') :
                        # print "here: cuts (t,l)", NcutTight, NcutLoose
                        
                        den = hsubtract.ProjectionX("histoDen",0,-1,"e").IntegralAndError(0,NcutLoose-1,denErr)
                        num = hsubtract.ProjectionX("histoNum",0,NcutTight-1, "e").IntegralAndError(0,NcutLoose-1,numErr)
                        antiNum = hsubtract.ProjectionX("histoNum",NcutTight,-1, "e").IntegralAndError(0,NcutLoose-1,antiNumErr)

                        # scaleFactorLumi = 1
                        # if(num!= 0 and den!=0) :
                        #     scaleFactorLumi= numErr*numErr/num
                        #     num4err = num /scaleFactorLumi
                        #     den4err = den /scaleFactorLumi
                        #     fake_err = 1/den4err*math.sqrt(num4err*(1-num4err/den4err))*scaleFactorLumi #standard eff error rewighted on scale factor
                        # print "SCALE FACTOR LUMI:", scaleFactorLumi


                        if kind == 'fake' or kind == 'fakeMC' : #not QCD
                            numErr_EWKbkg = ROOT.Double(0)
                            denErr_EWKbkg = ROOT.Double(0)
                            numErr_WToMuNu = ROOT.Double(0)
                            denErr_WToMuNu = ROOT.Double(0)
                            den_EWKbkg = hdict[p+e+s+varname+'EWKbkg'+'Tot'].ProjectionX("histoDen",0,-1,"e").IntegralAndError(0,NcutLoose-1,denErr_EWKbkg)
                            num_EWKbkg = hdict[p+e+s+varname+'EWKbkg'+'Tot'].ProjectionX("histoNum",0,NcutTight-1, "e").IntegralAndError(0,NcutLoose-1,numErr_EWKbkg)
                            den_WToMuNu = hdict[p+e+s+varname+'WToMuNu'+'Tot'].ProjectionX("histoDen",0,-1,"e").IntegralAndError(0,NcutLoose-1,denErr_WToMuNu)
                            num_WToMuNu = hdict[p+e+s+varname+'WToMuNu'+'Tot'].ProjectionX("histoNum",0,NcutTight-1, "e").IntegralAndError(0,NcutLoose-1,numErr_WToMuNu)

                            #Iso_pt EWSF
                            w_only_region_data_Err_w = ROOT.Double(0)
                            w_only_region_data_Err_qcd = ROOT.Double(0)
                            w_only_region_MC_Err_w = ROOT.Double(0)
                            w_only_region_MC_Err_ewk = ROOT.Double(0)
                            QCD_multiplier = 1.0#1.1 #systemtatic variation
                            if self.fastHistos :
                                w_only_region_data = hdict[p+e+s+varname+datakind+'Tot'+'IsoEWKSF'].ProjectionX("histoNum",0,1, "e").IntegralAndError(NcutLoose,-1,w_only_region_data_Err_w)-QCD_multiplier*hdict[p+e+s+varname+'QCD'+'Tot'+'IsoEWKSF'].ProjectionX("histoNum",0,1, "e").IntegralAndError(NcutLoose,-1,w_only_region_data_Err_qcd)
                                w_only_region_MC=hdict[p+e+s+varname+'WToMuNu'+'Tot'+'IsoEWKSF'].ProjectionX("histoNum",0,1, "e").IntegralAndError(NcutLoose,-1,w_only_region_MC_Err_w)+hdict[p+e+s+varname+'EWKbkg'+'Tot'+'IsoEWKSF'].ProjectionX("histoNum",0,1, "e").IntegralAndError(NcutLoose,-1,w_only_region_MC_Err_ewk)
                                # print "bin=", p,e,s,varname, datakind, "values=", w_only_region_data, w_only_region_data
                            else : 
                                w_only_region_data= hsubtract.ProjectionX("histoNum",0,1, "e").IntegralAndError(NcutLoose,-1,w_only_region_data_Err_w)-QCD_multiplier*hdict[p+e+s+varname+'QCD'+'Tot'].ProjectionX("histoNum",0,1, "e").IntegralAndError(NcutLoose,-1,w_only_region_data_Err_qcd)
                                w_only_region_MC = hdict[p+e+s+varname+'WToMuNu'+'Tot'].ProjectionX("histoNum",0,1, "e").IntegralAndError(NcutLoose,-1,w_only_region_MC_Err_w)+hdict[p+e+s+varname+'EWKbkg'+'Tot'].ProjectionX("histoNum",0,1, "e").IntegralAndError(NcutLoose,-1,w_only_region_MC_Err_ewk)
                            # w_only_region_data= hsubtract.ProjectionX("histoNum",0,1, "e").IntegralAndError(0,-1,w_only_region_data_Err_w)-QCD_multiplier*hdict[p+e+s+varname+'QCD'+'Tot'].ProjectionX("histoNum",0,1, "e").IntegralAndError(0,-1,w_only_region_data_Err_qcd)
                            # w_only_region_MC = hdict[p+e+s+varname+'WToMuNu'+'Tot'].ProjectionX("histoNum",0,1, "e").IntegralAndError(0,-1,w_only_region_MC_Err_w)+hdict[p+e+s+varname+'EWKbkg'+'Tot'].ProjectionX("histoNum",0,1, "e").IntegralAndError(0,-1,w_only_region_MC_Err_ewk)

                            EWSF_iso_pt = w_only_region_data/w_only_region_MC
                            EWSF_iso_pt_err_num=math.sqrt(w_only_region_data_Err_w**2+(QCD_multiplier*w_only_region_data_Err_qcd)**2)
                            EWSF_iso_pt_err_den=math.sqrt(w_only_region_MC_Err_w**2+w_only_region_MC_Err_ewk**2)
                            EWSF_iso_pt_err = 1/(w_only_region_MC**2)*math.sqrt((w_only_region_MC**2)*(EWSF_iso_pt_err_num**2)+(w_only_region_data**2)*(EWSF_iso_pt_err_den**2))
                            hEWSF_iso_pt.SetBinContent(self.ptBinningS.index(p)+1,EWSF_iso_pt)
                            hEWSF_iso_pt.SetBinError(self.ptBinningS.index(p)+1,EWSF_iso_pt_err)
                            scaleFactorEW['Iso_pt'] = EWSF_iso_pt
                            scaleFactorEWErr['Iso_pt'] = EWSF_iso_pt_err

                            # print "pt dependent EWSF=", EWKSF_pt, "pt=",p, "MC QCD % = ", hdict[p+e+s+varname+'QCD'+'Tot'].ProjectionX("histoNum",0,1, "e").Integral(NcutLoose-1,-1)/hsubtract.ProjectionX("histoNum",0,1, "e").Integral(NcutLoose-1,-1)
                            # EWKSF_pt =1
                            # print "EWSF ERROR STUDY...----------------------------",s,e,p
                            # print  "relative error=",EWSF_iso_pt_err/EWSF_iso_pt
                            # print "breakdown of the error=", "W=",w_only_region_data_Err_w, "QCD=", w_only_region_data_Err_qcd, "EWK=",EWSF_iso_pt_err_den
                            # print "breakdown of the relative=", "W=",w_only_region_data_Err_w/hsubtract.ProjectionX("histoNum",0,1, "e").IntegralAndError(NcutLoose-1,-1,w_only_region_data_Err_w),
                            # print  "QCD=", w_only_region_data_Err_qcd/hdict[p+e+s+varname+'QCD'+'Tot'].ProjectionX("histoNum",0,1, "e").IntegralAndError(NcutLoose-1,-1,w_only_region_data_Err_qcd),
                            # print "EWK=",EWSF_iso_pt_err_den/w_only_region_MC
                            # print "events:" "W=", hsubtract.ProjectionX("histoNum",0,1, "e").IntegralAndError(NcutLoose-1,-1,w_only_region_data_Err_w),
                            # print "QCD=", hdict[p+e+s+varname+'QCD'+'Tot'].ProjectionX("histoNum",0,1, "e").IntegralAndError(NcutLoose-1,-1,w_only_region_data_Err_qcd),
                            # print "EWK=", w_only_region_MC
                            # print "sqrtn", "W=", math.sqrt(hsubtract.ProjectionX("histoNum",0,1, "e").IntegralAndError(NcutLoose-1,-1,w_only_region_data_Err_w)),
                            # print "QCD=", math.sqrt(hdict[p+e+s+varname+'QCD'+'Tot'].ProjectionX("histoNum",0,1, "e").IntegralAndError(NcutLoose-1,-1,w_only_region_data_Err_qcd)),
                            # print "EWK=", math.sqrt(w_only_region_MC)


                            if(asymmetry_EW) :

                                asymmetry_EW = self.asymmetryEW(p=p,e=e,ratio_differential=False,EWsubtraction=True,hdict = hdict,varname = varname,NcutLoose=NcutLoose, NcutTight=NcutTight)
                                    # print asymmetry_EW
                                # print "rapporto=", s, num/asymmetry_EW['num'+s], asymmetry_EW['num'+s]
                                den = den - asymmetry_EW['den'+s] -asymmetry_EW['num'+s] #num=C, den=A, in the asymmetryEW only!
                                num = num -  asymmetry_EW['num'+s]
                            else :
                                # print ((den_EWKbkg + den_WToMuNu)*scaleFactorEW[EWSF])/num
                                den = den - (den_EWKbkg + den_WToMuNu)*scaleFactorEW[EWSF]
                                num = num - (num_EWKbkg + num_WToMuNu)*scaleFactorEW[EWSF]
                            # print s, "DEN=",(den_EWKbkg + den_WToMuNu)*scaleFactorEW[EWSF], "NUM=", (num_EWKbkg + num_WToMuNu)*scaleFactorEW[EWSF]
                            # den = den - (den_EWKbkg + den_WToMuNu)*EWKSF_pt
                            # num = num - (num_EWKbkg + num_WToMuNu)*EWKSF_pt


                            denErr = math.sqrt(denErr**2 + (denErr_EWKbkg**2 + denErr_WToMuNu**2)*(scaleFactorEW[EWSF])**2+(scaleFactorEWErr[EWSF]**2)*((den_EWKbkg + den_WToMuNu)**2))
                            numErr = math.sqrt(numErr**2 + (numErr_EWKbkg**2 + numErr_WToMuNu**2)*(scaleFactorEW[EWSF])**2+(scaleFactorEWErr[EWSF]**2)*((num_EWKbkg + num_WToMuNu)**2))

                            # print "numerr", denErr, ", EWSKERR=", scaleFactorEWErr[EWSF]*(den_EWKbkg + den_WToMuNu), "relative=", math.sqrt(scaleFactorEWErr[EWSF]**2*(den_EWKbkg + den_WToMuNu)**2)/denErr
                            # print den_EWKbkg, den_WToMuNu, scaleFactorEWErr[EWSF], scaleFactorEW[EWSF]
                            # print ((den_EWKbkg + den_WToMuNu)*scaleFactorEW[EWSF])/den

                            #ERROR ON SUM EVALUATION
                            antiNumErr_EWKbkg = ROOT.Double(0)
                            antiNumErr_WToMuNu = ROOT.Double(0)
                            antiNum_EWKbkg = hdict[p+e+s+varname+'EWKbkg'+'Tot'].ProjectionX("histoNum",NcutTight,-1, "e").IntegralAndError(0,NcutLoose-1,antiNumErr_EWKbkg)
                            antiNum_WToMuNu = hdict[p+e+s+varname+'WToMuNu'+'Tot'].ProjectionX("histoNum",NcutTight,-1, "e").IntegralAndError(0,NcutLoose-1,antiNumErr_WToMuNu)

                            # print "DEBUG", e, p, s,"antinum=",antiNum, "num=",num,
                            antiNum = antiNum - (antiNum_EWKbkg + antiNum_WToMuNu)*scaleFactorEW[EWSF]
                            # antiNumErr = math.sqrt((antiNumErr**2 + antiNumErr_EWKbkg**2 + antiNumErr_WToMuNu**2)*(scaleFactorEW[EWSF]**2)+0*(scaleFactorEWErr[EWSF]**2)*(antiNum**2))
                            antiNumErr = math.sqrt(antiNumErr**2 + (antiNumErr_EWKbkg**2 + antiNumErr_WToMuNu**2)*(scaleFactorEW[EWSF])**2+(scaleFactorEWErr[EWSF]**2)*((antiNum_EWKbkg + antiNum_WToMuNu)**2))
                            
                            # print  "(BIS) antinum=",antiNum, "num=", num 
                            #Debug histograms
                            hFakes_pt_Cdata.SetBinContent(self.ptBinningS.index(p)+1, num+(num_EWKbkg + num_WToMuNu)*scaleFactorEW[EWSF])
                            hFakes_pt_Adata.SetBinContent(self.ptBinningS.index(p)+1, antiNum+(antiNum_EWKbkg + antiNum_WToMuNu)*scaleFactorEW[EWSF])
                            hFakes_pt_Cweak.SetBinContent(self.ptBinningS.index(p)+1, num_EWKbkg + num_WToMuNu)
                            hFakes_pt_Aweak.SetBinContent(self.ptBinningS.index(p)+1, antiNum_EWKbkg + antiNum_WToMuNu)
                            hFakes_pt_ratioCA.SetBinContent(self.ptBinningS.index(p)+1, num/antiNum)
                            # if kind == 'fake' :
                                # print "INSIDE; e,p", e,p, "num=", num+(num_EWKbkg + num_WToMuNu)*scaleFactorEW[EWSF], ", ew num=", (num_EWKbkg + num_WToMuNu)*scaleFactorEW[EWSF], ",   antinum=", antiNum+(antiNum_EWKbkg + antiNum_WToMuNu)*scaleFactorEW[EWSF], ",   antinum ew=", (antiNum_EWKbkg + antiNum_WToMuNu)*scaleFactorEW[EWSF]


                            # if(num!=0 and den!=0 and antiNum!=0) :
                            #     num4err = num /scaleFactorLumi
                            #     den4err = den /scaleFactorLumi
                            #     antiNum4err = antiNum /scaleFactorLumi

                                # d_num2 = (scaleFactorLumi**2) * ((num4err**2)+(scaleFactorEW**2)*((num4err_EWKbkg**2)+(num4err_WToMuNu**2))) #error SQUARE on num4err
                                # d_antiNum2 = (scaleFactorLumi**2) * ((antiNum4err**2)+(scaleFactorEW**2)*((antiNum4err_EWKbkg**2)+(antiNum4err_WToMuNu**2))) #error SQUARE on antinum4err
                                # fake_err=(1/(den4err**2))*math.sqrt(d_num2*(antiNum4err**2)+d_antiNum2*(num4err**2))


                        # for x in range(hsubtract.GetNbinsX()) :
                        #     for y in range(hsubtract.GetNbinsY()) :
                        #             if(hsubtract.GetBinContent(x,y)>0) : radice = math.sqrt(hsubtract.GetBinContent(x,y))
                        #             else : radice = 0
                        #             print "esempio bin ------------------------------", hsubtract.GetBinContent(x,y),  hsubtract.GetBinError(x,y),radice


                    else : #prompt calulated in signal region (or valdiationSigReg)
                        # hsubtract.Sumw2()
                        den = hsubtract.ProjectionX("histoDen",0,-1,"e").IntegralAndError(NcutLoose,-1,denErr)
                        num = hsubtract.ProjectionX("histoNum",0,NcutTight-1, "e").IntegralAndError(NcutLoose,-1,numErr)
                        # print"bin 3,val + content,", hsubtract.ProjectionX("histoDen",0,-1,"e").GetBinContent(3), hsubtract.ProjectionX("histoDen",0,-1,"e").GetBinError(3)
                        # print"bin 3,val + content, no e opt", hsubtract.ProjectionX("histoDen").GetBinContent(3), hsubtract.ProjectionX("histoDen").GetBinError(3)
                        antiNum = hsubtract.ProjectionX("histoNum",NcutTight,-1, "e").IntegralAndError(NcutLoose,-1,antiNumErr)
                        # print "debug integral", s,e,p, "num=", num, numErr,math.sqrt(num), "    , den=",antiNum,antiNumErr,math.sqrt(antiNum)
                       
                        # print "-------------------------------------------------"
                        # print "debug bin:", hsubtract.GetBinContent(1,2),  hsubtract.GetBinContent(2,2),  hsubtract.GetBinContent(1,1),  hsubtract.GetBinContent(2,1)
                        # print "baseline=", "num=", hsubtract.ProjectionX("histoNum",0,NcutTight-1, "e").IntegralAndError(NcutLoose,-1,numErr), "den=", hsubtract.ProjectionX("histoDen",0,-1,"e").IntegralAndError(NcutLoose,-1,denErr), "antinum=", hsubtract.ProjectionX("histoNum",NcutTight,-1, "e").IntegralAndError(NcutLoose,-1,antiNumErr)
                        # print "NUM?=", hsubtract.ProjectionX("histoNum",1,1, "e").IntegralAndError(2,2,numErr), "DEN?=", hsubtract.ProjectionX("histoDen",1,2,"e").IntegralAndError(2,2,denErr), "ANTINUM?=", hsubtract.ProjectionX("histoNum",2,2, "e").IntegralAndError(2,2,antiNumErr)
                        # print "BIS: NUM?=", hsubtract.IntegralAndError(2,2,1,1,numErr), "DEN?=", hsubtract.IntegralAndError(2,2,1,2,denErr), "ANTINUM?=", hsubtract.IntegralAndError(2,2,2,2,antiNumErr)
                       
                        # scaleFactorLumi = 1
                        # if(num!= 0 and den!=0) :
                        #     scaleFactorLumi= numErr*numErr/num
                        #     num = num /scaleFactorLumi
                        #     den = den /scaleFactorLumi
                        #     fake_err = 1/den*math.sqrt(num*(1-num/den))*scaleFactorLumi #standard eff error rewighted on scal factor
                        # print "SCALE FACTOR LUMI :", scaleFactorLumi

                    # print("kind", kind, "eta,pt", e, p, "num,den", num, den, "s",s)
                    if(den == 0) :
                        fake = 0
                        print "WARNING: fake rate den = 0 --> num=", num, "data kind=",kind, "(pt,eta,sign)=",p,e,s
                    if(num==0) :
                        fake = 0
                        print "WARNING: fake rate num = 0 --> den=", den, "data kind=",kind, "(pt,eta,sign)=",p,e,s
                    else:
                        # print "Ok: fake rate --> num/den=", num, den, num/den, "data kind=",kind, "(pt,eta,sign)=",p,e,s
                        # if(kind == 'fake') :
                            #  print "e,p", e,p, ",    C=", num, numErr, ", A+C=", den,denErr, ", A=", antiNum, antiNumErr, ", fake rate=", scaleFactorEW['Mt_pt']
                        fake = num/den
                        # if kind=='prompt' :
                            # if fake>1 : 
                                # print "DEBUG PROMPTRATE=", "num=",num, "den=",den, "antiNum=",antiNum, "fake=", fake
                                # print "debug bin:", hsubtract.GetBinContent(1,2),  hsubtract.GetBinContent(2,2),  hsubtract.GetBinContent(1,1),  hsubtract.GetBinContent(2,1)
                                
                        # print num, numErr, math.sqrt(num),den, denErr, math.sqrt(den)
                        # fake_err = 1/(den**2)*math.sqrt((numErr**2)*(den**2)+(denErr**2)*(num**2)) #UNCORRELATED!!!!
                        fake_err=(1/(den**2))*math.sqrt((numErr**2)*(antiNum**2)+(antiNumErr**2)*(num**2))


                    hFakes_pt.SetBinContent(self.ptBinningS.index(p)+1,fake)
                    h2Fakes_sign.SetBinContent(self.etaBinningS.index(e)+1, self.ptBinningS.index(p)+1,fake)
                    hFakes_pt.SetBinError(self.ptBinningS.index(p)+1,fake_err)
                    h2Fakes_sign.SetBinError(self.etaBinningS.index(e)+1, self.ptBinningS.index(p)+1,fake_err)

                    #debug lines ----
                    # if(kind == 'fake') :
                    #     filee=ROOT.TFile.Open(self.outdir+'/bkg_plots_MOD'+self.nameSuff+".root")
                    #     histoo = filee.Get('c_comparison_'+s+'_'+e).GetPrimitive('hFakes_pt_fake_'+s+'_'+e)
                    #     # for p in self.ptBinningS :
                    #     print "debug saved file=",s,e,p, histoo.GetBinContent(self.ptBinningS.index(p)+1), "from dict=", fake#hFakes[s+e].GetBinContent(self.ptBinningS.index(p)+1)
                    #             # print 'hFakes_pt_fake_'+s+'_'+e, "...........VS.......", fakedict[s+e].GetName(), fakedict[s+e].GetTitle()
                    #     filee.Close()
                     #end of debug ----

                if kind == 'fake' or kind == 'fakeMC' :
                    hEWSF_Fit["EWSF_chi2"+s+e] = hEWSF_chi2_pt
                    hEWSF_Fit["EWSF_sig"+s+e] = hEWSF_sig_pt
                    hEWSF_Fit["EWSF_bkg"+s+e] = hEWSF_bkg_pt
                    hEWSF_Fit["EWSF_iso"+s+e] = hEWSF_iso_pt
                    hEWSF_Fit["EWSF_Mt"+s+e] = hEWSF_Mt_pt

                    hEWSF_Fit["region_Cdata"+s+e] = hFakes_pt_Cdata
                    hEWSF_Fit["region_Adata"+s+e] = hFakes_pt_Adata
                    hEWSF_Fit["region_Cweak"+s+e] = hFakes_pt_Cweak
                    hEWSF_Fit["region_Aweak"+s+e] = hFakes_pt_Aweak
                    hEWSF_Fit["region_ratioCA"+s+e] = hFakes_pt_ratioCA
                    # print "EWSF_count"+s+e





                hFakes[s+e] = hFakes_pt

                if parabolaFit and kind=='prompt':
                    # fitFake = ROOT.TF1("fitFake", 'pol2',0,100,3)
                    # fitFake.SetParameters(0.5,0.1,-0.1)
                    # fitFake.SetParNames("offset","slope",'2deg')

                    # fitFake = ROOT.TF1("fitFake", "[0]*1/(1+[1]*exp(-[2]*x))",0,100,3)
                    # fitFake.SetParameters(1,1,1)
                    # fitFake.SetParNames("offset","slope",'2deg')

                    # fitFake = ROOT.TF1("fitFake", "[0]*erf([1]*(x-30)+[2])",0,100,3)
                    fitFake = ROOT.TF1("fitFake", "[0]*erf([1]*(x)+[2])",0,100,3)
                    fitFake.SetParameters(1,0.1,-3)
                    # fitFake.SetParameters(1,1,0)
                    fitFake.SetParNames("offset","slope",'2deg')

                    def evaluate_erf_error(ERFfitResult, ERFp0,ERFp1, ERFp2) :
                        ntoys = 1000
                        covtoy ={}
                        xvec = np.zeros(len(self.ptBinning)-1)
                        for xx in range(xvec.size) :
                            xvec[xx] = float(self.ptBinning[xx])+float((self.ptBinning[xx+1]-self.ptBinning[xx]))/2
                        yvec = np.zeros((xvec.size,ntoys))
                        parvec=np.zeros(3)
                        parvec[0] = ERFp0
                        parvec[1] = ERFp1
                        parvec[2] = ERFp2
                        covvec =np.zeros((3,3))

                        for xx in range (3) :
                            for yy in range (3) :
                                covvec[xx][yy] = ROOT.TMatrixDRow(ERFfitResult,xx)(yy)

                        def my_erf(x,par) :
                            val = np.zeros(x.size)
                            val = par[0]*erf(par[1]*(x)+par[2])
                            return val

                        for itoy in range(ntoys) :
                            covtoy[itoy] = np.random.multivariate_normal(parvec, covvec)
                            yvec[:,itoy] = my_erf(xvec,covtoy[itoy])
                        sigmavec = np.std(yvec,axis=1)

                        return sigmavec


                else :
                    fitFake = ROOT.TF1("fitFake", 'pol1',0,100,2)
                    # fitFake = ROOT.TF1("fitFake", ROOT.rejline,0,100,2)
                    fitFake.SetParameters(0.5,0.1)
                    fitFake.SetParNames("offset","slope")

                # fitFake = ROOT.TF1("fitFake", 'pol2',30,65,2)
                # fitFake.SetParameters(0.5,0.1,0.1)
                # fitFake.SetParNames("offset","slope","sndDeg")
                # fit_result = hFakes_pt.Fit(fitFake,"Q","",0,120)
                fit_result = hFakes_pt.Fit(fitFake,"QS","",25,65)
                # print "--------------------------------------------------- s,e,", s,e
                # fit_result.Print("V")
                cov = fit_result.GetCovarianceMatrix()
                hFakes[s+e+'offset']=fitFake.GetParameter(0)
                hFakes[s+e+'slope']=fitFake.GetParameter(1)#+0.1*fitFake.GetParameter(1) #systemtatic
                hFakes[s+e+'offsetErr']=fitFake.GetParError(0)
                hFakes[s+e+'slopeErr']=fitFake.GetParError(1)
                hFakes[s+e+'offset*slope'] = ROOT.TMatrixDRow(cov,0)(1) #covarinace
                hFakes[s+e+'chi2red'] =fitFake.GetChisquare()/fitFake.GetNDF()

                if parabolaFit and kind=='prompt':
                    hFakes[s+e+'2deg']=fitFake.GetParameter(2)
                    hFakes[s+e+'2degErr']=fitFake.GetParError(2)
                    hFakes[s+e+'offset*2deg'] = ROOT.TMatrixDRow(cov,0)(2)
                    hFakes[s+e+'slope*2deg'] = ROOT.TMatrixDRow(cov,1)(2)
                    hFakes[s+e+'fitRes'] = cov
                    hFakes[s+e+'sigmaERFvec'] = evaluate_erf_error(ERFfitResult=cov,ERFp0=hFakes[s+e+'offset'],ERFp1=hFakes[s+e+'slope'],ERFp2=hFakes[s+e+'2deg'])

                else:  #only to have a coherent filling
                    hFakes[s+e+'2deg']=0
                    hFakes[s+e+'2degErr']=0
                    hFakes[s+e+'offset*2deg'] = 0
                    hFakes[s+e+'slope*2deg'] = 0
                    hFakes[s+e+'fitRes'] = 0
                    hFakes[s+e+'sigmaERFvec'] = 0
                if(fitFake.GetNDF()>0) :
                    hTempl_chi2.SetBinContent(self.etaBinningS.index(e)+1,fitFake.GetChisquare()/fitFake.GetNDF())
                    hTempl_chi2.SetBinError(self.etaBinningS.index(e)+1,math.sqrt(2*fitFake.GetNDF())/fitFake.GetNDF())
                    hTempl_slope.SetBinContent(self.etaBinningS.index(e)+1,fitFake.GetParameter(1))
                    hTempl_slope.SetBinError(self.etaBinningS.index(e)+1,fitFake.GetParError(1))
                    hTempl_offset.SetBinContent(self.etaBinningS.index(e)+1,fitFake.GetParameter(0))
                    hTempl_offset.SetBinError(self.etaBinningS.index(e)+1,fitFake.GetParError(0))
                    if parabolaFit  and kind=='prompt':
                        hTempl_2deg.SetBinContent(self.etaBinningS.index(e)+1,fitFake.GetParameter(2))
                        hTempl_2deg.SetBinError(self.etaBinningS.index(e)+1,fitFake.GetParError(2))
                    else : #only to have a coherent filling
                        hTempl_2deg.SetBinContent(self.etaBinningS.index(e)+1,0)
                        hTempl_2deg.SetBinError(self.etaBinningS.index(e)+1,0)

            h2Fakes[s] = h2Fakes_sign
            if kind == 'fake' or kind == 'fakeMC' :

                hEWSF_Fit["EWSF_chi2"+s] = hEWSF_chi2
                hEWSF_Fit["EWSF_sig"+s] = hEWSF_sig
                hEWSF_Fit["EWSF_bkg"+s] = hEWSF_bkg
            hTempl_Fit["Templ_chi2"+s] = hTempl_chi2
            hTempl_Fit["Templ_slop"+s] = hTempl_slope # the index of the dict is not a typo, it is to avoid error in continue during writing.
            hTempl_Fit["Templ_offse"+s] = hTempl_offset # the index of the dict is not a typo, it is to avoid error in continue during writing.
            if parabolaFit : #and kind=='prompt':
                hTempl_Fit["Templ_2de"+s] = hTempl_2deg # the index of the dict is not a typo, it is to avoid error in continue during writing.
        hFakes.update(h2Fakes)
        hFakes.update(hTempl_Fit)
        hFakes.update(hEWSF_Fit)

        if correlatedFit :
            parCorFit = self.correlatedFitter(hFakes)
            hFakes.update(parCorFit)

        return hFakes

    def bkg_template(self, kind, fakedict, promptdict, hdict, fit = False, tightcut = 0.15, loosecut=40, varname = 'pfRelIso04_all_corrected_MET_nom_mt', parabolaFit=False,correlatedFit = False) :
        # self.kind = kind
        # self.fakedict = fakedict
        # self.promptdict = promptdict
        # self.hdict = hdict
        # self.fit = fit
        # self.varname = varname
        # self.loosecut = loosecut
        # self.tightcut = tightcut
        # self.parabolaFit = parabolaFit
        # self.correlatedFit = correlatedFit

        # print "loosecut template", loosecut

        kindDict = {
            'fake' : 'Data',
            'validation' : 'QCD',
            'fakeMC' : 'DataLike' ,
            'prompt' : 'WToMuNu',
            'EWKbkg' : 'EWKbkg',
        }

        datakind = kindDict[kind]

        htempl = {}
        h2templ = {}
        # systDict = bkg_systematics


        #LINES MOVED IN separate fuction (correlatedFitter) >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # if correlatedFit :
        #    file_dict = {}
        #    histo_fake_dict = {}
        #    systList = []
        # #    bin4corFit = [30,33,35,37,39,41,43,45,47,50,53,56,59,62,65]
        #    bin4corFit = [30,32,34,36,38,40,42,44,47,50,53,56,59,62,65]
        #    binChange = 7 # bin 1-8: merge 2 pt bins, bin 8-end: merge 3 bins.
        # #    bin4corFit = [30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65]
        # #    bin4corFit = [30,32,34,36,38,40,42,44,45]

        #    bin4corFitS = ['{:.2g}'.format(x) for x in bin4corFit[:-1]]

        #    for sKind, sList in systDict.iteritems():
        #        for sName in sList :
        #             systList.append(sName)
        #             systdir = self.outdir.replace("bkg_nom","bkg_"+sName+'/')
        #             file_dict[sName]=ROOT.TFile.Open(systdir+'bkg_plots'+self.nameSuff+".root")

        #             for s in self.signList :
        #                 for e in self.etaBinningS :
        #                     # print systdir+"bkg_plots"+self.nameSuff+".root"
        #                     # print file_dict[sName], sName
        #                     histo_fake_dict[sName+s+e] = file_dict[sName].Get('c_comparison_'+s+'_'+e).GetPrimitive('hFakes_pt_fake_'+s+'_'+e)

        #                     temp_histREB = ROOT.TH1F(histo_fake_dict[sName+s+e].GetName()+'_reb',histo_fake_dict[sName+s+e].GetName()+'_reb',len(bin4corFit)-1,array('d',bin4corFit))
        #                     for r in range(1,len(bin4corFit)) :
        #                         if r<binChange :
        #                             valueBinRebinned = (histo_fake_dict[sName+s+e].GetBinContent(2*r)+histo_fake_dict[sName+s+e].GetBinContent(2*r-1))/2
        #                             valueBinRebinnedErr = (histo_fake_dict[sName+s+e].GetBinError(2*r)+histo_fake_dict[sName+s+e].GetBinError(2*r-1))/2
        #                         else :
        #                             valueBinRebinned = (histo_fake_dict[sName+s+e].GetBinContent(3*r-binChange)+histo_fake_dict[sName+s+e].GetBinContent(3*r-binChange-1)+histo_fake_dict[sName+s+e].GetBinContent(3*r-binChange-2))/3 #the not-simplified value of the bin number is: 2*N+3*(r-N), -1, -2.
        #                             valueBinRebinnedErr = (histo_fake_dict[sName+s+e].GetBinError(3*r-binChange)+histo_fake_dict[sName+s+e].GetBinError(3*r-binChange-1)+histo_fake_dict[sName+s+e].GetBinError(3*r-binChange-2))/3 #the not-simplified value of the bin number is: 2*N+3*(r-N), -1, -2.

        #                         temp_histREB.SetBinContent(r,valueBinRebinned)
        #                         temp_histREB.SetBinError(r,valueBinRebinnedErr)
        #                     temp_histREB.AddDirectory(False)
        #                     histo_fake_dict[sName+s+e+'reb'] = temp_histREB.Clone()
        #                     #rebinning for minuit
        #                     # histo_fake_dict[sName+s+e+'reb'] = histo_fake_dict[sName+s+e].Rebin(len(bin4corFit)-1,histo_fake_dict[sName+s+e].GetName()+'_reb', array('d',bin4corFit))
        #                     # histo_fake_dict[sName+s+e+'reb'].AddDirectory(False)
        #                     # temp_histREB = histo_fake_dict[sName+s+e].Rebin(len(bin4corFit)-1,'temp_histREB', array('d',bin4corFit))
        #                     # temp_histREB.AddDirectory(False)
        #                     # histo_fake_dict[sName+s+e+'reb'] = temp_histREB.Clone()
        #                     # print "number of bins",e,s, histo_fake_dict[sName+s+e+'reb'].GetNbinsX()
        #                     # for i in range(histo_fake_dict[sName+s+e+'reb'].GetNbinsX()) :
        #                     #     print "bin value=", e, s, sName, i, histo_fake_dict[sName+s+e+'reb'].GetBinCenter(i+1),histo_fake_dict[sName+s+e+'reb'].GetBinContent(i+1)

        #             file_dict[sName].Close()
        #     #nominal
        #    # file_dict['nom']=ROOT.TFile.Open(self.outdir+'/bkg_plots_MOD'+self.nameSuff+".root")
        #    # for s in self.signList :
        #    #              for e in self.etaBinningS :
        #    #                  histo_fake_dict['nom'+s+e] = file_dict['nom'].Get('c_comparison_'+s+'_'+e).GetPrimitive('hFakes_pt_fake_'+s+'_'+e)
        #    #                  # histo_fake_dict['nom'+s+e] = file_dict['nom'].Get('c_comparison_'+s+'_'+e).GetPrimitive('hFakes_pt_fake_'+s+'_'+e)
        #    #                  # histoo = file_dict['nom'].Get('c_comparison_'+s+'_'+e).GetPrimitive('hFakes_pt_fake_'+s+'_'+e)
        #    #                  for p in self.ptBinningS :
        #    #                      # print  self.ptBinningS
        #    #                      print "debug saved file=",s,e,p, histo_fake_dict['nom'+s+e].GetBinContent(self.ptBinningS.index(p)+1), "from dict=", fakedict[s+e].GetBinContent(self.ptBinningS.index(p)+1)
        #    #                      # print 'hFakes_pt_fake_'+s+'_'+e, "...........VS.......", fakedict[s+e].GetName(), fakedict[s+e].GetTitle()
        #    # file_dict['nom'].Close()

            #END OF MOVED IN separate fuction (correlatedFitter) >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


        # print "DEBUGDIO 1"
        for s in self.signList :
            h2templ_sign = ROOT.TH2F("h2templ_{kind}_{sign}".format(kind=kind, sign=s),"h2templ_{kind}_{sign}".format(kind=kind, sign=s),len(self.etaBinning)-1, array('f',self.etaBinning), len(self.ptBinning)-1, array('f',self.ptBinning) )
            for e in self.etaBinningS :

                #MOVED THESE LINES IN differential_fakerate()-------------------------
                # def evaluate_erf_error(fitResult) :
                #     ntoys = 1000
                #     covtoy ={}
                #     xvec = np.zeros(len(self.ptBinning)-1)
                #     for xx in range(xvec.size) :
                #         xvec[xx] = float(self.ptBinning[xx])+float((self.ptBinning[xx+1]-self.ptBinning[xx]))/2
                #     yvec = np.zeros((xvec.size,ntoys))
                #     parvec=np.zeros(3)
                #     parvec[0] = promptdict[s+e+'offset']
                #     parvec[1] = promptdict[s+e+'slope']
                #     parvec[2] = promptdict[s+e+'2deg']
                #     covvec =np.zeros((3,3))

                #     for xx in range (3) :
                #         for yy in range (3) :
                #             covvec[xx][yy] = ROOT.TMatrixDRow(fitResult,xx)(yy)

                #     def my_erf(x,par) :
                #         val = np.zeros(x.size)
                #         val = par[0]*erf(par[1]*(x)+par[2])
                #         return val

                #     for itoy in range(ntoys) :
                #         covtoy[itoy] = np.random.multivariate_normal(parvec, covvec)
                #         yvec[:,itoy] = my_erf(xvec,covtoy[itoy])
                #     sigmavec = np.std(yvec,axis=1)

                #     return sigmavec

                # if fit and parabolaFit:
                #     sigma_erf_vec = evaluate_erf_error(promptdict[s+e+'fitRes'])
                #END OF MOVED LINES---------------------

                htempl_pt = ROOT.TH1F("htempl_pt_{kind}_{sign}_{eta}".format(kind=kind,sign=s,eta=e),"htempl_pt_{kind}_{sign}_{eta}".format(kind=kind,sign=s,eta=e), len(self.ptBinning)-1, array('f',self.ptBinning) )


                #LINES MOVED IN separate fuction (correlatedFitter) >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                # if correlatedFit: #fit to the fake rate using bin-bin correlation and systemtatics uncertainities
                #     np.set_printoptions(threshold=np.inf)

                #     # err_multiplier = 1/100000#0.0001
                #     err_multiplier=1

                #     dimFit = len(bin4corFitS)
                #     print "fit dimension=",dimFit

                #     #debuglineREB
                #     # dimFit = 15#len(bin4corFitS) #17#len(self.ptBinning)-1

                #     xx_ = np.zeros(dimFit)
                #     yy_ = np.zeros(dimFit)
                #     cov_ = np.zeros(( len(systList)+1,dimFit,dimFit))

                #     #debug lines -----------------------
                #     # covdict = {}
                #     # for syst in  systList :
                #     #     covdict[syst] = np.zeros((dimFit,dimFit))
                #     # covdict['nom'] = np.zeros((dimFit,dimFit))

                #     # histo_fake_dict['nom'+s+e+'reb'] = fakedict[s+e].Rebin(len(bin4corFit)-1,fakedict[s+e].GetName()+'_reb', array('d',bin4corFit))
                #     # histo_fake_dict['nom'+s+e+'reb'] =fakedict[s+e].GetName()+'_reb'

                #     histo_fake_dict['nom'+s+e+'reb'] = ROOT.TH1F(fakedict[s+e].GetName()+'_reb',fakedict[s+e].GetName()+'_reb',len(bin4corFit)-1,array('d',bin4corFit))
                #     for r in range(1,len(bin4corFit)) :
                #         if r<binChange :
                #             valueBinRebinned = (fakedict[s+e].GetBinContent(2*r)+fakedict[s+e].GetBinContent(2*r-1))/2
                #             valueBinRebinnedErr = (fakedict[s+e].GetBinError(2*r)+fakedict[s+e].GetBinError(2*r-1))/2
                #         else :
                #             valueBinRebinned = (fakedict[s+e].GetBinContent(3*r-binChange)+fakedict[s+e].GetBinContent(3*r-binChange-1)+fakedict[s+e].GetBinContent(3*r-binChange-2))/3 #the not-simplified value of the bin number is: 2*N+3*(r-N), -1, -2.
                #             valueBinRebinnedErr = (fakedict[s+e].GetBinError(3*r-binChange)+fakedict[s+e].GetBinError(3*r-binChange-1)+fakedict[s+e].GetBinError(3*r-binChange-2))/3 #the not-simplified value of the bin number is: 2*N+3*(r-N), -1, -2.

                #         histo_fake_dict['nom'+s+e+'reb'].SetBinContent(r,valueBinRebinned)
                #         histo_fake_dict['nom'+s+e+'reb'].SetBinError(r,valueBinRebinnedErr)
                #         print r, valueBinRebinned

                #     #debuglineREB
                #     # histo_fake_dict['nom'+s+e+'reb'] =  fakedict[s+e]


                #     for pp in range(xx_.size) :
                #         # if fakedict[s+e].GetBinCenter(pp+1)>35 and fakedict[s+e].GetBinCenter(pp+1)<45 :
                #         #     print "centro skipped", fakedict[s+e].GetBinCenter(pp+1)
                #         #     continue
                #         jump = 0
                #         # if pp==16 :jump = 16

                #         xx_[pp] = histo_fake_dict['nom'+s+e+'reb'].GetBinCenter(pp+1+jump)
                #         print "bin center=",pp, xx_[pp]
                #         # yy_[pp] = fakedict[s+e+'offset']+xx_[pp]*fakedict[s+e+'slope']
                #         yy_[pp] = histo_fake_dict['nom'+s+e+'reb'].GetBinContent(pp+1+jump)

                #         #debug
                #         # print "FIT,",s,e,pp,", centro=", fakedict[s+e].GetBinCenter(pp+1), ",  fake=", yy_[pp], "variation=", histo_fake_dict["puWeightUp"+s+e].GetBinContent(pp+1) #, histo_fake_dict['nom'+s+e].GetBinContent(pp+1)

                #     for pp in range(xx_.size) : #separate loop because needed xx,yy fully filled
                #         # print "()()()()()()()() entro in pp", pp
                #         jump1=0
                #         # if pp == 16 : jump1 = 16
                #         for p2 in range(xx_.size) :
                #             jump2 = 0
                #             # if p2 == 16 : jump2 = 16
                #             # print "--->>>>>>>>>>--->_>_>_entro in p2", p2
                #             for syst in range(len(systList)+1) :
                #                 # print "entro in syst", syst
                #                 if pp==p2 and syst==len(systList):

                #                     dx_f = (histo_fake_dict['nom'+s+e+'reb'].GetBinWidth(pp+1+jump1))/2
                #                     # erv = fakedict[s+e+'offsetErr']**2+(dx_f**2)*(fakedict[s+e+'slope']**2)+(xx_[pp]**2)*(fakedict[s+e+'slopeErr']**2)+2*xx_[pp]*fakedict[s+e+'offset*slope']
                #                     erv = err_multiplier*histo_fake_dict['nom'+s+e+'reb'].GetBinError(pp+1+jump1)**2
                #                     cov_[syst][pp][p2] = erv
                #                     # covdict['nom'][pp][p2] = erv
                #                 elif syst<len(systList):
                #                     if 'Up' in systList[syst] :#do not use down syst, will be symmetrized with up later
                #                         # if 'puWeight' in systList[syst]:
                #                             systUp =systList[syst]
                #                             systDown =  systUp.replace("Up","Down")

                #                             #debuglineREB
                #                             # histo_fake_dict[systUp+s+e+'reb'] = histo_fake_dict[systUp+s+e]
                #                             # histo_fake_dict[systDown+s+e+'reb'] = histo_fake_dict[systDown+s+e]
                #                             #EODREB

                #                             deltaPP = (abs(yy_[pp]-histo_fake_dict[systUp+s+e+'reb'].GetBinContent(pp+1+jump1))+ abs(yy_[pp]-histo_fake_dict[systDown+s+e+'reb'].GetBinContent(pp+1+jump1)))/2
                #                             deltaP2 = (abs(yy_[p2]-histo_fake_dict[systUp+s+e+'reb'].GetBinContent(p2+1+jump2))+ abs(yy_[p2]-histo_fake_dict[systDown+s+e+'reb'].GetBinContent(p2+1+jump2)))/2
                #                             # erv = (yy_[pp]-histo_fake_dict[systList[syst]+s+e].GetBinContent(pp+1))*(yy_[p2]-histo_fake_dict[systList[syst]+s+e].GetBinContent(p2+1))
                #                             erv = err_multiplier*deltaPP*deltaP2
                #                             # print "riempo, syst, pp, p2", systList[syst], pp, p2, systUp,systDown
                #                             # if 'ID' in systList[syst] : erv = 0
                #                             cov_[syst][pp][p2] = erv
                #                             # covdict[systList[syst]][pp][p2] = erv
                #                             if pp==p2:
                #                                 # print "sign=",s," fake=", yy_[pp], " varied=", systUp, histo_fake_dict[systUp+s+e].GetBinContent(pp+1)
                #                                 debug_notsym = (yy_[pp]-histo_fake_dict[systUp+s+e+'reb'].GetBinContent(pp+1+jump1))**2
                #                                 # debug_erv = fakedict[s+e+'offsetErr']**2+(((fakedict[s+e].GetBinWidth(pp+1))/2)**2)*(fakedict[s+e+'slope']**2)+(xx_[pp]**2)*(fakedict[s+e+'slopeErr']**2)+2*xx_[pp]*fakedict[s+e+'offset*slope']
                #                                 debug_erv=histo_fake_dict['nom'+s+e+'reb'].GetBinError(pp+1+jump1)**2
                #                                 # print "FIT:",p2+35,pp+35,"sig=",s,", err(syst)=", erv, ", err(stat)=", debug_erv,  " ratio(sym) syst/stat=",erv/debug_erv, systList[syst]# " not_sym_erv= ",debug_notsym," ratio(nsy)=", debug_notsym/debug_erv

                #     q0_ = fakedict[s+e+'offset']
                #     p0_ = fakedict[s+e+'slope']
                #     q0Err_ = fakedict[s+e+'offsetErr']
                #     p0Err_ = fakedict[s+e+'slopeErr']
                #     # print "PREPROJJJ---------------------------", cov_.shape
                #     # print cov_
                #     cov_proj = cov_.sum(axis=0) #square sum of syst
                #     # print "MATRIX---------------------------", cov_proj.shape
                #     # print cov_proj
                #     # for pp in range(xx_.size) :

                #     #     xx_[pp] = xx_[pp]-(fakedict[s+e].GetBinCenter(1)-fakedict[s+e].GetBinWidth(1)/2)
                #         # xx_[pp] = xx_[pp]-30
                #         # print "post", xx_[pp]

                #     #uncomment here -----------------------------------
                #     # matt = np.zeros((dimFit,dimFit))
                #     # for syst in  systList :
                #     #     print "rank of", syst,  np.linalg.matrix_rank(covdict[syst])
                #     #     matt = matt+covdict[syst]
                #     # matt = matt + covdict['nom']
                #     # print "rank of all",  np.linalg.matrix_rank(cov_proj), np.linalg.slogdet(cov_proj)
                #     # print "rank of matt", np.linalg.matrix_rank(matt), np.linalg.slogdet(matt)
                #     # # print "eigval and egvec of matt=", np.linalg.eig(matt)
                #     # matt = matt- cov_proj
                #     # # print "debugg", matt
                #     #end of good debug ----------------------------

                #     invCov_ = np.linalg.inv(cov_proj)
                #     minuitDict = self.MinuitLinearFit( yy=yy_, xx=xx_, invCov=invCov_, p0=p0_, q0=q0_,p0Err=p0Err_, q0Err=q0Err_)
                #END OF LINES MOVED IN separate fuction (correlatedFitter) >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


                # print "DEBUGDIO 2"
                for p in self.ptBinningS :
                    # print "NAME:   ", 'templ'+p+'_'+e+'_'+datakind+s+'_'+varname
                    # print "KEY:   ", p+e+s+varname+datakind+'Tot'
                    # print "DEBUGDIO 2.1 ",p+e+s+varname+datakind+'Tot', hdict[p+e+s+varname+datakind+'Tot'].GetNbinsX()
                    htemp = hdict[p+e+s+varname+datakind+'Tot'].Clone('templ'+p+'_'+e+'_'+datakind+s+'_'+varname)
                    # print "DEBUGDIO 2.2", p+e+s+varname+datakind+'Tot'
                    isoMin= htemp.GetYaxis().GetBinCenter(1)-htemp.GetYaxis().GetBinWidth(1)/2
                    binsizeTight = htemp.GetYaxis().GetBinWidth(1)
                    NcutTight=(tightcut-isoMin)/binsizeTight
                    NcutTight = int(NcutTight)

                    mtMin= htemp.GetXaxis().GetBinCenter(1)-htemp.GetXaxis().GetBinWidth(1)/2
                    binsizeLoose = htemp.GetXaxis().GetBinWidth(1)
                    # NcutLoose=(loosecut-mtMin)/binsizeLoose
                    NcutLoose=(self.hardcodeLooseCut-mtMin)/binsizeLoose #hardcode loosecut=40
                    NcutLoose = int(NcutLoose)
                    
                    
                    if self.fastHistos :
                        NcutTight=2
                        NcutLoose=2

                    tightErr = ROOT.Double(0)
                    notTightErr = ROOT.Double(0)
                    # print "cut, l, t, ", NcutLoose,NcutTight
                    Ntight = htemp.ProjectionX("htight",0,NcutTight-1, "e").IntegralAndError(NcutLoose,-1,tightErr)
                    NnotTight = htemp.ProjectionX("hNotTigth",NcutTight,-1, "e").IntegralAndError(NcutLoose,-1,notTightErr)

                    if kind=='fake' or kind=='fakeMC'  : #Data or DataLike
                        pr = 1
                        fr = 0
                        dpr =0
                        dfr =0

                        # print "Ntight,NnotTight",  Ntight, NnotTight

                        if(fit) :
                            # print "DEBUG>>> template", s,e,p, kind
                            xf = fakedict[s+e].GetBinCenter(self.ptBinningS.index(p)+1)
                            xp = promptdict[s+e].GetBinCenter(self.ptBinningS.index(p)+1)
                            fr = fakedict[s+e+'offset']+xf*fakedict[s+e+'slope']
                            # print "standard",s,e,p,", centro=", fakedict[s+e].GetBinCenter(self.ptBinningS.index(p)+1), ", offset=", fakedict[s+e+'offset'], ", slope=", fakedict[s+e+'slope'],", fake=", fr
                            # print "standard",s,e,p, fakedict[s+e].GetBinContent(self.ptBinningS.index(p)+1)
                            pr = promptdict[s+e+'offset']+xp*promptdict[s+e+'slope']
                            dx_p =(promptdict[s+e].GetBinWidth(self.ptBinningS.index(p)+1))/2
                            dx_f = (fakedict[s+e].GetBinWidth(self.ptBinningS.index(p)+1))/2
                            # print "value dfr square= ", fakedict[s+e+'offsetErr']**2+(dx_f**2)*(fakedict[s+e+'slope']**2)+(xf**2)*(fakedict[s+e+'slopeErr']**2)+2*xf*fakedict[s+e+'offset*slope'],
                            # print fakedict[s+e+'slope'],fakedict[s+e+'offset'], fakedict[s+e+'slopeErr'], fakedict[s+e+'offsetErr'],fakedict[s+e+'offset*slope'], xf
                            dfr = math.sqrt(fakedict[s+e+'offsetErr']**2+(dx_f**2)*(fakedict[s+e+'slope']**2)+(xf**2)*(fakedict[s+e+'slopeErr']**2)+2*xf*fakedict[s+e+'offset*slope'])
                            dpr = math.sqrt(promptdict[s+e+'offsetErr']**2+(dx_p**2)*(promptdict[s+e+'slope']**2)+(xp**2)*(promptdict[s+e+'slopeErr']**2)+2*xp*promptdict[s+e+'offset*slope'])
                            
                            # if (p=='30' and correlatedFit==False) :
                                    # print "DEBUG final:",  s,e, fakedict[s+e+'offset'], fakedict[s+e+'slope'], fakedict[s+e+'offsetErr'], fakedict[s+e+'slopeErr'], fakedict[s+e+'offset*slope']

                            if parabolaFit:
                                # fr = fr+(xf)**2*fakedict[s+e+'2deg']
                                # dfr =math.sqrt(dfr**2+(4*fakedict[s+e+'2deg']**2*(xf)**2+4*fakedict[s+e+'2deg']*xf*fakedict[s+e+'slope'])*(dx_f)**2+2*((xf**3)*fakedict[s+e+'slope*2deg']+(xf**2)*fakedict[s+e+'offset*2deg']))


                                #GOOD BLOCK
                                a= promptdict[s+e+'offset']
                                b = promptdict[s+e+'slope']
                                c = promptdict[s+e+'2deg']
                                # da= promptdict[s+e+'offsetErr']
                                # db = promptdict[s+e+'slopeErr']
                                # dc = promptdict[s+e+'2degErr']
                                # dab=  promptdict[s+e+'offset*slope']
                                # dac=  promptdict[s+e+'offset*2deg']
                                # dbc=  promptdict[s+e+'slope*2deg']


                                #parabolic error
                                # pr = pr+(xp)**2*promptdict[s+e+'2deg']
                                # dpr2 = dpr**2+4*(promptdict[s+e+'2degErr']**2)*(xp**4)+(4*promptdict[s+e+'2deg']**2*(xf)**2+4*promptdict[s+e+'2deg']*xp*promptdict[s+e+'slope'])*(dx_f)**2+2*((xp**3)*promptdict[s+e+'slope*2deg']+(xp**2)*promptdict[s+e+'offset*2deg'])

                                #sigmoid error
                                # pr= a*1/(1+b*math.exp(-c*xf))
                                # dpr2 = (math.exp(2*c*xf)*(math.exp(2*c*xf)*da**2+2*math.exp(c*xf)*(a*b*dac*xf-a*dab+b*da**2)+c**2*a**2*b**2*dx_p**2+a**2*b**2*dc**2*xf**2-2*a*(a*dbc-b*dac)*b*xf+a**2*db**2-2*a*b*dab+b**2*da**2))/((math.exp(c*xf)+b)**4)

                                #erf error
                                # xp = xp-30
                                pr= a*erf(b*xp+c)
                                # dpr = sigma_erf_vec[self.ptBinningS.index(p)]*math.sqrt(promptdict[s+e+'chi2red']) #chi2 is to artificially obtain chi2=1
                                dpr = promptdict[s+e+'sigmaERFvec'][self.ptBinningS.index(p)]*math.sqrt(promptdict[s+e+'chi2red'])
                                # print "DEBUG THE MOVING", dpr-dprTry, dpr, dprTry
                                # print "promt rate", pr,
                                # print "val exp", -2*c**2-4*c*b*xp-2*b**2*xp**2, c**2+4*c*b*xp+2*b**2*xp**2, c**2+2*c*b*xp+b**2*xp**2
                                # print "erf", erf(xp*b+c)
                                # print "exp", mpmath.exp(-2*c**2-4*c*b*xp-2*b**2*xp**2), mpmath.exp(c**2+4*c*b*xp+2*b**2*xp**2), mpmath.exp(c**2+2*c*b*xp+b**2*xp**2)


                                # dpr2 = ((4*mpmath.exp(-2*c**2-4*c*b*xp-2*b**2*xp**2)*(mpmath.exp(2*c**2+4*c*b*xp+2*b**2*xp**2)*(math.sqrt(math.pi)/2*erf(xp*b+c))**2*da**2+2*mpmath.exp(c**2+2*c*b*xp+b**2*xp**2)*(math.sqrt(math.pi)/2*erf(xp*b+c))*a*(dab*xp+dac)+a**2*(b**2*dx_p**2+db**2*xp**2+2*dbc*xp+dc**2)))/(math.pi))



                                #GOOD BLOCK
                                # dpr2 = ((4*mpmath.exp(-2*c**2-4*c*b*xp-2*b**2*xp**2)*(mpmath.exp(2*c**2+4*c*b*xp+2*b**2*xp**2)*(math.sqrt(math.pi)/2*erf(xp*b+c))**2*da**2+2*mpmath.exp(c**2+2*c*b*xp+b**2*xp**2)*(math.sqrt(math.pi)/2*erf(xp*b+c))*a*(dab*xp+dac)+a**2*(b**2*dx_p**2+db**2*xp**2+2*dbc*xp+dc**2)))/(math.pi))


                                # if(kind=='fake') :
                                #     print "----------------------------------------------------------"
                                #     print "bin:", e, p, s
                                #     print xp,dx_p, a,b,c,da,db,dc,dab,dac,dbc
                                #     print "pr=", pr, "+/-", math.sqrt(dpr2), ",    nofit values:", promptdict[s].GetBinContent(self.etaBinningS.index(e)+1, self.ptBinningS.index(p)+1), "+/-", promptdict[s].GetBinError(self.etaBinningS.index(e)+1, self.ptBinningS.index(p)+1)
                                #     print "relative errors: fit=",math.sqrt(dpr2)/pr, ",   nofit=",promptdict[s].GetBinError(self.etaBinningS.index(e)+1, self.ptBinningS.index(p)+1)/promptdict[s].GetBinContent(self.etaBinningS.index(e)+1, self.ptBinningS.index(p)+1)



                                # print "3 pezzi",e,p,s, (promptdict[s+e+'offsetErr']**2+(dx_p**2)*(promptdict[s+e+'slope']**2)+(xp**2)*(promptdict[s+e+'slopeErr']**2)+2*xp*promptdict[s+e+'offset*slope']),
                                # print 4*(promptdict[s+e+'2degErr']**2)*(xp**4)+(4*promptdict[s+e+'2deg']**2*(xf)**2+4*promptdict[s+e+'2deg']*xp*promptdict[s+e+'slope'])*(dx_f)**2,
                                # print 2*((xp**3)*promptdict[s+e+'slope*2deg']+(xp**2)*promptdict[s+e+'offset*2deg'])
                                # print "splitted:", fakedict[s+e+'offsetErr']**2+(dx_f**2)*(fakedict[s+e+'slope']**2)+(xf**2)*(fakedict[s+e+'slopeErr']**2),
                                # print 2*xp*promptdict[s+e+'offset*slope']
                                # print 4*(promptdict[s+e+'2degErr']**2)*(xp**4)+(4*promptdict[s+e+'2deg']**2*(xf)**2+4*promptdict[s+e+'2deg']*xp*promptdict[s+e+'slope'])*(dx_f)**2,
                                # print 2*((xp**3)*promptdict[s+e+'slope*2deg']+(xp**2)*promptdict[s+e+'offset*2deg'])

                                #GOOD BLOCK
                                # if  dpr2 < 0:
                                #     dpr =0
                                #     print "WARNING!!!!!, error on prompt rate set to 0, original value=", dpr2, "bin", s,e,p
                                # else :
                                #     dpr = math.sqrt(dpr2)


                                    # print "prompr rate=", pr, dpr, dpr/pr, "signle point unc.", promptdict[s].GetBinContent(self.etaBinningS.index(e)+1, self.ptBinningS.index(p)+1), promptdict[s].GetBinError(self.etaBinningS.index(e)+1, self.ptBinningS.index(p)+1)
                                # dpr =math.sqrt(dpr**2+(4*promptdict[s+e+'2deg']**2*(xp)**2+4*promptdict[s+e+'2deg']*xp*promptdict[s+e+'slope'])*(dx_f)**2+2*((xp**3)*promptdict[s+e+'slope*2deg']+(xp**2)*promptdict[s+e+'offset*2deg']))

                                # pr = promptdict[s].GetBinContent(self.etaBinningS.index(e)+1, self.ptBinningS.index(p)+1)
                                # dpr = promptdict[s].GetBinError(self.etaBinningS.index(e)+1, self.ptBinningS.index(p)+1)

                            if(correlatedFit) : #fit to the fake rate using bin-bin correlation and systemtatics uncertainities
                                fr = fakedict[s+e+'offset'+'Minuit']+xf*fakedict[s+e+'slope'+'Minuit']
                                dfr = math.sqrt(fakedict[s+e+'offset'+'Minuit'+'Err']**2+(dx_f**2)*(fakedict[s+e+'slope'+'Minuit']**2)+(xf**2)*(fakedict[s+e+'slope'+'Minuit'+'Err']**2)+2*xf*fakedict[s+e+'offset*slope'+'Minuit'])
                                # print "fr, dfr", fr, dfr
                                # if (p=='30') :
                                    # print "DEBUG final:",  s,e, fakedict[s+e+'offset'+'Minuit'], fakedict[s+e+'slope'+'Minuit'], fakedict[s+e+'offsetMinuitErr'], fakedict[s+e+'slopeMinuitErr'], fakedict[s+e+'offset*slope'+'Minuit']


                            if pr>1:
                                print "WARNING!!!!!!, pr>1", pr, fr, "datakind=",kind, ", with eta, pt, sign =", e, p, s,
                                print ", not fitted value=", promptdict[s].GetBinContent(self.etaBinningS.index(e)+1, self.ptBinningS.index(p)+1)
                                pr = 1
                            if fr>1 :
                                print "WARNING!!!!!!, fr>1,", pr, fr, "datakind=",kind, ", with eta, pt, sign =", e, p, s,
                                print ", not fitted value=", fakedict[s].GetBinContent(self.etaBinningS.index(e)+1, self.ptBinningS.index(p)+1)
                                fr = 0

                            # print "debug template", s, e, "fr=", fr, "pr=", pr
                        else :
                            fr = fakedict[s].GetBinContent(self.etaBinningS.index(e)+1, self.ptBinningS.index(p)+1)
                            pr = promptdict[s].GetBinContent(self.etaBinningS.index(e)+1, self.ptBinningS.index(p)+1)
                            dfr = fakedict[s].GetBinError(self.etaBinningS.index(e)+1, self.ptBinningS.index(p)+1)
                            dpr = promptdict[s].GetBinError(self.etaBinningS.index(e)+1, self.ptBinningS.index(p)+1)
                            if pr==0 and fr==0 :
                                print "WARNING!!!!!!, pr=fr=0, with eta, pt, sign =", e, p, s
                                fr = 0
                                pr = 1
                        
                        # fr=0.5
                        # dfr=0
                        # notTightErr=0
                        # tightErr=0
                        # dfr=0
                        # dpr=0
                        scaleTight = -fr*(1-pr)/(pr-fr)
                        scaleNotTight = fr*pr/(pr-fr)
                        # scaleTightErr = math.sqrt((pr**4)*(dfr**2)-2*(pr**3)*(dfr**2)+(pr**2)*(dfr**2)+(fr**2)*((fr-1)**2)*(dpr**2))/((pr-fr)**2)

                        # scaleTightErr = math.sqrt((((fr**4)-2*(fr**3)+(fr**2))*(dpr**2)+(pr**2)*(dfr**2)*(pr-1)**2)/((pr-fr)**4))
                        # scaleNotTightErr = math.sqrt(((pr**4)*(dfr**2)+(fr**4)*(dpr**2))/((pr-fr)**4))
                        NQCD=Ntight*scaleTight+NnotTight*scaleNotTight
                        # NQCDErr = math.sqrt((scaleTight**2)*(tightErr**2)+(scaleTightErr**2)*(Ntight**2)+(scaleNotTight**2)*(notTightErr**2)+(scaleNotTightErr**2)*(NnotTight**2)   ) #no va bene perche propago separatamente l'errore sulle due scale quando sono invece correlate (sono le stesse quantita)
                        # NQCDErr= ((fr**4*dpr**2*(NnotTight+Ntight)**2-2*fr**3*dpr**2*(NnotTight+Ntight)*Ntight+fr**2*(pr**2*dfr**2*(NnotTight+Ntight)-pr*dfr**2*Ntight+dpr**2*Ntight**2)-2*fr*pr**2*(pr*(NnotTight+Ntight)-Ntight)*dfr**2+pr**3*(pr*(NnotTight+Ntight)-Ntight)*dfr**2)/((fr-pr)**4))
                        # NQCDErr = NQCDErr+(scaleTight**2)*(tightErr**2)+(scaleNotTight**2)*(notTightErr**2)
                        NQCDErr = (fr**4*(dpr**2*Ntight**2+2*NnotTight*dpr**2*Ntight+NnotTight**2*dpr**2+notTightErr**2*pr**2+tightErr**2*(pr-1)**2)-2*fr**(3)*(dpr**2*Ntight**2+NnotTight*dpr**2*Ntight+(notTightErr**2*pr**2+tightErr**2*(pr-1)**2)*pr)+fr**2*(dpr**2*Ntight**2+(notTightErr**2*pr**2+tightErr**2*(pr-1)**2)*pr**2)+dfr**2*pr**2*((pr-1)*Ntight+NnotTight*pr)**2)/((fr-pr)**4)
                        NQCDErr = math.sqrt(NQCDErr)
                        # if correlatedFit:
                            # # print "def ERR=", NQCDErr, "def val=", NQCD
                            # print "DEBUG FR", "bin=",e,s,p,NQCD, "errors=", NQCDErr/NQCD, dpr/pr, dfr/fr, tightErr/Ntight, notTightErr/NnotTight
                        
                        NQCDErr_COVMAT=True #completely equivalent to the explicit probagation (cross-check done!)
                        if NQCDErr_COVMAT and correlatedFit :
                            def evaluate_NQCD_error(fr,pr,nt,nnt, dfr, dpr,dnt,dnnt) :
                                ntoys = 1000
                                covtoy ={}
                                yvec = nyvec = np.zeros((ntoys))
                                parvec=np.zeros(4)
                                parvec[0] = fr
                                parvec[1] = pr
                                parvec[2] = nt
                                parvec[3] = nnt
                                
                                covvec =np.zeros((4,4))

                                covvec[0][0] = dfr**2
                                covvec[1][1] = dpr**2
                                covvec[2][2] = dnt**2
                                covvec[3][3] = dnnt**2
                                # print "NQCD inside=", nt*(-fr*(1-pr)/(pr-fr))+nnt*fr*pr/(pr-fr)
                               
                                def my_NQCD(par) :
                                    val = par[2]*(-par[0]*(1-par[1])/(par[1]-par[0]))+par[3]*par[0]*par[1]/(par[1]-par[0])
                                    return val

                                for itoy in range(ntoys) :
                                    covtoy[itoy] = np.random.multivariate_normal(parvec, covvec)
                                    yvec[itoy] = my_NQCD(covtoy[itoy])
                                sigmavec = np.std(yvec)
                                return sigmavec
                                
                            # print "debug for ext=",        fr,pr,Ntight,NnotTight, dfr, dpr,tightErr,notTightErr
                            NQCDErr_covmat = evaluate_NQCD_error(fr=fr,pr=pr,nt=Ntight,nnt=NnotTight, dfr=dfr, dpr=dpr,dnt=tightErr,dnnt=notTightErr)
                            
                            # print "debug NQCDerr=", s, p, NQCDErr, NQCDErr_covmat, ", cov/def_ratio=",NQCDErr_covmat/NQCDErr
                            # NQCDErr_COVMAT=False

                        
                        # print "SCALE:>>>>>>>>>> bin=",e,p,s, ", errore tot", NQCDErr, ", errore relativo=", NQCDErr/NQCD, ", tightErr=",tightErr/Ntight, ", notTightErr=", notTightErr/NnotTight, ", scaleTightErr=", scaleTightErr/scaleTight, ", scaleNotTightErr=",scaleNotTightErr/scaleNotTight
                        # print "spaccato (scaletight err):", dfr/fr, fr,dpr/pr, pr
                        # print "bin=",e,p,s, ", errore ",scaleTightErr, dpr,fr,Ntight,scaleTight

                        # print "value of template:", NQCD, "+/-", NQCDErr, ",  errore relativo=", NQCDErr/NQCD
                        # print "value of N tight:", Ntight, "+/-", tightErr, ",  errore relativo=", tightErr/Ntight
                        # print "value of scale tight:", scaleTight, "+/-", scaleTightErr, ",  errore relativo=", scaleTightErr/scaleTight
                        # print "value of N NOT tight:", NnotTight, "+/-", notTightErr, ",  errore relativo=", notTightErr/NnotTight
                        # print "value of scale NOT tight:", scaleNotTight, "+/-", scaleNotTightErr, ",  errore relativo=", scaleNotTightErr/scaleNotTight

                    else :#if kind == "prompt" or kind=="validation" or kind=='EWKbkg' :
                        # print "prompt and fake rate not applied"
                        NQCD=Ntight
                        NQCDErr = tightErr
                    # if(p=='30' and s=='Plus' and e=='0') : print "NQCD", NQCD, p,s,e, datakind
                    htempl_pt.SetBinContent(self.ptBinningS.index(p)+1,NQCD)
                    # print "NQCD", NQCD, "kind=", kind,"---not tight=", NnotTight, "tight=", Ntight
                    h2templ_sign.SetBinContent(self.etaBinningS.index(e)+1, self.ptBinningS.index(p)+1,NQCD)
                    htempl_pt.SetBinError(self.ptBinningS.index(p)+1,NQCDErr)
                    # print "PROBLEMA: ERRORE NON ASSEGNATO", NQCDErr
                    ERRBIS = NQCDErr #error solving without any sense
                    h2templ_sign.SetBinError(self.etaBinningS.index(e)+1, self.ptBinningS.index(p)+1,ERRBIS)

                h2templ[s+e] = htempl_pt

            htempl[s] = h2templ_sign

        htempl.update(h2templ)
        # print "inside---------------------------", htempl

        return htempl


    def dict2histConverter(self,fakedict,promptdict,hdict, minimal=False, parabolaFit=True,correlatedFit=True) :
        # self.fakedict = fakedict
        # self.promptdict = promptdict
        # self.hdict = hdict
        # self.minimal = minimal
        # self.parabolaFit = parabolaFit
        # self.correlatedFit = correlatedFit

        outdict = {}

        if not minimal :
            for e in self.etaBinningS :
                for s in self.signList :
                    outdict[s+e+'fake'] = fakedict[s+e]
                    outdict[s+e+'prompt'] = promptdict[s+e]
                    if self.etaBinningS.index(e)==0 :
                            outdict[s+'fake'] = fakedict[s]
                            outdict[s+'prompt'] = promptdict[s]
                    for p in self.ptBinningS :
                        for v,name in map(None,self.varList,self.varName) :
                            outdict[p+e+s+v+'Data'] = hdict[p+e+s+v+'Data'+'Tot']#add also histograms of data binned in pt and eta to produce template
            if parabolaFit : #error of the prompt already evaluated using covariance matrix
                outdict['prompt'+'sigmaERFvec'] = ROOT.TH3D('prompt_sigmaERFvec','prompt_sigmaERFvec',len(self.signList),array('f',[0,1,2]),len(self.etaBinning)-1,array('f',self.etaBinning),len(self.ptBinning)-1,array('f',self.ptBinning))
                for s in self.signList :
                        for e in self.etaBinningS :
                            for p in self.ptBinningS :
                                outdict['prompt'+'sigmaERFvec'].SetBinContent(self.signList.index(s)+1,self.etaBinningS.index(e)+1,self.ptBinningS.index(p)+1, promptdict[s+e+'sigmaERFvec'][self.ptBinningS.index(p)])

        if parabolaFit :
            nameDict = {
                'prompt' : ['offset','slope','2deg', 'offset*slope', 'offset*2deg','slope*2deg', 'chi2red'],
                'fake'   : ['offset','slope','offset*slope']
                }
        else :
            nameDict = {
                'prompt' : ['offset','slope','offset*slope'],
                'fake'   : ['offset','slope','offset*slope']
                }

        dictDict = {
            'prompt' :  promptdict,
            'fake' : fakedict
            }

        #book and fill the histos
        for kind, par in nameDict.iteritems() :
            for pp in par :
                if correlatedFit and kind=='fake' :
                    pint = pp+'Minuit'
                else :
                    pint = pp
                outdict[kind+pp]= ROOT.TH2D(kind+'_'+pp,kind+'_'+pp,len(self.signList),array('f',[0,1,2]),len(self.etaBinning)-1,array('f',self.etaBinning))
                for s in self.signList :
                     for e in self.etaBinningS :
                        #  print s,e,kind,pint, dictDict[kind][s+e+pint]
                         outdict[kind+pp].SetBinContent(self.signList.index(s)+1,self.etaBinningS.index(e)+1,dictDict[kind][s+e+pint])
                        #  print s,e,kind,pint,outdict[kind+pint].GetBinContent(self.signList.index(s)+1,self.etaBinningS.index(e)+1),
                         if pp == 'offset' or pp=='slope' or pp=='2deg' :
                            outdict[kind+pp].SetBinError(self.signList.index(s)+1,self.etaBinningS.index(e)+1,dictDict[kind][s+e+pint+'Err'])

        return outdict


    def hist2dictConverter(self,kind, outDir,parabolaFit=True,minimal=True, syst='nom') :
        # self.parabolaFit = parabolaFit
        # self.kind = kind #available kind = fake, prompt, histo
        # self.minimal=minimal
        outdict = {}
        inputfile=ROOT.TFile.Open(outDir+"/bkg_"+syst+"/bkg_parameters_file"+self.corrFitSuff+".root")

        if parabolaFit :
            nameDict = {
                'prompt' : ['offset','slope','2deg', 'offset*slope', 'offset*2deg','slope*2deg', 'chi2red'],
                'fake'   : ['offset','slope','offset*slope']
                }
        else :
            nameDict = {
                'prompt' : ['offset','slope','offset*slope'],
                'fake'   : ['offset','slope','offset*slope']
                }

        if kind=="histo" :
            for p in self.ptBinningS :
                for e in self.etaBinningS :
                    for s in self.signList :
                        for v,name in map(None,self.varList,self.varName) :
                            outdict[p+e+s+v+'Data'+'Tot'] = inputfile.Get(p+'_'+e+'_Data_'+s+'_'+name+'_Tot')
                            # Htemp = inputfile.Get(p+'_'+e+'_Data_'+s+'_'+name+'_Tot')
                            # outdict[p+e+s+v+'Data'+'Tot'] = Htemp.Clone(Htemp.GetName())
                            
        else :
            for par in nameDict[kind] :
                histotemp = inputfile.Get(kind+'_'+par)
                for s in self.signList :
                     for e in self.etaBinningS :
                         outdict[s+e+par] = histotemp.GetBinContent(self.signList.index(s)+1,self.etaBinningS.index(e)+1)
                        #  print "reading point ",kind,  s, e, par, outdict[s+e+par], syst
                         if par == 'offset' or par=='slope' or par=='2deg' :
                            outdict[s+e+par+'Err'] = histotemp.GetBinError(self.signList.index(s)+1,self.etaBinningS.index(e)+1)
                            # print "reading point ", kind, s, e, par, 'err', outdict[s+e+par+'Err'], syst
            if not minimal :
                for s in self.signList :
                     outdict[s] = inputfile.Get('h2Fakes_'+kind+'_'+s)
                    #  Htemp =  inputfile.Get('h2Fakes_'+kind+'_'+s)
                    #  outdict[s] = Htemp.Clone(Htemp.GetName())
                     
                    
                     for e in self.etaBinningS :
                          outdict[s+e] = inputfile.Get('hFakes_pt_'+kind+'_'+s+'_'+e)
                        #  Htemp = inputfile.Get('hFakes_pt_'+kind+'_'+s+'_'+e)
                        #  outdict[s+e] = Htemp.Clone(Htemp.GetName())
                        #  if s=='Plus' and e=='2.3' :
                        #     print "debug histos=", kind, s, e,
                        #     print outdict[s+e].GetNbinsX()
                        #     print outdict[s+e]
                if kind=='prompt':
                    histotemp = inputfile.Get(kind+'_'+'sigmaERFvec')
                    for s in self.signList :
                            for e in self.etaBinningS :
                                sigmaERFvec = []
                                for p in self.ptBinningS :
                                    sigmaERFvec.append(histotemp.GetBinContent(self.signList.index(s)+1,self.etaBinningS.index(e)+1,self.ptBinningS.index(p)+1))
                                outdict[s+e+'sigmaERFvec'] = sigmaERFvec
        # if(kind=='fake') :
        #     print "inside", 
        #     print outdict['Plus2.3']
        return outdict



    def integrated_preliminary(self) :

        # print "getting histos"
        histoDict = {}
        for s in self.signList :
            for v,name in map(None,self.varList,self.varName) :
                for f,rootFile in map(None,self.sampleList,self.rootFiles) :
                    if(f!='DataLike') :
                        for r in self.regionList :
                            if(r!='Tot') :
                                # print "file", f, rootFile
                                # print "Get histo:", 'bkg_'+r+s+'/nom/bkgSel_'+v
                                # print "key=",s+v+f+r
                                histoDict[s+v+f+r] =  rootFile.Get('bkg_'+r+s+'/nom/bkgSel_'+v)
                                # print histoDict[s+v+f+r].GetName()
                                if(f!='Data') : histoDict[s+v+f+r].Scale(self.norm)
                            else:
                                # print "clone histo:", f+'_'+s+'_'+name+'_Tot'
                                histoDict[s+v+f+r] = histoDict[s+v+f+'Sideband'].Clone(f+'_'+s+'_'+name+'_Tot')
                                for rr in self.regionList :
                                    if (rr =="Sideband" or rr=="Tot") : continue
                                    # print "Added histo:", histoDict[s+v+f+rr].GetName()
                                    # print "key=",s+v+f+r
                                    # print "key added=",s+v+f+rr
                                    histoDict[s+v+f+r].Add(histoDict[s+v+f+rr])

                    else :
                        # print "cloned (datalike) histo:", 'DataLike_'+s+'_'+name+'_Tot'
                        # print "key=",s+v+f+'Tot'
                        histoDict[s+v+f+'Tot']= histoDict[s+v+'WToMuNuTot'].Clone('DataLike_'+s+'_'+name+'_Tot')
                        for ff in self.sampleList :
                            if (ff =="WToMuNu" or ff=="Data" or ff=="DataLike"):  continue
                            # print "Added (data like) histo:", histoDict[s+v+ff+'Tot'].GetName()
                            # print "key summed=",s+v+ff+'Tot'
                            histoDict[s+v+f+'Tot'].Add(histoDict[s+v+ff+'Tot'])
                # print "======================================================================="

        # print histos
        # print "ratios (integrated, preliminary)"
        ratios = []
        for s in self.signList :
            for v,name in map(None,self.varList,self.varName) :
                for f in self.sampleList :
                    # print 'ratio_'+histoDict[s+v+f+'Tot'].GetName()
                    if 'relIso' in name : cutvalue =  self.tightCut #self.relisoCUT
                    else : cutvalue = self.isoCUT
                    ratios.append(self.ratio_2Dto1D(histoDict[s+v+f+'Tot'],cutvalue,'ratio_'+histoDict[s+v+f+'Tot'].GetName()))

        output = ROOT.TFile(self.outdir+"/bkg_integrated_preliminary"+self.nameSuff+".root","recreate")
        for h in range(len(ratios)):
            ratios[h].Write()



    def differential_preliminary(self, fakerate = False, correlatedFit=False,produce_ext_output=False) :
        # print "loosecut preliminary", self.looseCut
        # self.fakerate = fakerate #if true calculate the fakerate in bin of eta, pt
        # self.correlatedFit=correlatedFit
        # self.produce_ext_output =produce_ext_output

        print "getting histos..."
        histoDict = {}
        mtDict = {}
        PVDict = {}

        for p in self.ptBinningS :
            for e in self.etaBinningS :
                for s in self.signList :
                    for v,name in map(None,self.varList,self.varName) :
                        PVCond = bool(self.ptBinningS.index(p)==0 and self.etaBinningS.index(e)==0 and self.varList.index(v)==0)
                        MtCond = bool(self.ptBinningS.index(p)==0 and self.varList.index(v)==0)
                        for f,rootFile in map(None,self.sampleList,self.rootFiles) :
                            if(f!='DataLike') :
                                for r in self.regionList :
                                    # print "DEBUG>>>>>: p,e,s,v,f",p,e,s,v,f
                                    if(r!='Tot') :
                                        # print "file", f, rootFile
                                        # print "Get histo:" 'bkg_'+r+s+'/nom/bkgSel_'+v+'_'+e+'_'+p
                                        # print "key=",p+e+s+v+f+r
                                        histoDict[p+e+s+v+f+r] =  rootFile.Get('bkg_'+r+s+'/nom/bkgSel_'+v+'_'+e+'_'+p)
                                        if self.fastHistos :
                                            histoDict[p+e+s+v+f+r+'IsoEWKSF'] =  rootFile.Get('bkg_'+r+s+'/nom/bkgSel_'+v+'_'+e+'_'+p+'IsoEWKSF')
                                        if(f!='Data') : 
                                            # print "main", p+e+s+v+f+r, "GET=",'bkg_'+r+s+'/nom/bkgSel_'+v+'_'+e+'_'+p
                                            histoDict[p+e+s+v+f+r].Scale(self.norm)
                                            if self.fastHistos :
                                                # print "iso", p+e+s+v+f+r+'IsoEWKSF', "GET=",'bkg_'+r+s+'/nom/bkgSel_'+v+'_'+e+'_'+p+'IsoEWKSF'
                                                histoDict[p+e+s+v+f+r+'IsoEWKSF'].Scale(self.norm)
                                        if not self.fastHistos :
                                            if(MtCond) :
                                                # print "Get histo Mt:" 'bkg_'+r+s+'/nom/bkgSel_Muon_corrected_MET_nom_mt_'+e
                                                mtDict[e+s+f+r] = rootFile.Get('bkg_'+r+s+'/nom/bkgSel_Muon_corrected_MET_nom_mt_'+e)
                                                # print "mt", e,s,f,r, "GET=", 'bkg_'+r+s+'/nom/bkgSel_Muon_corrected_MET_nom_mt_'+e
                                                if(f!='Data') : mtDict[e+s+f+r].Scale(self.norm)
                                                # for pp in self.ptBinningS :
                                                #     mtDict[pp+e+s+f+r] =rootFile.Get('bkg_'+r+s+'/nom/bkgSel_'+v+'_'+e+'_'+pp).ProjectionX('bkgSel_Muon_corrected_MET_nom_mt_'+e+'_'+pp,0,-1,"e")
                                                #     if(f!='Data') : mtDict[pp+e+s+f+r].Scale(self.norm)
                                            if(PVCond) :
                                                PVDict[s+f+r] = rootFile.Get('bkg_'+r+s+'/nom/bkgSel_PV_npvsGood')
                                                if(f!='Data') : PVDict[s+f+r].Scale(self.norm)

                                    else:
                                        # print "clone histo:", p+e+f+'_'+s+'_'+name+'_Tot'
                                        histoDict[p+e+s+v+f+r] = histoDict[p+e+s+v+f+'Sideband'].Clone(p+'_'+e+'_'+f+'_'+s+'_'+name+'_Tot')
                                        if self.fastHistos :
                                            histoDict[p+e+s+v+f+r+'IsoEWKSF'] = histoDict[p+e+s+v+f+'Sideband'+'IsoEWKSF'].Clone(p+'_'+e+'_'+f+'_'+s+'_'+name+'_Tot'+'IsoEWKSF')
                                        else :
                                            if(MtCond) :
                                                mtDict[e+s+f+r] = mtDict[e+s+f+'Sideband'].Clone('Mt_'+e+'_'+f+'_'+s+'_Tot') #PUT SIGNAL PER FAR FUNZIONARE
                                                # for pp in self.ptBinningS :
                                                    # mtDict[pp+e+s+f+r] = mtDict[pp+e+s+f+'Sideband'].Clone('Mt_'+pp+'_'+e+'_'+f+'_'+s+'_Tot')
                                            if(PVCond) : PVDict[s+f+r] = PVDict[s+f+'Sideband'].Clone('PV_'+f+'_'+s+'_Tot')
                                        for rr in self.regionList :
                                            if (rr =="Sideband" or rr=="Tot") : continue
                                            # print "Added histo:", histoDict[p+e+s+v+f+rr].GetName()
                                            # print "key=",p+e+s+v+f+r
                                            # print "key added=",p+e+s+v+f+rr
                                            histoDict[p+e+s+v+f+r].Add(histoDict[p+e+s+v+f+rr])
                                            if self.fastHistos :
                                               histoDict[p+e+s+v+f+r+'IsoEWKSF'].Add(histoDict[p+e+s+v+f+rr+'IsoEWKSF']) 
                                            else :
                                                if(MtCond) :
                                                    # print "skipped sideband adding in Mt!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
                                                    # continue
                                                    mtDict[e+s+f+r].Add(mtDict[e+s+f+rr])
                                                    # for pp in self.ptBinningS :
                                                    #     mtDict[pp+e+s+f+r].Add(mtDict[pp+e+s+f+rr])
                                                if(PVCond) :
                                                    PVDict[s+f+r].Add(PVDict[s+f+rr])



                            else :
                                # print "cloned (datalike) histo:", 'DataLike_'+s+'_'+name+'_Tot'
                                # print "key=",p+e+s+v+f+'Tot'
                                histoDict[p+e+s+v+f+'Tot']= histoDict[p+e+s+v+'WToMuNuTot'].Clone(p+'_'+e+'_'+'DataLike_'+s+'_'+name+'_Tot')
                                if self.fastHistos :
                                    histoDict[p+e+s+v+f+'Tot'+'IsoEWKSF']= histoDict[p+e+s+v+'WToMuNuTot'+'IsoEWKSF'].Clone(p+'_'+e+'_'+'DataLike_'+s+'_'+name+'_Tot'+'IsoEWKSF')
                                else :
                                    if(MtCond) :
                                        mtDict[e+s+f+'Tot'] = mtDict[e+s+'WToMuNuTot'].Clone('Mt_'+e+'_'+'DataLike_'+s+'_'+'_Tot')
                                        # for pp in self.ptBinningS :
                                            # mtDict[pp+e+s+f+'Tot'] = mtDict[pp+e+s+'WToMuNuTot'].Clone('Mt_'+pp+'_'+e+'_'+'DataLike_'+s+'_'+'_Tot')
                                    if(PVCond) : PVDict[s+f+'Tot'] = PVDict[s+'WToMuNuTot'].Clone('Mt_'+'DataLike_'+s+'_'+'_Tot')
                                # print "><>>><<>><<>><<>>>>>>><<>><>>>>>>>>"
                                for ff in self.sampleList :
                                    if (ff =="WToMuNu" or ff=="Data" or ff=="DataLike"):  continue
                                    # print "Added (data like) histo:", histoDict[p+e+s+v+ff+'Tot'].GetName()
                                    # print "key summed=",p+e+s+v+ff+'Tot'
                                    histoDict[p+e+s+v+f+'Tot'].Add(histoDict[p+e+s+v+ff+'Tot'])
                                    if self.fastHistos :
                                        histoDict[p+e+s+v+f+'Tot'+'IsoEWKSF'].Add(histoDict[p+e+s+v+ff+'Tot'+'IsoEWKSF'])
                                    else : 
                                        if(MtCond) :
                                            mtDict[e+s+f+'Tot'].Add(mtDict[e+s+ff+'Tot'])
                                            # for pp in self.ptBinningS :
                                                # mtDict[pp+e+s+f+'Tot'].Add(mtDict[pp+e+s+ff+'Tot'])
                                        if(PVDict) : PVDict[s+f+'Tot'].Add(PVDict[s+ff+'Tot'])

                                #DEBUUUG
                                errore = ROOT.Double(0)
                                binsizeTight = histoDict[p+e+s+v+f+'Tot'].GetYaxis().GetBinWidth(1)
                                NcutTight=(self.tightCut)/binsizeTight
                                NcutTight = int(NcutTight)

                                binsizeLoose = histoDict[p+e+s+v+f+'Tot'].GetXaxis().GetBinWidth(1)
                                NcutLoose=(self.looseCut)/binsizeLoose
                                NcutLoose = int(NcutLoose)
                                
                                if self.fastHistos :
                                    NcutTight=2
                                    NcutLoose=2
                                
                                # print "cut, l, t, ", NcutLoose,NcutTight
                                # print "ENTRIES=", histoDict[p+e+s+v+f+'Tot'].ProjectionX("htight",NcutTight,-1, "e").IntegralAndError(NcutLoose-1,-1,errore), histoDict[p+e+s+v+f+'Tot'].ProjectionX("htight",-1,NcutTight, "e").IntegralAndError(NcutLoose-1,-1,errore)
                                #END OF DEBUG
                        # print "======================================================================="
        for p in self.ptBinningS :
            for e in self.etaBinningS :
                for s in self.signList :
                    for v,name in map(None,self.varList,self.varName) :
                        if  self.varList.index(v)!=0 : continue
                        for f,rootFile in map(None,self.sampleList,self.rootFiles) :
                            if self.fastHistos : continue 
                            # print "DEBUG>>> projection:", p,e,s,v,f

                            #README uncomment this line for Mt_pt_all mt_all
                            mtDict[p+e+s+f+'Tot']= histoDict[p+e+s+v+f+'Tot'].ProjectionX('Mt_'+p+'_'+e+'_'+f+'_'+s+'_Tot',0,-1,"e")

                            isoMin= histoDict[p+e+s+v+f+'Tot'].GetYaxis().GetBinCenter(1)-histoDict[p+e+s+v+f+'Tot'].GetYaxis().GetBinWidth(1)/2
                            binsizeTight = histoDict[p+e+s+v+f+'Tot'].GetYaxis().GetBinWidth(1)
                            NcutTight=(self.tightCut-isoMin)/binsizeTight
                            NcutTight = int(NcutTight)
                            
                            if self.fastHistos :
                                NcutTight=2

                            #README uncomment this line for Mt_pt_tight mt_tight
                            # mtDict[p+e+s+f+'Tot']= histoDict[p+e+s+v+f+'Tot'].ProjectionX('Mt_'+p+'_'+e+'_'+f+'_'+s+'_Tot',0,NcutTight,"e")




        # print histos
        # print "ratios (integrated, preliminary)"
        ratios = []
        for p in self.ptBinningS :
            for e in self.etaBinningS :
                for s in self.signList :
                    for v,name in map(None,self.varList,self.varName) :
                        for f in self.sampleList :
                            if self.fastHistos : continue
                            # print "DEBUG>>> ratios:", p,e,s,v,f
                            # print 'ratio_'+histoDict[p+e+s+v+f+'Tot'].GetName()
                            if 'relIso' in name : cutvalue =  self.tightCut #self.relisoCUT
                            else : cutvalue = self.isoCUT
                            # if(p+e == '30-2.4') : print "DEBUG KEY", p+e+s+v+f+'Tot'
                            ratios.append(self.ratio_2Dto1D(histoDict[p+e+s+v+f+'Tot'],cutvalue,'ratio_'+histoDict[p+e+s+v+f+'Tot'].GetName()))
       
        output = ROOT.TFile(self.outdir+"/bkg_differential_fakerate"+self.corrFitSuff+self.nameSuff+".root","recreate")

        preliminary_dir = output.mkdir("RatiosVSMt")
        preliminary_dir.cd()
        for h in range(len(ratios)):
            if self.fastHistos : continue
            ratios[h].Write()
        # output.Close()

        histo_dir = output.mkdir("IsoVSMt")
        histo_dir.cd()
        for p in self.ptBinningS :
            for e in self.etaBinningS :
                for s in self.signList :
                    for v,name in map(None,self.varList,self.varName) :
                        for f,rootFile in map(None,self.sampleList,self.rootFiles) :
                            # print "DEBUG, writing>>>", p,e,s,v,f
                            histoDict[p+e+s+v+f+'Tot'].Write()

        # ptVSeta_map(hdict = histoDict)
        # ABCD_hypo(hdict = histoDict)
        Mt_dir = output.mkdir("Mt")
        Mt_dir.cd()
        for e in self.etaBinningS :
            for s in self.signList :
                if self.fastHistos : continue
                if(self.onData) : dataNameMt = 'Data'
                else : dataNameMt = 'DataLike'
                mtDict[e+s+'WToMuNuTot'].Write()
                mtDict[e+s+'EWKbkgTot'].Write()
                mtDict[e+s+'QCDTot'].Write()
                mtDict[e+s+dataNameMt+'Tot'].Write()
                for pp in self.ptBinningS :
                    mtDict[pp+e+s+'WToMuNuTot'].Write()
                    mtDict[pp+e+s+'EWKbkgTot'].Write()
                    mtDict[pp+e+s+'QCDTot'].Write()
                    mtDict[pp+e+s+dataNameMt+'Tot'].Write()

        # ABCD_dir = output.mkdir("ABCD_checks")
        # ABCD_dir.cd()
        if not self.fastHistos : 
            print "isolation analysis..."
            hIsoMC = self.isolationAna(kind=self.dataOpt,hdict=histoDict,varname = self.varFake, loosecut = self.looseCut)
            hIsoValidation = self.isolationAna(kind = 'validation',hdict=histoDict,varname = self.varFake, loosecut = self.looseCut)
            hIsoPrompt = self.isolationAna(kind = 'prompt',hdict=histoDict,varname = self.varFake, loosecut = self.looseCut)
            hIsoEWKbkg = self.isolationAna(kind = 'EWKbkg',hdict=histoDict,varname = self.varFake, loosecut = self.looseCut)
            fakerate_dir = output.mkdir("Isolation")
            fakerate_dir.cd()
            for a,b,c,d in map(None,hIsoMC,hIsoValidation,hIsoPrompt,hIsoEWKbkg):
                    if self.fastHistos : continue
                    hIsoMC[a].Write()
                    hIsoValidation[b].Write()
                    hIsoPrompt[c].Write()
                    hIsoEWKbkg[d].Write()

            PV_dir = output.mkdir("PV")
            PV_dir.cd()
            for s in self.signList :
                    if self.fastHistos : continue
                    if(self.onData) : dataNameMt = 'Data'
                    else : dataNameMt = 'DataLike'
                    PVDict[s+'WToMuNuTot'].Write()
                    PVDict[s+'EWKbkgTot'].Write()
                    PVDict[s+'QCDTot'].Write()
                    PVDict[s+dataNameMt+'Tot'].Write()

        if(fakerate) :
            print "evaluating fakerates..."
            hfakesMC = self.differential_fakerate(kind = self.dataOpt, hdict = histoDict, mtDict = mtDict, varname = self.varFake, tightcut = self.tightCut, loosecut = self.looseCut, EWSF=self.EWSF, highMtCut=90,parabolaFit = self.parabolaFit, asymmetry_EW=False,correlatedFit=correlatedFit)
            hprompt =self.differential_fakerate(kind = 'prompt', hdict = histoDict, mtDict = mtDict, varname = self.varFake, tightcut = self.tightCut, loosecut = self.looseCut,parabolaFit = self.parabolaFit)
            if self.extraValidationPlots : 
                hvalidation =self.differential_fakerate(kind = 'validation', hdict = histoDict, mtDict = mtDict, varname = self.varFake, tightcut = self.tightCut, loosecut = self.looseCut,parabolaFit = self.parabolaFit)
                hvalidationSigReg =self.differential_fakerate(kind = 'validationSigReg', hdict = histoDict, mtDict = mtDict, varname = self.varFake, tightcut = self.tightCut, loosecut = self.looseCut,parabolaFit = self.parabolaFit)
                hpromptSideband =self.differential_fakerate(kind = 'promptSideband', hdict = histoDict, mtDict = mtDict, varname = self.varFake, tightcut = self.tightCut, loosecut = self.looseCut,parabolaFit = self.parabolaFit)

            # outputFake = ROOT.TFile(self.outdir+"/bkg_differential_fakerate.root","recreate")
            fakerate_dir = output.mkdir("Fakerate")
            fakerate_dir.cd()

            # print ("writing fakerates")
            # for b,c,d,e in map(None,hprompt,hvalidation,hvalidationSigReg,hpromptSideband):
            for b in hprompt : 
                if 'offset' in (b or c or d or e) or 'slope' in (b or c or d or e) or '2deg' in (b or c or d or e) or 'fitRes' in (b or c or d or e) or 'chi2red' in (b or c or d or e) or 'sigmaERFvec' in (b or c or d or e): continue
                # if 'offset' in (b or c or d or e) or 'slope' in (b or c or d or e) : continue
                hprompt[b].Write()
            if self.extraValidationPlots :
                for c,d,e in map(None,hvalidation,hvalidationSigReg,hpromptSideband):
                    if 'offset' in (b or c or d or e) or 'slope' in (b or c or d or e) or '2deg' in (b or c or d or e) or 'fitRes' in (b or c or d or e) or 'chi2red' in (b or c or d or e) or 'sigmaERFvec' in (b or c or d or e): continue 
                    # if 'offset' in (b or c or d or e) or 'slope' in (b or c or d or e) : continue   
                    hvalidation[c].Write()
                    hvalidationSigReg[d].Write()
                    hpromptSideband[e].Write()
            for a in hfakesMC:
                if 'offset' in a or 'slope' in a  or '2deg' in a or 'fitRes' in a or 'chi2red' in a or 'sigmaERFvec' in a: continue
                # if 'offset' in a or 'slope' in a: continue
                hfakesMC[a].Write()
            template_dir = output.mkdir("Template")
            template_dir.cd()
            print "evaluating templates..."
            bkg_templateMC = self.bkg_template(kind = self.dataOpt, fakedict=hfakesMC, promptdict=hprompt, hdict =histoDict, fit =self.fitOnTemplate, tightcut = self.tightCut, loosecut=self.looseCut, varname = self.varFake, parabolaFit = self.parabolaFit, correlatedFit=correlatedFit)
            bkg_templatePrompt = self.bkg_template(kind = 'prompt', fakedict=hfakesMC, promptdict=hprompt, hdict =histoDict, fit =self.fitOnTemplate, tightcut = self.tightCut, loosecut=self.looseCut, varname = self.varFake, parabolaFit = self.parabolaFit)
            bkg_templateValidation = self.bkg_template(kind = 'validation', fakedict=hfakesMC, promptdict=hprompt, hdict =histoDict, fit =self.fitOnTemplate, tightcut = self.tightCut, loosecut=self.looseCut, varname = self.varFake, parabolaFit = self.parabolaFit)
            bkg_templateEWKbkg = self.bkg_template(kind = 'EWKbkg', fakedict=hfakesMC, promptdict=hprompt, hdict =histoDict, fit =self.fitOnTemplate, tightcut = self.tightCut, loosecut=self.looseCut, varname = self.varFake, parabolaFit = self.parabolaFit)
            # print "Writing templates"
            template_dir.cd()
            for a,b,c,d in map(None, bkg_templateMC,bkg_templatePrompt,bkg_templateValidation, bkg_templateEWKbkg) :
                # print a, bkg_templateMC[a]
                bkg_templateMC[a].Write()
                bkg_templatePrompt[b].Write()
                bkg_templateValidation[c].Write()
                bkg_templateEWKbkg[d].Write()

        output.Save()
        if produce_ext_output :
            external_histoDict = self.dict2histConverter(fakedict=hfakesMC,promptdict=hprompt,hdict=histoDict, minimal=False, parabolaFit=self.parabolaFit, correlatedFit=correlatedFit)
            # external_output = ROOT.TFile(self.folder+"/bkg/bkg_parameters_file.root","recreate")
            external_output = ROOT.TFile(self.outdir+"/bkg_parameters_file"+self.corrFitSuff+self.nameSuff+".root","recreate")
            external_output.cd()
            for a in external_histoDict :
                external_histoDict[a].Write()
            external_output.Close()

        output.Close()

    def fakerate_plots(self, variations=False,tightCutList=[0.15],looseCutList=[40], parabolaFit = False, correlatedFit=False) :
        print "plotting..."
        # self.variations = variations
        # self.tightCutList= tightCutList
        # self.looseCutList= looseCutList
        # self.parabolaFit = parabolaFit
        inputFile = ROOT.TFile.Open(self.outdir+"/bkg_differential_fakerate"+self.corrFitSuff+self.nameSuff+".root")

        canvasList = []
        legDict = {}
        stackDict ={}

        for s in self.signList :
            if not self.fastHistos :
                #---------------------------------------------PV PLOTS ---------------------------------------------#
                # print "PV plots"

                c_PV = ROOT.TCanvas("c_PV_{sign}".format(sign=s),"c_PV_{sign}".format(sign=s),800,600)
                c_PV.cd()
                c_PV.SetGridx()
                c_PV.SetGridy()

                if(self.onData) : dataNameMt = 'Data'
                else : dataNameMt = 'DataLike'

                h_PV_data = inputFile.Get("PV/PV_"+dataNameMt+"_"+s+"_Tot")
                h_PV_bkg = inputFile.Get("PV/PV_QCD_"+s+"_Tot")
                h_PV_sig = inputFile.Get("PV/PV_WToMuNu_"+s+"_Tot")
                h_PV_EWKbkg = inputFile.Get("PV/PV_EWKbkg_"+s+"_Tot")
                h_PV_sig.Add(h_PV_EWKbkg)

                # h_PV_sig.Rebin(3)
                # h_PV_bkg.Rebin(3)
                # h_PV_data.Rebin(3)

                h_PV_data.SetLineWidth(3)
                h_PV_bkg.SetLineWidth(3)
                h_PV_sig.SetLineWidth(3)
                # h_fake.SetLineWidth(3)

                # h_PV_data.SetLineColor(632+2) #red
                h_PV_data.SetLineColor(1) #black
                h_PV_bkg.SetLineColor(600-4) #blue
                h_PV_sig.SetLineColor(416+2) #green
                h_PV_bkg.SetFillColor(600-4) #blue
                h_PV_sig.SetFillColor(416+2) #green
                # h_fake.SetLineColor(1) #black

                h_PV_data.Sumw2()
                h_PV_data.SetMarkerStyle(20)
                h_PV_data.Draw()


                stackDict[s+"PV"] = ROOT.THStack("PV"+s,"")
                stackDict[s+"PV"].Add(h_PV_sig)
                stackDict[s+"PV"].Add(h_PV_bkg)
                stackDict[s+"PV"].Draw("SAME HIST")
                h_PV_data.DrawCopy("SAME")
                # h_PV_bkg.Draw("SAME")
                # h_PV_sig.Draw("SAME")
                # h_fake.Draw("SAME")

                h_PV_data.GetYaxis().SetTitle("dN/dPV/{size} [1/GeV]".format(size=h_PV_data.GetBinWidth(1)))
                h_PV_data.GetYaxis().SetTitleOffset(1)
                h_PV_data.GetXaxis().SetTitle("N PV good")
                # h_PV_data.SetTitle("Fake Rates, {min}<#eta<{max}, W {sign}".format(min=self.etaBinning[self.etaBinning.index(float(e))-1], max=e, sign=s))
                h_PV_data.SetTitle("Number of Primary vertices, W {sign}".format(sign=s))

                legDict[s+"PV"] = ROOT.TLegend(0.1,0.7,0.48,0.9)
                legDict[s+"PV"].AddEntry(h_PV_data,"Data")
                legDict[s+"PV"].AddEntry(h_PV_bkg, "QCD MC")
                legDict[s+"PV"].AddEntry(h_PV_sig, "EWK MC")
                # legDict[e+s].AddEntry(h_fake, "Data")
                legDict[s+"PV"].Draw("SAME")

                canvasList.append(c_PV)
                # c_comparison.SaveAs(self.outdir+"/plot/"+c_Mt_EWSF.GetName()+'.png')

            for e in self.etaBinningS :

                    #---------------------------------------------COMPARISON PLOTS ---------------------------------------------#

                    # print "comparison plots"

                    c_comparison = ROOT.TCanvas("c_comparison_{sign}_{eta}".format(sign=s,eta=e),"c_comparison_{sign}_{eta}".format(sign=s,eta=e),800,600)
                    c_comparison.cd()
                    c_comparison.SetGridx()
                    c_comparison.SetGridy()


                    h_fakeMC = inputFile.Get("Fakerate/hFakes_pt_"+self.dataOpt+"_"+s+"_"+e)
                    h_prompt = inputFile.Get("Fakerate/hFakes_pt_prompt_"+s+"_"+e)
                    if self.extraValidationPlots : 
                        h_validation = inputFile.Get("Fakerate/hFakes_pt_validation_"+s+"_"+e)

                    # h_fake = inputFile.Get("Fakerate/hFakes_pt_fake_"+s+"_"+e)

                    h_fakeMC.SetLineWidth(3)
                    h_prompt.SetLineWidth(3)
                    if self.extraValidationPlots : h_validation.SetLineWidth(3)
                    # h_fake.SetLineWidth(3)

                    h_fakeMC.SetLineColor(632+2) #red
                    h_prompt.SetLineColor(600-4) #blue
                    if self.extraValidationPlots :  h_validation.SetLineColor(416+2) #green
                    # h_fake.SetLineColor(1) #black

                    h_fakeMC.Draw()
                    h_prompt.Draw("SAME")
                    if self.extraValidationPlots :  h_validation.Draw("SAME")
                    # h_fake.Draw("SAME")

                    h_fakeMC.GetYaxis().SetRangeUser(0,1.1)
                    h_fakeMC.GetYaxis().SetTitle("Isolation Cut Efficiency")
                    h_fakeMC.GetYaxis().SetTitleOffset(1)
                    h_fakeMC.GetXaxis().SetTitle("p_{T}^{#mu} [GeV]")
                    # h_fakeMC.SetTitle("Fake Rates, {min}<#eta<{max}, W {sign}".format(min=self.etaBinning[self.etaBinning.index(float(e))-1], max=e, sign=s))
                    h_fakeMC.SetTitle("Fake Rates, {min}<#eta<{max}, W {sign}".format(min=e, max=self.etaBinning[self.etaBinning.index(float(e))+1], sign=s))

                    legDict[e+s] = ROOT.TLegend(0.1,0.7,0.48,0.9)
                    legDict[e+s].AddEntry(h_fakeMC,"Data")
                    legDict[e+s].AddEntry(h_prompt, "W MC")
                    if self.extraValidationPlots :  legDict[e+s].AddEntry(h_validation, "QCD MC")
                    # legDict[e+s].AddEntry(h_fake, "Data")
                    legDict[e+s].Draw("SAME")

                    canvasList.append(c_comparison)
                    # c_comparison.SaveAs(self.outdir+"/plot/"+c_comparison.GetName()+'.png')
                    
                    if self.extraValidationPlots : 
                        #---------------------------------------------ABCD cehcks PLOTS ---------------------------------------------#
                        # print "ABCD check plots"

                        c_ABCDcheck = ROOT.TCanvas("c_ABCDcheck_{sign}_{eta}".format(sign=s,eta=e),"c_ABCDcheck_{sign}_{eta}".format(sign=s,eta=e),800,600)
                        c_ABCDcheck.cd()
                        c_ABCDcheck.SetGridx()
                        c_ABCDcheck.SetGridy()


                        h_prompt = inputFile.Get("Fakerate/hFakes_pt_prompt_"+s+"_"+e)
                        h_validation = inputFile.Get("Fakerate/hFakes_pt_validation_"+s+"_"+e)
                        h_promptSideband = inputFile.Get("Fakerate/hFakes_pt_promptSideband_"+s+"_"+e)
                        h_validationSigReg = inputFile.Get("Fakerate/hFakes_pt_validationSigReg_"+s+"_"+e)

                        # h_fake = inputFile.Get("Fakerate/hFakes_pt_fake_"+s+"_"+e)

                        h_promptSideband.SetLineWidth(3)
                        h_prompt.SetLineWidth(3)
                        h_validation.SetLineWidth(3)
                        h_validationSigReg.SetLineWidth(3)

                        h_promptSideband.SetLineColor(632+2) #red
                        h_prompt.SetLineColor(600-4) #blue
                        h_validation.SetLineColor(416+2) #green
                        h_validationSigReg.SetLineColor(1) #black

                        h_promptSideband.Draw()
                        h_prompt.Draw("SAME")
                        h_validation.Draw("SAME")
                        h_validationSigReg.Draw("SAME")

                        h_promptSideband.GetYaxis().SetRangeUser(0,1.1)
                        h_promptSideband.GetYaxis().SetTitle("Isolation Cut Efficiency")
                        h_promptSideband.GetYaxis().SetTitleOffset(1)
                        h_promptSideband.GetXaxis().SetTitle("p_{T}^{#mu} [GeV]")
                        h_promptSideband.SetTitle("Fake Rates, {min}<#eta<{max}, ABCD check, W {sign}".format(min=e, max=self.etaBinning[self.etaBinning.index(float(e))+1], sign=s))

                        legDict[e+s+'ABCD'] = ROOT.TLegend(0.1,0.7,0.48,0.9)
                        legDict[e+s+'ABCD'].AddEntry(h_promptSideband,"W, Sideband")
                        legDict[e+s+'ABCD'].AddEntry(h_prompt, "W Signal Region")
                        legDict[e+s+'ABCD'].AddEntry(h_validation, "QCD Sideband")
                        legDict[e+s+'ABCD'].AddEntry(h_validationSigReg, "QCD Signal Region")
                        legDict[e+s+'ABCD'].Draw("SAME")

                        canvasList.append(c_ABCDcheck)
                        # c_comparison.SaveAs(self.outdir+"/plot/"+c_ABCDcheck.GetName()+'.png')


                    #---------------------------------------------TEMPLATE PLOTS ---------------------------------------------#
                    # print "template plots"

                    c_template = ROOT.TCanvas("c_template_{sign}_{eta}".format(sign=s,eta=e),"c_template_{sign}_{eta}".format(sign=s,eta=e),800,600)
                    c_template.cd()
                    c_template.SetGridx()
                    c_template.SetGridy()


                    h_template = inputFile.Get("Template/htempl_pt_"+self.dataOpt+"_"+s+"_"+e)
                    h_W = inputFile.Get("Template/htempl_pt_prompt_"+s+"_"+e)
                    h_qcd = inputFile.Get("Template/htempl_pt_validation_"+s+"_"+e)
                    h_EWK = inputFile.Get("Template/htempl_pt_EWKbkg_"+s+"_"+e)
                    h_W.Add(h_EWK)
                    # h_W.Add(h_template)

                    # if(s=='Plus' and e=='0') : print "inside the plotter", h_template.GetBinContent(1)

                    # h_fake = inputFile.Get("Fakerate/hFakes_pt_fake_"+s+"_"+e)

                    h_template.SetLineWidth(3)
                    h_W.SetLineWidth(3)
                    h_qcd.SetLineWidth(3)
                    # h_fake.SetLineWidth(3)

                    h_template.SetLineColor(632+2) #red
                    h_W.SetLineColor(600-4) #blue
                    h_qcd.SetLineColor(416+2) #green
                    # h_fake.SetLineColor(1) #black

                    h_W.Draw()
                    h_template.Draw("SAME")
                    h_qcd.Draw("SAME")
                    # h_fake.Draw("SAME")

                    h_W.GetYaxis().SetRangeUser(0,1500000)
                    h_W.GetYaxis().SetTitle("Events")
                    h_W.GetYaxis().SetTitleOffset(1)
                    h_W.GetXaxis().SetTitle("p_{T}^{#mu} [GeV]")
                    h_W.SetTitle("Compared yelds, {min}<#eta<{max}, W {sign}".format(min=e, max=self.etaBinning[self.etaBinning.index(float(e))+1], sign=s))

                    legDict[e+s+"templ"] = ROOT.TLegend(0.1,0.7,0.48,0.9)
                    legDict[e+s+"templ"].AddEntry(h_template,"Template bkg MC")
                    legDict[e+s+"templ"].AddEntry(h_W, "EWK+Template MC")
                    legDict[e+s+"templ"].AddEntry(h_qcd, "QCD MC")
                    # legDict[e+s].AddEntry(h_fake, "Data")
                    legDict[e+s].Draw("SAME")

                    canvasList.append(c_template)
                    # c_comparison.SaveAs(self.outdir+"/plot/"+c_template.GetName()+'.png')


                    #---------------------------------------------Mt EWSF PLOTS ---------------------------------------------#
                    # print "Mt EWSF plots"
                    if not self.fastHistos :

                        c_Mt_EWSF = ROOT.TCanvas("c_Mt_EWSF_{sign}_{eta}".format(sign=s,eta=e),"c_Mt_EWSF_{sign}_{eta}".format(sign=s,eta=e),800,600)
                        c_Mt_EWSF.cd()
                        c_Mt_EWSF.SetGridx()
                        c_Mt_EWSF.SetGridy()

                        if(self.onData) : dataNameMt = 'Data'
                        else : dataNameMt = 'DataLike'

                        h_Mt_data = inputFile.Get("Mt/Mt_"+e+"_"+dataNameMt+"_"+s+"_Tot")
                        h_Mt_bkg = inputFile.Get("Mt/Mt_"+e+"_QCD_"+s+"_Tot")
                        h_Mt_sig = inputFile.Get("Mt/Mt_"+e+"_WToMuNu_"+s+"_Tot")
                        h_Mt_EWKbkg = inputFile.Get("Mt/Mt_"+e+"_EWKbkg_"+s+"_Tot")
                        h_Mt_sig.Add(h_Mt_EWKbkg)

                        # h_Mt_sig.Rebin(3)
                        # h_Mt_bkg.Rebin(3)
                        # h_Mt_data.Rebin(3)

                        h_Mt_data.SetLineWidth(3)
                        h_Mt_bkg.SetLineWidth(3)
                        h_Mt_sig.SetLineWidth(3)
                        # h_fake.SetLineWidth(3)

                        # h_Mt_data.SetLineColor(632+2) #red
                        h_Mt_data.SetLineColor(1) #black
                        h_Mt_bkg.SetLineColor(600-4) #blue
                        h_Mt_sig.SetLineColor(416+2) #green
                        h_Mt_bkg.SetFillColor(600-4) #blue
                        h_Mt_sig.SetFillColor(416+2) #green
                        # h_fake.SetLineColor(1) #black

                        # h_Mt_data.Sumw2()
                        h_Mt_data.SetMarkerStyle(20)
                        h_Mt_data.Draw()


                        stackDict[e+s+"Mt"] = ROOT.THStack("Mt"+e+s,"")
                        stackDict[e+s+"Mt"].Add(h_Mt_sig)
                        stackDict[e+s+"Mt"].Add(h_Mt_bkg)
                        stackDict[e+s+"Mt"].Draw("SAME HIST")
                        h_Mt_data.DrawCopy("SAME")
                        # h_Mt_bkg.Draw("SAME")
                        # h_Mt_sig.Draw("SAME")
                        # h_fake.Draw("SAME")

                        h_Mt_data.GetYaxis().SetTitle("dN/dMt/{size} [1/GeV]".format(size=h_Mt_data.GetBinWidth(1)))
                        h_Mt_data.GetYaxis().SetTitleOffset(1)
                        h_Mt_data.GetXaxis().SetTitle("M_{T} [GeV]")
                        # h_Mt_data.SetTitle("Fake Rates, {min}<#eta<{max}, W {sign}".format(min=self.etaBinning[self.etaBinning.index(float(e))-1], max=e, sign=s))
                        h_Mt_data.SetTitle("Transverse Mass, {min}<#eta<{max}, W {sign}".format(min=e, max=self.etaBinning[self.etaBinning.index(float(e))+1], sign=s))

                        legDict[e+s+"Mt"] = ROOT.TLegend(0.1,0.7,0.48,0.9)
                        legDict[e+s+"Mt"].AddEntry(h_Mt_data,"Data")
                        legDict[e+s+"Mt"].AddEntry(h_Mt_bkg, "QCD MC")
                        legDict[e+s+"Mt"].AddEntry(h_Mt_sig, "EWK MC")
                        # legDict[e+s].AddEntry(h_fake, "Data")
                        legDict[e+s+"Mt"].Draw("SAME")

                        canvasList.append(c_Mt_EWSF)
                        # c_comparison.SaveAs(self.outdir+"/plot/"+c_Mt_EWSF.GetName()+'.png')

                    notIsoPlots = False
                    for p in self.ptBinningS :
                        if self.fastHistos : continue
                        if(notIsoPlots) : continue
                        #---------------------------------------------ISO PLOTS ---------------------------------------------#
                        # print "ISO plots"

                        c_Iso = ROOT.TCanvas("c_Iso_{sign}_{eta}_{pt}".format(sign=s,eta=e, pt=p),"c_Iso_{sign}_{eta}_{pt}".format(sign=s,eta=e, pt=p),800,600)

                        c_Iso.cd()
                        c_Iso.SetGridx()
                        c_Iso.SetGridy()

                        if(self.onData) : dataNameIso = 'fake'
                        else : dataNameIso = 'FakeMC'
                        h_iso_data = inputFile.Get("Isolation/Iso_"+dataNameIso+"_"+s+"_"+e+"_"+p)
                        h_iso_bkg = inputFile.Get("Isolation/Iso_validation_"+s+"_"+e+"_"+p)
                        h_iso_sig = inputFile.Get("Isolation/Iso_prompt_"+s+"_"+e+"_"+p)
                        h_iso_EWKbkg = inputFile.Get("Isolation/Iso_EWKbkg_"+s+"_"+e+"_"+p)
                        # print "Isolation/iso_EWKbkg_"+s+"_"+e+"_"+p
                        # print "Isolation/iso_prompt_"+s+"_"+e+"_"+p
                        h_iso_sig.Add(h_iso_EWKbkg)


                        # h_iso_sig.Rebin(20)
                        # h_iso_bkg.Rebin(20)
                        # h_iso_data.Rebin(20)

                        h_iso_data.SetLineWidth(3)
                        h_iso_bkg.SetLineWidth(3)
                        h_iso_sig.SetLineWidth(3)
                        # h_fake.SetLineWidth(3)

                        # h_iso_data.SetLineColor(632+2) #red
                        h_iso_data.SetLineColor(1) #black
                        h_iso_bkg.SetLineColor(600-4) #blue
                        h_iso_sig.SetLineColor(416+2) #green
                        h_iso_bkg.SetFillColor(600-4) #blue
                        h_iso_sig.SetFillColor(416+2) #green
                        # h_fake.SetLineColor(1) #black

                        # h_iso_data.Sumw2()
                        h_iso_data.SetMarkerStyle(20)
                        h_iso_data.Draw()

                        stackDict[e+s+p+"Iso"] = ROOT.THStack("Iso"+e+s+p,"")
                        stackDict[e+s+p+"Iso"].Add(h_iso_sig)
                        stackDict[e+s+p+"Iso"].Add(h_iso_bkg)
                        stackDict[e+s+p+"Iso"].Draw("SAME HIST")
                        h_iso_data.DrawCopy("SAME")
                        # h_iso_bkg.Draw("SAME")
                        # h_iso_sig.Draw("SAME")
                        # h_fake.Draw("SAME")

                        h_iso_data.GetYaxis().SetTitle("dN/dIso/{size} [1/GeV]".format(size=h_iso_data.GetBinWidth(1)))
                        h_iso_data.GetYaxis().SetTitleOffset(1)
                        h_iso_data.GetXaxis().SetTitle("RelIso_{T} ")
                        # h_iso_data.SetTitle("Fake Rates, {min}<#eta<{max}, W {sign}".format(min=self.etaBinning[self.etaBinning.index(float(e))-1], max=e, sign=s))
                        h_iso_data.SetTitle("Relaitve Isolation 04, {min}<#eta<{max},{pmin}<Pt<{pmax}, W {sign}".format(min=e, max=self.etaBinning[self.etaBinning.index(float(e))+1],pmin=p, pmax=self.ptBinning[self.ptBinning.index(float(p))+1], sign=s))

                        legDict[e+s+p+"Iso"] = ROOT.TLegend(0.1,0.7,0.48,0.9)
                        legDict[e+s+p+"Iso"].AddEntry(h_iso_data,"Data")
                        legDict[e+s+p+"Iso"].AddEntry(h_iso_bkg, "QCD MC")
                        legDict[e+s+p+"Iso"].AddEntry(h_iso_sig, "EWK MC")
                        # legDict[e+s].AddEntry(h_fake, "Data")
                        legDict[e+s+p+"Iso"].Draw("SAME")

                        canvasList.append(c_Iso)
                        # c_comparison.SaveAs(self.outdir+"/plot/"+c_Iso.GetName()+'.png')


                        #---------------------------------------------Mt EWSF PLOTS (PT dependednt)---------------------------------------------#
                        # print "Mt EWSF plots"

                        c_Mt_EWSF = ROOT.TCanvas("c_Mt_EWSF_{sign}_{eta}_{pt}".format(sign=s,eta=e,pt=p),"c_Mt_EWSF_{sign}_{eta}_{pt}".format(sign=s,eta=e,pt=p),800,600)
                        c_Mt_EWSF.cd()
                        c_Mt_EWSF.SetGridx()
                        c_Mt_EWSF.SetGridy()

                        if(self.onData) : dataNameMt = 'Data'
                        else : dataNameMt = 'DataLike'

                        h_Mt_data = inputFile.Get("Mt/Mt_"+p+"_"+e+"_"+dataNameMt+"_"+s+"_Tot")
                        h_Mt_bkg = inputFile.Get("Mt/Mt_"+p+"_"+e+"_QCD_"+s+"_Tot")
                        h_Mt_sig = inputFile.Get("Mt/Mt_"+p+"_"+e+"_WToMuNu_"+s+"_Tot")
                        h_Mt_EWKbkg = inputFile.Get("Mt/Mt_"+p+"_"+e+"_EWKbkg_"+s+"_Tot")
                        h_Mt_sig.Add(h_Mt_EWKbkg)

                        # h_Mt_sig.Rebin(3)
                        # h_Mt_bkg.Rebin(3)
                        # h_Mt_data.Rebin(3)

                        h_Mt_data.SetLineWidth(3)
                        h_Mt_bkg.SetLineWidth(3)
                        h_Mt_sig.SetLineWidth(3)
                        # h_fake.SetLineWidth(3)

                        # h_Mt_data.SetLineColor(632+2) #red
                        h_Mt_data.SetLineColor(1) #black
                        h_Mt_bkg.SetLineColor(600-4) #blue
                        h_Mt_sig.SetLineColor(416+2) #green
                        h_Mt_bkg.SetFillColor(600-4) #blue
                        h_Mt_sig.SetFillColor(416+2) #green
                        # h_fake.SetLineColor(1) #black

                        # h_Mt_data.Sumw2()
                        h_Mt_data.SetMarkerStyle(20)
                        h_Mt_data.Draw()


                        stackDict[p+e+s+"Mt"] = ROOT.THStack("Mt"+e+s,"")
                        stackDict[p+e+s+"Mt"].Add(h_Mt_sig)
                        stackDict[p+e+s+"Mt"].Add(h_Mt_bkg)
                        stackDict[p+e+s+"Mt"].Draw("SAME HIST")
                        h_Mt_data.DrawCopy("SAME")
                        # h_Mt_bkg.Draw("SAME")
                        # h_Mt_sig.Draw("SAME")
                        # h_fake.Draw("SAME")

                        h_Mt_data.GetYaxis().SetTitle("dN/dMt/{size} [1/GeV]".format(size=h_Mt_data.GetBinWidth(1)))
                        h_Mt_data.GetYaxis().SetTitleOffset(1)
                        h_Mt_data.GetXaxis().SetTitle("M_{T} [GeV]")
                        # h_Mt_data.SetTitle("Fake Rates, {min}<#eta<{max}, W {sign}".format(min=self.etaBinning[self.etaBinning.index(float(e))-1], max=e, sign=s))
                        h_Mt_data.SetTitle("Transverse Mass, {min}<#eta<{max}, {pmin}<Pt<{pmax}, W {sign}".format(min=e, max=self.etaBinning[self.etaBinning.index(float(e))+1], sign=s,pmin=p, pmax=self.ptBinning[self.ptBinning.index(float(p))+1]))

                        legDict[p+e+s+"Mt"] = ROOT.TLegend(0.1,0.7,0.48,0.9)
                        legDict[p+e+s+"Mt"].AddEntry(h_Mt_data,"Data")
                        legDict[p+e+s+"Mt"].AddEntry(h_Mt_bkg, "QCD MC")
                        legDict[p+e+s+"Mt"].AddEntry(h_Mt_sig, "EWK MC")
                        # legDict[e+s].AddEntry(h_fake, "Data")
                        legDict[p+e+s+"Mt"].Draw("SAME")

                        canvasList.append(c_Mt_EWSF)
                        # c_comparison.SaveAs(self.outdir+"/plot/"+c_Mt_EWSF.GetName()+'.png')







        #---------------------------------------------FIT CHECK PLOTS ---------------------------------------------#
        # print "Fit check plots"

        if not parabolaFit :
            typeFitDict = {
                'EWSF' : ['chi2', 'bkg', 'sig'],
                'Templ' : ['chi2','slope', 'offset'],
            }
        else :
            typeFitDict = {
                'EWSF' : ['chi2', 'bkg', 'sig' ],
                'Templ' : ['chi2','slope', 'offset', '2deg'],
            }



        c_fitDict = {}
        hFitDict_Plus = {}
        hFitDict_Minus = {}

        if not self.fastHistos :
            for ty in typeFitDict :
                if ty == "Templ" : kind = [self.dataOpt, 'prompt']
                else : kind = [self.dataOpt]
                for var in typeFitDict[ty] :

                    for ki in kind :
                        if ki!='prompt' and var=='2deg' :
                            continue
                        c_fitDict[ty+var+ki] = ROOT.TCanvas("c_"+ty+"_"+var+'_'+ki,"c_"+ty+"_"+var+'_'+ki,800,600)
                        c_fitDict[ty+var+ki].cd()
                        c_fitDict[ty+var+ki].SetGridx()
                        c_fitDict[ty+var+ki].SetGridy()
                        # print "Fakerate/h"+ty+"_"+var+"_"+ki+"_Plus"
                        hFitDict_Plus[ty+var+ki] = inputFile.Get("Fakerate/h"+ty+"_"+var+"_"+ki+"_Plus")
                        hFitDict_Minus[ty+var+ki] = inputFile.Get("Fakerate/h"+ty+"_"+var+"_"+ki+"_Minus")
                        # hEWSF_chi2_fake_Plus = inputFile.Get("Fakerate/hEWSF_chi2_fake_Plus")
                        # hEWSF_chi2_fake_Minus = inputFile.Get("Fakerate/hEWSF_chi2_fake_Minus")
                        hFitDict_Plus[ty+var+ki].SetLineWidth(3)
                        hFitDict_Minus[ty+var+ki].SetLineWidth(3)
                        hFitDict_Plus[ty+var+ki].SetLineColor(632+2) #red
                        hFitDict_Minus[ty+var+ki].SetLineColor(600-4) #blue
                        hFitDict_Plus[ty+var+ki].Draw()
                        hFitDict_Minus[ty+var+ki].Draw("SAME")
                        hFitDict_Plus[ty+var+ki].GetYaxis().SetTitleOffset(1)
                        hFitDict_Plus[ty+var+ki].GetXaxis().SetTitle("#eta^{#mu}")

                        if(var=="chi2") :
                            hFitDict_Plus[ty+var+ki].GetYaxis().SetTitle("Reduced #chi^{2}")
                        else :
                            hFitDict_Plus[ty+var+ki].GetYaxis().SetTitle("Par. Value")
                        hFitDict_Plus[ty+var+ki].SetTitle("{FitKind} Fit, {var}, {kind} ".format(FitKind=ty,var=var,kind=ki))
                        legDict[ty+var+ki] = ROOT.TLegend(0.1,0.7,0.48,0.9)
                        legDict[ty+var+ki].AddEntry(hFitDict_Plus[ty+var+ki],"W plus")
                        legDict[ty+var+ki].AddEntry(hFitDict_Minus[ty+var+ki], "W minus")
                        legDict[ty+var+ki].Draw("SAME")
                        # canvasList.append(c_EWSF_chi2)
                        canvasList.append(c_fitDict[ty+var+ki])
                        # c_comparison.SaveAs(self.outdir+"/plot/"+c_fitDict[ty+var+ki].GetName()+'.png')
            ty='EWSF'
            ki = self.dataOpt
            for var in ['chi2', 'bkg', 'sig', 'iso', 'Mt'] :
                for e in self.etaBinningS :
                                c_fitDict[ty+var+ki+e] = ROOT.TCanvas("c_"+ty+"_"+var+'_'+ki+'_'+e,"c_"+ty+"_"+var+'_'+ki+'_'+e,800,600)
                                c_fitDict[ty+var+ki+e].cd()
                                c_fitDict[ty+var+ki+e].SetGridx()
                                c_fitDict[ty+var+ki+e].SetGridy()
                                hFitDict_Plus[ty+var+ki+e] = inputFile.Get("Fakerate/h"+ty+"_"+var+"_"+ki+"_Plus_"+e)
                                hFitDict_Minus[ty+var+ki+e] = inputFile.Get("Fakerate/h"+ty+"_"+var+"_"+ki+"_Minus_"+e)
                                hFitDict_Plus[ty+var+ki+e].SetLineWidth(3)
                                hFitDict_Minus[ty+var+ki+e].SetLineWidth(3)
                                hFitDict_Plus[ty+var+ki+e].SetLineColor(632+2) #red
                                hFitDict_Minus[ty+var+ki+e].SetLineColor(600-4) #blue
                                hFitDict_Plus[ty+var+ki+e].Draw()
                                hFitDict_Minus[ty+var+ki+e].Draw("SAME")
                                hFitDict_Plus[ty+var+ki+e].GetYaxis().SetTitleOffset(1)
                                hFitDict_Plus[ty+var+ki+e].GetXaxis().SetTitle("P_{T}^{#mu}")

                                if(var=="chi2") :
                                    hFitDict_Plus[ty+var+ki+e].GetYaxis().SetTitle("Reduced #chi^{2}")
                                else :
                                    hFitDict_Plus[ty+var+ki+e].GetYaxis().SetTitle("Par. Value")
                                hFitDict_Plus[ty+var+ki+e].SetTitle("{FitKind} Fit, {var}, {kind} ".format(FitKind=ty,var=var,kind=ki))
                                legDict[ty+var+ki+e] = ROOT.TLegend(0.1,0.7,0.48,0.9)
                                legDict[ty+var+ki+e].AddEntry(hFitDict_Plus[ty+var+ki+e],"W plus")
                                legDict[ty+var+ki+e].AddEntry(hFitDict_Minus[ty+var+ki+e], "W minus")
                                legDict[ty+var+ki+e].Draw("SAME")
                                # canvasList.append(c_EWSF_chi2)
                                canvasList.append(c_fitDict[ty+var+ki+e])


        #---------------------------------------------Fakerate checks PLOTS (region) ---------------------------------------------#
        colorList = [600,616,416,632,432,800,900,881,402]
        c_regionDict = {}
        hregionDict= {}
        ki = self.dataOpt
        for s in self.signList :
            for e in self.etaBinningS :
                c_regionDict['region'+s+ki+e] = ROOT.TCanvas("c_"+'region'+"_"+s+'_'+ki+'_'+e,"c_"+'region'+"_"+s+'_'+ki+'_'+e,800,600)
                c_regionDict['region'+s+ki+e].cd()
                c_regionDict['region'+s+ki+e].SetGridx()
                c_regionDict['region'+s+ki+e].SetGridy()
                i=0
                legDict['region'+s+ki+e] = ROOT.TLegend(0.1,0.7,0.48,0.9)
                for var in ['Cdata', 'Adata', 'Aweak', 'Cweak', 'ratioCA'] :
                    hregionDict['region'+var+ki+e+s] = inputFile.Get("Fakerate/hFakes_pt"+"_"+var+"_"+ki+"_"+s+"_"+e)
                    hregionDict['region'+var+ki+e+s].SetLineWidth(3)
                    hregionDict['region'+var+ki+e+s].SetLineColor(colorList[i]) #red
                    i=i+1
                    hregionDict['region'+var+ki+e+s].GetYaxis().SetTitleOffset(1)
                    hregionDict['region'+var+ki+e+s].GetXaxis().SetTitle("P_{T}^{#mu}")
                    hregionDict['region'+var+ki+e+s].GetYaxis().SetTitle("Events")
                    hregionDict['region'+var+ki+e+s].SetTitle("region count, {var} {sign} eta{eta}, {kind} ".format(var=var,kind=ki,sign=s, eta=e))
                    if var=='Cdata' :
                        hregionDict['region'+var+ki+e+s].Draw()
                    else :
                        hregionDict['region'+var+ki+e+s].Draw("SAME")
                    legDict['region'+s+ki+e].AddEntry(hregionDict['region'+var+ki+e+s],var)
                legDict['region'+s+ki+e].Draw("SAME")
                canvasList.append(c_regionDict['region'+s+ki+e])





        #---------------------------------------------VARIATION OF CUTS PLOTS ---------------------------------------------#

        if(variations) :
            print "Cut Variation plots"

            fileVarDict = {}
            graphVarDict = {}

            for lcut in looseCutList :
                for tcut in tightCutList :
                    fileVarDict[str(lcut)+str(tcut)] = ROOT.TFile.Open(self.outdir+"/bkg_differential_fakerate"+"_"+str(lcut)+"_"+str(tcut)+".root")

            for s in self.signList :
                for e in self.etaBinningS :
                    ptPoint = 1
                    for p in self.ptBinningS :
                        c_variation = ROOT.TCanvas("c_variations_{sign}_{eta}_{pt}".format(sign=s,eta=e,pt=p),"c_variations_{sign}_{eta}_{pt}".format(sign=s,eta=e, pt=p),800,600)
                        c_variation.cd()
                        legDict[e+s+p+"Variation"] = ROOT.TLegend(0.1,0.7,0.48,0.9)
                        tightPoint =0

                        #line of W QCD value
                        h_templW = fileVarDict[str(lcut)+str(tcut)].Get("Template/htempl_pt_prompt_"+s+"_"+e)
                        Wvalue = ROOT.TLine(4,h_templW.GetBinContent(ptPoint),86,h_templW.GetBinContent(ptPoint))
                        Wvalue.SetLineColor(880)
                        Wvalue.SetLineStyle(2)
                        Wvalue.SetLineWidth(3)
                        # print "W VALUE", h_templW.GetBinContent(ptPoint), "sep", s,e, p

                        for tcut in tightCutList :
                            graphVarDict[s+e+p+str(tcut)] = ROOT.TGraphErrors()
                            loosePoint = 0
                            for lcut in looseCutList :
                                h_template = fileVarDict[str(lcut)+str(tcut)].Get("Template/htempl_pt_"+self.dataOpt+"_"+s+"_"+e)
                                graphVarDict[s+e+p+str(tcut)].SetPoint(loosePoint,lcut,h_template.GetBinContent(ptPoint))
                                graphVarDict[s+e+p+str(tcut)].SetPointError(loosePoint,0,h_template.GetBinError(ptPoint))
                                # print "s,e,p", s,e,p,"_____ l-t=",lcut, tcut, loosePoint, tightPoint, "point=",h_template.GetBinContent(ptPoint)
                                loosePoint = loosePoint+1
                            graphVarDict[s+e+p+str(tcut)].SetMarkerColor(tightPoint+1)
                            graphVarDict[s+e+p+str(tcut)].SetLineColor(tightPoint+1)
                            if(tightPoint==0) :
                                graphVarDict[s+e+p+str(tcut)].Draw()
                            else :
                                graphVarDict[s+e+p+str(tcut)].Draw("SAME")  #"P"
                            graphVarDict[s+e+p+str(tcut)].GetXaxis().SetTitle("M_{T} cut [GeV] ")
                            graphVarDict[s+e+p+str(tcut)].GetYaxis().SetTitle("N QCD tight")
                            graphVarDict[s+e+p+str(tcut)].GetYaxis().SetTitleOffset(1)
                            graphVarDict[s+e+p+str(tcut)].SetTitle("QCD tight varying the cuts, {min}<#eta<{max},{pmin}<Pt<{pmax}, W {sign}".format(min=e, max=self.etaBinning[self.etaBinning.index(float(e))+1],pmin=p, pmax=self.ptBinning[self.ptBinning.index(float(p))+1], sign=s))
                            if(tightCutList.index(tcut)==len(tightCutList)-1) :
                                valuemaxX = ROOT.Double(0)
                                valuemaxY = ROOT.Double(0)
                                graphVarDict[s+e+p+str(tcut)].GetPoint(0,valuemaxX,valuemaxY)
                                graphVarDict[s+e+p+str(tightCutList[0])].GetYaxis().SetRangeUser(0,valuemaxY+valuemaxY/20)
                            legDict[e+s+p+"Variation"].AddEntry(graphVarDict[s+e+p+str(tcut)], "Iso<"+str(tcut))
                            tightPoint = tightPoint+1
                        Wvalue.Draw("SAME")
                        legDict[e+s+p+"Variation"].AddEntry(Wvalue, "W MC={val:.0g}".format(val=h_templW.GetBinContent(ptPoint)))
                        legDict[e+s+p+"Variation"].Draw("SAME")
                        ptPoint = ptPoint+1
                        canvasList.append(c_variation)
                        # c_comparison.SaveAs(self.outdir+"/plot/"+c_variation.GetName()+'.png')
            #---------------------------------------------QCD TRENDS with VARIAION OF CUTS PLOTS ---------------------------------------------#
            # print "QCD trends plots"

            for s in self.signList :
                for e in self.etaBinningS :
                    for p in self.ptBinningS :

                        h2qcd = ROOT.TH2F("h2qcd_{sign}_{eta}_{pt}".format(sign=s,eta=e, pt=p),"h2qcd_{sign}_{eta}_{pt}".format(sign=s,eta=e, pt=p),len(looseCutList)-1, array('f',looseCutList), len(tightCutList)-1, array('f',tightCutList) )
                        # tightPoint =0
                        for tcut in tightCutList :
                            # loosePoint = 0
                            if tightCutList.index(tcut)== len(tightCutList)-1 : continue #skip the lat
                            y_t_down = graphVarDict[s+e+p+str(tcut)].GetY()
                            tcutUP = tightCutList[tightCutList.index(tcut)+1]
                            y_t_up = graphVarDict[s+e+p+str(tcutUP)].GetY()
                            diff_list= []
                            for ll in range(len(looseCutList)) :
                                diff_list.append(y_t_up[ll]-y_t_down[ll])
                            for ll in range(len(looseCutList)) :
                                if ll == len(looseCutList)-1 : continue #skip the last
                                valBin = diff_list[ll]-diff_list[ll+1]
                                h2qcd.SetBinContent(ll+1,tightCutList.index(tcut)+1,valBin)
                                # print ll+1, tightCutList.index(tcut)+1, valBin


                        h2qcd.GetXaxis().SetTitle("M_{T} [GeV]")
                        h2qcd.GetYaxis().SetTitle("Relative Isolation")
                        h2qcd.GetYaxis().SetTitleOffset(1)
                        h2qcd.SetTitle("QCD trends, {min}<#eta<{max},{pmin}<Pt<{pmax}, W {sign}".format(min=e, max=self.etaBinning[self.etaBinning.index(float(e))+1],pmin=p, pmax=self.ptBinning[self.ptBinning.index(float(p))+1], sign=s))
                        canvasList.append(h2qcd)
                        c_QCDtrend = ROOT.TCanvas("c_QCDtrend_{sign}_{eta}_{pt}".format(sign=s,eta=e,pt=p),"c_QCDtrend_{sign}_{eta}_{pt}".format(sign=s,eta=e, pt=p),800,600)
                        c_QCDtrend.cd()
                        h2qcd.Draw("lego2z")
                        canvasList.append(c_QCDtrend)
                        # c_comparison.SaveAs(self.outdir+"/plot/"+c_QCDtrend.GetName()+'.png')

        outputFake = ROOT.TFile(self.outdir+"/bkg_plots"+self.corrFitSuff+self.nameSuff+".root","recreate")

        for h in range(len(canvasList)) :
            if "h2qcd" in canvasList[h].GetName() :
                 continue
            else :
                canvasList[h].Write()
                # canvasList[h].SaveAs(self.outdir+"/bkg_plot/"+canvasList[h].GetName()+'.png')

        for h in range(len(canvasList)) :
            if "h2qcd" in canvasList[h].GetName() :
                 continue
            else :
                canvasList[h].IsA().Destructor(canvasList[h])
        
        if self.MarcFit :
            print "ATTENTION: FIT RANGE 25-45, MARC-LIKE TEST!!!"


    def finalPlots(self, outDir,systDict =bkg_systematics, sum2Bands=True,correlatedFit = False, noratio=False) :
        # self.systDict = systDict
        # self.sum2Bands =sum2Bands
        # self.outDir = outDir
        # self.correlatedFit = correlatedFit
        print "plotting (final)..."
        noratio = False

        # NB: if noratio=True In the ratio plots are plotted fake and prompt rate of systematics and nominals


        if self.extraValidationPlots :
            histoNameDict = {
            'comparison' : {
                'Fakes' : ['fake', 'prompt', 'validation']
                },
            'ABCDcheck' : {
                'Fakes' : ['promptSideband','prompt', 'validation','validationSigReg']
                },
            'template' : {
                'templ' : ['fake', 'prompt', 'validation']
                }
            }
        else :
            histoNameDict = {
            'comparison' : {
                'Fakes' : ['fake', 'prompt']
                },
            'template' : {
                'templ' : ['fake', 'prompt']
                }
            }
            
        #getting canvas and histoss
        finalCanvasDict = {}
        finalPlotFileDict = {}
        finalHistoDict = {}
        finalLegDict = {}

        for sKind, sList in systDict.iteritems():
            for sName in sList :
                finalPlotFileDict[sName]=ROOT.TFile.Open(outDir+"/bkg_"+sName+"/bkg_plots"+self.nameSuff+".root")
                for s in self.signList :
                    for e in self.etaBinningS :
                        for canvas in histoNameDict :
                            # finalCanvasDict[sName+canvas+s+e] = finalPlotFileDict[sName].Get('c_'+canvas+'_'+s+'_'+e)
                            for name in histoNameDict[canvas] :
                                for histo in histoNameDict[canvas][name] :
                                    finalHistoDict[sName+canvas+histo+s+e] =   finalPlotFileDict[sName].Get('c_'+canvas+'_'+s+'_'+e).GetPrimitive('h'+name+'_pt_'+histo+'_'+s+'_'+e)
        #nominal
        finalPlotFileDict['nom']=ROOT.TFile.Open(outDir+"/bkg_"+"nom"+"/bkg_plots"+self.corrFitSuff+self.nameSuff+".root")
        for s in self.signList :
            for e in self.etaBinningS :
                for canvas in histoNameDict : #comparison, ABCD...,
                    for name in histoNameDict[canvas] : #Fakes,Fakes, templ....
                        for histo in histoNameDict[canvas][name] : #fake, prompt,....
                            # finalHistoDict['nom'+canvas+histo+s+e] = finalCanvasDict['nom'+canvas+s+e].GetPrimitive('h'+name+'_pt_'+histo+'_'+s+'_'+e)
                            finalHistoDict['nom'+canvas+histo+s+e] = finalPlotFileDict['nom'].Get('c_'+canvas+'_'+s+'_'+e).GetPrimitive('h'+name+'_pt_'+histo+'_'+s+'_'+e)
        
        if correlatedFit: #if correlated fit produce another version of varied template without variation of fake rate
            par4TemplateDict={}
            for kind in ['fake','prompt','histo'] :
                par4TemplateDict[kind+'nom'] = self.hist2dictConverter(syst='nom', kind=kind,outDir=outDir, minimal=False)
                # print "DEBUGDIO PRE0", 
                # print par4TemplateDict[kind+'nom']['Plus2.3']
            # prova = self.bkg_template(kind = self.dataOpt, fakedict=par4TemplateDict['fake'+'nom'], promptdict=par4TemplateDict['prompt'+'nom'], hdict =par4TemplateDict['histo'+'nom'], fit =self.fitOnTemplate, tightcut = self.tightCut, loosecut=self.looseCut, varname = self.varFake, parabolaFit = self.parabolaFit, correlatedFit=False)

            for sKind, sList in systDict.iteritems():
                for sName in sList :
                    par4TemplateDict['prompt'+sName] = self.hist2dictConverter(syst=sName, kind='prompt',outDir=outDir, minimal=False)
                    # print "DEBUGDIO 0", sName
                    # print type(par4TemplateDict['prompt'+sName]['Plus2.3'])
                    # templateCorrelatedFit = self.bkg_template(kind = self.dataOpt, fakedict=par4TemplateDict['fake'+'nom'], promptdict=par4TemplateDict['prompt'+'nom'], hdict =par4TemplateDict['histo'+'nom'], fit =self.fitOnTemplate, tightcut = self.tightCut, loosecut=self.looseCut, varname = self.varFake, parabolaFit = self.parabolaFit, correlatedFit=False)
                    templateCorrelatedFit = self.bkg_template(kind = self.dataOpt, fakedict=par4TemplateDict['fake'+'nom'], promptdict=par4TemplateDict['prompt'+sName], hdict =par4TemplateDict['histo'+'nom'], fit =self.fitOnTemplate, tightcut = self.tightCut, loosecut=self.looseCut, varname = self.varFake, parabolaFit = self.parabolaFit, correlatedFit=False)
                    for s in self.signList :
                        for e in self.etaBinningS :
                            canvas = 'template'
                            histo = 'fake'
                            finalHistoDict[sName+canvas+histo+s+e] = templateCorrelatedFit[s+e]
             
        #building of error bands on the "nom" hisotgrams
        # finalPlotFileDict['nom']=ROOT.TFile.Open(outDir+"/bkg_"+"nom"+"/bkg_plots"+self.nameSuff+".root")
        for s in self.signList :
            for e in self.etaBinningS :
                for canvas in histoNameDict : #comparison, ABCD...,                  
                    finalCanvasDict['nom'+canvas+s+e] = finalPlotFileDict['nom'].Get('c_'+canvas+'_'+s+'_'+e).Clone()
                    finalCanvasDict['nom'+canvas+s+e].cd()
                    fillSyle =0
                    for name in histoNameDict[canvas] : #Fakes,Fakes, templ....
                        for histo in histoNameDict[canvas][name] : #fake, prompt,....
                            # finalHistoDict['nom'+canvas+histo+s+e] = finalCanvasDict['nom'+canvas+s+e].GetPrimitive('h'+name+'_pt_'+histo+'_'+s+'_'+e)
                            finalHistoDict['nom'+canvas+histo+s+e+'error'] = ROOT.TGraphAsymmErrors()#finalCanvasDict['nom'+canvas+s+e]
                            finalHistoDict['nom'+canvas+histo+s+e+'error'].SetName(finalHistoDict['nom'+canvas+histo+s+e].GetName()+'_error')

                            if(correlatedFit and canvas=='comparison' and histo=='fake') : #histo=='fake' is only to select one, this is done once per canvas
                            
                                def createFitGraph(self, offset=par4TemplateDict['fake'+'nom'][s+e+'offset'],slope=par4TemplateDict['fake'+'nom'][s+e+'slope'],key='def') :
                                    fit_func =ROOT.TF1("fit_func_{s}_{e}".format(s=s,e=e), 'pol1',25,66,2)
                                    fit_func.SetParameters(offset,slope)
                                    finalHistoDict['nom'+canvas+s+e+'functionG'+key] = ROOT.TGraphErrors()
                                    npoint = 40
                                    for xg in range(npoint) :
                                        xgraph = 25+xg*40/npoint+0.5*(40/npoint)
                                        finalHistoDict['nom'+canvas+s+e+'functionG'+key].SetPoint(xg,xgraph,fit_func(xgraph))
                                        dx_f = float(abs(xgraph-(25+(xg+1)*40/40+0.5*(40/npoint))))/2
                                        if key=='def' :
                                            errg = math.sqrt(par4TemplateDict['fake'+'nom'][s+e+'offsetErr']**2+(dx_f**2)*(par4TemplateDict['fake'+'nom'][s+e+'slope']**2)+(xgraph**2)*(par4TemplateDict['fake'+'nom'][s+e+'slopeErr']**2)+2*xg*par4TemplateDict['fake'+'nom'][s+e+'offset*slope'])
                                            finalHistoDict['nom'+canvas+s+e+'functionG'+key].SetPointError(xg,dx_f,errg)         
                                    # print "DEBUG", key, offset, slope                

                                offPlus= par4TemplateDict['fake'+'nom'][s+e+'offset']+par4TemplateDict['fake'+'nom'][s+e+'offsetErr']
                                offMinus= par4TemplateDict['fake'+'nom'][s+e+'offset']-par4TemplateDict['fake'+'nom'][s+e+'offsetErr']
                                slopePlus= par4TemplateDict['fake'+'nom'][s+e+'slope']+par4TemplateDict['fake'+'nom'][s+e+'slopeErr']
                                slopeMinus= par4TemplateDict['fake'+'nom'][s+e+'slope']-par4TemplateDict['fake'+'nom'][s+e+'slopeErr']
                                createFitGraph(self)
                                createFitGraph(self, offset=offPlus,key='offsePlus')
                                createFitGraph(self, offset=offMinus,key='offsetMinus')
                                createFitGraph(self, slope=slopePlus,key='slopePlus')
                                createFitGraph(self, slope=slopeMinus,key='slopeMinus')
                                
                                
                                # finalHistoDict['nom'+canvas+s+e+'function'] =ROOT.TF1("fit_func_{s}_{e}".format(s=s,e=e), 'pol1',30,66,2)
                                # finalHistoDict['nom'+canvas+s+e+'function'].SetParameters(float(par4TemplateDict['fake'+'nom'][s+e+'offset']),float(par4TemplateDict['fake'+'nom'][s+e+'slope']) )
                                # # finalHistoDict['nom'+canvas+s+e+'function'].Draw("SAME")
                                # # print "func(30)", finalHistoDict['nom'+canvas+s+e+'function'](30), "func(40)", finalHistoDict['nom'+canvas+s+e+'function'](40), "func(60)", finalHistoDict['nom'+canvas+s+e+'function'](60)
                                # finalHistoDict['nom'+canvas+s+e+'functionG'] = ROOT.TGraphErrors()
                                # for xg in range(35) :
                                #     xgraph = 30+xg*35/35+0.5
                                #     finalHistoDict['nom'+canvas+s+e+'functionG'].SetPoint(xg,xgraph,finalHistoDict['nom'+canvas+s+e+'function'](xgraph))
                                #     dx_f = float(abs(xgraph-(30+(xg+1)*35/35+0.5)))/2
                                #     # print "dx_f=", xg, xgraph,dx_f, 30+(xg+1)*35/35
                                #     errg = math.sqrt(par4TemplateDict['fake'+'nom'][s+e+'offsetErr']**2+(dx_f**2)*(par4TemplateDict['fake'+'nom'][s+e+'slope']**2)+(xgraph**2)*(par4TemplateDict['fake'+'nom'][s+e+'slopeErr']**2)+2*xg*par4TemplateDict['fake'+'nom'][s+e+'offset*slope'])
                                #     print "errore=",s,e,xg, errg
                                #     finalHistoDict['nom'+canvas+s+e+'functionG'].SetPointError(xg,dx_f,errg)
                                



                            for p in self.ptBinning :
                                if(p==self.ptBinning[-1]) : continue
                                varErr = []
                                varErr.append(finalHistoDict['nom'+canvas+histo+s+e].GetBinContent(self.ptBinning.index(float(p))+1))
                                varErrSum2Up = 0
                                varErrSum2Down = 0.
                                for sKind, sList in systDict.iteritems():
                                    # if canvas == 'template' and histo=='prompt' and ('Muon' not in sKind) :
                                    #     print "JUMPED", sKind, sList, canvas, histo
                                        # continue #for data-like template only Muon SF to compare scale of the error
                                    for sName in sList :
                                        varErr.append(finalHistoDict[sName+canvas+histo+s+e].GetBinContent(self.ptBinning.index(float(p))+1))
                                        if "Up" in sName :
                                            varErrSum2Up = varErrSum2Up+ (finalHistoDict[sName+canvas+histo+s+e].GetBinContent(self.ptBinning.index(float(p))+1)-finalHistoDict['nom'+canvas+histo+s+e].GetBinContent(self.ptBinning.index(float(p))+1))**2
                                        if "Down" in sName :
                                            varErrSum2Down = varErrSum2Down+ (finalHistoDict[sName+canvas+histo+s+e].GetBinContent(self.ptBinning.index(float(p))+1)-finalHistoDict['nom'+canvas+histo+s+e].GetBinContent(self.ptBinning.index(float(p))+1))**2
                                varErrSum2Up = math.sqrt(varErrSum2Up)
                                varErrSum2Down = math.sqrt(varErrSum2Down)
                                varErr.sort()
                                minBand = varErr[0]
                                maxBand = varErr[len(varErr)-1]
                                errLow = finalHistoDict['nom'+canvas+histo+s+e].GetBinContent(self.ptBinning.index(float(p))+1)-minBand
                                errHigh = maxBand-finalHistoDict['nom'+canvas+histo+s+e].GetBinContent(self.ptBinning.index(float(p))+1)
                                if sum2Bands :
                                    errLow = varErrSum2Down
                                    errHigh = varErrSum2Up
                                    # if histo == 'fake' and canvas =='comparison': #debug lines
                                        # errsyst = varErrSum2Up#sabs(varErrSum2Down)+abs(varErrSum2Up)/2
                                        # errsyst = errsyst**2
                                        # errstat = finalHistoDict['nom'+canvas+histo+s+e].GetBinError(self.ptBinning.index(float(p))+1)
                                        # errstat=errstat**2
                                        # print "PLOT: bin=",s,e,p, sName, "fake=",finalHistoDict['nom'+canvas+histo+s+e].GetBinContent(self.ptBinning.index(float(p))+1), "varied=",finalHistoDict['puWeightUp'+canvas+histo+s+e].GetBinContent(self.ptBinning.index(float(p))+1),",   err (syst)=", errsyst, ",    err(stat)=", errstat, ", ratio syst/stat=", errsyst/errstat
                                # symBand = (maxBand-minBand)/2
                                # print "WARNING: SYMMETRIC BANDS FOR SYST USED!!!"
                                # finalHistoDict['nom'+canvas+histo+s+e+'error'].SetBinError(self.ptBinning.index(float(p))+1,symBand)
                                finalHistoDict['nom'+canvas+histo+s+e+'error'].SetPoint(self.ptBinning.index(float(p)),finalHistoDict['nom'+canvas+histo+s+e].GetBinCenter(self.ptBinning.index(float(p))+1),finalHistoDict['nom'+canvas+histo+s+e].GetBinContent(self.ptBinning.index(float(p))+1))
                                finalHistoDict['nom'+canvas+histo+s+e+'error'].SetPointEYhigh(self.ptBinning.index(float(p)),errHigh)
                                finalHistoDict['nom'+canvas+histo+s+e+'error'].SetPointEYlow(self.ptBinning.index(float(p)),errLow)
                                finalHistoDict['nom'+canvas+histo+s+e+'error'].SetPointEXhigh(self.ptBinning.index(float(p)),finalHistoDict['nom'+canvas+histo+s+e].GetBinWidth(self.ptBinning.index(float(p))+1)/2)
                                finalHistoDict['nom'+canvas+histo+s+e+'error'].SetPointEXlow(self.ptBinning.index(float(p)),finalHistoDict['nom'+canvas+histo+s+e].GetBinWidth(self.ptBinning.index(float(p))+1)/2)

                            finalHistoDict['nom'+canvas+histo+s+e+'error'].SetLineColor(finalHistoDict['nom'+canvas+histo+s+e].GetLineColor()-3)
                            finalHistoDict['nom'+canvas+histo+s+e+'error'].SetMarkerColor(finalHistoDict['nom'+canvas+histo+s+e].GetLineColor()-3)
                            finalHistoDict['nom'+canvas+histo+s+e+'error'].SetFillColor(finalHistoDict['nom'+canvas+histo+s+e].GetLineColor()-3)
                            finalHistoDict['nom'+canvas+histo+s+e+'error'].SetFillStyle(3003+fillSyle)
                            finalHistoDict['nom'+canvas+histo+s+e+'error'].SetLineWidth(1)

                            finalHistoDict['nom'+canvas+histo+s+e+'error'].Draw("SAME 0P5")
                            if(correlatedFit and canvas=='comparison' and histo=='fake') :
                                keyList = ['def','offsePlus','offsetMinus','slopePlus','slopeMinus']
                                for key in keyList :
                                    finalHistoDict['nom'+canvas+s+e+'functionG'+key].Draw("SAME")
                                    finalHistoDict['nom'+canvas+s+e+'functionG'+key].SetLineWidth(3)
                                    finalHistoDict['nom'+canvas+s+e+'functionG'+key].SetLineColor(2+keyList.index(key))


                            finalCanvasDict['nom'+canvas+s+e].Update()
                            finalCanvasDict['nom'+canvas+s+e].Modified()
                            fillSyle =fillSyle+1

                            # c1 = finalCanvasDict['nom'+canvas+s+e].Clone()
                            # c1.cd()
                            # c1.Update()
                            # c1.Modified()
                            # c1.Write()
                            # finalCanvasDict['nom'+canvas+s+e].Write()
                            # outputFinal.cd()

        #ratio plot creation
        for s in self.signList :
            for e in self.etaBinningS :
                for canvas in histoNameDict :
                    for name in histoNameDict[canvas] :
                        for histo in histoNameDict[canvas][name] :
                            c_ratioSyst = ROOT.TCanvas("c_ratioSyst_{sign}_{eta}_{canvas}_{histo}".format(sign=s,eta=e,canvas=canvas,histo=histo),"c_ratioSyst_{sign}_{eta}_{canvas}_{histo}".format(sign=s,eta=e,canvas=canvas,histo=histo),800,600)
                            c_ratioSyst.cd()
                            c_ratioSyst.SetGridx()
                            c_ratioSyst.SetGridy()
                            finalLegDict[e+s+canvas+histo+"ratioSyst"] = ROOT.TLegend(0.1,0.7,0.48,0.9)

                            sameFlag = True
                            colorNumber = 1
                            colorList = [600,616,416,632,432,800,900]
                            colorCounter = 0

                            for sKind, sList in systDict.iteritems():
                                colorNumber = colorList[colorCounter]
                                colorCounter = colorCounter+1
                                for sName in sList :
                                    colorNumber = colorNumber-2
                                    if colorNumber < colorList[colorCounter-1]-10 :
                                        colorNumber = colorList[colorCounter]+2
                                    finalHistoDict[sName+canvas+histo+s+e+'ratio'] = ROOT.TH1F(canvas+'_'+finalHistoDict[sName+canvas+histo+s+e].GetName()+'_'+sName+'_ratio',canvas+'_'+finalHistoDict[sName+canvas+histo+s+e].GetName()+'_'+sName+'_ratio',len(self.ptBinning)-1, array('f',self.ptBinning))
                                    finalHistoDict[sName+canvas+histo+s+e+'ratio'].Divide(finalHistoDict[sName+canvas+histo+s+e],finalHistoDict['nom'+canvas+histo+s+e],1,1)
                                    if noratio :
                                        finalHistoDict[sName+canvas+histo+s+e+'ratio'] = finalHistoDict[sName+canvas+histo+s+e].Clone()

                                    finalHistoDict[sName+canvas+histo+s+e+'ratio'].SetLineColor(colorNumber)
                                    for b in range(1,finalHistoDict[sName+canvas+histo+s+e+'ratio'].GetNbinsX()+1) :
                                        finalHistoDict[sName+canvas+histo+s+e+'ratio'].SetBinError(b,0)
                                    c_ratioSyst.cd()
                                    if sameFlag :
                                        finalHistoDict[sName+canvas+histo+s+e+'ratio'].Draw()
                                        finalHistoDict[sName+canvas+histo+s+e+'ratio'].GetYaxis().SetRangeUser(0.6,1.7)
                                    else :
                                        finalHistoDict[sName+canvas+histo+s+e+'ratio'].Draw("SAME")
                                        finalHistoDict[sName+canvas+histo+s+e+'ratio'].GetYaxis().SetRangeUser(0,3)
                                    finalHistoDict[sName+canvas+histo+s+e+'ratio'].SetLineWidth(3)
                                    sameFlag=False
                                    finalLegDict[e+s+canvas+histo+"ratioSyst"].AddEntry(finalHistoDict[sName+canvas+histo+s+e+'ratio'], sName)

                            #nominal
                            finalHistoDict['nom'+canvas+histo+s+e+'ratio'] = ROOT.TH1F(canvas+'_'+finalHistoDict['nom'+canvas+histo+s+e].GetName()+'_'+'nom'+'_ratio',canvas+'_'+finalHistoDict['nom'+canvas+histo+s+e].GetName()+'_'+'nom'+'_ratio',len(self.ptBinning)-1, array('f',self.ptBinning))
                            finalHistoDict['nom'+canvas+histo+s+e+'ratio'].Divide(finalHistoDict['nom'+canvas+histo+s+e],finalHistoDict['nom'+canvas+histo+s+e],1,1)
                            if noratio :
                                finalHistoDict['nom'+canvas+histo+s+e+'ratio'] =finalHistoDict['nom'+canvas+histo+s+e].Clone()

                            finalHistoDict['nom'+canvas+histo+s+e+'ratio'].SetLineColor(1)
                            for b in range(1,finalHistoDict['nom'+canvas+histo+s+e+'ratio'].GetNbinsX()+1) :
                                # print "DEBUG=", s,e, canvas, histo, b, finalHistoDict['nom'+canvas+histo+s+e].GetBinContent(b)
                                # finalHistoDict['nom'+canvas+histo+s+e+'ratio'].SetBinError(b,math.sqrt(2)*finalHistoDict['nom'+canvas+histo+s+e].GetBinError(b)/finalHistoDict['nom'+canvas+histo+s+e].GetBinContent(b))
                                if finalHistoDict['nom'+canvas+histo+s+e].GetBinContent(b)!=0 :
                                    finalHistoDict['nom'+canvas+histo+s+e+'ratio'].SetBinError(b,finalHistoDict['nom'+canvas+histo+s+e].GetBinError(b)/finalHistoDict['nom'+canvas+histo+s+e].GetBinContent(b))
                                else :
                                     print "WARNING: bin content of ", canvas, histo, "is 0, bin (s,e,p)=", s,e,b, ". error of ratio plot not correctly normalized."
                                     finalHistoDict['nom'+canvas+histo+s+e+'ratio'].SetBinError(b,finalHistoDict['nom'+canvas+histo+s+e].GetBinError(b))
                            c_ratioSyst.cd()
                            finalHistoDict['nom'+canvas+histo+s+e+'ratio'].Draw("SAME E2")
                            finalHistoDict['nom'+canvas+histo+s+e+'ratio'].GetYaxis().SetRangeUser(0,3)
                            finalHistoDict['nom'+canvas+histo+s+e+'ratio'].SetLineWidth(0)
                            finalHistoDict['nom'+canvas+histo+s+e+'ratio'].SetFillColor(1)
                            finalHistoDict['nom'+canvas+histo+s+e+'ratio'].SetFillStyle(3002)
                            finalLegDict[e+s+canvas+histo+"ratioSyst"].AddEntry(finalHistoDict['nom'+canvas+histo+s+e+'ratio'], 'Nominal')


                            #sum2 errorband in the ratios (DISABLED, set=1 se vuoi vedere la banda dei sum2 sui ratio)
                            sum2Flag = 0
                            if sum2Flag :
                                finalHistoDict['nom'+canvas+histo+s+e+'ratio_sum2'] = ROOT.TGraphAsymmErrors()
                                finalHistoDict['nom'+canvas+histo+s+e+'ratio_sum2'].SetName(canvas+'_'+finalHistoDict['nom'+canvas+histo+s+e].GetName()+'_'+'nom'+'_ratio_sum2')
                                finalHistoDict['nom'+canvas+histo+s+e+'ratio_sum2'].SetLineColor(2)
                                for p in self.ptBinning :
                                    if(p==self.ptBinning[-1]) : continue
                                    bin_p = self.ptBinning.index(float(p))
                                    finalHistoDict['nom'+canvas+histo+s+e+'ratio_sum2'].SetPoint(bin_p,finalHistoDict['nom'+canvas+histo+s+e].GetBinCenter(bin_p+1),1)
                                    finalHistoDict['nom'+canvas+histo+s+e+'ratio_sum2'].SetPointEYhigh(bin_p,finalHistoDict['nom'+canvas+histo+s+e+'error'].GetErrorYhigh(bin_p)/finalHistoDict['nom'+canvas+histo+s+e].GetBinContent(bin_p+1))
                                    finalHistoDict['nom'+canvas+histo+s+e+'ratio_sum2'].SetPointEYlow(bin_p,finalHistoDict['nom'+canvas+histo+s+e+'error'].GetErrorYlow(bin_p)/finalHistoDict['nom'+canvas+histo+s+e].GetBinContent(bin_p+1))
                                    finalHistoDict['nom'+canvas+histo+s+e+'ratio_sum2'].SetPointEXhigh(bin_p,finalHistoDict['nom'+canvas+histo+s+e+'error'].GetErrorXhigh(bin_p))
                                    finalHistoDict['nom'+canvas+histo+s+e+'ratio_sum2'].SetPointEXlow(bin_p,finalHistoDict['nom'+canvas+histo+s+e+'error'].GetErrorXlow(bin_p))
                                c_ratioSyst.cd()
                                finalHistoDict['nom'+canvas+histo+s+e+'ratio_sum2'].Draw("SAME OP5")
                                finalHistoDict['nom'+canvas+histo+s+e+'ratio_sum2'].SetLineWidth(1)
                                finalHistoDict['nom'+canvas+histo+s+e+'ratio_sum2'].SetFillColor(2)
                                finalHistoDict['nom'+canvas+histo+s+e+'ratio_sum2'].SetFillStyle(3016)
                                finalLegDict[e+s+canvas+histo+"ratioSyst"].AddEntry(finalHistoDict['nom'+canvas+histo+s+e+'ratio_sum2'], 'Square Sum')

                            finalLegDict[e+s+canvas+histo+"ratioSyst"].Draw("SAME")
                            finalCanvasDict['ratio'+canvas+histo+s+e] = c_ratioSyst

        #sum2 errorband in the ratios
        for s in self.signList :
            for e in self.etaBinningS :
                c_errCompare = ROOT.TCanvas("c_errCompare_{sign}_{eta}".format(sign=s,eta=e),"c_errCompare_{sign}_{eta}".format(sign=s,eta=e),800,600)
                c_errCompare.cd()
                c_errCompare.SetGridx()
                c_errCompare.SetGridy()
                finalLegDict[e+s+'errCompare'] = ROOT.TLegend(0.1,0.7,0.48,0.9)
                canvas = 'template'
                for histo in ['fake','prompt'] :
                            finalHistoDict['nom'+canvas+histo+s+e+'sum2'] = ROOT.TGraphAsymmErrors()
                            finalHistoDict['nom'+canvas+histo+s+e+'sum2'].SetName(canvas+'_'+finalHistoDict['nom'+canvas+histo+s+e].GetName()+'_'+'nom'+'_ratio_sum2')

                            for p in self.ptBinning :
                                if(p==self.ptBinning[-1]) : continue
                                bin_p = self.ptBinning.index(float(p))
                                finalHistoDict['nom'+canvas+histo+s+e+'sum2'].SetPoint(bin_p,finalHistoDict['nom'+canvas+histo+s+e].GetBinCenter(bin_p+1),1)
                                finalHistoDict['nom'+canvas+histo+s+e+'sum2'].SetPointEYhigh(bin_p,math.sqrt(finalHistoDict['nom'+canvas+histo+s+e+'error'].GetErrorYhigh(bin_p)**2+finalHistoDict['nom'+canvas+histo+s+e].GetBinError(bin_p+1)**2))
                                finalHistoDict['nom'+canvas+histo+s+e+'sum2'].SetPointEYlow(bin_p,math.sqrt(finalHistoDict['nom'+canvas+histo+s+e+'error'].GetErrorYlow(bin_p)**2+finalHistoDict['nom'+canvas+histo+s+e].GetBinError(bin_p+1)**2))
                                finalHistoDict['nom'+canvas+histo+s+e+'sum2'].SetPointEXhigh(bin_p,finalHistoDict['nom'+canvas+histo+s+e+'error'].GetErrorXhigh(bin_p))
                                finalHistoDict['nom'+canvas+histo+s+e+'sum2'].SetPointEXlow(bin_p,finalHistoDict['nom'+canvas+histo+s+e+'error'].GetErrorXlow(bin_p))
                                # print "DEBUG Err compare: bin", s,e, p, bin_p, histo, ", values (x, dy+,dy-,dx+,dx-)",  
                                # print finalHistoDict['nom'+canvas+histo+s+e].GetBinCenter(bin_p+1),
                                # print math.sqrt(finalHistoDict['nom'+canvas+histo+s+e+'error'].GetErrorYhigh(bin_p)**2+finalHistoDict['nom'+canvas+histo+s+e].GetBinError(bin_p+1)**2),
                                # print math.sqrt(finalHistoDict['nom'+canvas+histo+s+e+'error'].GetErrorYlow(bin_p)**2+finalHistoDict['nom'+canvas+histo+s+e].GetBinError(bin_p+1)**2),
                                # print finalHistoDict['nom'+canvas+histo+s+e+'error'].GetErrorXhigh(bin_p), finalHistoDict['nom'+canvas+histo+s+e+'error'].GetErrorXlow(bin_p)
                                # if correlatedFit :
                                    # print "only if prompt rate syst is negligible"
                                    # finalHistoDict['nom'+canvas+histo+s+e+'sum2'].SetPointEYhigh(bin_p,finalHistoDict['nom'+canvas+histo+s+e].GetBinError(bin_p))
                                    # finalHistoDict['nom'+canvas+histo+s+e+'sum2'].SetPointEYlow(bin_p,finalHistoDict['nom'+canvas+histo+s+e].GetBinError(bin_p))

                            c_errCompare.cd()
                            if histo == 'fake' :
                                finalHistoDict['nom'+canvas+histo+s+e+'sum2'].Draw()
                                finalHistoDict['nom'+canvas+histo+s+e+'sum2'].Draw("SAME 5")
                                finalHistoDict['nom'+canvas+histo+s+e+'sum2'].SetLineColor(632+2) #red
                                finalHistoDict['nom'+canvas+histo+s+e+'sum2'].SetFillColor(632+2) #red
                                finalHistoDict['nom'+canvas+histo+s+e+'sum2'].SetFillStyle(3002)
                            else:
                                finalHistoDict['nom'+canvas+histo+s+e+'sum2'].Draw("SAME 5")
                                finalHistoDict['nom'+canvas+histo+s+e+'sum2'].SetLineColor(600-4) #blue
                                finalHistoDict['nom'+canvas+histo+s+e+'sum2'].SetFillColor(600-4) #blue
                                finalHistoDict['nom'+canvas+histo+s+e+'sum2'].SetFillStyle(3005)
                            finalHistoDict['nom'+canvas+histo+s+e+'sum2'].SetLineWidth(1)

                            finalLegDict[e+s+'errCompare'].AddEntry(finalHistoDict['nom'+canvas+histo+s+e+'sum2'], histo)
                finalCanvasDict['sum2Error'+s+e] = c_errCompare


        #unrolled plot creation

        #binning
        unrolledPtEta= list(self.ptBinning)
        # lastPtValue = self.ptBinning[-1]
        # lastPtValue = 100 #here set to 100 the unroll limit to read clearly the pt
        intervalPtBin = []
        for p in self.ptBinning[:-1] :
            intervalPtBin.append(self.ptBinning[self.ptBinning.index(p)+1]-self.ptBinning[self.ptBinning.index(p)])

        for e in range(len(self.etaBinning)-2) :
            for p in intervalPtBin :
                unrolledPtEta.append(unrolledPtEta[-1]+p)
        print "unrolledPtEta", unrolledPtEta

        #final plot and syst
        for s in self.signList :
            for canvas in histoNameDict :
                c_unrolled = ROOT.TCanvas("c_unrolled_{canvas}_{sign}".format(canvas=canvas,sign=s),"c_unrolled_{canvas}_{sign}".format(canvas=canvas,sign=s),800,600)
                c_unrolled.cd()
                c_unrolled.SetGridx()
                c_unrolled.SetGridy()
                finalLegDict[s+canvas+'unrolled'] = ROOT.TLegend(0.1,0.7,0.48,0.9)
                sameFlagUNR=True
                for name in histoNameDict[canvas] :
                    for histo in histoNameDict[canvas][name] :
                        finalHistoDict[s+canvas+histo+'unrolled'] = ROOT.TH1F(canvas+'_'+finalHistoDict['nom'+canvas+histo+s+'0'].GetName()+'_unrolled',canvas+'_'+finalHistoDict['nom'+canvas+histo+s+'0'].GetName()+'_unrolled',len(unrolledPtEta)-1, array('f',unrolledPtEta))
                        finalHistoDict[s+canvas+histo+'unrolled'].SetLineColor(finalHistoDict['nom'+canvas+histo+s+'0'].GetLineColor())
                        finalHistoDict[s+canvas+histo+'unrolled'].SetLineWidth(finalHistoDict['nom'+canvas+histo+s+'0'].GetLineWidth())
                        finalHistoDict[s+canvas+histo+'unrolled'].GetXaxis().SetTitle(finalHistoDict['nom'+canvas+histo+s+'0'].GetXaxis().GetTitle())
                        finalHistoDict[s+canvas+histo+'unrolled'].GetYaxis().SetTitle(finalHistoDict['nom'+canvas+histo+s+'0'].GetYaxis().GetTitle())

                        finalHistoDict[s+canvas+histo+'unrolled'+'error'] = ROOT.TGraphAsymmErrors()
                        finalHistoDict[s+canvas+histo+'unrolled'+'error'].SetName(finalHistoDict[s+canvas+histo+'unrolled'].GetName()+'_error')
                        finalHistoDict[s+canvas+histo+'unrolled'+'error'].SetLineColor(finalHistoDict['nom'+canvas+histo+s+'0'+'error'].GetLineColor())
                        finalHistoDict[s+canvas+histo+'unrolled'+'error'].SetMarkerColor(finalHistoDict['nom'+canvas+histo+s+'0'+'error'].GetLineColor())
                        finalHistoDict[s+canvas+histo+'unrolled'+'error'].SetFillColor(finalHistoDict['nom'+canvas+histo+s+'0'+'error'].GetLineColor())
                        finalHistoDict[s+canvas+histo+'unrolled'+'error'].SetFillStyle(finalHistoDict['nom'+canvas+histo+s+'0'+'error'].GetFillStyle())
                        finalHistoDict[s+canvas+histo+'unrolled'+'error'].SetLineWidth(finalHistoDict['nom'+canvas+histo+s+'0'+'error'].GetLineWidth())



                        for e in self.etaBinningS :
                            for p in self.ptBinningS :
                                indexUNR = self.etaBinning.index(float(e))*len(self.ptBinningS)+self.ptBinning.index(float(p))
                                finalHistoDict[s+canvas+histo+'unrolled'].SetBinContent(indexUNR+1,finalHistoDict['nom'+canvas+histo+s+e].GetBinContent(self.ptBinning.index(float(p))+1))
                                finalHistoDict[s+canvas+histo+'unrolled'].SetBinError(indexUNR+1,finalHistoDict['nom'+canvas+histo+s+e].GetBinError(self.ptBinning.index(float(p))+1))

                                finalHistoDict[s+canvas+histo+'unrolled'+'error'].SetPoint(indexUNR,finalHistoDict[s+canvas+histo+'unrolled'].GetBinCenter(indexUNR+1),finalHistoDict[s+canvas+histo+'unrolled'].GetBinContent(indexUNR+1))
                                finalHistoDict[s+canvas+histo+'unrolled'+'error'].SetPointEYhigh(indexUNR,finalHistoDict['nom'+canvas+histo+s+e+'error'].GetErrorYhigh(self.ptBinning.index(float(p))))
                                finalHistoDict[s+canvas+histo+'unrolled'+'error'].SetPointEYlow(indexUNR,finalHistoDict['nom'+canvas+histo+s+e+'error'].GetErrorYlow(self.ptBinning.index(float(p))))
                                finalHistoDict[s+canvas+histo+'unrolled'+'error'].SetPointEXhigh(indexUNR,finalHistoDict[s+canvas+histo+'unrolled'].GetBinWidth(indexUNR+1)/2)
                                finalHistoDict[s+canvas+histo+'unrolled'+'error'].SetPointEXlow(indexUNR,finalHistoDict[s+canvas+histo+'unrolled'].GetBinWidth(indexUNR+1)/2)

                        if sameFlagUNR :
                            finalHistoDict[s+canvas+histo+'unrolled'].Draw()
                            if(canvas!="template") :
                                finalHistoDict[s+canvas+histo+'unrolled'].GetYaxis().SetRangeUser(0,1.1)
                        else :
                            finalHistoDict[s+canvas+histo+'unrolled'].Draw("SAME")
                        sameFlagUNR=False
                        finalLegDict[s+canvas+'unrolled'].AddEntry(finalHistoDict[s+canvas+histo+'unrolled'], histo)
                        finalHistoDict[s+canvas+histo+'unrolled'+'error'].Draw("SAME 0P5")
                finalLegDict[s+canvas+'unrolled'].Draw("SAME")
                finalCanvasDict['unrolled'+canvas+histo+s] = c_unrolled


        #ratios unrolled
        for s in self.signList :
            for canvas in histoNameDict :
                for name in histoNameDict[canvas] :
                    for histo in histoNameDict[canvas][name] :
                        c_ratioSyst_unrolled = ROOT.TCanvas("c_ratioSyst_unrolled_{sign}_{canvas}_{histo}".format(sign=s,canvas=canvas,histo=histo),"c_ratioSyst_unrolled_{sign}_{canvas}_{histo}".format(sign=s,canvas=canvas,histo=histo),800,600)
                        c_ratioSyst_unrolled.cd()
                        c_ratioSyst_unrolled.SetGridx()
                        c_ratioSyst_unrolled.SetGridy()
                        finalLegDict[s+canvas+histo+"ratioSyst_unrolled"] = ROOT.TLegend(0.1,0.7,0.48,0.9)

                        sameFlagUNR = True

                        for sKind, sList in systDict.iteritems():
                            for sName in sList :
                                finalHistoDict[sName+s+canvas+histo+'ratio_unrolled'] = ROOT.TH1F(finalHistoDict[sName+canvas+histo+s+'0ratio'].GetName()+'_ratio_unrolled',finalHistoDict[sName+canvas+histo+s+'0ratio'].GetName()+'_ratio_unrolled',len(unrolledPtEta)-1, array('f',unrolledPtEta))
                                finalHistoDict[sName+s+canvas+histo+'ratio_unrolled'].SetLineColor(finalHistoDict[sName+canvas+histo+s+'0ratio'].GetLineColor())
                                finalHistoDict[sName+s+canvas+histo+'ratio_unrolled'].SetLineWidth(finalHistoDict[sName+canvas+histo+s+'0ratio'].GetLineWidth())
                                finalHistoDict[sName+s+canvas+histo+'ratio_unrolled'].GetXaxis().SetTitle(finalHistoDict[sName+canvas+histo+s+'0ratio'].GetXaxis().GetTitle())
                                finalHistoDict[sName+s+canvas+histo+'ratio_unrolled'].GetYaxis().SetTitle(finalHistoDict[sName+canvas+histo+s+'0ratio'].GetYaxis().GetTitle())

                                for e in self.etaBinningS :
                                    for p in self.ptBinningS :
                                        indexUNR = self.etaBinning.index(float(e))*len(self.ptBinningS)+self.ptBinning.index(float(p))
                                        finalHistoDict[sName+s+canvas+histo+'ratio_unrolled'].SetBinContent(indexUNR+1,finalHistoDict[sName+canvas+histo+s+e+'ratio'].GetBinContent(self.ptBinning.index(float(p))+1))
                                        finalHistoDict[sName+s+canvas+histo+'ratio_unrolled'].SetBinError(indexUNR+1,finalHistoDict[sName+canvas+histo+s+e+'ratio'].GetBinError(self.ptBinning.index(float(p))+1))
                                c_ratioSyst_unrolled.cd()
                                if sameFlagUNR :
                                    finalHistoDict[sName+s+canvas+histo+'ratio_unrolled'].Draw()
                                    finalHistoDict[sName+s+canvas+histo+'ratio_unrolled'].GetYaxis().SetRangeUser(0.6,1.7)
                                else :
                                    finalHistoDict[sName+s+canvas+histo+'ratio_unrolled'].Draw("SAME")
                                    finalHistoDict[sName+s+canvas+histo+'ratio_unrolled'].GetYaxis().SetRangeUser(0,3)
                                finalHistoDict[sName+s+canvas+histo+'ratio_unrolled'].SetLineWidth(3)
                                sameFlagUNR=False
                                finalLegDict[s+canvas+histo+"ratioSyst_unrolled"].AddEntry(finalHistoDict[sName+s+canvas+histo+'ratio_unrolled'], sName)

                        #nominal
                        finalHistoDict['nom'+s+canvas+histo+'ratio_unrolled'] = ROOT.TH1F(finalHistoDict['nom'+canvas+histo+s+'0ratio'].GetName()+'_ratio_unrolled',finalHistoDict['nom'+canvas+histo+s+'0ratio'].GetName()+'_ratio_unrolled',len(unrolledPtEta)-1, array('f',unrolledPtEta))
                        finalHistoDict['nom'+s+canvas+histo+'ratio_unrolled'].SetLineColor(finalHistoDict['nom'+canvas+histo+s+'0ratio'].GetLineColor())
                        finalHistoDict['nom'+s+canvas+histo+'ratio_unrolled'].SetLineWidth(finalHistoDict['nom'+canvas+histo+s+'0ratio'].GetLineWidth())
                        finalHistoDict['nom'+s+canvas+histo+'ratio_unrolled'].GetXaxis().SetTitle(finalHistoDict['nom'+canvas+histo+s+'0ratio'].GetXaxis().GetTitle())
                        finalHistoDict['nom'+s+canvas+histo+'ratio_unrolled'].GetYaxis().SetTitle(finalHistoDict['nom'+canvas+histo+s+'0ratio'].GetYaxis().GetTitle())
                        for e in self.etaBinningS :
                            for p in self.ptBinningS :
                                indexUNR = self.etaBinning.index(float(e))*len(self.ptBinningS)+self.ptBinning.index(float(p))
                                # print "index=", indexUNR, ", set=",indexUNR+1, "get=", self.ptBinning.index(float(p))+1
                                finalHistoDict['nom'+s+canvas+histo+'ratio_unrolled'].SetBinContent(indexUNR+1,finalHistoDict['nom'+canvas+histo+s+e+'ratio'].GetBinContent(self.ptBinning.index(float(p))+1))
                                finalHistoDict['nom'+s+canvas+histo+'ratio_unrolled'].SetBinError(indexUNR+1,finalHistoDict['nom'+canvas+histo+s+e+'ratio'].GetBinError(self.ptBinning.index(float(p))+1))
                        c_ratioSyst_unrolled.cd()
                        finalHistoDict['nom'+s+canvas+histo+'ratio_unrolled'].Draw("SAME E2")
                        finalHistoDict['nom'+s+canvas+histo+'ratio_unrolled'].GetYaxis().SetRangeUser(0,3)
                        finalHistoDict['nom'+s+canvas+histo+'ratio_unrolled'].SetLineWidth(0)
                        finalHistoDict['nom'+s+canvas+histo+'ratio_unrolled'].SetFillColor(1)
                        finalHistoDict['nom'+s+canvas+histo+'ratio_unrolled'].SetFillStyle(3002)
                        finalLegDict[s+canvas+histo+"ratioSyst_unrolled"].AddEntry(finalHistoDict['nom'+s+canvas+histo+'ratio_unrolled'], 'Nominal')

                        #sum2 errorband in the ratios (DISABLED!)
                        sum2Flag_unr = 0
                        if sum2Flag_unr :
                            finalHistoDict[s+canvas+histo+'unrolled'+'ratio_sum2'] = ROOT.TGraphAsymmErrors()
                            finalHistoDict[s+canvas+histo+'unrolled'+'ratio_sum2'].SetName(finalHistoDict[s+canvas+histo+'unrolled'].GetName()+'_ratio_sum2')
                            finalHistoDict[s+canvas+histo+'unrolled'+'ratio_sum2'].SetLineColor(finalHistoDict['nom'+canvas+histo+s+'0'+'ratio_sum2'].GetLineColor())
                            finalHistoDict[s+canvas+histo+'unrolled'+'ratio_sum2'].SetMarkerColor(finalHistoDict['nom'+canvas+histo+s+'0'+'ratio_sum2'].GetLineColor())
                            finalHistoDict[s+canvas+histo+'unrolled'+'ratio_sum2'].SetFillColor(finalHistoDict['nom'+canvas+histo+s+'0'+'ratio_sum2'].GetLineColor())
                            finalHistoDict[s+canvas+histo+'unrolled'+'ratio_sum2'].SetFillStyle(finalHistoDict['nom'+canvas+histo+s+'0'+'ratio_sum2'].GetFillStyle())
                            finalHistoDict[s+canvas+histo+'unrolled'+'ratio_sum2'].SetLineWidth(finalHistoDict['nom'+canvas+histo+s+'0'+'ratio_sum2'].GetLineWidth())
                            for e in self.etaBinningS :
                                for p in self.ptBinningS :
                                    indexUNR = self.etaBinning.index(float(e))*len(self.ptBinningS)+self.ptBinning.index(float(p))
                                    finalHistoDict[s+canvas+histo+'unrolled'+'ratio_sum2'].SetPoint(indexUNR,finalHistoDict[s+canvas+histo+'unrolled'].GetBinCenter(indexUNR+1),1)
                                    finalHistoDict[s+canvas+histo+'unrolled'+'ratio_sum2'].SetPointEYhigh(indexUNR,finalHistoDict['nom'+canvas+histo+s+e+'ratio_sum2'].GetErrorYhigh(self.ptBinning.index(float(p))))
                                    finalHistoDict[s+canvas+histo+'unrolled'+'ratio_sum2'].SetPointEYlow(indexUNR,finalHistoDict['nom'+canvas+histo+s+e+'ratio_sum2'].GetErrorYlow(self.ptBinning.index(float(p))))
                                    finalHistoDict[s+canvas+histo+'unrolled'+'ratio_sum2'].SetPointEXhigh(indexUNR,finalHistoDict[s+canvas+histo+'unrolled'].GetBinWidth(indexUNR+1)/2)
                                    finalHistoDict[s+canvas+histo+'unrolled'+'ratio_sum2'].SetPointEXlow(indexUNR,finalHistoDict[s+canvas+histo+'unrolled'].GetBinWidth(indexUNR+1)/2)
                            # finalHistoDict[s+canvas+histo+'unrolled'+'ratio_sum2'].Draw("SAME 0P5")
                            finalLegDict[s+canvas+histo+"ratioSyst_unrolled"].AddEntry(finalHistoDict[s+canvas+histo+'unrolled'+'ratio_sum2'], 'Square Sum')

                        finalLegDict[s+canvas+histo+"ratioSyst_unrolled"].Draw("SAME")
                        finalCanvasDict['ratio_unrolled'+canvas+histo+s] = c_ratioSyst_unrolled


        #unrolled sum2 errorbands canvas
        for s in self.signList :
            c_errCompare_unrolled = ROOT.TCanvas("c_errCompare_unrolled_{sign}".format(sign=s),"c_errCompare_unrolled_{sign}".format(sign=s),800,600)
            c_errCompare_unrolled.cd()
            c_errCompare_unrolled.SetGridx()
            c_errCompare_unrolled.SetGridy()
            finalLegDict[s+'errCompare_unrolled'] = ROOT.TLegend(0.1,0.7,0.48,0.9)
            canvas = 'template'
            for histo in ['fake','prompt'] :
                            finalHistoDict[s+canvas+histo+'unrolled'+'sum2'] = ROOT.TGraphAsymmErrors()
                            finalHistoDict[s+canvas+histo+'unrolled'+'sum2'].SetName(finalHistoDict[s+canvas+histo+'unrolled'].GetName()+'_sum2')
                            finalHistoDict[s+canvas+histo+'unrolled'+'sum2'].SetLineColor(finalHistoDict['nom'+canvas+histo+s+'0'+'sum2'].GetLineColor())
                            finalHistoDict[s+canvas+histo+'unrolled'+'sum2'].SetMarkerColor(finalHistoDict['nom'+canvas+histo+s+'0'+'sum2'].GetLineColor())
                            finalHistoDict[s+canvas+histo+'unrolled'+'sum2'].SetFillColor(finalHistoDict['nom'+canvas+histo+s+'0'+'sum2'].GetLineColor())
                            finalHistoDict[s+canvas+histo+'unrolled'+'sum2'].SetFillStyle(finalHistoDict['nom'+canvas+histo+s+'0'+'sum2'].GetFillStyle())
                            finalHistoDict[s+canvas+histo+'unrolled'+'sum2'].SetLineWidth(finalHistoDict['nom'+canvas+histo+s+'0'+'sum2'].GetLineWidth())
                            for e in self.etaBinningS :
                                for p in self.ptBinningS :
                                    indexUNR = self.etaBinning.index(float(e))*len(self.ptBinningS)+self.ptBinning.index(float(p))
                                    finalHistoDict[s+canvas+histo+'unrolled'+'sum2'].SetPoint(indexUNR,finalHistoDict[s+canvas+histo+'unrolled'].GetBinCenter(indexUNR+1),1)
                                    finalHistoDict[s+canvas+histo+'unrolled'+'sum2'].SetPointEYhigh(indexUNR,finalHistoDict['nom'+canvas+histo+s+e+'sum2'].GetErrorYhigh(self.ptBinning.index(float(p))))
                                    finalHistoDict[s+canvas+histo+'unrolled'+'sum2'].SetPointEYlow(indexUNR,finalHistoDict['nom'+canvas+histo+s+e+'sum2'].GetErrorYlow(self.ptBinning.index(float(p))))
                                    finalHistoDict[s+canvas+histo+'unrolled'+'sum2'].SetPointEXhigh(indexUNR,finalHistoDict[s+canvas+histo+'unrolled'].GetBinWidth(indexUNR+1)/2)
                                    finalHistoDict[s+canvas+histo+'unrolled'+'sum2'].SetPointEXlow(indexUNR,finalHistoDict[s+canvas+histo+'unrolled'].GetBinWidth(indexUNR+1)/2)
                            if histo=='fake' :
                                finalHistoDict[s+canvas+histo+'unrolled'+'sum2'].Draw("")
                                finalHistoDict[s+canvas+histo+'unrolled'+'sum2'].Draw("5")
                            else :
                                finalHistoDict[s+canvas+histo+'unrolled'+'sum2'].Draw("SAME 5")
                            finalLegDict[s+"errCompare_unrolled"].AddEntry(finalHistoDict[s+canvas+histo+'unrolled'+'sum2'], histo)

            finalLegDict[s+'errCompare_unrolled'].Draw("SAME")
            finalCanvasDict['sum2Error_unrolled'+s] = c_errCompare_unrolled



        #fit parameters i.e. the real templates -------
        
        ParnameDict = {
            'prompt' : ['offset','slope','2deg', 'offset*slope', 'offset*2deg','slope*2deg', 'chi2red'],
            'fake'   : ['offset','slope','offset*slope']
            }
        for sKind, sList in systDict.iteritems():
            for sName in sList :
                finalPlotFileDict[sName+'parameters'] = ROOT.TFile.Open(outDir+"/bkg_"+sName+"/bkg_parameters_file"+self.corrFitSuff+".root")
                for s in self.signList :
                    for kind in ParnameDict :
                        for par in ParnameDict[kind] :
                                temp2DHist =   finalPlotFileDict[sName+'parameters'].Get(kind+'_'+par)
                                if s== 'Plus' : sCount=1
                                else : sCount =2
                                finalHistoDict[sName+kind+par+s] = temp2DHist.ProjectionY('parameters_'+kind+'_'+par+'_'+s,sCount,sCount,"e")
        #nominal
        sName='nom'
        finalPlotFileDict[sName+'parameters'] = ROOT.TFile.Open(outDir+"/bkg_"+sName+"/bkg_parameters_file"+self.corrFitSuff+".root")
        for s in self.signList :
            for kind in ParnameDict :
                for par in ParnameDict[kind] :
                    temp2DHist =   finalPlotFileDict[sName+'parameters'].Get(kind+'_'+par)
                    if s== 'Plus' : sCount=1
                    else : sCount =2
                    #NB: if i run with correlatedFit=1 in bkg_parameters_file.root there are the "Minuit" (aka correlatedFit) parameters. 
                    finalHistoDict[sName+kind+par+s] = temp2DHist.ProjectionY('parameters_'+kind+'_'+par+'_'+s,sCount,sCount,"e")     
       
        #building bands
        for s in self.signList :
            for kind in ParnameDict : 
                for par in ParnameDict[kind] :              
                    finalCanvasDict['parameters'+'nom'+kind+par+s] = ROOT.TCanvas("c_parameters_{sign}_{kind}_{par}".format(sign=s,kind=kind,par=par),"c_parameters_{sign}_{kind}_{par}".format(sign=s,kind=kind,par=par),800,600)#finalPlotFileDict['nom'].Get('c_'+canvas+'_'+s+'_'+e).Clone()
                    finalCanvasDict['parameters'+'nom'+kind+par+s].cd()
                    fillSyle =0
                    finalHistoDict['nom'+kind+par+s+'error'] = ROOT.TGraphAsymmErrors()
                    finalHistoDict['nom'+kind+par+s+'error'].SetName(finalHistoDict['nom'+kind+par+s].GetName()+'_error')

                    for e in self.etaBinning :
                        if(e==self.etaBinning[-1]) : continue
                        varErr = []
                        varErr.append(finalHistoDict['nom'+kind+par+s].GetBinContent(self.etaBinning.index(float(e))+1))
                        varErrSum2Up = 0
                        varErrSum2Down = 0.
                        for sKind, sList in systDict.iteritems():
                            for sName in sList :
                                varErr.append(finalHistoDict[sName+kind+par+s].GetBinContent(self.etaBinning.index(float(e))+1))
                                if "Up" in sName :
                                    varErrSum2Up = varErrSum2Up+ (finalHistoDict[sName+kind+par+s].GetBinContent(self.etaBinning.index(float(e))+1)-finalHistoDict['nom'+kind+par+s].GetBinContent(self.etaBinning.index(float(e))+1))**2
                                if "Down" in sName :
                                    varErrSum2Down = varErrSum2Down+ (finalHistoDict[sName+kind+par+s].GetBinContent(self.etaBinning.index(float(e))+1)-finalHistoDict['nom'+kind+par+s].GetBinContent(self.etaBinning.index(float(e))+1))**2
                        varErrSum2Up = math.sqrt(varErrSum2Up)
                        varErrSum2Down = math.sqrt(varErrSum2Down)
                        varErr.sort()
                        minBand = varErr[0]
                        maxBand = varErr[len(varErr)-1]
                        errLow = finalHistoDict['nom'+kind+par+s].GetBinContent(self.etaBinning.index(float(e))+1)-minBand
                        errHigh = maxBand-finalHistoDict['nom'+kind+par+s].GetBinContent(self.etaBinning.index(float(e))+1)
                        if sum2Bands :
                            errLow = varErrSum2Down
                            errHigh = varErrSum2Up
                        finalHistoDict['nom'+kind+par+s+'error'].SetPoint(self.etaBinning.index(float(e)),finalHistoDict['nom'+kind+par+s].GetBinCenter(self.etaBinning.index(float(e))+1),finalHistoDict['nom'+kind+par+s].GetBinContent(self.etaBinning.index(float(e))+1))
                        finalHistoDict['nom'+kind+par+s+'error'].SetPointEYhigh(self.etaBinning.index(float(e)),errHigh)
                        finalHistoDict['nom'+kind+par+s+'error'].SetPointEYlow(self.etaBinning.index(float(e)),errLow)
                        finalHistoDict['nom'+kind+par+s+'error'].SetPointEXhigh(self.etaBinning.index(float(e)),finalHistoDict['nom'+kind+par+s].GetBinWidth(self.etaBinning.index(float(e))+1)/2)
                        finalHistoDict['nom'+kind+par+s+'error'].SetPointEXlow(self.etaBinning.index(float(e)),finalHistoDict['nom'+kind+par+s].GetBinWidth(self.etaBinning.index(float(e))+1)/2)

                    finalHistoDict['nom'+kind+par+s+'error'].SetLineColor(8)
                    finalHistoDict['nom'+kind+par+s+'error'].SetMarkerColor(8)
                    finalHistoDict['nom'+kind+par+s+'error'].SetFillColor(8)
                    finalHistoDict['nom'+kind+par+s+'error'].SetFillStyle(3003+fillSyle)
                    finalHistoDict['nom'+kind+par+s+'error'].SetLineWidth(1)
                    finalHistoDict['nom'+kind+par+s].Draw()
                    finalHistoDict['nom'+kind+par+s].SetLineWidth(3)
                    finalHistoDict['nom'+kind+par+s+'error'].Draw("SAME 0P5")

                    finalCanvasDict['parameters'+'nom'+kind+par+s].Update()
                    finalCanvasDict['parameters'+'nom'+kind+par+s].Modified()
                    fillSyle =fillSyle+1

        #ratio plot creation
        for s in self.signList :
            for kind in ParnameDict : 
                for par in ParnameDict[kind] : 
                            c_ratioSyst = ROOT.TCanvas("c_parameters_ratioSyst_{sign}_{kind}_{par}".format(sign=s,kind=kind,par=par),"c_parameters_ratioSyst_{sign}_{kind}_{par}".format(sign=s,kind=kind,par=par),800,600)
                            c_ratioSyst.cd()
                            c_ratioSyst.SetGridx()
                            c_ratioSyst.SetGridy()
                            finalLegDict[s+kind+par+"ratioSyst"] = ROOT.TLegend(0.1,0.7,0.48,0.9)

                            sameFlag = True
                            colorNumber = 1
                            colorList = [600,616,416,632,432,800,900]
                            colorCounter = 0

                            for sKind, sList in systDict.iteritems():
                                colorNumber = colorList[colorCounter]
                                colorCounter = colorCounter+1
                                for sName in sList :
                                    colorNumber = colorNumber-2
                                    if colorNumber < colorList[colorCounter-1]-10 :
                                        colorNumber = colorList[colorCounter]+2
                                    finalHistoDict[sName+kind+par+s+'ratio'] = ROOT.TH1F(canvas+'_'+finalHistoDict[sName+kind+par+s].GetName()+'_'+sName+'_ratio',canvas+'_'+finalHistoDict[sName+kind+par+s].GetName()+'_'+sName+'_ratio',len(self.etaBinning)-1, array('f',self.etaBinning))
                                    finalHistoDict[sName+kind+par+s+'ratio'].Divide(finalHistoDict[sName+kind+par+s],finalHistoDict['nom'+kind+par+s],1,1)
                                    if noratio :
                                        finalHistoDict[sName+kind+par+s+'ratio'] = finalHistoDict[sName+kind+par+s].Clone()

                                    finalHistoDict[sName+kind+par+s+'ratio'].SetLineColor(colorNumber)
                                    for b in range(1,finalHistoDict[sName+kind+par+s+'ratio'].GetNbinsX()+1) :
                                        finalHistoDict[sName+kind+par+s+'ratio'].SetBinError(b,0)
                                    c_ratioSyst.cd()
                                    if sameFlag :
                                        finalHistoDict[sName+kind+par+s+'ratio'].Draw()
                                        finalHistoDict[sName+kind+par+s+'ratio'].GetYaxis().SetRangeUser(0.6,1.7)
                                    else :
                                        finalHistoDict[sName+kind+par+s+'ratio'].Draw("SAME")
                                        finalHistoDict[sName+kind+par+s+'ratio'].GetYaxis().SetRangeUser(0,3)
                                    finalHistoDict[sName+kind+par+s+'ratio'].SetLineWidth(3)
                                    sameFlag=False
                                    finalLegDict[s+kind+par+"ratioSyst"].AddEntry(finalHistoDict[sName+kind+par+s+'ratio'], sName)

                            #nominal
                            finalHistoDict['nom'+kind+par+s+'ratio'] = ROOT.TH1F(canvas+'_'+finalHistoDict['nom'+kind+par+s].GetName()+'_'+'nom'+'_ratio',canvas+'_'+finalHistoDict['nom'+kind+par+s].GetName()+'_'+'nom'+'_ratio',len(self.etaBinning)-1, array('f',self.etaBinning))
                            finalHistoDict['nom'+kind+par+s+'ratio'].Divide(finalHistoDict['nom'+kind+par+s],finalHistoDict['nom'+kind+par+s],1,1)
                            if noratio :
                                finalHistoDict['nom'+kind+par+s+'ratio'] =finalHistoDict['nom'+kind+par+s].Clone()

                            finalHistoDict['nom'+kind+par+s+'ratio'].SetLineColor(1)
                            for b in range(1,finalHistoDict['nom'+kind+par+s+'ratio'].GetNbinsX()+1) :
                                # finalHistoDict['nom'+kind+par+s+'ratio'].SetBinError(b,math.sqrt(2)*finalHistoDict['nom'+kind+par+s].GetBinError(b)/finalHistoDict['nom'+kind+par+s].GetBinContent(b))
                                if finalHistoDict['nom'+kind+par+s].GetBinContent(b)!=0 :
                                    finalHistoDict['nom'+kind+par+s+'ratio'].SetBinError(b,finalHistoDict['nom'+kind+par+s].GetBinError(b)/finalHistoDict['nom'+kind+par+s].GetBinContent(b))
                                else :
                                     print "WARNING: bin content of ", canvas, histo, "is 0, bin (s,e,p)=", s,e,b, ". error of ratio plot not correctly normalized."
                                     finalHistoDict['nom'+kind+par+s+'ratio'].SetBinError(b,finalHistoDict['nom'+kind+par+s].GetBinError(b))
                            c_ratioSyst.cd()
                            finalHistoDict['nom'+kind+par+s+'ratio'].Draw("SAME E2")
                            finalHistoDict['nom'+kind+par+s+'ratio'].GetYaxis().SetRangeUser(0,3)
                            finalHistoDict['nom'+kind+par+s+'ratio'].SetLineWidth(0)
                            finalHistoDict['nom'+kind+par+s+'ratio'].SetFillColor(1)
                            finalHistoDict['nom'+kind+par+s+'ratio'].SetFillStyle(3002)
                            finalLegDict[s+kind+par+"ratioSyst"].AddEntry(finalHistoDict['nom'+kind+par+s+'ratio'], 'Nominal')
                            
                            finalLegDict[s+kind+par+"ratioSyst"].Draw("SAME")
                            finalCanvasDict['parameters'+'ratio'+kind+par+s] = c_ratioSyst


    


        # outputFinal.Close()
        outputFinal = ROOT.TFile(outDir+"/final_plots"+self.corrFitSuff+self.nameSuff+".root","recreate")

        dirFinalDict = {}
        for s in self.signList :
            for e in self.etaBinningS :
                dirFinalDict[s+e] =    outputFinal.mkdir(s+"_eta"+e)
                # dirFinalDict[s+e].cd()   #DECOMMENTA QUESTO SE NON FUNZIONANO LE DIRECTORY
            dirFinalDict[s+'unrolled'] =    outputFinal.mkdir(s+'_unrolled')
            dirFinalDict[s+'parameters'] = outputFinal.mkdir(s+'_Fit_parameters')
            
        for ind, obj in finalCanvasDict.iteritems():
                for s in self.signList :
                    
                    if ind.startswith('parameters') :
                        dirFinalDict[s+'parameters'].cd()
                        obj.Write()                        
                    elif 'unrolled' in ind and s in ind:
                        dirFinalDict[s+'unrolled'].cd()
                        obj.Write()
                    else :
                        for e in self.etaBinningS :
                            if ind.endswith(s+e) :
                                dirFinalDict[s+e].cd()
                                obj.Write()


    def strategy_syst(self, preOutDir) :
        # self.preOutDir = preOutDir

        systlist = ['mT_fit', 'EWSFdown10','EWSFup10', 'slopeDown10','slopeUp10', 'mT_fit_2deg', 'mT_countHigh', 'MET_fit', 'MET_countHigh']
        colorList = [600,616,416,632,432,800,900,881,402]
        straSystDict_file = {}
        straSystDict_histo = {}
        straSystDict_leg = {}
        straSystDict_canvas = {}
        straSystDict_pad = {}

        unrolledPtEta= list(self.ptBinning)
        intervalPtBin = []
        for p in self.ptBinning[:-1] :
            intervalPtBin.append(self.ptBinning[self.ptBinning.index(p)+1]-self.ptBinning[self.ptBinning.index(p)])
        for e in range(len(self.etaBinning)-2) :
            for p in intervalPtBin :
                unrolledPtEta.append(unrolledPtEta[-1]+p)

        for var in systlist :
            straSystDict_file[var]=ROOT.TFile.Open(preOutDir+"/bkg_"+var+"/final_plots"+self.nameSuff+".root")
            for s in self.signList :

                straSystDict_histo[var+s] =   straSystDict_file[var].Get(s+'_unrolled/c_unrolled_template'+'_'+s).GetPrimitive('template_htempl_pt_fake_'+s+'_0_unrolled')
                straSystDict_histo[var+s].SetLineColor(colorList[systlist.index(var)])
                if var == 'mT_fit' :
                    straSystDict_histo[var+s+'error'] =   straSystDict_file[var].Get(s+'_unrolled/c_unrolled_template'+'_'+s).GetPrimitive('template_htempl_pt_fake_'+s+'_0_unrolled_error')
                    straSystDict_histo[var+s+'error'].SetLineColor(colorList[systlist.index(var)])

                if var != 'mT_fit' :
                    straSystDict_histo[var+s+'ratio'] = ROOT.TH1F(straSystDict_histo[var+s].GetName()+'_ratio',straSystDict_histo[var+s].GetName()+'_ratio',len(unrolledPtEta)-1, array('f',unrolledPtEta))
                    straSystDict_histo[var+s+'ratio'].Divide(straSystDict_histo[var+s],straSystDict_histo['mT_fit'+s],1,1)
                    straSystDict_histo[var+s+'ratio'].SetLineColor(colorList[systlist.index(var)])
                    straSystDict_histo[var+s+'ratio'].SetLineWidth(2)
                    straSystDict_histo[var+s+'ratio'].GetYaxis().SetTitle("Syst/Nom")


        for s in self.signList :
            c_straSyst = ROOT.TCanvas("c_straSyst_{sign}".format(sign=s),"c_straSyst_{sign}".format(sign=s),800,700)
            c_straSyst.cd()
            c_straSyst.SetGridx()
            c_straSyst.SetGridy()

            straSystDict_leg[s] = ROOT.TLegend(0.30,0.10,0.80,0.4)

            p_straSyst_histo = ROOT.TPad("p_straSyst_histo_"+s, "c_straSyst_"+s,0,0.5,1,1)
            p_straSyst_ratio = ROOT.TPad("p_straSyst_ratio_"+s, "c_straSyst_"+s,0,0,1,0.5)
            p_straSyst_histo.SetBottomMargin(0.02)
            p_straSyst_histo.Draw()
            p_straSyst_ratio.SetTopMargin(0)
            p_straSyst_ratio.SetBottomMargin(0.25)
            p_straSyst_ratio.Draw()

            sameFlagSS=True
            sameFlagSS_ratio = True
            for var in systlist :
                p_straSyst_histo.cd()
                if sameFlagSS :
                    straSystDict_histo[var+s].Draw()
                else :
                    straSystDict_histo[var+s].Draw("SAME")
                straSystDict_leg[s].AddEntry(straSystDict_histo[var+s],var)
                sameFlagSS=False

                if var!= "mT_fit" :
                    p_straSyst_ratio.cd()
                    if sameFlagSS_ratio :
                        straSystDict_histo[var+s+'ratio'].Draw()
                    else :
                        straSystDict_histo[var+s+'ratio'].Draw("SAME")
                    sameFlagSS_ratio = False
            p_straSyst_histo.cd()
            straSystDict_leg[s].Draw("SAME")

            straSystDict_canvas[s] = c_straSyst

        outputraSyst= ROOT.TFile(preOutDir+"/bkg_mT_fit/strategy_syst"+self.nameSuff+".root","recreate")
        for s in self.signList :
            straSystDict_canvas[s].Write()


    def clousure_plots(self, outdir, MC=False) :
        # self.outDir = outDir
        # self.MC = MC #do not apply correction


        histoDict = {}
        clousureVarList = []
        legDict = {}
        stackDict = {}
        canvasList = []

        #get variables for the stacked and correct the QCD
        for var in bkg_variables_standalone['variables'] :
            if var!='Muon_corrected_pt' : continue
            clousureVarList.append(var)

        for s in self.signList :
            for v in clousureVarList:
                for f,rootFile in map(None,self.sampleList[:-1],self.rootFilesRaw) :
                    for r in self.regionList :
                            if(r!='Tot') :
                                # print 'bkg_'+r+s+'/nom/bkgSel_'+v+'_nom', f, rootFile
                                histoDict[s+v+f+r] = rootFile.Get('bkg_'+r+s+'/nom/bkgSel_'+v+'_nom')
                                if f!='Data' :
                                    histoDict[s+v+f+r].Scale(self.norm)
                            else:
                                histoDict[s+v+f+r] = histoDict[s+v+f+'Signal'].Clone(f+'_'+s+'_'+v+'_Tot') #only isolated!!!!
                                # for rr in self.regionList :
                                #     if (rr =="Sideband" or rr=="Tot") : continue
                                #     histoDict[s+v+f+r].Add(histoDict[s+v+f+rr])

                #features of histograms
                histoDict[s+v+'Data'+'Tot'].SetLineColor(1) #black
                histoDict[s+v+'QCD'+'Tot'].SetLineColor(632+2) #red
                histoDict[s+v+'EWKbkg'+'Tot'].SetLineColor(600-4)#blue
                histoDict[s+v+'WToMuNu'+'Tot'].SetLineColor(416+2)#green

                histoDict[s+v+'QCD'+'Tot'].SetFillColor(632+2) #red
                histoDict[s+v+'EWKbkg'+'Tot'].SetFillColor(600-4)#blue
                histoDict[s+v+'WToMuNu'+'Tot'].SetFillColor(416+2)#green

                histoDict[s+v+'Data'+'Tot'].SetMarkerStyle(20)
                histoDict[s+v+'Data'+'Tot'].Sumw2()
                histoDict[s+v+'Data'+'Tot'].SetLineWidth(3)
                histoDict[s+v+'Data'+'Tot'].GetYaxis().SetTitle("dN/d{name}/{size} [1/GeV]".format(size=histoDict[s+v+'Data'+'Tot'].GetBinWidth(1),name=v))
                histoDict[s+v+'Data'+'Tot'].GetYaxis().SetTitleOffset(1)
                histoDict[s+v+'Data'+'Tot'].GetXaxis().SetTitle("{name} [GeV]".format(name=v))
                histoDict[s+v+'Data'+'Tot'].SetTitle("{name} {sign}".format(name=v,sign=s))

                stackDict[s+v] = ROOT.THStack(v+'_'+s,"")
                stackDict[s+v].Add(histoDict[s+v+'QCD'+'Tot'])
                stackDict[s+v].Add(histoDict[s+v+'EWKbkg'+'Tot'])
                stackDict[s+v].Add(histoDict[s+v+'WToMuNu'+'Tot'])

                legDict[s+v] = ROOT.TLegend(0.1,0.7,0.48,0.9)
                legDict[s+v].AddEntry(histoDict[s+v+'Data'+'Tot'],"Data")
                legDict[s+v].AddEntry(histoDict[s+v+'QCD'+'Tot'], "QCD")
                legDict[s+v].AddEntry(histoDict[s+v+'EWKbkg'+'Tot'], "EWK bkg MC")
                legDict[s+v].AddEntry(histoDict[s+v+'WToMuNu'+'Tot'], "Signal MC")

                #ratio MC/data
                histoDict[s+v+'sum'] = histoDict[s+v+'QCD'+'Tot'].Clone(histoDict[s+v+'QCD'+'Tot'].GetName()+'sum')
                histoDict[s+v+'sum'].Sumw2()
                for f in self.sampleList[:-1] :
                    if f=='Data' or f=='QCD': continue
                    histoDict[s+v+f+'Tot'].Sumw2()
                    histoDict[s+v+'sum'].Add(histoDict[s+v+f+'Tot'])
                histoDict[s+v+'sum'].Divide(histoDict[s+v+'Data'+'Tot'])

                histoDict[s+v+'sum'].SetLineColor(632) #red
                histoDict[s+v+'sum'].SetLineWidth(3)
                histoDict[s+v+'sum'].GetYaxis().SetTitle("MC/data")
                histoDict[s+v+'sum'].GetYaxis().SetTitleOffset(1)
                histoDict[s+v+'sum'].GetXaxis().SetTitle("{name} [GeV]".format(name=v))
                legDict[s+v].AddEntry(histoDict[s+v+'sum'], "MC/data")


                #stacked plot creation
                c_clousure = ROOT.TCanvas("c_clousure_{var}_{sign}".format(sign=s,var=v),"c_clousure_{var}_{sign}".format(sign=s,var=v),800,700)
                c_clousure.cd()
                c_clousure.SetGridx()
                c_clousure.SetGridy()

                p_clousure_histo = ROOT.TPad("p_clousure_histo_"+v+"_"+s, "c_clousure_"+v+"_"+s,0,0.3,1,1)
                p_clousure_ratio = ROOT.TPad("p_clousure_ratio_"+v+"_"+s, "c_clousure_"+v+"_"+s,0,0,1,0.3)
                p_clousure_histo.SetBottomMargin(0.02)
                p_clousure_histo.Draw()
                p_clousure_ratio.SetTopMargin(0)
                p_clousure_ratio.SetBottomMargin(0.25)
                p_clousure_ratio.Draw()

                p_clousure_histo.cd()
                histoDict[s+v+'Data'+'Tot'].Draw()
                stackDict[s+v].Draw("SAME HIST")
                histoDict[s+v+'Data'+'Tot'].DrawCopy("SAME")

                p_clousure_ratio.cd()
                histoDict[s+v+'sum'].Draw()

                p_clousure_histo.cd()
                legDict[s+v].Draw("SAME")

                canvasList.append(c_clousure)

        outputFake = ROOT.TFile(outDir+"/bkg_clousure.root","recreate")
        for h in range(len(canvasList)) :
            canvasList[h].Write()
























    #uncomment all the function if needed (usa valori nei template per chiudere invece che ripesare evento per evento)
    # def clousure_plots_wrongVersion(self, outdir, MC=False) :
    #     self.outDir = outdir
    #     self.MC = MC #do not apply correction

    #     canvasList = []

    #     #get templates for QCD (data and MC) and bild the ratio
    #     fileTemplate = ROOT.TFile.Open(self.outDir+"/bkg_nom/bkg_differential_fakerate"+self.nameSuff+".root")
    #     templDict = {}
    #     for s in self.signList :
    #         for kind in ['fake', 'validation'] :
    #             templDict[s+kind] = fileTemplate.Get('Template/h2templ_'+kind+'_'+s)
    #             canvasList.append(templDict[s+kind])
    #         templDict[s+'ratio']=templDict[s+'fake'].Clone(templDict[s+'fake'].GetName()+'_ratio')
    #         templDict[s+'ratio'].Divide(templDict[s+'validation'])
    #         # canvasList.append(templDict[s+'ratio'])

    #     #get variables for the stacked and correct the QCD
    #     histoDict = {}
    #     clousureVarList = []
    #     for var in bkg_variables_standalone['ClousureVariables'] :
    #         clousureVarList.append(var)
    #     clousureVarName = ['Mt','PtMu']
    #     clousureVarName1D = ['Muon_corrected_MET_nom_mt']

    #     legDict = {}
    #     stackDict = {}

    #     for s in self.signList :
    #         for name1D,name,v in map(None,clousureVarList,clousureVarName,clousureVarName1D) :
    #             if v==None or name==None or name1D==None : continue
    #             for f,rootFile in map(None,self.sampleList[:-1],self.rootFilesRaw) :
    #                 for r in self.regionList :
    #                         if(r!='Tot') :
    #                             if f=='QCD' :
    #                                 histoDict[s+v+f+r] =  rootFile.Get('bkg_'+r+s+'/nom/bkgSel_'+v+'_VS_pt_VS_etanom')
    #                             else :
    #                                 histoDict['1D'+s+v+f+r] = rootFile.Get('bkg_'+r+s+'/nom/bkgSel_'+v+'_nom')
    #                             if f!='Data' :
    #                                 if f=='QCD' :
    #                                     histoDict[s+v+f+r].Scale(self.norm)
    #                                 else :
    #                                     histoDict['1D'+s+v+f+r].Scale(self.norm)
    #                         else:
    #                             if f=='QCD' :
    #                                  histoDict[s+v+f+r] = histoDict[s+v+f+'Sideband'].Clone(f+'_'+s+'_'+name+'_Tot')
    #                             else :
    #                                 histoDict['1D'+s+v+f+r] = histoDict['1D'+s+v+f+'Sideband'].Clone(f+'_'+s+'_'+v+'_Tot')
    #                             for rr in self.regionList :
    #                                 if (rr =="Sideband" or rr=="Tot") : continue
    #                                 if f=='QCD' :
    #                                     histoDict[s+v+f+r].Add(histoDict[s+v+f+rr])
    #                                 else :
    #                                     histoDict['1D'+s+v+f+r].Add(histoDict['1D'+s+v+f+rr])

    #                 if f=='QCD' : #copy for comparison
    #                     histoDict[s+v+f+'Tot'+'MC'] = histoDict[s+v+f+'Tot'].Clone(histoDict[s+v+f+'Tot'].GetName()+'_MC')
    #                 if(f=='QCD' and  (not self.MC)) : #apply correciton to QCD
    #                         for p in self.ptBinningS :
    #                             for e in self.etaBinningS :
    #                                 corr = templDict[s+'ratio'].GetBinContent(self.etaBinningS.index(e)+1,self.ptBinningS.index(p)+1)
    #                                 for x in range(1, bkg_variables_standalone['ClousureVariables'][name1D][1]) :#number of bins in the variable
    #                                     val = corr*histoDict[s+v+f+'Tot'].GetBinContent(x, self.ptBinningS.index(p)+1,self.etaBinningS.index(e)+1)
    #                                     histoDict[s+v+f+'Tot'].SetBinContent(x, self.ptBinningS.index(p)+1,self.etaBinningS.index(e)+1,val)
    #                 #project QCD
    #                 if f=='QCD' :
    #                     histoDict['1D'+s+v+f] =  histoDict[s+v+f+'Tot'].Project3D("xe")
    #                     histoDict['1D'+s+v+'MC'] =   histoDict[s+v+f+'Tot'+'MC'].Project3D("xe")
    #                     # canvasList.append(histoDict[s+v+f+'Tot'])
    #                     # canvasList.append(histoDict['1D'+s+v+f])


    #             #features of histograms
    #             histoDict['1D'+s+v+'Data'+'Tot'].SetLineColor(1) #black
    #             histoDict['1D'+s+v+'QCD'].SetLineColor(632+2) #red
    #             histoDict['1D'+s+v+'EWKbkg'+'Tot'].SetLineColor(600-4)#blue
    #             histoDict['1D'+s+v+'WToMuNu'+'Tot'].SetLineColor(416+2)#green

    #             histoDict['1D'+s+v+'Data'+'Tot'].Rebin(2)
    #             histoDict['1D'+s+v+'EWKbkg'+'Tot'].Rebin(2)
    #             histoDict['1D'+s+v+'WToMuNu'+'Tot'].Rebin(2)

    #             histoDict['1D'+s+v+'QCD'].SetFillColor(632+2) #red
    #             histoDict['1D'+s+v+'EWKbkg'+'Tot'].SetFillColor(600-4)#blue
    #             histoDict['1D'+s+v+'WToMuNu'+'Tot'].SetFillColor(416+2)#green

    #             histoDict['1D'+s+v+'Data'+'Tot'].SetMarkerStyle(20)
    #             histoDict['1D'+s+v+'Data'+'Tot'].Sumw2()
    #             histoDict['1D'+s+v+'Data'+'Tot'].SetLineWidth(3)
    #             histoDict['1D'+s+v+'Data'+'Tot'].GetYaxis().SetTitle("dN/d{name}/{size} [1/GeV]".format(size=histoDict['1D'+s+v+'Data'+'Tot'].GetBinWidth(1),name=name))
    #             histoDict['1D'+s+v+'Data'+'Tot'].GetYaxis().SetTitleOffset(1)
    #             histoDict['1D'+s+v+'Data'+'Tot'].GetXaxis().SetTitle("{name} [GeV]".format(name=name))
    #             histoDict['1D'+s+v+'Data'+'Tot'].SetTitle("{name} {sign}".format(name=name,sign=s))

    #             stackDict[s+v] = ROOT.THStack(v+'_'+s,"")
    #             stackDict[s+v].Add(histoDict['1D'+s+v+'QCD'])
    #             stackDict[s+v].Add(histoDict['1D'+s+v+'EWKbkg'+'Tot'])
    #             stackDict[s+v].Add(histoDict['1D'+s+v+'WToMuNu'+'Tot'])

    #             legDict[s+v] = ROOT.TLegend(0.1,0.7,0.48,0.9)
    #             legDict[s+v].AddEntry(histoDict['1D'+s+v+'Data'+'Tot'],"Data")
    #             legDict[s+v].AddEntry(histoDict['1D'+s+v+'QCD'], "QCD")
    #             legDict[s+v].AddEntry(histoDict['1D'+s+v+'EWKbkg'+'Tot'], "EWK bkg MC")
    #             legDict[s+v].AddEntry(histoDict['1D'+s+v+'WToMuNu'+'Tot'], "Signal MC")

    #             #"stack" for ratio
    #             histoDict['1D'+s+v+'sum'] = histoDict['1D'+s+v+'QCD'].Clone(histoDict['1D'+s+v+'QCD'].GetName()+'sum')
    #             histoDict['1D'+s+v+'sum'].Sumw2()
    #             histoDict['1D'+s+v+'MC'].Sumw2()
    #             print 'start sum'
    #             for f in self.sampleList[:-1] :
    #                 if f=='QCD' or f=='Data': continue
    #                 print '1D'+s+v+f
    #                 histoDict['1D'+s+v+f+'Tot'].Sumw2()
    #                 histoDict['1D'+s+v+'sum'].Add(histoDict['1D'+s+v+f+'Tot'])
    #                 histoDict['1D'+s+v+'MC'].Add(histoDict['1D'+s+v+f+'Tot'])
    #             histoDict['1D'+s+v+'sum'].Divide(histoDict['1D'+s+v+'Data'+'Tot'])
    #             histoDict['1D'+s+v+'MC'].Divide(histoDict['1D'+s+v+'Data'+'Tot'])

    #             histoDict['1D'+s+v+'sum'].SetLineColor(632) #red
    #             histoDict['1D'+s+v+'MC'].SetLineColor(880+1) #violet
    #             histoDict['1D'+s+v+'sum'].SetLineWidth(3)
    #             histoDict['1D'+s+v+'MC'].SetLineWidth(3)
    #             histoDict['1D'+s+v+'sum'].SetFillColor(0)
    #             legDict[s+v].AddEntry(histoDict['1D'+s+v+'sum'], "corrected/data")
    #             legDict[s+v].AddEntry(histoDict['1D'+s+v+'MC'], "default/data")

    #             histoDict['1D'+s+v+'sum'].GetYaxis().SetTitle("MC/data")
    #             histoDict['1D'+s+v+'sum'].GetYaxis().SetTitleOffset(1)
    #             histoDict['1D'+s+v+'sum'].GetXaxis().SetTitle("{name} [GeV]".format(name=name))

    #             histoDict['1D'+s+v+'Data'+'Tot'+'ratio'] = histoDict['1D'+s+v+'Data'+'Tot'].Clone(histoDict['1D'+s+v+'Data'+'Tot'].GetName()+'_clone')
    #             histoDict['1D'+s+v+'Data'+'Tot'+'ratio'].Divide(histoDict['1D'+s+v+'Data'+'Tot'+'ratio'])
    #             histoDict['1D'+s+v+'Data'+'Tot'+'ratio'].SetLineWidth(0)
    #             histoDict['1D'+s+v+'Data'+'Tot'+'ratio'].SetFillColor(1)
    #             histoDict['1D'+s+v+'Data'+'Tot'+'ratio'].SetFillStyle(3002)




    #             #stacked plot creation
    #             c_clousure = ROOT.TCanvas("c_clousure_{var}_{sign}".format(sign=s,var=v),"c_clousure_{var}_{sign}".format(sign=s,var=v),800,700)
    #             c_clousure.cd()
    #             c_clousure.SetGridx()
    #             c_clousure.SetGridy()

    #             p_clousure_histo = ROOT.TPad("p_clousure_histo_"+v+"_"+s, "c_clousure_"+v+"_"+s,0,0.5,1,1)
    #             p_clousure_ratio = ROOT.TPad("p_clousure_ratio_"+v+"_"+s, "c_clousure_"+v+"_"+s,0,0,1,0.5)
    #             p_clousure_histo.SetBottomMargin(0.02)
    #             p_clousure_histo.Draw()
    #             p_clousure_ratio.SetTopMargin(0)
    #             p_clousure_ratio.SetBottomMargin(0.25)
    #             p_clousure_ratio.Draw()

    #             p_clousure_histo.cd()
    #             histoDict['1D'+s+v+'Data'+'Tot'].Draw()
    #             stackDict[s+v].Draw("SAME HIST")
    #             histoDict['1D'+s+v+'Data'+'Tot'].DrawCopy("SAME")

    #             p_clousure_ratio.cd()
    #             histoDict['1D'+s+v+'sum'].Draw()
    #             histoDict['1D'+s+v+'MC'].Draw("SAME")
    #             histoDict['1D'+s+v+'Data'+'Tot'+'ratio'].Draw("SAME E2")

    #             p_clousure_histo.cd()
    #             legDict[s+v].Draw("SAME")

    #             canvasList.append(c_clousure)

    #     outputFake = ROOT.TFile(self.outDir+"/bkg_clousure.root","recreate")
    #     for h in range(len(canvasList)) :
    #         canvasList[h].Write()
