import math 
import ROOT

import sys
sys.path.append('../../framework')
from module import *

class controlPlots(module):
   
    def __init__(self, selections, variables, dataType, xsec, file, targetLumi = 1.):
        
        self.myTH1 = []
        self.myTH2 = []
        self.myTH3 = []

        self.dataType = dataType # mc or data
        self.selections = selections # for example, 'W'
        self.variables = variables 

        self.xsec = xsec / 0.001 # pb to fb conversion
        self.file = file
        self.targetLumi = targetLumi



    def run(self,d):


        RDF = ROOT.ROOT.RDataFrame
        runs = RDF('Runs', self.file)

        if self.dataType == 'mc': 
            genEventSumw = runs.Sum("genEventSumw").GetValue()
            print (1.*self.xsec)/genEventSumw, 'lumiweight', genEventSumw, 'genEventSumw', self.xsec, 'xsec'
            #genEventSumw=1

        self.d = d.Filter(self.selections[self.dataType]['cut'])

        # define mc specific weights

        if self.dataType == 'mc':
            
            self.d = self.d.Define('lumiweight', '({L}*{xsec})/({genEventSumw})'.format(L=self.targetLumi, genEventSumw = genEventSumw, xsec = self.xsec))\
            .Define('totweight', 'lumiweight*Generator_weight*{}'.format(self.selections[self.dataType]['weight']))

        else:
            self.d = self.d.Define('totweight', '1')

        # loop over variables

        for Collection,dic in self.variables.iteritems():


            if not dic['newCollection'] == '':

                if 'index' in dic:
                    
                    # first of all define a new subcollection with all the columns of the original collection

                    self.d = self.defineSubcollectionFromIndex(Collection, dic['newCollection'], dic['index'], self.d)
                
            for var,tools in dic['variables'].iteritems():

                columns = list(self.d.GetDefinedColumnNames())

                h = self.d.Histo1D((var, " ; {}; ".format(tools[0]), tools[1],tools[2], tools[3]), dic['newCollection']+dic['modifiers']+'_'+var, 'totweight')
                
                self.myTH1.append(h)

        return self.d

