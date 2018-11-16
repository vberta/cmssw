#include "ROOT/RDataFrame.hxx"
#include "ROOT/RVec.hxx"
#include "ROOT/RDF/RInterface.hxx"
#include "TH1D.h"
#include "TH2D.h"
#include "module.h"

using namespace ROOT::VecOps;
using RNode = ROOT::RDF::RNode;
using rvec_f = const RVec<float> &;
using rvec_i = const RVec<int> &;


class AngCoeff : public Module {

	private:

  	std::vector<ROOT::RDF::RResultPtr<TH1D>> _h1List;
  	std::vector<ROOT::RDF::RResultPtr<TH2D>> _h2List;
	
	public:
  	
  	AngCoeff() {};
  	~AngCoeff() {};
  	RNode doSomething(RNode) override;
  	std::vector<ROOT::RDF::RResultPtr<TH1D>> getTH1() override;
  	std::vector<ROOT::RDF::RResultPtr<TH2D>> getTH2() override;


};

RNode AngCoeff::doSomething(RNode d){


	// angular coefficients as defined in https://arxiv.org/pdf/1609.02536.pdf

	// A0 
	auto d0 = d.Define("P0", [](float cos_theta, float phi, float w) -> float{ return 1./2*(1-3*cos_theta*cos_theta)*w;}, {"CStheta_preFSR", "CSphi_preFSR", "Generator_weight"});
	// A1
	auto d1 = d0.Define("P1", [](float cos_theta, float phi, float w) -> float{ return (2*cos_theta*sqrt(1.-cos_theta*cos_theta)*cos(phi))*w;}, {"CStheta_preFSR", "CSphi_preFSR", "Generator_weight"});
	// A2 
	auto d2 = d1.Define("P2", [](float cos_theta, float phi, float w) -> float{ return 1./2 *(1-cos_theta*cos_theta)*cos(2*phi)*w ;}, {"CStheta_preFSR", "CSphi_preFSR", "Generator_weight"});
	// A3
	auto d3 = d2.Define("P3", [](float cos_theta, float phi, float w) -> float{ return sqrt(1.-cos_theta*cos_theta)*cos(phi)*w ;}, {"CStheta_preFSR", "CSphi_preFSR", "Generator_weight"});	
	// A4
	auto d4 = d3.Define("P4", [](float cos_theta, float phi, float w) -> float{ return cos_theta*w;}, {"CStheta_preFSR", "CSphi_preFSR", "Generator_weight"});	
	// A5
	auto d5 = d4.Define("P5", [](float cos_theta, float phi, float w) -> float{ return (1.-cos_theta*cos_theta)*sin(2*phi)*w;}, {"CStheta_preFSR", "CSphi_preFSR", "Generator_weight"});	
	// A6
	auto d6 = d5.Define("P6", [](float cos_theta, float phi, float w) -> float{ return (2*cos_theta*sqrt(1-cos_theta*cos_theta)*sin(phi))*w;}, {"CStheta_preFSR", "CSphi_preFSR", "Generator_weight"});	
	// A7
	auto d7 = d6.Define("P7", [](float cos_theta, float phi, float w) -> float{ return (sqrt(1-cos_theta*cos_theta)*sin(phi))*w;}, {"CStheta_preFSR", "CSphi_preFSR", "Generator_weight"});	
	
	return d7;

}

std::vector<ROOT::RDF::RResultPtr<TH1D>> AngCoeff::getTH1(){

	return _h1List;
}

std::vector<ROOT::RDF::RResultPtr<TH2D>> AngCoeff::getTH2(){

	return _h2List;
}







	