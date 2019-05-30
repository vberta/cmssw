import ROOT
from array import array
import math 
import sys
import copy as copy
sys.path.append('../../framework')
from module import *
from header import *
from bkg_variables import *
from bkg_selections import *




# class bkg_fakerateAnalyzer(module):
class bkg_fakerateAnalyzer:  
    # def __init__(self, outdir='./bkg', folder='./', norm = 1, skipHisto = 1, fileList,)  :
    def __init__(self, ptBinning, etaBinning, outdir='./bkg', folder='./', norm = 1)  :
    
        self.outdir = outdir
        self.folder = folder
        self.norm = norm
        # self.skipHisto = skipHisto
        # self.fileList = fileList 
        self.ptBinning = ptBinning
        self.etaBinning = etaBinning
        
        self.rootFiles = []
        self.relisoCUT = 0.15
        self.isoCUT = 5
        self.QCDmult = 1. #multiplication factor to QCD bkg
        
        # self.sampleList = ['WToMuNu','QCD','EWKbkg','Data','DataLike']
        self.sampleList = ['WToMuNu','QCD','EWKbkg','DataLike']
        # self.sampleList = ['WToMuNu','QCD','Data','DataLike']

        self.signList = ['Plus','Minus']
        self.regionList = ['Signal','Sideband', 'Tot']
        self.varList = []
        for var in bkg_variables['Muon1']['D2variables'] : self.varList.append(var)
        # self.varList = ["pfRelIso04_all_VS_corrected_MET_nom_mt","pfRelIso04_all_TIMES_corrected_pt_VS_corrected_MET_nom_mt","pfRelIso04_all_VS_MET_pt","pfRelIso04_all_TIMES_corrected_pt_VS_MET_pt"]
        self.varName = ["relIso_vs_Mt", "absIso_vs_Mt","relIso_vs_MET", "absIso_vs_MET"]
        self.ptBinningS = ['{:.2g}'.format(x) for x in self.ptBinning[1:]]
        self.etaBinningS = ['{:.2g}'.format(x) for x in self.etaBinning[1:]]
        
        #open all the useful rootfile
        # for f in fileList
        #     rootFiles.append(ROOT.TFile.Open(self.folder+'/'+f))
        for f in range(len(self.sampleList)-1) :
            if (self.sampleList[f]!='DataLike') : self.rootFiles.append(ROOT.TFile.Open(self.folder+'/'+self.sampleList[f]+'.root'))
    
    
    def ratio_2Dto1D(self,histo,isocut =0.15,name = "histoRate") : #histo = 2D isto iso:Mt, isocut=tight def., name=output histo name
        #this func. produce an histogram of fake or prompt rate in fuction of Mt (to verify ABCD assumption)
        isoMin= histo.GetYaxis().GetBinCenter(1)-histo.GetYaxis().GetBinWidth(1)/2
        binsize = histo.GetYaxis().GetBinWidth(1)
        Ncut=(isocut-isoMin)/binsize
        Ncut = int(Ncut)
        # print name,isocut, Ncut, isoMin
        # histoDen = histo.ProjectionX("histoDen",Ncut,-1)
        histoDen = histo.ProjectionX("histoDen")
        histoNum = histo.ProjectionX("histoNum",0,Ncut-1)
        histoRate = histoNum.Clone(name)
        histoRate.Divide(histoNum,histoDen,1,1)
        return histoRate
    
    def Fit4ScaleFactorEW(self,mtDict, sign, datakind) :
        self.mtDict = mtDict
        self.sign = sign
        self.datakind = datakind
        
        class linearHistoFit:
            def __call__(self, x, parameters):
                s = parameters[0] # weight signal
                b = parameters[1] # weight bkg
                x = x[0]
                ysig = hsig.GetBinContent(hsig.GetXaxis().FindFixBin(x));
                ybkg = hbkg.GetBinContent(hbkg.GetXaxis().FindFixBin(x));
                y = s*ysig+b*ybkg
                # print "value y",y
                return y  
        
        # def linearHistoFit(x, parameters) :
        #         s = parameters[0] # weight signal
        #         b = parameters[1] # weight bkg
        #         x = x[0]
        #         ysig = hsig.GetBinContent(hsig.GetXaxis().FindFixBin(x));
        #         ybkg = hbkg.GetBinContent(hbkg.GetXaxis().FindFixBin(x));
        #         y = s*hsig+b*hbkg
        #         return y              
                
        hsig = mtDict[self.sign+'WToMuNuTot']
        hsig.Add(mtDict[self.sign+'EWKbkgTot'])
        hbkg = mtDict[self.sign+'QCDTot']
        fitFunc = ROOT.TF1("fitFunc", linearHistoFit(),0,120,2)
        # fitFunc = ROOT.TF1("fitFunc", linearHistoFit,0,120,2)
        fitFunc.SetParameters(1,1)
        fitFunc.SetParNames("sig","bkg")
        mtDict[self.sign+self.datakind+'Tot'].Fit(fitFunc,"","",0,120)
        
        print "FIT RESULTS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Post fit, values:", fitFunc.GetParameter(0), fitFunc.GetParameter(1)
        # print "Pre fit values: (tot,w,QCD)   ", mtDict[self.sign+self.datakind+'Tot'].GetBinContent(10), mtDict[self.sign+'WToMuNuTot'].GetBinContent(10)+mtDict[self.sign+'QCDTot'].GetBinContent(10)+mtDict[self.sign+'EWKbkgTot'].GetBinContent(10)

        return fitFunc.GetParameter(0)
        
        
        
        
    
    
    def differential_fakerate(self, hdict, mtDict, tightcut = 0.15, loosecut=40, varname = 'pfRelIso04_all_corrected_MET_nom_mt', kind = 'fake') :
        self.loosecut = loosecut
        self.tightcut = tightcut
        self.varname = varname
        self.kind = kind # fake = calculate the fakerate (measurement ABCD), prompt = the promptrate (from MC), validation = the fakerate on MC QCD, fakeMC = fakerate from dataLike (MC) SEE DICT BELOW
        self.hdct = hdict 
        self.mtDict =mtDict
        
        kindDict = {
            'fake' : 'Data',
            'validation' : 'QCD',
            'fakeMC' : 'DataLike' ,
            'prompt' : 'WToMuNu',
            'validationSigReg' : 'QCD',
            'promptSideband' : 'WToMuNu',
        }
        datakind = kindDict[self.kind]            

        hFakes = {}
        h2Fakes = {}
        # TH2F h2Fakes = TH2F("h2Fakes","h2Fakes",len(self.etaBinning)-1, array('f',self.etaBinning), len(self.ptBinning)-1, array('f',self.ptBinning) )
        # h2Fakes[0] = TH2F("h2Fakes_plus","h2Fakes_plus",len(self.etaBinning)-1, array('f',self.etaBinning), len(self.ptBinning)-1, array('f',self.ptBinning) )
        # h2Fakes[1] = TH2F("h2Fakes_minus","h2Fakes_minus",len(self.etaBinning)-1, array('f',self.etaBinning), len(self.ptBinning)-1, array('f',self.ptBinning) )
        for s in self.signList :
            h2Fakes_sign = ROOT.TH2F("h2Fakes_{kind}_{sign}".format(kind=self.kind,sign=s),"h2Fakes_{kind}_{sign}".format(kind=self.kind,sign=s),len(self.etaBinning)-1, array('f',self.etaBinning), len(self.ptBinning)-1, array('f',self.ptBinning) )
            scaleFactorEW =1 
            if self.kind == 'fake' or self.kind == 'fakeMC' : 
                print "PRE FIT (sign, kind))", s, datakind
                scaleFactorEW=self.Fit4ScaleFactorEW(mtDict,s,datakind)
            for e in self.etaBinningS :
                hFakes_pt = ROOT.TH1F("hFakes_pt_{kind}_{sign}_{eta}".format(kind=self.kind,sign=s,eta=e),"hFakes_pt_{kind}_{sign}_{eta}".format(kind=self.kind,sign=s,eta=e), len(self.ptBinning)-1, array('f',self.ptBinning) )
                for p in self.ptBinningS :
                    hsubtract= hdict[p+e+s+varname+datakind+'Tot'].Clone(p+'_'+e+'_'+'datakind'+s+'_'+varname)
                    # if self.kind == 'fake' or self.kind == 'fakeMC' :
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
                    # print "cuts=, ", NcutTight, NcutLoose
                    
                    numErr = ROOT.Double(0)
                    denErr = ROOT.Double(0)
                    antiNumErr = ROOT.Double(0) #antinum = b region (not tight)
                    fake_err =0
                    if (self.kind=='fake' or self.kind=='validation' or self.kind=='fakeMC' or self.kind=='promptSideband') :
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
                        
                        
                        if self.kind == 'fake' or self.kind == 'fakeMC' : #not QCD
                            numErr_EWKbkg = ROOT.Double(0)
                            denErr_EWKbkg = ROOT.Double(0)
                            numErr_WToMuNu = ROOT.Double(0)
                            denErr_WToMuNu = ROOT.Double(0)
                            den_EWKbkg = hdict[p+e+s+varname+'EWKbkg'+'Tot'].ProjectionX("histoDen",0,-1,"e").IntegralAndError(0,NcutLoose-1,denErr_EWKbkg)
                            num_EWKbkg = hdict[p+e+s+varname+'EWKbkg'+'Tot'].ProjectionX("histoNum",0,NcutTight-1, "e").IntegralAndError(0,NcutLoose-1,numErr_EWKbkg)            
                            den_WToMuNu = hdict[p+e+s+varname+'WToMuNu'+'Tot'].ProjectionX("histoDen",0,-1,"e").IntegralAndError(0,NcutLoose-1,denErr_WToMuNu)
                            num_WToMuNu = hdict[p+e+s+varname+'WToMuNu'+'Tot'].ProjectionX("histoNum",0,NcutTight-1, "e").IntegralAndError(0,NcutLoose-1,numErr_WToMuNu)
                            
                            # print "PRE FIT (sign, kind))", s, datakind
                            # scaleFactorEW = self.Fit4ScaleFactorEW(mtDict,s,datakind)    
                            den = den - (den_EWKbkg + den_WToMuNu)*scaleFactorEW
                            num = num - (num_EWKbkg + num_WToMuNu)*scaleFactorEW
                            
                            # denErr = math.sqrt(denErr**2 + denErr_EWKbkg**2 + denErr_WToMuNu**2)
                            # numErr = math.sqrt(numErr**2 + numErr_EWKbkg**2 + numErr_WToMuNu**2)
                            
                            #ERROR ON SUM EVALUATION
                            antiNumErr_EWKbkg = ROOT.Double(0)
                            antiNumErr_WToMuNu = ROOT.Double(0)
                            antiNum_EWKbkg = hdict[p+e+s+varname+'EWKbkg'+'Tot'].ProjectionX("histoNum",NcutTight,-1, "e").IntegralAndError(0,NcutLoose-1,antiNumErr_EWKbkg)            
                            antiNum_WToMuNu = hdict[p+e+s+varname+'WToMuNu'+'Tot'].ProjectionX("histoNum",NcutTight,-1, "e").IntegralAndError(0,NcutLoose-1,antiNumErr_WToMuNu)

                            antiNum = antiNum - (antiNum_EWKbkg + antiNum_WToMuNu)*scaleFactorEW

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
                        den = hsubtract.ProjectionX("histoDen",0,-1,"e").IntegralAndError(NcutLoose-1,-1,denErr)
                        num = hsubtract.ProjectionX("histoNum",0,NcutTight-1, "e").IntegralAndError(NcutLoose-1,-1,numErr)
                        # print"bin 3,val + content,", hsubtract.ProjectionX("histoDen",0,-1,"e").GetBinContent(3), hsubtract.ProjectionX("histoDen",0,-1,"e").GetBinError(3)
                        # print"bin 3,val + content, no e opt", hsubtract.ProjectionX("histoDen").GetBinContent(3), hsubtract.ProjectionX("histoDen").GetBinError(3)
                        antiNum = hsubtract.ProjectionX("histoNum",NcutTight,-1, "e").IntegralAndError(NcutLoose-1,-1,antiNumErr)
                        # scaleFactorLumi = 1
                        # if(num!= 0 and den!=0) : 
                        #     scaleFactorLumi= numErr*numErr/num
                        #     num = num /scaleFactorLumi
                        #     den = den /scaleFactorLumi
                        #     fake_err = 1/den*math.sqrt(num*(1-num/den))*scaleFactorLumi #standard eff error rewighted on scal factor
                        # print "SCALE FACTOR LUMI :", scaleFactorLumi

                    # print("kind", self.kind, "eta,pt", e, p, "num,den", num, den, "s",s)
                    if(den == 0) : 
                        fake = 0
                        print "WARNING: fake rate den = 0 --> num=", num, "data kind=",self.kind, "(pt,eta,sign)=",p,e,s 
                    if(num==0) :
                        print "WARNING: fake rate num = 0 --> den=", den, "data kind=",self.kind, "(pt,eta,sign)=",p,e,s 
                    else:
                        print "Ok: fake rate --> num/den=", num, den, num/den, "data kind=",self.kind, "(pt,eta,sign)=",p,e,s  
                        fake = num/den
                        # print num, numErr, math.sqrt(num),den, denErr, math.sqrt(den)
                        # fake_err = 1/(den**2)*math.sqrt((numErr**2)*(den**2)+(denErr**2)*(num**2)) #UNCORRELATED!!!!
                        fake_err=(1/(den**2))*math.sqrt((numErr**2)*(antiNum**2)+(antiNumErr**2)*(num**2))

                    hFakes_pt.SetBinContent(self.ptBinningS.index(p)+1,fake)
                    h2Fakes_sign.SetBinContent(self.etaBinningS.index(e)+1, self.ptBinningS.index(p)+1,fake)
                    hFakes_pt.SetBinError(self.ptBinningS.index(p)+1,fake_err)
                    h2Fakes_sign.SetBinError(self.etaBinningS.index(e)+1, self.ptBinningS.index(p)+1,fake_err)
                hFakes[s+e] = hFakes_pt
                
                fitFake = ROOT.TF1("fitFake", 'pol1',30,65,2)
                fitFake.SetParameters(0.5,0.1)
                fitFake.SetParNames("offse","slope")
                hFakes_pt.Fit(fitFake,"","",0,120)
                hFakes[s+e+'offset']=fitFake.GetParameter(0)            
                hFakes[s+e+'slope']=fitFake.GetParameter(1)            

            h2Fakes[s] = h2Fakes_sign
        
        hFakes.update(h2Fakes)
        return hFakes        
    
    
    # def ptVSeta_map(self, hdict) :
    #     self.hdict = hdict 

    # def ABCD_hypo(self, hdict) :
        #  self.hdict = hdict         
        
    def bkg_template(self, data, fakedict, promptdict, hdict, fit = False, tightcut = 0.15, loosecut=40, varname = 'pfRelIso04_all_corrected_MET_nom_mt') :
        self.data = data
        self.fakedict = fakedict
        self.promptdict = promptdict
        self.hdict = hdict
        self.fit = fit
        self.varname = varname
        self.loosecut = loosecut
        self.tightcut = tightcut      
        
        kindDict = {
            'fake' : 'Data',
            'validation' : 'QCD',
            'fakeMC' : 'DataLike' ,
            'prompt' : 'WToMuNu',
            'validationSigReg' : 'QCD',
            'promptSideband' : 'WToMuNu',
        }
        datakind = kindDict[self.data]                    
        
        htempl = {}
        
        for s in self.signList :
            h2temp_sign = ROOT.TH2F("h2templ_{sign}".format(sign=s),"h2templ_{sign}".format(sign=s),len(self.etaBinning)-1, array('f',self.etaBinning), len(self.ptBinning)-1, array('f',self.ptBinning) )
            for e in self.etaBinningS :
                for p in self.ptBinningS :
                    htemp = hdict[p+e+s+varname+datakind+'Tot'].Clone('templ'+p+'_'+e+'_'+datakind+s+'_'+varname)
                    
                    isoMin= htemp.GetYaxis().GetBinCenter(1)-htemp.GetYaxis().GetBinWidth(1)/2
                    binsizeTight = htemp.GetYaxis().GetBinWidth(1)
                    NcutTight=(tightcut-isoMin)/binsizeTight
                    NcutTight = int(NcutTight)
                    
                    mtMin= htemp.GetXaxis().GetBinCenter(1)-htemp.GetXaxis().GetBinWidth(1)/2
                    binsizeLoose = htemp.GetXaxis().GetBinWidth(1)
                    NcutLoose=(loosecut-mtMin)/binsizeLoose
                    NcutLoose = int(NcutLoose)    
                    
                    tightErr = ROOT.Double(0)
                    notTightErr = ROOT.Double(0)                                    
                    
                    Ntight = htemp.ProjectionX("htight",NcutTight,-1, "e").IntegralAndError(NcutLoose-1,-1,tightErr)
                    NnotTight = htemp.ProjectionX("hNotTigth",0,NcutTight-1, "e").IntegralAndError(NcutLoose-1,-1,notTightErr)
                    
                    pr = 1
                    fr = 0
                    
                        
                    if(fit) :
                        fr = fakedict[s+e+'offset']+fakedict[s+e].GetBinCenter(self.ptBinningS.index(p)+1)*fakedict[s+e+'slope']
                        pr = promptdict[s+e+'offset']+promptdict[s+e].GetBinCenter(self.ptBinningS.index(p)+1)*promptdict[s+e+'slope']
                        if pr>1 or fr>1 :
                            print "WARNING!!!!!!, pr>1 or fr>1,", pr, fr
                            fr = 0
                            pr = 1                        
                    else :
                        fr = fakedict[s].GetBinContent(self.etaBinningS.index(e)+1, self.ptBinningS.index(p)+1)
                        pr = promptdict[s].GetBinContent(self.etaBinningS.index(e)+1, self.ptBinningS.index(p)+1)
                        if pr==0 and fr==0 :
                            print "WARNING!!!!!!, pr=fr=0"
                            fr = 0
                            pr = 1 
                    
                    print "fake rate=", fr, "prompt rate=",pr, "(eta,pt)=",e,p, "sign=", s
                    scaleTight = -fr*(1-pr)/(pr-fr)
                    scaleNotTight = fr*pr/(pr-fr)
                    
                    NQCD=Ntight*scaleTight+NnotTight*scaleNotTight
                    
                    h2temp_sign.SetBinContent(self.etaBinningS.index(e)+1, self.ptBinningS.index(p)+1,NQCD)
            htempl[s] = h2temp_sign
        return htempl
            
    
    def integrated_preliminary(self) :
    
        print "getting histos"
        histoDict = {}                          
        for s in self.signList :
            for v,name in map(None,self.varList,self.varName) :
                for f,rootFile in map(None,self.sampleList,self.rootFiles) :
                    if(f!='DataLike') :
                        for r in self.regionList :
                            if(r!='Tot') :
                                # print "Get histo:" 'controlPlotsbkg_'+r+s+'/nom/Muon1_'+v
                                # print "key=",s+v+f+r
                                histoDict[s+v+f+r] =  rootFile.Get('controlPlotsbkg_'+r+s+'/nom/Muon1_'+v)
                                histoDict[s+v+f+r].Scale(self.norm)
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
        print "ratios (integrated, preliminary)"
        ratios = []
        for s in self.signList :
            for v,name in map(None,self.varList,self.varName) :
                for f in self.sampleList :
                    # print 'ratio_'+histoDict[s+v+f+'Tot'].GetName()
                    if 'relIso' in name : cutvalue =  self.relisoCUT
                    else : cutvalue = self.isoCUT
                    ratios.append(self.ratio_2Dto1D(histoDict[s+v+f+'Tot'],cutvalue,'ratio_'+histoDict[s+v+f+'Tot'].GetName()))
        
        output = ROOT.TFile(self.outdir+"/bkg_integrated_preliminary.root","recreate")
        for h in range(len(ratios)):
            ratios[h].Write()



    def differential_preliminary(self, fakerate = False) :
        
        self.fakerate = fakerate #if true calculate the fakerate in bin of eta, pt 
        
        print "getting histos"
        histoDict = {}
        mtDict = {}


        for p in self.ptBinningS :
            for e in self.etaBinningS :                          
                for s in self.signList :
                    for v,name in map(None,self.varList,self.varName) :
                        MtCond = bool(self.ptBinningS.index(p)==0 and self.etaBinningS.index(e)==0 and self.varList.index(v)==0)
                        for f,rootFile in map(None,self.sampleList,self.rootFiles) :
                            if(f!='DataLike') :
                                for r in self.regionList :
                                    if(r!='Tot') :
                                        # print "Get histo:" 'controlPlotsbkg_'+r+s+'/nom/Muon1_'+v+'_'+e+'_'+p
                                        # print "key=",p+e+s+v+f+r
                                        histoDict[p+e+s+v+f+r] =  rootFile.Get('controlPlotsbkg_'+r+s+'/nom/Muon1_'+v+'_'+e+'_'+p)
                                        histoDict[p+e+s+v+f+r].Scale(self.norm)
                                        if(MtCond) : mtDict[s+f+r] = rootFile.Get('controlPlotsbkg_'+r+s+'/nom/Muon1_corrected_MET_nom_mt')

                                    else:
                                        # print "clone histo:", p+e+f+'_'+s+'_'+name+'_Tot'
                                        histoDict[p+e+s+v+f+r] = histoDict[p+e+s+v+f+'Sideband'].Clone(p+'_'+e+'_'+f+'_'+s+'_'+name+'_Tot')
                                        if(MtCond) : mtDict[s+f+r] = mtDict[s+f+'Sideband'].Clone(f+'_'+s+'_Mt_Tot')
                                        for rr in self.regionList :
                                            if (rr =="Sideband" or rr=="Tot") : continue
                                            # print "Added histo:", histoDict[p+e+s+v+f+rr].GetName()
                                            # print "key=",p+e+s+v+f+r
                                            # print "key added=",p+e+s+v+f+rr
                                            histoDict[p+e+s+v+f+r].Add(histoDict[p+e+s+v+f+rr])
                                            if(MtCond) : mtDict[s+f+r].Add(mtDict[s+f+rr])
                                            


                            else :
                                # print "cloned (datalike) histo:", 'DataLike_'+s+'_'+name+'_Tot'
                                # print "key=",p+e+s+v+f+'Tot'
                                histoDict[p+e+s+v+f+'Tot']= histoDict[p+e+s+v+'WToMuNuTot'].Clone(p+'_'+e+'_'+'DataLike_'+s+'_'+name+'_Tot')
                                if(MtCond) : mtDict[s+f+'Tot'] = mtDict[s+'WToMuNuTot'].Clone('DataLike_'+s+'_'+'Mt_Tot')
                                for ff in self.sampleList :
                                    if (ff =="WToMuNu" or ff=="Data" or ff=="DataLike"):  continue
                                    # print "Added (data like) histo:", histoDict[p+e+s+v+ff+'Tot'].GetName()
                                    # print "key summed=",p+e+s+v+ff+'Tot'
                                    histoDict[p+e+s+v+f+'Tot'].Add(histoDict[p+e+s+v+ff+'Tot'])
                                    if(MtCond) : mtDict[s+f+'Tot'].Add(mtDict[s+ff+'Tot'])
                        # print "=======================================================================" 
    
        # print histos            
        # print "ratios (integrated, preliminary)"
        ratios = []
        for p in self.ptBinningS :
            for e in self.etaBinningS :  
                for s in self.signList :
                    for v,name in map(None,self.varList,self.varName) :
                        for f in self.sampleList :
                            # print 'ratio_'+histoDict[p+e+s+v+f+'Tot'].GetName()
                            if 'relIso' in name : cutvalue =  self.relisoCUT
                            else : cutvalue = self.isoCUT
                            ratios.append(self.ratio_2Dto1D(histoDict[p+e+s+v+f+'Tot'],cutvalue,'ratio_'+histoDict[p+e+s+v+f+'Tot'].GetName()))
        
        output = ROOT.TFile(self.outdir+"/bkg_differential_fakerate.root","recreate")
        preliminary_dir = output.mkdir("RatiosVSMt")
        preliminary_dir.cd()
        for h in range(len(ratios)):
            ratios[h].Write()  
        # output.Close()
        
        # ptVSeta_map(hdict = histoDict)
        # ABCD_hypo(hdict = histoDict)
        
        
        ABCD_dir = output.mkdir("ABCD_checks")
        ABCD_dir.cd()
        
            
        
        if(self.fakerate) :
            hfakesMC = self.differential_fakerate(kind = 'fakeMC', hdict = histoDict, mtDict = mtDict)
            hprompt =self.differential_fakerate(kind = 'prompt', hdict = histoDict, mtDict = mtDict)
            hvalidation =self.differential_fakerate(kind = 'validation', hdict = histoDict, mtDict = mtDict)       
            hvalidationSigReg =self.differential_fakerate(kind = 'validationSigReg', hdict = histoDict, mtDict = mtDict)       
            hpromptSideband =self.differential_fakerate(kind = 'promptSideband', hdict = histoDict, mtDict = mtDict)       

            # outputFake = ROOT.TFile(self.outdir+"/bkg_differential_fakerate.root","recreate")
            fakerate_dir = output.mkdir("Fakerate")
            fakerate_dir.cd()
            for a,b,c,d,e in map(None,hfakesMC,hprompt,hvalidation,hvalidationSigReg,hpromptSideband):
                if 'offset' in (a or b or c or d or e) or 'slope' in (a or b or c or d or e) : continue
                hfakesMC[a].Write()  
                hprompt[b].Write() 
                hvalidation[c].Write()  
                hvalidationSigReg[d].Write()  
                hpromptSideband[e].Write()  

            bkg_templateMC = self.bkg_template(data = 'fakeMC', fakedict=hfakesMC, promptdict=hprompt, hdict =histoDict, fit =True, tightcut = 0.15, loosecut=40, varname = 'pfRelIso04_all_corrected_MET_nom_mt')
            for a in bkg_templateMC:
                bkg_templateMC[a].Write()

                
        output.Close()
            
    def fakerate_plots(self) :
        
        inputFile = ROOT.TFile.Open(self.outdir+"/bkg_differential_fakerate.root")
        
        canvasList = []
        legDict = {}
        for s in self.signList :
            for e in self.etaBinningS :
                
                    #---------------------------------------------COMPARISON PLOTS ---------------------------------------------#
                    
                    c_comparison = ROOT.TCanvas("c_comparison_{sign}_{eta}".format(kind=self.kind,sign=s,eta=e),"c_comparison_{kind}_{sign}_{eta}".format(kind=self.kind,sign=s,eta=e),800,600)
                    c_comparison.cd()
                    c_comparison.SetGridx()
                    c_comparison.SetGridy()


                    h_fakeMC = inputFile.Get("Fakerate/hFakes_pt_fakeMC_"+s+"_"+e)
                    h_prompt = inputFile.Get("Fakerate/hFakes_pt_prompt_"+s+"_"+e)
                    h_validation = inputFile.Get("Fakerate/hFakes_pt_validation_"+s+"_"+e)

                    # h_fake = inputFile.Get("Fakerate/hFakes_pt_fake_"+s+"_"+e)
                    
                    h_fakeMC.SetLineWidth(3)
                    h_prompt.SetLineWidth(3)
                    h_validation.SetLineWidth(3)
                    # h_fake.SetLineWidth(3)

                    h_fakeMC.SetLineColor(632+2) #red
                    h_prompt.SetLineColor(600-4) #blue
                    h_validation.SetLineColor(416+2) #green
                    # h_fake.SetLineColor(1) #black
                    
                    h_fakeMC.Draw()
                    h_prompt.Draw("SAME")
                    h_validation.Draw("SAME")
                    # h_fake.Draw("SAME")
                    
                    h_fakeMC.GetYaxis().SetRangeUser(0,1.1)   
                    h_fakeMC.GetYaxis().SetTitle("Isolation Cut Efficiency")
                    h_fakeMC.GetYaxis().SetTitleOffset(1)
                    h_fakeMC.GetXaxis().SetTitle("p_{T}^{#mu} [GeV]")
                    h_fakeMC.SetTitle("Fake Rates, {min}<#eta<{max}, W {sign}".format(min=self.etaBinning[self.etaBinning.index(float(e))], max=e, sign=s))
                    
                    legDict[e+s] = ROOT.TLegend(0.1,0.7,0.48,0.9)
                    legDict[e+s].AddEntry(h_fakeMC,"Data-Like MC")
                    legDict[e+s].AddEntry(h_prompt, "W MC")
                    legDict[e+s].AddEntry(h_validation, "QCD MC")
                    # legDict[e+s].AddEntry(h_fake, "Data")
                    legDict[e+s].Draw("SAME")

                    canvasList.append(c_comparison)
                    
                    
                    #---------------------------------------------ABCD cehcks PLOTS ---------------------------------------------#
                    
                    c_ABCDcheck = ROOT.TCanvas("c_ABCDcheck_{sign}_{eta}".format(kind=self.kind,sign=s,eta=e),"c_ABCDcheck_{kind}_{sign}_{eta}".format(kind=self.kind,sign=s,eta=e),800,600)
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
                    h_promptSideband.SetTitle("Fake Rates, {min}<#eta<{max}, ABCD check, W {sign}".format(min=self.etaBinning[self.etaBinning.index(float(e))], max=e, sign=s))
                    
                    legDict[e+s+'ABCD'] = ROOT.TLegend(0.1,0.7,0.48,0.9)
                    legDict[e+s+'ABCD'].AddEntry(h_promptSideband,"W, Sideband")
                    legDict[e+s+'ABCD'].AddEntry(h_prompt, "W Signal Region")
                    legDict[e+s+'ABCD'].AddEntry(h_validation, "QCD Sideband")
                    legDict[e+s+'ABCD'].AddEntry(h_validationSigReg, "QCD Signal Region")
                    legDict[e+s+'ABCD'].Draw("SAME")

                    canvasList.append(c_ABCDcheck)                    
        
        outputFake = ROOT.TFile(self.outdir+"/bkg_plots.root","recreate")
        for h in range(len(canvasList)) :
            canvasList[h].Write()
            
        
                    
                    
                    
                                        


                
                       
        
        
        
        
        
        
        
        
        



    def integrated_preliminary_OLD_NOT_USE(self) :
        # lvar = [0 for v in range(len(self.varList))]
        # lreg = [lvar for r in range(len(self.regionList))]
        # lsig = [lreg for s in range(len(self.signList))]
        # histos = [lsig for f in range(len(self.sampleList))]
        
        lreg = [0 for r in range(len(self.regionList))]
        lsam = [copy.deepcopy(lreg) for f in range(len(self.sampleList))]
        lvar = [copy.deepcopy(lsam) for v in range(len(self.varList))]
        histos = [copy.deepcopy(lvar) for s in range(len(self.signList))]
        # for f in range(len(self.sampleList)) :
        #     if (self.sampleList[f]!='DataLike') : rootfile = ROOT.TFile.Open(self.folder+'/'+self.sampleList[f]+'.root')
        #     for s in range(len(self.signList)) :
        #         for r in range(len(self.regionList)) :
        #             for v in range(len(self.varList)) :
        #                 if(self.sampleList[f]!='DataLike' and self.regionList[f]!='Tot') :
        #                     histos[f][s][r][v] =  rootfile.Get('controlPlotsbkg_'+self.regionList[r]+self.signList[s]+'/nom/+Muon1_'+self.varList[v])
        print histos      
        print "getting histos"                          
        for s in range(len(self.signList)) :
            # if (self.sampleList[f]!='DataLike') : rootfile = ROOT.TFile.Open(self.folder+'/'+self.sampleList[f]+'.root')
            for v in range(len(self.varList)) :
                for f in range(len(self.sampleList)) :
                    if(self.sampleList[f]!='DataLike') :
                        for r in range(len(self.regionList)) :
                            if(self.regionList[r]!='Tot') :
                                print "Get histo:" 'controlPlotsbkg_'+self.regionList[r]+self.signList[s]+'/nom/+Muon1_'+self.varList[v]#, "from file:",self.rootFiles[f] 
                                histos[s][v][f][r] =  self.rootFiles[f].Get('controlPlotsbkg_'+self.regionList[r]+self.signList[s]+'/nom/Muon1_'+self.varList[v])
                                
                                #line below the dictionary approach, not used.
                                # hdict[self.sampleList[f]+'_'+self.regionList[r]+'_'+self.signList[s]+'_'+self.varList[v]] = self.rootFiles[f].Get('controlPlotsbkg_'+self.regionList[r]+self.signList[s]+'/nom/Muon1_'+self.varList[v])
                                # print "HISTO", s,v,f,r, "name", histos[s][v][f][r]
                            else:
                                print "clone histo:", self.sampleList[f]+'_'+self.signList[s]+'_'+histos[s][v][f][r-1].GetName()+'_Tot'
                                histos[s][v][f][r] = histos[s][v][f][r-1].Clone(self.sampleList[f]+'_'+self.signList[s]+'_'+self.varName[v]+'_Tot')
                                for rr in range(len(self.regionList)-2) :
                                    print "Added histo:", histos[s][v][f][rr].GetName()
                                    histos[s][v][f][r].Add(histos[s][v][f][rr])
                                # print "HISTO",  s,v,f,r, histos[s][v][f][r]

                    else :
                        print "cloned (datalike) histo:", 'DataLike_'+self.signList[s]+'_'+histos[s][v][f-2][len(self.regionList)-1].GetName()+'_Tot'
                        histos[s][v][f][len(self.regionList)-1] = histos[s][v][f-2][len(self.regionList)-1].Clone('DataLike_'+self.signList[s]+'_'+self.varName[v]+'_Tot')
                        for ff in range(len(self.sampleList)-3) :
                            print "Added (data like) histo:", histos[s][v][ff][len(self.regionList)-1].GetName()
                            histos[s][v][f][len(self.regionList)-1].Add(histos[s][v][ff][len(self.regionList)-1])
                        # print "HISTO",  s,v,f,r, histos[s][v][f][len(self.regionList)-1]
                print "======================================================================="

        # print histos            
        print "ratios (integrated, preliminary)"
        ratios = []
        for s in range(len(self.signList)) :
            for v in range(len(self.varList)) :
                for f in range(len(self.sampleList)) :
                    print 'ratio_'+histos[s][v][f][len(self.regionList)-1].GetName()
                    if v == 0 or v==2 : cutvalue =  self.relisoCUT
                    else : cutvalue = self.isoCUT
                    ratios.append(self.ratio_2Dto1D(histos[s][v][f][len(self.regionList)-1],cutvalue,'ratio_'+histos[s][v][f][len(self.regionList)-1].GetName()))
        
        output = ROOT.TFile(self.outdir+"/bkg_integrated_preliminary.root","recreate")
        for h in range(len(ratios)):
            ratios[h].Write()