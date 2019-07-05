#include "module.h"


std::vector<ROOT::RDF::RResultPtr<TH1D>> Module::getTH1(){ 
	return _h1List;
}
std::vector<ROOT::RDF::RResultPtr<TH2D>> Module::getTH2(){ 
	return _h2List;
}
std::vector<ROOT::RDF::RResultPtr<TH3D>> Module::getTH3(){ 
	return _h3List;
}

void Module::reset(){
	
	_h1List.clear();
	_h2List.clear();
	_h3List.clear();

}
