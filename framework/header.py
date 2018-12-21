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