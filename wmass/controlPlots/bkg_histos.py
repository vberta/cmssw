import math 
import ROOT
import re

import sys
sys.path.append('../../framework')
from module import *
from header import *
from array import array


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
                    
                    if dic.has_key('D2variables'):
                        for var,tools in dic['D2variables'].iteritems():

                            for nom, variations in self.syst.iteritems():
                                for v in variations:
                        
                                    self.d = self.d.Filter(selection)
                                    
                                    h =self.d.Histo2D((Collection+'_'+var+'_'+v, " ; {}; ".format(tools[0]), tools[4],tools[5], tools[6],tools[1],tools[2], tools[3]), collectionName+'_'+var+'_X',collectionName+'_'+var+'_Y', 'totweight_{}'.format(v))
                                    
                                    self.myTH2.append(h) 

            else:        
                print nom, "this is a systematic of type Up/Down variations"

                # loop over variables
                for Collection,dic in self.variables.iteritems():
                    collectionName = dic['inputCollection']

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
                    
                    if dic.has_key('D2variables'):
                        for D2var, definition in dic['D2variables'].iteritems():
                            self.d = self.d.Define(collectionName+'_'+D2var+'_Y', definition[7]) 
                            self.d = self.d.Define(collectionName+'_'+D2var+'_X', definition[8])                     
                    
                    h_mt_eta = ROOT.TH1F("h_mt_eta", "h_mt_eta", len(self.etaBins)-1, array('f',self.etaBins)) #fake hiso for binning only in eta (for mt)
                    for var,tools in dic['variables'].iteritems():
                    
                        if not self.dataType == 'MC': 
                            h = self.d.Filter(selection).Histo1D((Collection+'_'+var, " ; {}; ".format(tools[0]), tools[1],tools[2], tools[3]), collectionName+'_'+var, 'totweight')
                            
                            self.myTH1.append(h)
                            if(var=='corrected_MET_nom_mt') :
                                for ieta in range(1, h_mt_eta.GetNbinsX()+1): #for each eta bin
                                    lowEdgeEta = h_mt_eta.GetXaxis().GetBinLowEdge(ieta)
                                    upEdgeEta = h_mt_eta.GetXaxis().GetBinUpEdge(ieta) 
                                    hbin = self.d.Filter(selection+'&& Muon_eta[Idx_mu1]<{upEta} && Muon_eta[Idx_mu1]>{lowEta}'.format(upEta=upEdgeEta, lowEta=lowEdgeEta)).Histo1D((Collection+'_'+var+'_{eta:.2g}'.format(eta=lowEdgeEta), " ; {}; ".format(tools[0]), tools[1],tools[2], tools[3]),collectionName+'_'+var,'totweight')    
                                    self.myTH1.append(hbin)                                                
                                

                        else:
                            for nom, variations in self.syst.iteritems():
                    
                                if len(variations)==0:
                                   
                                    h = self.d.Filter(selection).Histo1D((Collection+'_'+var, " ; {}; ".format(tools[0]), tools[1],tools[2], tools[3]), collectionName+'_'+var, 'totweight')
                                    self.myTH1.append(h) 
                                    
                                    if(var=='corrected_MET_nom_mt') :
                                        for ieta in range(1, h_mt_eta.GetNbinsX()+1): #for each eta bin
                                            lowEdgeEta = h_mt_eta.GetXaxis().GetBinLowEdge(ieta)
                                            upEdgeEta = h_mt_eta.GetXaxis().GetBinUpEdge(ieta) 
                                            hbin = self.d.Filter(selection+'&& Muon_eta[Idx_mu1]<{upEta} && Muon_eta[Idx_mu1]>{lowEta}'.format(upEta=upEdgeEta, lowEta=lowEdgeEta)).Histo1D((Collection+'_'+var+'_{eta:.2g}'.format(eta=lowEdgeEta), " ; {}; ".format(tools[0]), tools[1],tools[2], tools[3]),collectionName+'_'+var,'totweight')    
                                            self.myTH1.append(hbin)    
                                            
                                else:

                                    for v in variations:
                                        if not nom in var: continue
                                        h = self.d.Filter(selection.replace(nom,v)).Histo1D((Collection+'_'+var.replace(nom,v), " ; {}; ".format(tools[0]), tools[1],tools[2], tools[3]), collectionName+'_'+var.replace(nom,v), 'totweight')
                                        self.myTH1.append(h)
                                        
                                        print var
                                        if(var=='corrected_MET_nom_mt') :    
                                            for ieta in range(1, h_mt_eta.GetNbinsX()+1): #for each eta bin
                                                lowEdgeEta = h_mt_eta.GetXaxis().GetBinLowEdge(ieta)
                                                upEdgeEta = h_mt_eta.GetXaxis().GetBinUpEdge(ieta) 
                                                hbin = self.d.Filter(selection.replace(nom,v)+'&& Muon_eta[Idx_mu1]<{upEta} && Muon_eta[Idx_mu1]>{lowEta}'.format(upEta=upEdgeEta, lowEta=lowEdgeEta)).Histo1D((Collection+'_'+var.replace(nom,v)+'_{eta:.2g}'.format(eta=lowEdgeEta), " ; {}; ".format(tools[0]), tools[1],tools[2], tools[3]),collectionName+'_'+var.replace(nom,v),'totweight')    
                                                self.myTH1.append(hbin)                                           


                    if dic.has_key('D2variables'):
                        h_fake = ROOT.TH2F("h_fake", "h_fake", len(self.etaBins)-1, array('f',self.etaBins), len(self.ptBins)-1, array('f',self.ptBins)) #fake hiso for binning only
                        for var,tools in dic['D2variables'].iteritems():
                            
                            #produce the list for the variable binning of TH3D
                            xbins = []
                            xbinsize = (tools[6]-tools[5])/tools[4]
                            for x in range (tools[4]) :
                                edgeX= tools[5]+x*xbinsize
                                xbins.append(edgeX)
                            ybins = []
                            ybinsize = (tools[3]-tools[2])/tools[1]
                            for y in range (tools[1]) :
                                edgeY= tools[2]+y*ybinsize
                                ybins.append(edgeY)
                               
                            if not self.dataType == 'MC': 
                                h = self.d.Filter(selection).Histo2D((Collection+'_'+var, " ; {}; ".format(tools[0]),  tools[4],tools[5], tools[6],tools[1],tools[2], tools[3]), collectionName+'_'+var+'_X',collectionName+'_'+var+'_Y', 'totweight')    
                                self.myTH2.append(h)
                                
                                for ieta in range(1, h_fake.GetNbinsX()+1): #for each eta bin
                                    lowEdgeEta = h_fake.GetXaxis().GetBinLowEdge(ieta)
                                    upEdgeEta = h_fake.GetXaxis().GetBinUpEdge(ieta)
                                    
                                    for ipt in range(1, h_fake.GetNbinsY()+1): #for each pt bin
                                        lowEdgePt = h_fake.GetYaxis().GetBinLowEdge(ipt)
                                        upEdgePt = h_fake.GetYaxis().GetBinUpEdge(ipt)
                                        # print "bin eta, pt  : ", ieta, ipt
                                        hbin = self.d.Filter(selection+'&& Muon_eta[Idx_mu1]<{upEta} && Muon_eta[Idx_mu1]>{lowEta} && Muon_corrected_pt[Idx_mu1]<{upPt} && Muon_corrected_pt[Idx_mu1]>{lowPt}'.format(upEta=upEdgeEta, lowEta=lowEdgeEta, upPt=upEdgePt, lowPt=lowEdgePt)).Histo2D((Collection+'_'+var+'_{eta:.2g}_{pt:.2g}'.format(eta=lowEdgeEta, pt=lowEdgePt), " ; {}; ".format(tools[0]), tools[4],tools[5], tools[6],tools[1],tools[2], tools[3]),collectionName+'_'+var+'_X',collectionName+'_'+var+'_Y','totweight')    
                                        self.myTH2.append(hbin)   
                                        
                            else:
                                for nom, variations in self.syst.iteritems():
                        
                                    if len(variations)==0:
                                        h = self.d.Filter(selection).Histo2D((Collection+'_'+var, " ; {}; ".format(tools[0]), tools[4],tools[5], tools[6],tools[1],tools[2], tools[3]), collectionName+'_'+var+'_X',collectionName+'_'+var+'_Y', 'totweight')
                                        self.myTH2.append(h)  
                                        
                                        for ieta in range(1, h_fake.GetNbinsX()+1): #for each eta bin
                                            lowEdgeEta = h_fake.GetXaxis().GetBinLowEdge(ieta)
                                            upEdgeEta = h_fake.GetXaxis().GetBinUpEdge(ieta)
                                            
                                            for ipt in range(1, h_fake.GetNbinsY()+1): #for each pt bin
                                                lowEdgePt = h_fake.GetYaxis().GetBinLowEdge(ipt)
                                                upEdgePt = h_fake.GetYaxis().GetBinUpEdge(ipt)
                                                # print "bin eta, pt  : ", ieta, ipt
                                                hbin = self.d.Filter(selection+'&& Muon_eta[Idx_mu1]<{upEta} && Muon_eta[Idx_mu1]>{lowEta} && Muon_corrected_pt[Idx_mu1]<{upPt} && Muon_corrected_pt[Idx_mu1]>{lowPt}'.format(upEta=upEdgeEta, lowEta=lowEdgeEta, upPt=upEdgePt, lowPt=lowEdgePt)).Histo2D((Collection+'_'+var+'_{eta:.2g}_{pt:.2g}'.format(eta=lowEdgeEta, pt=lowEdgePt), " ; {}; ".format(tools[0]), tools[4],tools[5], tools[6],tools[1],tools[2], tools[3]),collectionName+'_'+var+'_X',collectionName+'_'+var+'_Y','totweight')    
                                                self.myTH2.append(hbin)                                        


                                            
                                            
                                            # print "SELEZIONE=======", selection+'&& Muon_eta[Idx_mu1]<{up} && Muon_eta[Idx_mu1]>{low}'.format(up=upEdgeEta, low=lowEdgeEta)
                                            # print "Nome=", Collection+'_'+var+'_{}'.format(lowEdgeEta), collectionName+'_'+var+'_X',collectionName+'_'+var+'_Y'
                                            # h3D = ROOT.TH3D(Collection+'_'+var+'_{}'.format(lowEdgeEta),Collection+'_'+var+'_{}'.format(lowEdgeEta),tools[4],array('f',xbins),tools[1],array('f',ybins),len(self.ptBins)-1, array('f',self.ptBins))
                                            # hbin = self.d.Filter(selection+'&& Muon_eta[Idx_mu1]<{up} && Muon_eta[Idx_mu1]>{low}'.format(up=upEdgeEta, low=lowEdgeEta)).Histo3D(h3D,collectionName+'_'+var+'_X',collectionName+'_'+var+'_Y',collectionName+'_corrected_pt[Idx_mu1]','totweight')    
                                            # # hbin = self.d.Filter(selection+'&& Muon_eta[Idx_mu1]<{up} && Muon_eta[Idx_mu1]>{low}'.format(up=upEdgeEta, low=lowEdgeEta)).Histo3D((Collection+'_'+var+'_{}'.format(lowEdgeEta), " ; {}; ".format(tools[0]),  tools[4],tools[5], tools[6],tools[1],tools[2], tools[3],h_fake.GetNbinsY(), self.ptBins[0], self.ptBins[len(self.ptBins)-1]),collectionName+'_'+var+'_X',collectionName+'_'+var+'_Y',collectionName+'_corrected_pt[Idx_mu1]','totweight')    
                                            # # hbin = self.d.Filter(selection).Histo3D({"titolo", "nome", 100,0,100,100,0,100,10, 0, 65},'Muon_corrected_pt[Idx_mu1]','Muon_corrected_pt[Idx_mu1]','Muon_corrected_pt[Idx_mu1]')    
                                            # self.myTH3.append(hbin)                                        
                                        
                                        
                                    else:

                                        for v in variations:
                                            if not nom in var: continue
                                            h = self.d.Filter(selection.replace(nom,v)).Histo2D((Collection+'_'+var.replace(nom,v), " ; {}; ".format(tools[0]), tools[4],tools[5], tools[6],tools[1],tools[2], tools[3]), collectionName+'_'+var+'_X'.replace(nom,v),collectionName+'_'+var+'_Y'.replace(nom,v), 'totweight')
                                            self.myTH2.append(h)

        return self.d
