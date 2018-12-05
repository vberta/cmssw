#include "AngCoeff.h"

RNode AngCoeff::defineArmonics(RNode d){

     // angular coefficients as defined in https://arxiv.org/pdf/1609.02536.pdf

    // A0 
    auto d0 = d.Define("P0", [](float cos_theta, float phi) -> float{ return 1./2.*(1.-3.*cos_theta*cos_theta);}, {"CStheta_preFSR", "CSphi_preFSR"});
    // A1
    auto d1 = d0.Define("P1", [](float cos_theta, float phi) -> float{ return (2.*cos_theta*sqrt(1.-cos_theta*cos_theta)*cos(phi));}, {"CStheta_preFSR", "CSphi_preFSR"});
    // A2 
    auto d2 = d1.Define("P2", [](float cos_theta, float phi) -> float{ return 1./2. *(1.-cos_theta*cos_theta)*cos(2.*phi);}, {"CStheta_preFSR", "CSphi_preFSR"});
    // A3
    auto d3 = d2.Define("P3", [](float cos_theta, float phi) -> float{ return sqrt(1.-cos_theta*cos_theta)*cos(phi);}, {"CStheta_preFSR", "CSphi_preFSR"});    
    // A4
    auto d4 = d3.Define("P4", [](float cos_theta, float phi) -> float{ return cos_theta;}, {"CStheta_preFSR", "CSphi_preFSR"});    
    // A5
    auto d5 = d4.Define("P5", [](float cos_theta, float phi) -> float{ return (1.-cos_theta*cos_theta)*sin(2.*phi);}, {"CStheta_preFSR", "CSphi_preFSR"}); 
    // A6
    auto d6 = d5.Define("P6", [](float cos_theta, float phi) -> float{ return (2.*cos_theta*sqrt(1.-cos_theta*cos_theta)*sin(phi));}, {"CStheta_preFSR", "CSphi_preFSR"}); 
    // A7
    auto d7 = d6.Define("P7", [](float cos_theta, float phi) -> float{ return (sqrt(1.-cos_theta*cos_theta)*sin(phi));}, {"CStheta_preFSR", "CSphi_preFSR"});

    auto d8 = d7.Define("PUL", [](float cos_theta, float phi) -> float{ return 1-cos_theta*cos_theta;}, {"CStheta_preFSR", "CSphi_preFSR"});

    return d8;

}

RNode AngCoeff::defineArmonicsSqAndW(RNode d, std::string c){

    auto sq = [](float a, float w)-> float{ return a*a*w;};

    auto d2 = d.Define("P"+c+ "sq", sq, {"P"+c, "Generator_weight_norm"}).Define("P"+c+ "w", [](float p, float w){ return p*w;}, {"P"+c, "Generator_weight_norm"});

    return d2;

    }

RNode AngCoeff::doSomething(RNode d){

    auto dw = d.Filter("GenPart_pdgId[GenPart_preFSRMuonIdx]<0").Histo1D("Wrap_preFSR");

    _h1List.push_back(dw);

    return d;

}

std::vector<ROOT::RDF::RResultPtr<TH1D>> AngCoeff::getTH1(){

    return _h1List;
}

std::vector<ROOT::RDF::RResultPtr<TH2D>> AngCoeff::getTH2(){

    return _h2List;
}







    