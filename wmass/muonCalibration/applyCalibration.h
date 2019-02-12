#ifndef APPLYCALIBRATION_H
#define APPLYCALIBRATION_H


#include "ROOT/RDataFrame.hxx"
#include "ROOT/RVec.hxx"
#include "ROOT/RDF/RInterface.hxx"
#include "TH1D.h"
#include "TH2D.h"
#include "TString.h"
#include "TMath.h"
#include "TLorentzVector.h"
#include "../../framework/module.h"
#include "/scratch/emanca/WMass/MuonCalibration/KaMuCaSLC7/CMSSW_8_0_20/src/KaMuCa/Calibration/interface/KalmanMuonCalibrator.h"

using namespace ROOT::VecOps;
using RNode = ROOT::RDF::RNode;
using rvec_f = const RVec<float> &;
using rvec_i = const RVec<int> &;


class applyCalibration : public Module {

    private:

    std::vector<ROOT::RDF::RResultPtr<TH1D>> _h1List;
    std::vector<ROOT::RDF::RResultPtr<TH2D>> _h2List;
    std::vector<ROOT::RDF::RResultPtr<TH3D>> _h3List;
    std::string name_;
    KalmanMuonCalibrator *calib_;
    
    public:
    
    applyCalibration(std::string calibName): name_(calibName) {

        calib_ = new KalmanMuonCalibrator(name_);
    };
    ~applyCalibration() {};
    RNode run(RNode) override;
    std::vector<ROOT::RDF::RResultPtr<TH1D>> getTH1() override;
    std::vector<ROOT::RDF::RResultPtr<TH2D>> getTH2() override;
    std::vector<ROOT::RDF::RResultPtr<TH3D>> getTH3() override;

};

#endif