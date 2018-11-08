#include "ROOT/RDataFrame.hxx"
#include "ROOT/RVec.hxx"
#include "ROOT/RDF/RInterface.hxx"
#include "TH1D.h"

using namespace ROOT::VecOps;
using RNode = ROOT::RDF::RNode;
using rvec_f = const RVec<float> &;
using rvec_i = const RVec<int> &;

class leptonSelection {
  
  private:

  	std::vector<ROOT::RDF::RResultPtr<TH1D>> _h1List;
  	std::vector<ROOT::RDF::RResultPtr<TH2D>> _h2List;

  public:

  	leptonSelection();

  	~leptonSelection();

  	 RNode doSomething(RNode);
  	 std::vector<ROOT::RDF::RResultPtr<TH1D>> getTH1();
  	 std::vector<ROOT::RDF::RResultPtr<TH2D>> getTH2();
    
};

leptonSelection::leptonSelection(){}

leptonSelection::~leptonSelection(){}

RNode leptonSelection::doSomething(RNode d){

	// get bare muon & neutrino

	auto getBareMuonIdx = [](rvec_f pt, rvec_i statusFlags, rvec_i status, rvec_i pdgId){

		const auto idx = ROOT::VecOps::Reverse(ROOT::VecOps::Argsort(pt));
		auto imu = idx[(statusFlags & (1 << 0)) && abs(pdgId)==13 && status==1];

		if( imu.size()>0) return Int_t(imu[0]);
		else return -99;

	};

	auto getNeutrinoIdx = [](rvec_f pt, rvec_i statusFlags, rvec_i status, rvec_i pdgId){

		const auto idx = ROOT::VecOps::Reverse(ROOT::VecOps::Argsort(pt));
		auto imu = idx[(statusFlags & (1 << 0)) && abs(pdgId)==14 && status==1];

		if( imu.size()>0) return Int_t(imu[0]);
		else return -99;

	};

	auto d1 = d.Define("GenPart_NeutrinoIdx2", getNeutrinoIdx, {"GenPart_pt", "GenPart_statusFlags", "GenPart_status", "GenPart_pdgId"})
	.Filter("GenPart_NeutrinoIdx2!=-99");

	auto h = d1.Histo1D("GenPart_NeutrinoIdx2");

	_h1List.push_back(h);

	return d1;

}

std::vector<ROOT::RDF::RResultPtr<TH1D>> leptonSelection::getTH1(){

	return _h1List;
}

std::vector<ROOT::RDF::RResultPtr<TH2D>> leptonSelection::getTH2(){

	return _h2List;
}







	