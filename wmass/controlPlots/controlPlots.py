import math 
import ROOT
import re
import sys
sys.path.append('../../framework')
from module import *
from header import *

class controlPlots(module):
   
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
        print "DEBUG Info:", weight, type(weight)

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
                print "Variations of this weight:", variations
                for v in variations:
                    #print nom,v
                    # define mc specific weights
                    if self.dataType == 'MC':           
                        if re.search("[0-9]", v):
                            variation = v[:re.search("[0-9]", v).start()]
                            index = v[re.search("[0-9]", v).start():]
                            print 'lumiweight*{}[{}]'.format(variation,index)
                            nw = '{}[{}]'.format(nom + "*" + variation,i)
                            newWeight = weight.replace(nom,v)
                        else:
                            newWeight = weight.replace(nom,v)
                        newWeight = weight.replace(nom,v) 
                        print "Original Weight:", weight
                        print "New Weight", newWeight
                        self.d = self.d.Define('totweight_{}'.format(v), 'lumiweight*{}'.format(newWeight))
                        #else:
                        #    self.d = self.d.Define('totweight_{}'.format(v), 'lumiweight*{}'.format(v))
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
                    
                    for var,tools in dic['variables'].iteritems():

                        for nom, variations in self.syst.iteritems():
                            for v in variations:
                                self.d = self.d.Filter(selection)
                                if "LHE" in v:
                                    for i in range(0,99):
                                        variation = v + str(i)
                                        print "New histogram name=", Collection +'_' + var+'_'+ variation
                                        #print "DEBUG INFO:", tools[0], tools[1], tools[2], tools[3]
                                        h =self.d.Histo1D((Collection +'_' + var+'_'+ variation, " ; {}; ".format(tools[0]), tools[1],tools[2], tools[3]), collectionName+'_'+ var , 'totweight_{}'.format(variation))
                                        self.myTH1.append(h)
                                else:
                                    h =self.d.Histo1D((Collection+'_'+var+'_'+v, " ; {}; ".format(tools[0]), tools[1],tools[2], tools[3]), collectionName+'_'+var, 'totweight_{}'.format(v))
                                    self.myTH1.append(h)  
                    for h in  self.myTH1:
                        print h.GetName()

            else:        
                print nom, "this is a systematic of type Up/Down variations"
                print "DEBUG INFO:", self.variables.iteritems()
                # loop over variables
                for Collection,dic in self.variables.iteritems():
                    collectionName = dic['inputCollection']
                    print "DEBUG INFO:CollectionName=", collectionName
                  
                    # first of all define new variables in the input collection
                    if dic.has_key('newvariables'):
                        for newvar, definition in dic['newvariables'].iteritems():
                            print("DEBUG INFO:newVar, definition=%s,%s", (newvar, definition)) 
                            print "New var=", collectionName+'_'+newvar 
                                                     
                            # 4th entries in tuple is the string that defines the new variable
                            self.d = self.d.Define(collectionName+'_'+newvar, definition[4]) 

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

        for h in self.myTH1:
            print h.GetName() 
        return self.d
