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

    def __init__(self, selections, variables, dataType, xsec, inputFile, ptBins,etaBins,targetLumi = 1.,systKind='nom',systName='nom'):

        # TH lists
        self.myTH1 = []
        self.myTH2 = []
        self.myTH3 = []

        # MC or DATA
        self.dataType = dataType

        self.selections = selections
        self.variables = copy.deepcopy(variables)
        self.ptBins = ptBins
        self.etaBins = etaBins
        self.systKind = systKind
        self.systName = systName

        # pb to fb conversion
        self.xsec = xsec / 0.001
        self.targetLumi = targetLumi
        self.inputFile = inputFile
    
    def dictReplacerVar(self, old,new) :
        self.old = old
        self.new = new
        
        mod_variables = {}
        mod_D2variables = {}
        
        for keys, value in self.variables["variables"].iteritems():
            mod_keys = keys.replace(self.old,self.new)
            temp = []
            for i in range(0,len(value)) :
                if (i>0 and i<4)  : 
                    temp.append(value[i])
                else :
                    temp.append(value[i].replace(self.old, self.new))
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
    
    # def dictReplacerSel(self,old,new) :
    #     for keys, value in selection.iteritems():
    #         value = value.
    
    def run(self,d):

        self.d = d
        print "-"

        RDF = ROOT.ROOT.RDataFrame
        runs = RDF('Runs', self.inputFile)

        if self.dataType == 'MC':
            genEventSumw = runs.Sum("genEventSumw").GetValue()
        selection = self.selections[self.dataType]['cut']
        weight = self.selections[self.dataType]['weight']

        # # define mc specific weights (nominal)
        # if self.dataType == 'MC':
        #     self.d = self.d.Define('lumiweight', '({L}*{xsec})/({genEventSumw})'.format(L=self.targetLumi, genEventSumw = genEventSumw, xsec = self.xsec)) \
        #             .Define('totweight', 'lumiweight*{}'.format(weight))
        # else:
        #     self.d = self.d.Define('totweight', '1')
        # colWeightName =  'totweight'
        
        # if "SF" in systKind or "Weight" in systKind:   
        #     newWeight = weight.replace(systKind,systName)
        #     self.d = self.d.Define('totweight_{}'.format(systName), 'lumiweight*{}'.format(newWeight))                
        
        
        #Apply sistematics (weights variations)            
        if self.dataType == 'MC':
            self.d = self.d.Define('lumiweight', '({L}*{xsec})/({genEventSumw})'.format(L=self.targetLumi, genEventSumw = genEventSumw, xsec = self.xsec))
            
            if "SF" in self.systKind or "Weight" in self.systKind:
                newWeight = weight.replace(self.systKind,self.systName)
                colWeightName = 'totweight_{}'.format(self.systName)
                self.d = self.d.Define(colWeightName, 'lumiweight*{}'.format(newWeight))
            else :  
                colWeightName = 'totweight'
                self.d = self.d.Define(colWeightName, 'lumiweight*{}'.format(weight))
        else:
            self.d = self.d.Define('totweight', '1')        
            
        #Apply systematics (column variations)
        varMET='Muon_corrected_MET_nom_mt'
        varPt="bkgSel_Muon_corrected_pt"
        if self.dataType == 'MC' :
            if "nom" in self.systKind or "corrected" in self.systKind :
                self.dictReplacerVar(self.systKind,self.systName)
                selection = selection.replace(self.systKind,self.systName)
                
                varMET = varMET.replace(self.systKind,self.systName)
                varPt = varPt.replace(self.systKind,self.systName)                                 
                        
        # define variables 
        collName =  self.variables['prefix']
        for var,tools in self.variables['variables'].iteritems():
            self.d = self.d.Define(collName+'_'+var,tools[4])
        
        for D2var, tools in self.variables['D2variables'].iteritems():
                self.d = self.d.Define(collName+'_'+D2var+'_Y', tools[7])
                self.d = self.d.Define(collName+'_'+D2var+'_X', tools[8])
                self.d = self.d.Define(collName+'_'+D2var+'_Z', tools[9])

        # save histograms (1D, 2D, 3D)
        
        h_fake = ROOT.TH2F("h_fake", "h_fake", len(self.etaBins)-1, array('f',self.etaBins), len(self.ptBins)-1, array('f',self.ptBins)) #fake hiso for binning only
        for var,tools in self.variables['variables'].iteritems():
    
            h = self.d.Filter(selection).Histo1D((collName+'_'+var, " ; {}; ".format(tools[0]), tools[1],tools[2], tools[3]), collName+'_'+var, colWeightName)
            self.myTH1.append(h)
            
            if(var==varMET) :
                h2 = self.d.Filter(selection).Histo2D((collName+'_'+var+"_VS_eta", " ; {}; ".format(tools[0]),  tools[1],tools[2], tools[3],h_fake.GetNbinsX(), self.etaBins[0],self.etaBins[len(self.etaBins)-1]),collName+'_'+var,collName+'_Muon_eta', colWeightName)
                self.myTH2.append(h2)
    
        for D2var, tools in self.variables['D2variables'].iteritems():
        
                h3 = self.d.Filter(selection).Histo3D((collName+'_'+D2var, " ; {}; ".format(tools[0]),  tools[4],tools[5],tools[6],tools[1],tools[2], tools[3],h_fake.GetNbinsX(), self.etaBins[0],self.etaBins[len(self.etaBins)-1]),collName+'_'+D2var+'_X',collName+'_'+D2var+'_Y',collName+'_'+D2var+'_Z',colWeightName)
                self.myTH3.append(h3)
                         
                for ipt in range(1, h_fake.GetNbinsY()+1): #for each pt bin
                    lowEdgePt = h_fake.GetYaxis().GetBinLowEdge(ipt)
                    upEdgePt = h_fake.GetYaxis().GetBinUpEdge(ipt)

                    
                    dfilter = ROOT.sels(CastToRNode(self.d), lowEdgePt, upEdgePt, selection, varPt)
                
                    h3_ptbin = dfilter.Histo3D((collName+'_'+D2var+'_{eta:.2g}'.format(eta=lowEdgePt), " ; {}; ".format(tools[0]),  tools[4],tools[5],tools[6],tools[1],tools[2], tools[3],h_fake.GetNbinsX(), self.etaBins[0],self.etaBins[len(self.etaBins)-1]),collName+'_'+D2var+'_X',collName+'_'+D2var+'_Y',collName+'_'+D2var+'_Z',colWeightName)
                
                    # h3_ptbin = self.d.Filter(selection).Histo3D((collName+'_'+D2var+'_{eta:.2g}'.format(eta=lowEdgePt), " ; {}; ".format(tools[0]),  tools[4],tools[5],tools[6],tools[1],tools[2], tools[3],h_fake.GetNbinsX(), self.etaBins[0],self.etaBins[len(self.etaBins)-1]),collName+'_'+D2var+'_X',collName+'_'+D2var+'_Y',collName+'_'+D2var+'_Z','totweight')
                    
                    # h3_ptbin = ROOT.fillHisto3D(dfilter,collName+'_'+D2var+'_{eta:.2g}'.format(eta=lowEdgePt), " ; {}; ".format(tools[0]),  tools[4],tools[5],tools[6],tools[1],tools[2], tools[3],h_fake.GetNbinsX(), self.etaBins[0],self.etaBins[len(self.etaBins)-1],collName+'_'+D2var+'_X',collName+'_'+D2var+'_Y',collName+'_'+D2var+'_Z','totweight')


                    self.myTH3.append(h3_ptbin)
        
        
        # for Collection,dic in self.variables.iteritems():
        #     collectionName = dic['inputCollection']
        #     if 'newCollection' in dic: collectionNameNew = dic['newCollection'] 
        #     for var,tools in dic['variables'].iteritems():
        #         if 'index' in dic:   
        #             print collectionName, var
        #             self.d = self.d.Define(collectionNameNew+'_'+var,collectionName+'_'+var+'['+dic['index']+']')
        # 
        #         else :
        #             print collectionName, var
        #             self.d = self.d.Define(collectionNameNew+'_'+var,collectionName+'_'+var)
        #         
        #     # first of all define new variables in the input collection
        #     if dic.has_key('newvariables'):
        #         for newvar, definition in dic['newvariables'].iteritems():
        #             self.d = self.d.Define(collectionNameNew+'_'+newvar, definition[4]) # 4th entries in tuple is the string that defines the new variable
        #         dic['variables'].update(dic['newvariables'])
        # 
        #     collectionName = dic['newCollection']
        # 
        #     if dic.has_key('D2variables'):
        #         for D2var, definition in dic['D2variables'].iteritems():
        #             self.d = self.d.Define(collectionName+'_'+D2var+'_Y', definition[7])
        #             self.d = self.d.Define(collectionName+'_'+D2var+'_X', definition[8])
        #             self.d = self.d.Define(collectionName+'_'+D2var+'_Z', definition[9])
        
        
        
        
        
        
            # h_fake = ROOT.TH2F("h_fake", "h_fake", len(self.etaBins)-1, array('f',self.etaBins), len(self.ptBins)-1, array('f',self.ptBins)) #fake hiso for binning only
            # for var,tools in dic['variables'].iteritems():
            # 
            #     h = self.d.Filter(selection).Histo1D((Collection+'_'+var, " ; {}; ".format(tools[0]), tools[1],tools[2], tools[3]), collectionName+'_'+var, 'totweight')
            #     self.myTH1.append(h)
            # 
            #     if(var=='corrected_MET_nom_mt') :
            #         h2 = self.d.Filter(selection).Histo2D((Collection+'_'+var+"_VS_eta", " ; {}; ".format(tools[0]),  tools[1],tools[2], tools[3],h_fake.GetNbinsX(), self.etaBins[0],self.etaBins[len(self.etaBins)-1]), collectionName+'_'+var,collectionName+'_eta', 'totweight')
            #         self.myTH2.append(h2)
            # 
            # if dic.has_key('D2variables'):
            #     for var,tools in dic['D2variables'].iteritems():
            # 
            #         h3 = self.d.Filter(selection).Histo3D((Collection+'_'+var, " ; {}; ".format(tools[0]),  tools[4],tools[5],tools[6],tools[1],tools[2], tools[3],h_fake.GetNbinsX(), self.etaBins[0],self.etaBins[len(self.etaBins)-1]),collectionName+'_'+var+'_X',collectionName+'_'+var+'_Y',collectionName+'_'+var+'_Z','totweight')
            #         self.myTH3.append(h3)
            # 
            #         for ipt in range(1, h_fake.GetNbinsY()+1): #for each pt bin
            #             lowEdgePt = h_fake.GetYaxis().GetBinLowEdge(ipt)
            #             upEdgePt = h_fake.GetYaxis().GetBinUpEdge(ipt)
            # 
            #             dfilter = ROOT.sels(CastToRNode(self.d), lowEdgePt, upEdgePt, selection, "bkgSelMuon1_corrected_pt")
            # 
            #             h3_ptbin = dfilter.Histo3D((Collection+'_'+var+'_{eta:.2g}'.format(eta=lowEdgePt), " ; {}; ".format(tools[0]),  tools[4],tools[5],tools[6],tools[1],tools[2], tools[3],h_fake.GetNbinsX(), self.etaBins[0],self.etaBins[len(self.etaBins)-1]),collectionName+'_'+var+'_X',collectionName+'_'+var+'_Y',collectionName+'_'+var+'_Z','totweight')
            # 
            #             self.myTH3.append(h3_ptbin)

        return self.d
