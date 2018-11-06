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

  	std::vector<ROOT::RDF::RResultPtr<TH1D>> _myObj;

  public:

  	leptonSelection();

  	~leptonSelection();

  	 RNode doSomething(RNode);
  	 std::vector<ROOT::RDF::RResultPtr<TH1D>> getObjects();
    
};

leptonSelection::leptonSelection(){

	_myObj.resize(0);

}

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

	d.Define("GenPart_NeutrinoIdx", getNeutrinoIdx, {"GenPart_pt", "GenPart_statusFlags", "GenPart_status", "GenPart_pdgId"})
	.Filter("GenPart_NeutrinoIdx!=-99");

	return d;

}

std::vector<ROOT::RDF::RResultPtr<TH1D>> leptonSelection::getObjects(){

	
	return _myObj;
}







	