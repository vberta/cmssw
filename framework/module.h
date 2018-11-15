#ifndef MODULE_H
#define MODULE_H

#include "ROOT/RDataFrame.hxx"
#include "ROOT/RVec.hxx"
#include "ROOT/RDF/RInterface.hxx"

using namespace ROOT::VecOps;
using RNode = ROOT::RDF::RNode;
using rvec_f = const RVec<float> &;
using rvec_i = const RVec<int> &;

class Module {
  
  private:

  	std::vector<ROOT::RDF::RResultPtr<TH1D>> _h1List;
  	std::vector<ROOT::RDF::RResultPtr<TH2D>> _h2List;

  public:

  	virtual ~Module() {};
  	virtual RNode doSomething(RNode) = 0;
  	virtual std::vector<ROOT::RDF::RResultPtr<TH1D>> getTH1();
  	virtual std::vector<ROOT::RDF::RResultPtr<TH2D>> getTH2();
    
};

#endif






	