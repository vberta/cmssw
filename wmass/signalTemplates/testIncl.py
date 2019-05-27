import os
import sys
import ROOT
from math import *

# append location of the framework and of the modules to use

sys.path.append('../../framework')

from RDFtreeV2 import RDFtree

ROOT.ROOT.EnableImplicitMT(32)

inputFile = '/scratch/emanca/WMass/RDFprocessor/wmass/data/signalTree*.root'

p = RDFtree(outputDir = 'TEST', inputFile = inputFile, outputFile="test.root")

os.system("g++ -fPIC -Wall -O3 ../../framework/module.cpp ../../wmass/signalTemplates/TemplateBuilderIncl.cpp $(root-config --libs --cflags) -shared -o ../../wmass/signalTemplates/TemplateBuilderIncl.so")
ROOT.gInterpreter.Declare('#include "../../framework/module.h"')
ROOT.gInterpreter.Declare('#include "../../wmass/signalTemplates/TemplateBuilderIncl.h"')
ROOT.gSystem.Load('../../wmass/signalTemplates/TemplateBuilderIncl.so')

from TemplateProj import *
from TemplateFitter import *

p.branch(nodeToStart = 'input', nodeToEnd = 'Templates', modules = [ROOT.TemplateBuilderIncl()],outputFile="templatesIncl.root")
p.getOutput()
p.branch(nodeToStart = 'Templates', nodeToEnd = 'Templates2D', modules = [TemplateProj("TEST/templatesIncl.root")],outputFile="templates2DIncl.root")
p.getOutput()
p.branch(nodeToStart = 'Templates2D', nodeToEnd = 'fit', modules = [TemplateFitter("TEST/templates2DIncl.root")],outputFile="result.root")
p.getOutput()



