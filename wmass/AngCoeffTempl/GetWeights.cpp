#include "GetWeights.h"


RNode GetWeights::doSomething(RNode d){

    float yArr[] = {-6.0, -3.0, -2.5, -2.0, -1.6, -1.2, -0.8, -0.4, 0, 0.4, 0.8, 1.2 ,1.6, 2.0, 2.5, 3.0, 6.0};
    float ptArr[] = {0., 4., 8., 12., 16., 20., 24., 32., 40., 60., 100., 200.};
    
    int nBinsY = 16;
    int nBinsPt = 11;

     auto h = d.Histo2D(TH2D("hnormy", "hnormy", 16, -6, 6, 100, -20, 20), "Wrap_preFSR", "Pnorm");
     auto h1 = d.Histo2D(TH2D("hnormpt", "hnormpt", 100, 0, 200, 100, -20, 20), "Wpt_preFSR", "Pnorm");
    
    _h2List.push_back(h);
    _h2List.push_back(h1);

    auto w = d.Histo1D("PweightUL");

    _h1List.push_back(w);
    
    return d;
}

std::vector<ROOT::RDF::RResultPtr<TH1D>> GetWeights::getTH1(){

    return _h1List;
}

std::vector<ROOT::RDF::RResultPtr<TH2D>> GetWeights::getTH2(){

    return _h2List;
}







    