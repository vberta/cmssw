import math 
import ROOT

import sys
sys.path.append('../../framework')
from module import *

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
            #genEventSumw=1

        selection = self.selections[self.dataType]['cut']

        # define mc specific weights
        if self.dataType == 'MC':            
            self.d = self.d.Define('lumiweight', '({L}*{xsec})/({genEventSumw})'.format(L=self.targetLumi, genEventSumw = genEventSumw, xsec = self.xsec)) \
                .Define('totweight', 'lumiweight*Generator_weight*{}'.format(self.selections[self.dataType]['weight']))
        else:
            self.d = self.d.Define('totweight', '1')

        # loop over variables
        for Collection,dic in self.variables.iteritems():
            collectionName = ''
            if dic.has_key('newCollection') and dic['newCollection'] != '':
                if 'index' in dic:                    
                    # define a new subcollection with all the columns of the original collection                    
                    self.d = self.defineSubcollectionFromIndex(dic['inputCollection'], dic['newCollection'], dic['index'], self.d, self.syst)                 
                    collectionName = dic['newCollection']
            else:
                collectionName = dic['inputCollection']

            for var,tools in dic['variables'].iteritems():

                for nom, variations in self.syst.iteritems():
                    
                    if len(variations)==0:
                        print "Nominal"
                        print "Selection:", selection, "Variable", collectionName+'_'+var
                        h = self.d.Filter(selection).Histo1D((Collection+'_'+var, " ; {}; ".format(tools[0]), tools[1],tools[2], tools[3]), collectionName+'_'+var, 'totweight')
                        self.myTH1.append(h)  
                    else:

                        for v in variations:
                            if not nom in var: continue
                            print "Variations", v
                            print "Selection:", selection.replace(nom,v), "Variable", collectionName+'_'+var.replace(nom,v)
                            h = self.d.Filter(selection.replace(nom,v)).Histo1D((Collection+'_'+var.replace(nom,v), " ; {}; ".format(tools[0]), tools[1],tools[2], tools[3]), collectionName+'_'+var.replace(nom,v), 'totweight')
                            self.myTH1.append(h)

        return self.d
