# Built-in/Generic Imports
import os
import sys
import time
import ROOT
from foo import *

# Begin code for casting

# this injection can be replaced by properly having this in a header
# included in the interpreter at framework startup
ROOT.gInterpreter.Declare('''
template <typename T>
class NodeCaster {
   public:
   static ROOT::RDF::RNode Cast(T rdf)
   {
      return ROOT::RDF::RNode(rdf);
   }
};
''')

def CastToRNode(node):
   return ROOT.NodeCaster(node.__cppname__).Cast(node)

# end code for casting
"""
NSlots = 64
ROOT.gInterpreter.ProcessLine('''
                std::vector<TRandom3> myRndGens({NSlots});
                int seed = 1; // not 0 because seed 0 has a special meaning
                for (auto &&gen : myRndGens) gen.SetSeed(seed++);
                '''.format(NSlots = NSlots))
                """

getVector_code ='''
float getVector (std::vector<float> vec, int idx)
{
   return vec[idx];
}
'''

ROOT.gInterpreter.Declare(getVector_code)

debug_code ='''
float debug (float smth)
{
   std::cout<< "DEBUG LINE " << smth << std::endl;
   return smth;
}
'''

ROOT.gInterpreter.Declare(debug_code)

fillhisto3D ='''
ROOT::RDF::RResultPtr<::TH3D> fillHisto3D(ROOT::RDF::RNode df, char* hname, char* htitle, int nbinsx, double xlow, double xup, 
                                          int nbinsy, double ylow, double yup, int nbinsz, double zlow, double zup,
                                          std::string_view colNameX, std::string_view colNameY, std::string_view colNameZ, std::string_view weight) 
{
  
  return df.Histo3D<float, float, float, double>({hname, htitle, nbinsx, xlow, xup, nbinsy, ylow, yup, nbinsz, zlow, zup}, colNameX, colNameY,colNameZ, weight);
}
'''                                                                            
ROOT.gInterpreter.Declare(fillhisto3D)
