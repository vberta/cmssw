import math 
import ROOT

import sys
sys.path.append('../../framework')
from module import *
from header import *

class bkg_histos(module):
   
    def __init__(self, selections, variables, dataType, xsec, inputFile, targetLumi = 1.):
        
        # TH lists
        self.myTH1 = []
        self.myTH2 = []
        self.myTH3 = []

        # MC or DATA
        self.dataType = dataType
        self.selections = selections
        self.variables = variables 

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
            if "SF" in nom or "Weight" in nom: #if this is a systematic of type "weight variations"

                print nom, "this is a systematic of type weight variations"
                if not self.dataType == 'MC': break 

                for v in variations:
                    newWeight = weight.replace(nom,v)
                    print weight, newWeight

                    # define mc specific weights
                    if self.dataType == 'MC':           
                        self.d = self.d.Define('totweight_{}'.format(v), 'lumiweight*{}[0]'.format(v))
                    else:
                        self.d = self.d.Define('totweight', '1') # to be checked what to do with data
                          

                
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
                                    
                                    h =self.d.Histo2D((Collection+'_'+var+'_'+v, " ; {}; ".format(tools[0]), tools[4],tools[5], tools[6],tools[1],tools[2], tools[3]), collectionName+'_'+D2var+'_X',collectionName+'_'+D2var+'_Y', 'totweight_{}'.format(v))
                                    
                                    self.myTH1.append(h) 

            else:        
                print nom, "this is a systematic of type Up/Down variations"

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
                            if self.dataType == 'MC':                 
                                self.d = self.defineSubcollectionFromIndex(dic['inputCollection'], dic['newCollection'], dic['index'], self.d, self.syst)
                            else:
                                self.d = self.defineSubcollectionFromIndex(dic['inputCollection'], dic['newCollection'], dic['index'], self.d)

                            collectionName = dic['newCollection']
                    
                    if dic.has_key('D2variables'):
                        for D2var, definition in dic['D2variables'].iteritems():
                            self.d = self.d.Define(collectionName+'_'+D2var+'_Y', definition[7]) 
                            self.d = self.d.Define(collectionName+'_'+D2var+'_X', definition[8])                     
                        
                    for var,tools in dic['variables'].iteritems():

                    
                        if not self.dataType == 'MC': 
                            h = self.d.Filter(selection).Histo1D((Collection+'_'+var, " ; {}; ".format(tools[0]), tools[1],tools[2], tools[3]), collectionName+'_'+var, 'totweight')
                            
                            self.myTH1.append(h)

                        else:
                            for nom, variations in self.syst.iteritems():
                    
                                if len(variations)==0:
                                   
                                    h = self.d.Filter(selection).Histo1D((Collection+'_'+var, " ; {}; ".format(tools[0]), tools[1],tools[2], tools[3]), collectionName+'_'+var, 'totweight')
                                    self.myTH1.append(h)  
                                else:

                                    for v in variations:
                                        if not nom in var: continue
                                        h = self.d.Filter(selection.replace(nom,v)).Histo1D((Collection+'_'+var.replace(nom,v), " ; {}; ".format(tools[0]), tools[1],tools[2], tools[3]), collectionName+'_'+var.replace(nom,v), 'totweight')
                                        self.myTH1.append(h)


                    if dic.has_key('D2variables'):
                        for var,tools in dic['D2variables'].iteritems():
        
                            if not self.dataType == 'MC': 
                                h = self.d.Filter(selection).Histo2D((Collection+'_'+var, " ; {}; ".format(tools[0]),  tools[4],tools[5], tools[6],tools[1],tools[2], tools[3]), collectionName+'_'+D2var+'_X',collectionName+'_'+D2var+'_Y', 'totweight')
                                
                                self.myTH2.append(h)

                            else:
                                for nom, variations in self.syst.iteritems():
                        
                                    if len(variations)==0:
                                       
                                        h = self.d.Filter(selection).Histo2D((Collection+'_'+var, " ; {}; ".format(tools[0]), tools[4],tools[5], tools[6],tools[1],tools[2], tools[3]), collectionName+'_'+D2var+'_X',collectionName+'_'+D2var+'_Y', 'totweight')
                                        self.myTH2.append(h)  
                                    else:

                                        for v in variations:
                                            if not nom in var: continue
                                            h = self.d.Filter(selection.replace(nom,v)).Histo2D((Collection+'_'+var.replace(nom,v), " ; {}; ".format(tools[0]), tools[4],tools[5], tools[6],tools[1],tools[2], tools[3]), collectionName+'_'+D2var+'_X'.replace(nom,v),collectionName+'_'+D2var+'_Y'.replace(nom,v), 'totweight')
                                            self.myTH2.append(h)

        return self.d
