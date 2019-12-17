import math
import ROOT
import re
import copy


import sys
sys.path.append('../../framework')
from module import *
from header import *
from array import array
import numpy as np

sel_code = '''
    #include "ROOT/RDF/RInterface.hxx"
    ROOT::RDF::RNode sels(ROOT::RDF::RNode df, float lowEdgePt, float upEdgePt, TString selection, std::string varPt){

        auto sels= [=](float pt) { return (pt >lowEdgePt && pt < upEdgePt && selection);};
        std::vector<std::string> p;
        p.emplace_back(varPt);
        const ROOT::Detail::RDF::ColumnNames_t ptCol(p);
        return df.Filter(sels, {ptCol});
    }
'''
ROOT.gInterpreter.Declare(sel_code)
# 
# reweight_code2 = '''
#     double weiPt2( Double_t GenV_preFSR_qt){
#         double mw_over_mz = 0.881;
#         double value = GenV_preFSR_qt*mw_over_mz;
#         return value;
#     };
# '''
# ROOT.gInterpreter.Declare(reweight_code2)

# reweight_code = '''
#     double weiPt(Double_t GenV_preFSR_qt){
#         TFile * file = TFile::Open("/home/users/bertacch/RDF_scratch/wmass/controlPlots/NanoAOD2016-V1MCFinal_ptStudy_TEST/WptReweight.root");
#         TSpline3* spline = (TSpline3*)file->Get("splineRatio");
#         double mw_over_mz = 0.881;
#         double value = spline->Eval(GenV_preFSR_qt*mw_over_mz);
#         return value;
#     };
# '''
# ROOT.gInterpreter.Declare(reweight_code)
# ROOT.gInterpreter.Declare('''TSpline3 *cppspline; ''')


# mult_code = '''
#     double mult(Double_t x, Double_t y){
#         return x*y;
#     };
# '''
# ROOT.gInterpreter.Declare(mult_code)

# 

# reweight_code_merge = '''
#     std::string weiPt_merge(double wptw, TString wei){
#         return 'to_string(wptw)*wei';
#     }
# '''
# ROOT.gInterpreter.Declare(reweight_code_merge)

class bkg_histos_standalone(module):

    def __init__(self, selections, variables, dataType, xsec, inputFile, ptBins,etaBins,systDict, wptFunc, targetLumi = 1., clousureFlag=False, wpt=False, wptRew=False):

        # TH lists
        self.myTH1 = []
        self.myTH2 = []
        self.myTH3 = []

        # MC or DATA
        self.dataType = dataType

        self.selections = selections
        self.variablesUnvaried = variables
        self.ptBins = ptBins
        self.etaBins = etaBins
        # self.systKind = systKind
        # self.systName = systName
        self.systDict = systDict

        # pb to fb conversion
        self.xsec = xsec / 0.001
        self.targetLumi = targetLumi
        self.inputFile = inputFile
        self.clousureFlag = clousureFlag
        self.wpt= wpt #wpt calibration of Z ONLY
        self.wptFunc = wptFunc #function to rewight wpt
        self.wptRew = wptRew #activation of rewight wpt
        
        #debugger
    
    def dictReplacerVar(self, old,new) :
        self.old = old
        self.new = new
        
        mod_variables = {}
        mod_D2variables = {}
        
        for keys, value in self.variables["variables"].iteritems():
            mod_keys = keys.replace(self.old,self.new)
            temp = []
            for i in range(0,len(value)) :
                if (i==0 or i==4) :
                    temp.append(value[i].replace(self.old, self.new))
                else : 
                    temp.append(value[i])
            temp = tuple(temp)
            mod_variables[mod_keys] = temp

        for keys, value in self.variables["D2variables"].iteritems():
            mod_keys = keys.replace(self.old,self.new)
            temp = []
            for i in range(0,len(value)) :
                if (i>0 and i<7)  : 
                    temp.append(value[i])
                else :
                    temp.append(value[i].replace(self.old, self.new))
            temp = tuple(temp)
            mod_D2variables[mod_keys] = temp
        
        del self.variables["variables"]
        self.variables["variables"] =  mod_variables  
        
        del self.variables["D2variables"]
        self.variables["D2variables"] =  mod_D2variables  
    
    def bkg_histos(self,sKind,sName, selection,weight,colWeightName,wpt,wptFunc,wptRew) :

        self.systKind = sKind
        self.systName = sName
        self.colWeightName= colWeightName
        self.selection= selection
        self.weight= weight
        self.wpt = wpt
        self.wptFunc = wptFunc #function to rewight wpt
        self.wptRew = wptRew #activation of rewight wpt

        
        self.variables = copy.deepcopy(self.variablesUnvaried)

        # print "----------------------------ITERAZIONE:", self.systKind, self.systName
        
        varMT='Muon_corrected_MET_nom_mt'
        varMET='MET_pt'
        varPt="bkgSel_Muon_corrected_pt"
        
        #Apply sistematics            
        if self.dataType == 'MC':
            
            if "SF" in self.systKind or "Weight" in self.systKind:
                newWeight = weight.replace(self.systKind,self.systName)
                self.colWeightName = 'totweight_{}'.format(self.systName)
                self.d = self.d.Define(self.colWeightName, 'lumiweight*{}'.format(newWeight))
                if self.wptRew :
                    self.d = self.d.Define(self.colWeightName+'_wptRew', self.colWeightName+'*wptRew')
                    

            elif "nom" in self.systKind or "corrected" in self.systKind :
                self.dictReplacerVar(self.systKind,self.systName)
                self.selection = self.selection.replace(self.systKind,self.systName)            
                varMT = varMT.replace(self.systKind,self.systName)
                varMET = varMET.replace(self.systKind,self.systName)
                varPt = varPt.replace(self.systKind,self.systName)                          
            
            if self.wptRew :
                 self.colWeightName = self.colWeightName+'_wptRew'
        # define variables 
        
        collName =  self.variables['prefix']

        #debug lines ----
        # uno = 'uno'
        # self.d = self.d.Define(uno, '1')  
        # hx = self.d.Filter(self.selection).Histo1D((collName+'_'+self.colWeightName+'_'+self.systName, " ; {}; ", 100,0,10), self.colWeightName, uno)
        # self.myTH1.append(hx)
        # print  self.colWeightName
        #-----

        if not self.wpt: 

            for var,tools in self.variables['variables'].iteritems():
                if ((not self.systName in var) and self.systName!='nom'): continue
                self.d = self.d.Define(collName+'_'+var,tools[4])
            
            # for D2var, tools in self.variables['D2variables'].iteritems():
            #         if ((not self.systName in D2var) and self.systName!='nom'): continue
            #         # print "DEBUG DEFINE 2:", collName, D2var, tools[7], tools[8], tools[9]
            #         self.d = self.d.Define(collName+'_'+D2var+'_Y', tools[7])
            #         self.d = self.d.Define(collName+'_'+D2var+'_X', tools[8])
            #         self.d = self.d.Define(collName+'_'+D2var+'_Z', tools[9])

            # save histograms (1D, 2D, 3D)
            h_fake = ROOT.TH2F("h_fake", "h_fake", len(self.etaBins)-1, array('f',self.etaBins), len(self.ptBins)-1, array('f',self.ptBins)) #fake hiso for binning only
            for var,tools in self.variables['variables'].iteritems():
                if(not tools[5]): continue #variable for 3D histo axis only

                h = self.d.Filter(self.selection).Histo1D((collName+'_'+var+'_'+self.systName, " ; {}; ".format(tools[0]), tools[1],tools[2], tools[3]), collName+'_'+var, self.colWeightName)
                self.myTH1.append(h)
                
                if(var==varMT or var==varMET) :
                    h2 = self.d.Filter(self.selection).Histo2D((collName+'_'+var+'_VS_eta_'+self.systName, " ; {}; ".format(tools[0]),  tools[1],tools[2], tools[3],h_fake.GetNbinsX(), self.etaBins[0],self.etaBins[len(self.etaBins)-1]),collName+'_'+var,collName+'_Muon_eta', self.colWeightName)
                    self.myTH2.append(h2)

            for D2var, tools in self.variables['D2variables'].iteritems():
                    h3 = self.d.Filter(self.selection).Histo3D((collName+'_'+D2var+'_VS_eta_'+self.systName, " ; {}; ".format(tools[0]),  tools[1],tools[2],tools[3],tools[4],tools[5], tools[6],h_fake.GetNbinsX(), self.etaBins[0],self.etaBins[len(self.etaBins)-1]),collName+'_'+tools[7],collName+'_'+tools[8],collName+'_'+tools[9],self.colWeightName)
                    self.myTH3.append(h3)
                             
                    for ipt in range(1, h_fake.GetNbinsY()+1): #for each pt bin
                        lowEdgePt = h_fake.GetYaxis().GetBinLowEdge(ipt)
                        upEdgePt = h_fake.GetYaxis().GetBinUpEdge(ipt)
                        
                        dfilter = ROOT.sels(CastToRNode(self.d), lowEdgePt, upEdgePt, self.selection, varPt)
                    
                        h3_ptbin = dfilter.Filter(self.selection).Histo3D((collName+'_'+D2var+'_VS_eta_{eta:.2g}_'.format(eta=lowEdgePt)+self.systName, " ; {}; ".format(tools[0]),  tools[1],tools[2],tools[3],tools[4],tools[5], tools[6],h_fake.GetNbinsX(), self.etaBins[0],self.etaBins[len(self.etaBins)-1]),collName+'_'+tools[7],collName+'_'+tools[8],collName+'_'+tools[9],self.colWeightName)
                    
                        self.myTH3.append(h3_ptbin)
            if self.clousureFlag :
                for Cvar, tools in self.variables['ClousureVariables'].iteritems():
                        h3 = self.d.Filter(self.selection).Histo3D((collName+'_'+Cvar+'_'+self.systName, " ; {}; ".format(tools[0]),  tools[1],tools[2],tools[3],h_fake.GetNbinsY(), self.ptBins[0],self.ptBins[len(self.ptBins)-1], h_fake.GetNbinsX(), self.etaBins[0],self.etaBins[len(self.etaBins)-1]),collName+'_'+tools[4],collName+'_'+tools[5],collName+'_'+tools[6],self.colWeightName)
                        self.myTH3.append(h3)    
        
        else : #wpt=True
            for var,tools in self.variables['WptVariables'].iteritems():
                if ((not self.systName in var) and self.systName!='nom'): continue
                self.d = self.d.Define(collName+'_'+var,tools[4])   
                    
            h_fake = ROOT.TH2F("h_fake", "h_fake", len(self.etaBins)-1, array('f',self.etaBins), len(self.ptBins)-1, array('f',self.ptBins)) #fake hiso for binning only
            
            wptvar='RecoZ_Muon_corrected_pt' #z-pt and z-pt VS eta-mu VS pt-mu
            tools = self.variables['WptVariables'][wptvar]
            h = self.d.Filter(self.selection).Histo1D((collName+'_'+wptvar+'_'+self.systName, " ; {}; ".format(tools[0]), tools[1],tools[2], tools[3]), collName+'_'+wptvar, self.colWeightName)
            h3 = self.d.Filter(self.selection).Histo3D((collName+'_'+wptvar+'_'+self.systName+'_VS_eta_VS_pt', " ; {}; ".format(tools[0]),  tools[1],tools[2],tools[3],h_fake.GetNbinsY(), self.ptBins[0],self.ptBins[len(self.ptBins)-1], h_fake.GetNbinsX(), self.etaBins[0],self.etaBins[len(self.etaBins)-1]),collName+'_'+tools[4],collName+'_'+tools[5],collName+'_'+tools[6],self.colWeightName)
            self.myTH1.append(h) 
            self.myTH3.append(h3)
            
            wptvar='RecoZ_Muon_mass' #z-pt VS z-mass
            tools = self.variables['WptVariables'][wptvar]
            h2 = self.d.Filter(self.selection).Histo2D((collName+'_'+wptvar+'_'+self.systName+'_VS_Wpt', " ; {}; ".format(tools[0]),  tools[1],tools[2],tools[3],tools[5],tools[6],tools[7]),collName+'_'+tools[4],collName+'_'+tools[8],self.colWeightName)
            self.myTH2.append(h2) 
            
                

                
                    
    def run(self,d):
        self.d = d
        # print "-"

        RDF = ROOT.ROOT.RDataFrame
        runs = RDF('Runs', self.inputFile)

        if self.dataType == 'MC':
            genEventSumw = runs.Sum("genEventSumw").GetValue()
        selection = self.selections[self.dataType]['cut']
        weight = self.selections[self.dataType]['weight']
       
        if self.dataType == 'MC':
            self.d = self.d.Define('lumiweight', '({L}*{xsec})/({genEventSumw})'.format(L=self.targetLumi, genEventSumw = genEventSumw, xsec = self.xsec)) 
            colWeightName = 'totweight'
            self.d = self.d.Define(colWeightName, 'lumiweight*{}'.format(weight))
            if self.wptRew :
                # ROOT.cppspline = self.wptFunc
                # func = self.wptFunc
                self.d = self.d.Define('wptRew', 'wptFunc->Eval(GenV_preFSR_qt)')
                self.d = self.d.Define(colWeightName+'_wptRew','wptRew*'+colWeightName)

                # self.d = self.d.Define(colWeightName+'_wptRew','mult(wptRew,wptRew)')

            
        else:
            colWeightName = 'totweight'
            self.d = self.d.Define('totweight', '1')   
            
        # if self.wptRew and  self.dataType == 'MC': 
            # self.d = self.d.Define('nome','GenV_preFSR_qt')
            # print "SONO PASSATO DI QUI >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
                                # float mw_over_mz = 0.881;
                                # float value = spline.Eval(GenV_preFSR_qt*mw_over_mz);
                                # return to_string(value);
            # def weiPtpy(v) :
                # return v
            # self.d = self.d.Define(self.variabsles['prefix']+'_wptRew'+self.systName, 'PV_npvsGood')   
            # self.d = self.d.Define('wptRew', weiPtpy('GenV_preFSR_qt'})   
               
            # self.d = self.d.Define('wptRew', 'weiPt(GenV_preFSR_qt)')   
            # self.d = self.d.Define('wptRew', ROOT.weiPt, {self.wptFunc,'GenV_preFSR_qt'})                        
                             
                        # colWeightName= colWeightName+'_wptRew'
                        # if "SF" in self.systKind or "Weight" in self.systKind :
                        #     modWeight = newWeight
                        # else :
                        #     modWeight = weight
                        # self.d = self.d.Define(colWeightName, weiPt_merge,{'wptRew','lumiweight*{}'.format(modWeight)})
            # print ">>>>>>>>>>>>>>>>>>>>>>",colWeightName
            # mul = lambda x,y : x*y
            # self.d = self.d.Define(colWeightName+'_wptRew', mul, {}'colWeightName * wptRew')
            # self.d = self.d.Define(colWeightName+'_wptRew','mult(colWeightName,wptRew)')
        
        self.bkg_histos("nom","nom",selection,weight,colWeightName, self.wpt, self.wptFunc,self.wptRew)    
        
        for sKind, sList in self.systDict.iteritems():
            for sName in sList :
                self.bkg_histos(sKind,sName,selection,weight,colWeightName, self.wpt, self.wptFunc,self.wptRew)
                
        # print "number of defined columns=", len(self.d.GetDefinedColumnNames())
        return self.d
