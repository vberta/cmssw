#include "applyCalibration.h"


RNode applyCalibration::run(RNode d){

    auto correctedPtPos = [this](float pt, float eta, float phi){

    	float ptcorr = calib_->getCorrectedPt(pt,eta,phi,1);
    	return ptcorr;
    
	};

	auto correctedPtNeg = [this](float pt, float eta, float phi){

    	float ptcorr = calib_->getCorrectedPt(pt,eta,phi,-1);
    	return ptcorr;
    
	};

	auto d1 = d.Define("corrpt1", correctedPtPos, {"pt1", "eta1", "phi1"}).Define("corrpt2", correctedPtNeg, {"pt2", "eta2", "phi2"});

	
	return d1;


}

std::vector<ROOT::RDF::RResultPtr<TH1D>> applyCalibration::getTH1(){ 
  return _h1List;
}
std::vector<ROOT::RDF::RResultPtr<TH2D>> applyCalibration::getTH2(){ 
  return _h2List;
}
std::vector<ROOT::RDF::RResultPtr<TH3D>> applyCalibration::getTH3(){ 
  return _h3List;
}

