import os
import sys
import ROOT
from math import *

# append location of the framework and of the modules to use

sys.path.append('../../framework')

from RDFtreeV2 import RDFtree

from defineHarmonics import *


os.system("g++ -fPIC -Wall -O3 ../../framework/module.cpp ../../wmass/signalTemplates/AngCoeff.cpp $(root-config --libs --cflags) -shared -o ../../wmass/signalTemplates/AngCoeff.so")
ROOT.gInterpreter.Declare('#include "../../framework/module.h"')
ROOT.gInterpreter.Declare('#include "../../wmass/signalTemplates/AngCoeff.h"')
ROOT.gSystem.Load('../../wmass/signalTemplates/AngCoeff.so')
"""
import numpy as np

np_bins_qt_p0 = np.linspace( 0.0, 10.0, 6)
np_bins_qt_p1 = np.linspace(12.0, 20.0, 5)
np_bins_qt_p2 = np.linspace(24.0, 40.0, 5)
np_bins_qt_p3 = np.array([60, 80, 100, 200]) 
np_bins_qt    = np.append( np.append(np_bins_qt_p0, np_bins_qt_p1), np.append( np_bins_qt_p2, np_bins_qt_p3))

np_bins_y_p0 = np.linspace(-5.0, -2.5,  2)
np_bins_y_p1 = np.linspace(-2.0, +2.0, 21)
np_bins_y_p2 = np.linspace(+2.5, +5.0,  2)
np_bins_y    = np.append( np.append(np_bins_y_p0, np_bins_y_p1), np_bins_y_p2)

hmap = ROOT.TH2D("hmap","hmap",len(np_bins_y)-1,np_bins_y,len(np_bins_qt)-1,np_bins_qt)
"""
ROOT.ROOT.EnableImplicitMT(32)

inputFile = '/scratch/emanca/WMass/RDFprocessor/wmass/data/signalTree_1.root'

p = RDFtree(outputDir = 'TEST', inputFile = inputFile, outputFile="test.root")
p.branch(nodeToStart = 'input', nodeToEnd = 'AngCoeff', modules = [defineHarmonics(), ROOT.AngCoeff()],outputFile="test.root")
p.getOutput()

fIn = ROOT.TFile.Open('TEST/test.root')
myf = fIn.Get("AngCoeff/nom")

hList = []

hNum =[]
hNum2 =[]
hDen =[]

for key in myf.GetListOfKeys():

	hname = key.GetName()
	h = myf.Get(hname)

			
	if "denom" in hname:
		hDen.append(h)
	elif "A" in hname:
		hNum.append(h)
	else: 
		hNum2.append(h)


	
for p1,h in enumerate(hNum):

	h.SetName('A{p1}'.format(p1=p1))
		
	for n in range(1,h.GetNbinsY()+1):

		for m in range(1, h.GetNbinsX()+1):

			h.SetBinContent(m,n,h.GetBinContent(m,n)/hDen[0].GetBinContent(m,n))

                        # error p1rop1agation

                        stdErr2 = hNum2[p1].GetBinContent(m,n)/hDen[0].GetBinContent(m,n) - h.GetBinContent(m,n)*h.GetBinContent(m,n)
                        sqrtneff = hDen[0].GetBinContent(m,n)/hDen[0].GetBinError(m,n)

                        coefferr = sqrt(stdErr2)/sqrtneff

                        h.SetBinError(m,n,coefferr)

                        cont = h.GetBinContent(m,n)
                        err = h.GetBinError(m,n)

                        if p1 == 0:  
                                h.SetBinContent(m,n, 20./3.*cont + 2./3.)
                                h.SetBinError(m,n, 20./3.*err)

                        elif p1 == 1 or p1 == 5 or p1 == 6:        
                                h.SetBinContent(m,n, 5*cont)
                                h.SetBinError(m,n, 5*err)

                        elif p1 == 2:         
                                h.SetBinContent(m,n, 10*cont)
                                h.SetBinError(m,n, 10*err)

                        else:       
                                h.SetBinContent(m,n, 4*cont)
                                h.SetBinError(m,n, 4*err)

hList.extend(hNum) 

fO = ROOT.TFile('testAC.root', 'recreate')

fO.cd()

for h in hList:

	h.Write() 

os.system("g++ -fPIC -Wall -O3 ../../framework/module.cpp ../../wmass/signalTemplates/TemplateBuilder.cpp $(root-config --libs --cflags) -shared -o ../../wmass/signalTemplates/TemplateBuilder.so")
ROOT.gInterpreter.Declare('#include "../../framework/module.h"')
ROOT.gInterpreter.Declare('#include "../../wmass/signalTemplates/TemplateBuilder.h"')
ROOT.gSystem.Load('../../wmass/signalTemplates/TemplateBuilder.so')

os.system("g++ -fPIC -Wall -O3 ../../framework/module.cpp ../../wmass/signalTemplates/GetWeights.cpp $(root-config --libs --cflags) -shared -o ../../wmass/signalTemplates/GetWeights.so")
ROOT.gInterpreter.Declare('#include "../../framework/module.h"')
ROOT.gInterpreter.Declare('#include "../../wmass/signalTemplates/GetWeights.h"')
ROOT.gSystem.Load('../../wmass/signalTemplates/GetWeights.so')

from TemplateProj import *

p.branch(nodeToStart = 'AngCoeff', nodeToEnd = 'Templates', modules = [ROOT.GetWeights('testAC.root'), ROOT.TemplateBuilder()],outputFile="templates.root")
p.getOutput()
p.branch(nodeToStart = 'Templates', nodeToEnd = 'Templates2D', modules = [TemplateProj("TEST/templates.root")],outputFile="templates2D.root")
p.getOutput()




