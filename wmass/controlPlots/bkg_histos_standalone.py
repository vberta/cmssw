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



class bkg_histos_standalone(module):

    def __init__(self, selections, variables, dataType, xsec, inputFile, ptBins,etaBins,systDict, targetLumi = 1.):

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
        
        #debugger
        self.defineCounter = 0
    
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
    
    def bkg_histos(self,sKind,sName, selection,weight,colWeightName) :

        self.systKind = sKind
        self.systName = sName
        self.colWeightName= colWeightName
        self.selection= selection
        self.weight= weight
        
        self.variables = copy.deepcopy(self.variablesUnvaried)

        # print "----------------------------ITERAZIONE:", self.systKind, self.systName
        
        varMT='Muon_corrected_MET_nom_mt'
        varPt="bkgSel_Muon_corrected_pt"
        
        #Apply sistematics            
        if self.dataType == 'MC':
            
            if "SF" in self.systKind or "Weight" in self.systKind:
                newWeight = weight.replace(self.systKind,self.systName)
                colWeightName = 'totweight_{}'.format(self.systName)
                self.d = self.d.Define(colWeightName, 'lumiweight*{}'.format(newWeight))
                self.DefineCounter = self.DefineCounter+1

            elif "nom" in self.systKind or "corrected" in self.systKind :
                self.dictReplacerVar(self.systKind,self.systName)
                selection = selection.replace(self.systKind,self.systName)            
                varMT = varMT.replace(self.systKind,self.systName)
                varPt = varPt.replace(self.systKind,self.systName)                          
                        
        # define variables 
        collName =  self.variables['prefix']
        for var,tools in self.variables['variables'].iteritems():
            if ((not self.systName in var) and self.systName!='nom'): continue
            self.d = self.d.Define(collName+'_'+var,tools[4])
            self.DefineCounter= self.DefineCounter+1
        
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

            h = self.d.Filter(selection).Histo1D((collName+'_'+var, " ; {}; ".format(tools[0]), tools[1],tools[2], tools[3]), collName+'_'+var, colWeightName)
            self.myTH1.append(h)
            
            if(var==varMT) :
                h2 = self.d.Filter(selection).Histo2D((collName+'_'+var+"_VS_eta", " ; {}; ".format(tools[0]),  tools[1],tools[2], tools[3],h_fake.GetNbinsX(), self.etaBins[0],self.etaBins[len(self.etaBins)-1]),collName+'_'+var,collName+'_Muon_eta', colWeightName)
                self.myTH2.append(h2)

        for D2var, tools in self.variables['D2variables'].iteritems():
                h3 = self.d.Filter(selection).Histo3D((collName+'_'+D2var, " ; {}; ".format(tools[0]),  tools[4],tools[5],tools[6],tools[1],tools[2], tools[3],h_fake.GetNbinsX(), self.etaBins[0],self.etaBins[len(self.etaBins)-1]),collName+'_'+tools[7],collName+'_'+tools[8],collName+'_'+tools[9],colWeightName)
                self.myTH3.append(h3)
                         
                for ipt in range(1, h_fake.GetNbinsY()+1): #for each pt bin
                    lowEdgePt = h_fake.GetYaxis().GetBinLowEdge(ipt)
                    upEdgePt = h_fake.GetYaxis().GetBinUpEdge(ipt)
                    
                    dfilter = ROOT.sels(CastToRNode(self.d), lowEdgePt, upEdgePt, selection, varPt)
                
                    h3_ptbin = dfilter.Histo3D((collName+'_'+D2var+'_{eta:.2g}'.format(eta=lowEdgePt), " ; {}; ".format(tools[0]),  tools[4],tools[5],tools[6],tools[1],tools[2], tools[3],h_fake.GetNbinsX(), self.etaBins[0],self.etaBins[len(self.etaBins)-1]),collName+'_'+tools[7],collName+'_'+tools[8],collName+'_'+tools[9],colWeightName)
                
                    self.myTH3.append(h3_ptbin)
                    
                    
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
            self.DefineCounter= self.DefineCounter+2
        else:
            colWeightName = 'totweight'
            self.d = self.d.Define('totweight', '1')   
            self.DefineCounter= self.DefineCounter+1
        
        self.bkg_histos("nom","nom",selection,weight,colWeightName)    
        
        for sKind, sList in self.systDict.iteritems():
            for sName in sList :
                self.bkg_histos(sKind,sName,selection,weight,colWeightName)
        print "DEFINE COUNTING:", self.DefineCounter
        return self.d
