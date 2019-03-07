#include "reweightSample.h"


RNode reweightSample::run(RNode d){

    TFile *f = TFile::Open("TEST/beforeCalibData.root");
    TFile *f1 = TFile::Open("TEST/gen.root");

    TH1D *hTarget = (TH1D*)f->Get("ptRes");
    TH1D *h = (TH1D*)f1->Get("ptRes");

    hTarget->Divide(h);

    auto weights = [hTarget](float ptRes){

      int bin = hTarget->FindBin(ptRes);

      auto w = hTarget->GetBinContent(bin); 
      
      return w;

    };

    auto d1 = d.Define("ptWeight", weights, {"ptRes"});

    return d1;


}

std::vector<ROOT::RDF::RResultPtr<TH1D>> reweightSample::getTH1(){ 
    return _h1List;
}
std::vector<ROOT::RDF::RResultPtr<TH2D>> reweightSample::getTH2(){ 
    return _h2List;
}
std::vector<ROOT::RDF::RResultPtr<TH3D>> reweightSample::getTH3(){ 
    return _h3List;
}
