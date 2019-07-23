import math 
import ROOT
import re

import sys
sys.path.append('../../framework')
from module import *
from header import *
from array import array
import numpy as np

# sel_code = '''
#                             
#     ROOT::RDF::RResultPtr<TH3D> sel(ROOT::RDF::RNode df, float lowEdgePt, float upEdgePt){
#                             
#         auto sel= [=](float pt) { return (pt >lowEdgePt && pt < upEdgePt);};
#         
#         Float_t arr[] = {0,1,2,3,4};
#         int arrl = sizeof(arr)/sizeof(Float_t);
#                                         
#         return df.Filter(sel, {"bkgSelMuon1_corrected_pt"}).Histo3D(TH3D(Form("h3_%.2f",lowEdgePt), Form("h3_%.2f",lowEdgePt), arrl,arr,arrl,arr,arrl,arr),  "bkgSelMuon1_corrected_MET_nom_mt", "bkgSelMuon1_pfRelIso04_all", "bkgSelMuon1_eta");
#     }
# '''

sel_code = '''
                            
    ROOT::RDF::RNode sel(ROOT::RDF::RNode df, float lowEdgePt, float upEdgePt, TString selection, std::string_view varPt){
                            
        auto sel= [=](float pt) { return (pt >lowEdgePt && pt < upEdgePt && selection);};
                                        
        return df.Filter(sel, {"bkgSelMuon1_corrected_pt"});
    }
'''
ROOT.gInterpreter.Declare(sel_code)
                             
                            
                                                          

class bkg_histos(module):    
   
    def __init__(self, selections, variables, dataType, xsec, inputFile, ptBins,etaBins,targetLumi = 1.):
                
        # TH lists
        self.myTH1 = []
        self.myTH2 = []
        self.myTH3 = []

        # MC or DATA
        self.dataType = dataType
        
        self.selections = selections
        self.variables = variables 
        self.ptBins = ptBins
        self.etaBins = etaBins
        
        # pb to fb conversion
        self.xsec = xsec / 0.001
        self.targetLumi = targetLumi
        self.inputFile = inputFile
        

        
    def getSyst(self, syst):

        self.syst = syst # this is a dictionary. if empty, it corresponds to nominal

    def run(self,d):        
        
        self.d = d

        RDF = ROOT.ROOT.RDataFrame
        runs = RDF('Runs', self.inputFile)

        if self.dataType == 'MC': 
            genEventSumw = runs.Sum("genEventSumw").GetValue()
            print 'genEventSumw : '+'{:1.1f}'.format(genEventSumw)+' weighted events'
            print 'xsec         : '+'{:1.1f}'.format(self.xsec)+' pb'
            print 'lumiweight   : '+'{:1.8f}'.format((1.*self.xsec)/genEventSumw)+' (|Generator_weight| not accounted for)'

        selection = self.selections[self.dataType]['cut']
        weight = self.selections[self.dataType]['weight']

        # define mc specific weights (nominal)
        
        if self.dataType == 'MC':            
            self.d = self.d.Define('lumiweight', '({L}*{xsec})/({genEventSumw})'.format(L=self.targetLumi, genEventSumw = genEventSumw, xsec = self.xsec)) \
                    .Define('totweight', 'lumiweight*{}'.format(weight))
        else:
            self.d = self.d.Define('totweight', '1')

        for nom,variations in self.syst.iteritems():
            if "SF" in nom or "Weight" in nom or "weight" in nom: #if this is a systematic of type "weight variations"

                print nom, "this is a systematic of type weight variations"
                if not self.dataType == 'MC': break 

                for v in variations:
                    if re.search("[0-9]", v):
                        variation = v[:re.search("[0-9]", v).start()]
                        index = v[re.search("[0-9]", v).start():]
                        print 'lumiweight*{}[{}]'.format(variation,index)
                        nw = '{}[{}]'.format(nom + "*" + variation,index)
                        newWeight = weight.replace(nom,nw)
                    else:
                        newWeight = weight.replace(nom,v)
                    print "Original Weight:", weight
                    print "New Weight", newWeight
                    self.d = self.d.Define('totweight_{}'.format(v), 'lumiweight*{}'.format(newWeight))

                    # define mc specific weights
                    # if self.dataType == 'MC':           
                    # self.d = self.d.Define('totweight_{}'.format(v), 'lumiweight*{}'.format(newWeight))
                    # else:
                        # self.d = self.d.Define('totweight', '1') # to be checked what to do with data
                          

                
                # loop over variables
                for Collection,dic in self.variables.iteritems():
                    
                    collectionName = dic['inputCollection']

                    # first of all define new variables in the input collection
                    if dic.has_key('newvariables'):
                        for newvar, definition in dic['newvariables'].iteritems():
                            self.d = self.d.Define(collectionName+'_'+newvar, definition[4]) # 4th entries in tuple is the string that defines the new variable
                        dic['variables'].update(dic['newvariables'])

                    if dic.has_key('newCollection') and dic['newCollection'] != '':
                        if 'index' in dic:                    
                            # define a new subcollection with all the columns of the original collection                    
                            self.d = self.defineSubcollectionFromIndex(dic['inputCollection'], dic['newCollection'], dic['index'], self.d)                 
                            collectionName = dic['newCollection']
                    
                    if dic.has_key('D2variables'):
                        for D2var, definition in dic['D2variables'].iteritems():
                            self.d = self.d.Define(collectionName+'_'+D2var+'_Y', definition[7]) 
                            self.d = self.d.Define(collectionName+'_'+D2var+'_X', definition[8])                     
                    
                    for var,tools in dic['variables'].iteritems():

                        for nom, variations in self.syst.iteritems():
                            for v in variations:
                    
                                self.d = self.d.Filter(selection)
                                
                                h =self.d.Histo1D((Collection+'_'+var+'_'+v, " ; {}; ".format(tools[0]), tools[1],tools[2], tools[3]), collectionName+'_'+var, 'totweight_{}'.format(v))
                                
                                self.myTH1.append(h) 

                                if(var=='corrected_MET_nom_mt') :
                                    h2 = self.d.Filter(selection).Histo2D((Collection+'_'+var+"_VS_eta_"+v, " ; {}; ".format(tools[0]),  tools[1],tools[2], tools[3],h_fake.GetNbinsX(), self.etaBins[0],self.etaBins[len(self.etaBins)-1]), collectionName+'_'+var,collectionName+'_eta', 'totweight_{}'.format(v))    
                                    self.myTH2.append(h2)                                   
                                
                    
                    if dic.has_key('D2variables'):
                        for var,tools in dic['D2variables'].iteritems():

                            for nom, variations in self.syst.iteritems():
                                for v in variations:
                                    
                                    h3 = self.d.Filter(selection).Histo3D((Collection+'_'+var+'_'+v, " ; {}; ".format(tools[0]),  tools[4],tools[5],tools[6],tools[1],tools[2], tools[3],h_fake.GetNbinsX(), self.etaBins[0],self.etaBins[len(self.etaBins)-1]),collectionName+'_'+var+'_X',collectionName+'_'+var+'_Y',collectionName+'_eta','totweight_{}'.format(v))                                        
                                    self.myTH3.append(h3)  
                                    
                                    for ipt in range(1, h_fake.GetNbinsY()+1): #for each pt bin
                                        lowEdgePt = h_fake.GetYaxis().GetBinLowEdge(ipt)
                                        upEdgePt = h_fake.GetYaxis().GetBinUpEdge(ipt)

                                        dfilter = ROOT.sel(CastToRNode(self.d), lowEdgePt, upEdgePt, selection, "bkgSelMuon1_corrected_pt")                                                

                                        h3_ptbin = dfilter.Histo3D((Collection+'_'+var+'_{eta:.2g}_'+v.format(eta=lowEdgePt), " ; {}; ".format(tools[0]),  tools[4],tools[5],tools[6],tools[1],tools[2], tools[3],h_fake.GetNbinsX(), self.etaBins[0],self.etaBins[len(self.etaBins)-1]),collectionName+'_'+var+'_X',collectionName+'_'+var+'_Y',collectionName+'_eta','totweight_{}'.format(v))
                                                                                      
                                        self.myTH3.append(h3_ptbin)    

            else:        
                print nom, "this is a systematic of type Up/Down variations"

                # loop over variables
                for Collection,dic in self.variables.iteritems():
                    collectionName = dic['inputCollection']
                    print "collectionName1 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", collectionName

                    # first of all define new variables in the input collection
                    if dic.has_key('newvariables'):
                        for newvar, definition in dic['newvariables'].iteritems():
                            self.d = self.d.Define(collectionName+'_'+newvar, definition[4]) # 4th entries in tuple is the string that defines the new variable
                            
                            for v in variations:
                                if not nom in newvar: continue
                                self.d = self.d.Define(collectionName+'_'+newvar.replace(nom,v), definition[4].replace(nom,v))
                                
                        dic['variables'].update(dic['newvariables'])
                            
                    if dic.has_key('newCollection') and dic['newCollection'] != '':
                        if 'index' in dic:                    
                            # define a new subcollection with all the columns of the original collection 
                            if self.dataType == 'MC':                 
                                self.d = self.defineSubcollectionFromIndex(dic['inputCollection'], dic['newCollection'], dic['index'], self.d, self.syst)
                            else:
                                self.d = self.defineSubcollectionFromIndex(dic['inputCollection'], dic['newCollection'], dic['index'], self.d)

                            collectionName = dic['newCollection']
                            print "collectionName >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", collectionName

                    if dic.has_key('D2variables'):
                        for D2var, definition in dic['D2variables'].iteritems():
                            self.d = self.d.Define(collectionName+'_'+D2var+'_Y', definition[7]) 
                            self.d = self.d.Define(collectionName+'_'+D2var+'_X', definition[8])                     
                    
                    #h_mt_eta = ROOT.TH1F("h_mt_eta", "h_mt_eta", len(self.etaBins)-1, array('f',self.etaBins)) #fake hiso for binning only in eta (for mt)
                    h_fake = ROOT.TH2F("h_fake", "h_fake", len(self.etaBins)-1, array('f',self.etaBins), len(self.ptBins)-1, array('f',self.ptBins)) #fake hiso for binning only
                    print "VARIABILI",  dic['variables']
                    for var,tools in dic['variables'].iteritems():
                        
                        print "-------------------------------------<<<<"
                        print "Collection:", Collection+'_'+var
                        print "collectionName:", collectionName+'_'+var
                        print "-------------------------------------<<<<"                        
                    
                        if not self.dataType == 'MC': 
                            h = self.d.Filter(selection).Histo1D((Collection+'_'+var, " ; {}; ".format(tools[0]), tools[1],tools[2], tools[3]), collectionName+'_'+var, 'totweight')
                            
                            self.myTH1.append(h)
                            if(var=='corrected_MET_nom_mt') :
                                h2 = self.d.Filter(selection).Histo2D((Collection+'_'+var+"_VS_eta", " ; {}; ".format(tools[0]),  tools[1],tools[2], tools[3],h_fake.GetNbinsX(), self.etaBins[0],self.etaBins[len(self.etaBins)-1]), collectionName+'_'+var,collectionName+'_eta', 'totweight')    
                                self.myTH2.append(h2)                                               
                                

                        else:
                            
                            for nom, variations in self.syst.iteritems():
                    
                                if len(variations)==0:

                                    h = self.d.Filter(selection).Histo1D((Collection+'_'+var, " ; {}; ".format(tools[0]), tools[1],tools[2], tools[3]), collectionName+'_'+var, 'totweight')
                                    self.myTH1.append(h) 
                                    
                                    if(var=='corrected_MET_nom_mt') :
                                        
                                       h2 = self.d.Filter(selection).Histo2D((Collection+'_'+var+"_VS_eta", " ; {}; ".format(tools[0]),  tools[1],tools[2], tools[3],h_fake.GetNbinsX(), self.etaBins[0],self.etaBins[len(self.etaBins)-1]), collectionName+'_'+var,collectionName+'_eta', 'totweight')   
                                       self.myTH2.append(h2)                                        
                
                                else:

                                    for v in variations:
                                        if not nom in var: continue
                                        h = self.d.Filter(selection.replace(nom,v)).Histo1D((Collection+'_'+var.replace(nom,v), " ; {}; ".format(tools[0]), tools[1],tools[2], tools[3]), collectionName+'_'+var.replace(nom,v), 'totweight')
                                        self.myTH1.append(h)
                                        print "------------------------------------->>>"
                                        print "Collection:", Collection+'_'+var
                                        print "collectionName:", collectionName+'_'+var
                                        print "------------------------------------->>>"
                                        
                                        print var
                                        if(var=='corrected_MET_'+v+'_mt') :    
                                            
                                            h2 = self.d.Filter(selection.replace(nom,v)).Histo2D((Collection+'_'+var+"_VS_eta".replace(nom,v), " ; {}; ".format(tools[0]),  tools[1],tools[2], tools[3],h_fake.GetNbinsX(), self.etaBins[0],self.etaBins[len(self.etaBins)-1]), collectionName+'_'+var.replace(nom,v),collectionName+'_eta'.replace(nom,v), 'totweight')  
                                             
                                            self.myTH2.append(h2)                                           

                    if dic.has_key('D2variables'):
                        for var,tools in dic['D2variables'].iteritems():
                               
                            if not self.dataType == 'MC': 
                                 
                                        h3 = self.d.Filter(selection).Histo3D((Collection+'_'+var, " ; {}; ".format(tools[0]),  tools[4],tools[5],tools[6],tools[1],tools[2], tools[3],h_fake.GetNbinsX(), self.etaBins[0],self.etaBins[len(self.etaBins)-1]),collectionName+'_'+var+'_X',collectionName+'_'+var+'_Y',collectionName+'_eta','totweight')                                        
                                        self.myTH3.append(h3)  
                                        
                                        for ipt in range(1, h_fake.GetNbinsY()+1): #for each pt bin
                                            lowEdgePt = h_fake.GetYaxis().GetBinLowEdge(ipt)
                                            upEdgePt = h_fake.GetYaxis().GetBinUpEdge(ipt)

                                            dfilter = ROOT.sel(CastToRNode(self.d), lowEdgePt, upEdgePt, selection, "bkgSelMuon1_corrected_pt")                                                

                                            h3_ptbin = dfilter.Histo3D((Collection+'_'+var+'_{eta:.2g}'.format(eta=lowEdgePt), " ; {}; ".format(tools[0]),  tools[4],tools[5],tools[6],tools[1],tools[2], tools[3],h_fake.GetNbinsX(), self.etaBins[0],self.etaBins[len(self.etaBins)-1]),collectionName+'_'+var+'_X',collectionName+'_'+var+'_Y',collectionName+'_eta','totweight')
                                                                                                   
                                            self.myTH3.append(h3_ptbin)                                            
                                        
                            else:
                                for nom, variations in self.syst.iteritems():
                        
                                    if len(variations)==0:
                                        h3 = self.d.Filter(selection).Histo3D((Collection+'_'+var, " ; {}; ".format(tools[0]),  tools[4],tools[5],tools[6],tools[1],tools[2], tools[3],h_fake.GetNbinsX(), self.etaBins[0],self.etaBins[len(self.etaBins)-1]),collectionName+'_'+var+'_X',collectionName+'_'+var+'_Y',collectionName+'_eta','totweight')                                        
                                        self.myTH3.append(h3)  
                                        
                                        for ipt in range(1, h_fake.GetNbinsY()+1): #for each pt bin
                                            lowEdgePt = h_fake.GetYaxis().GetBinLowEdge(ipt)
                                            upEdgePt = h_fake.GetYaxis().GetBinUpEdge(ipt)

                                            varPt = "bkgSelMuon1_corrected_pt"
                                            dfilter = ROOT.sel(CastToRNode(self.d), lowEdgePt, upEdgePt, selection, varPt)                                                

                                            h3_ptbin = dfilter.Histo3D((Collection+'_'+var+'_{eta:.2g}'.format(eta=lowEdgePt), " ; {}; ".format(tools[0]),  tools[4],tools[5],tools[6],tools[1],tools[2], tools[3],h_fake.GetNbinsX(), self.etaBins[0],self.etaBins[len(self.etaBins)-1]),collectionName+'_'+var+'_X',collectionName+'_'+var+'_Y',collectionName+'_eta','totweight')
                                                
                                            #WORKING Th3 inside C++
                                            # h3 = ROOT.sel(CastToRNode(self.d), lowEdgePt, upEdgePt)                                                    
                                            self.myTH3.append(h3_ptbin)                                       
                                        
                                        
                                    else:

                                        for v in variations:
                                            if not nom in var: continue
                                                        
                                            # h3 = self.d.Filter(selection.replace(nom,v)).Histo3D((Collection+'_'+var.replace(nom,v), " ; {}; ".format(tools[0]),  tools[4],tools[5],tools[6],tools[1],tools[2], tools[3],h_fake.GetNbinsX(), self.etaBins[0],self.etaBins[len(self.etaBins)-1]),collectionName+'_'+var+'_X',collectionName+'_'+var+'_Y',collectionName+'_eta'.replace(nom,v),'totweight')  
                                            print "-----------------------------------------------------"
                                            print "variaz=",v
                                            print "selection=", selection
                                            print "var=", var
                                            print "collection=", Collection
                                            print "collectionName", collectionName
                                            if collectionName+'_'+var+'_X'.replace(nom,v) in self.d.GetDefinedColumnNames() : print "found X"
                                            if collectionName+'_'+var+'_Y'.replace(nom,v) in self.d.GetDefinedColumnNames() : print "found la Y"
                                            if collectionName+'_eta'.replace(nom,v) in self.d.GetDefinedColumnNames() : 
                                                print "found la Z"
                                            else : print  "cerco", collectionName+'_eta'.replace(nom,v)
                                            # print "DEFINED", self.d.GetDefinedColumnNames()

                                            print "-----------------------------------------------------"
                                            print "-----------------------------------------------------"
                                            print "-----------------------------------------------------"
                                            print "-----------------------------------------------------"
                                            print "-----------------------------------------------------"                                        
                                            # print "NOT DEFINED", self.d.GetColumnNames()

                                            h3 = self.d.Filter(selection.replace(nom,v)).Histo3D((Collection+'_'+var.replace(nom,v), " ; {}; ".format(tools[0]),  tools[4],tools[5],tools[6],tools[1],tools[2], tools[3],h_fake.GetNbinsX(), self.etaBins[0],self.etaBins[len(self.etaBins)-1]),collectionName+'_'+var+'_X'.replace(nom,v),collectionName+'_'+var+'_Y'.replace(nom,v),collectionName+'_eta'.replace(nom,v),'totweight')                                        
                                                                                  
                                            self.myTH3.append(h3)  
                                            
                                            for ipt in range(1, h_fake.GetNbinsY()+1): #for each pt bin
                                                lowEdgePt = h_fake.GetYaxis().GetBinLowEdge(ipt)
                                                upEdgePt = h_fake.GetYaxis().GetBinUpEdge(ipt)

                                                dfilter = ROOT.sel(CastToRNode(self.d), lowEdgePt, upEdgePt, selection.replace(nom,v),"bkgSelMuon1_corrected_pt".replace(nom,v))                                                

                                                h3_ptbin = dfilter.Histo3D((Collection+'_'+var+'_{eta:.2g}'.format(eta=lowEdgePt).replace(nom,v), " ; {}; ".format(tools[0]),  tools[4],tools[5],tools[6],tools[1],tools[2], tools[3],h_fake.GetNbinsX(), self.etaBins[0],self.etaBins[len(self.etaBins)-1]),collectionName+'_'+var+'_X.replace(nom,v)',collectionName+'_'+var+'_Y.replace(nom,v)',collectionName+'_eta'.replace(nom,v),'totweight')
                                                                                                      
                                                self.myTH3.append(h3_ptbin)                                             

        return self.d
