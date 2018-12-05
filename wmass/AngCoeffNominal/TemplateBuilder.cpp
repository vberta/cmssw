#include "TemplateBuilder.h"


RNode TemplateBuilder::doSomething(RNode d){

    return d;

}

std::vector<ROOT::RDF::RResultPtr<TH1D>> TemplateBuilder::getTH1(){ 

    	return _h1List;

}

std::vector<ROOT::RDF::RResultPtr<TH2D>> TemplateBuilder::getTH2(){ 

    	return _h2List;


}
