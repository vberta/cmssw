#include "module.h"


std::vector<ROOT::RDF::RResultPtr<TH1D>> Module::getTH1(){ 
	return _h1List;
}
std::vector<ROOT::RDF::RResultPtr<TH2D>> Module::getTH2(){ 
	return _h2List;
}
