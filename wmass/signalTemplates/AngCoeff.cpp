#include "AngCoeff.h"


RNode AngCoeff::defineArmonicsSqAndW(RNode d, std::string c){

    auto sq = [](float a, float w)-> float{ return a*a*w;};

    auto d2 = d.Define("P"+c+ "sq", sq, {"P"+c, "Generator_weight_norm"}).Define("P"+c+ "w", [](float p, float w){ return p*w;}, {"P"+c, "Generator_weight_norm"});

    return d2;

    }

RNode AngCoeff::run(RNode d){

    // first normalise generator weights
    
    auto dArm = d.Define("Generator_weight_norm", [](float w)-> float{ return w/abs(w);}, {"Generator_weight"});
    
    float yArr[] = {-6.0, -3.0, -2.5, -2.0, -1.6, -1.2, -0.8, -0.4, 0, 0.4, 0.8, 1.2 ,1.6, 2.0, 2.5, 3.0, 6.0};
    float ptArr[] = {0., 4., 8., 12., 16., 20., 24., 32., 40., 60., 100., 200.};
    
    int nBinsY = 16;
    int nBinsPt = 11;

    std::vector<std::string> coeff = {"0", "1", "2", "3", "4", "5", "6", "7"};

    // only once 
    auto hDenominator = dArm.Histo2D(TH2D("hdenom", "hdenom", nBinsY, yArr, nBinsPt, ptArr), "Wrap_preFSR", "Wpt_preFSR", "Generator_weight_norm");
    
    _h2List.push_back(hDenominator);

    for(auto c:coeff){

        auto dArm2 = defineArmonicsSqAndW(dArm, c);
        auto hNumerator = dArm2.Histo2D(TH2D(Form("A_%s", c.c_str()), Form("A_%s", c.c_str()), nBinsY, yArr, nBinsPt, ptArr), "Wrap_preFSR", "Wpt_preFSR", "P"+c+"w");
        auto hP2 =  dArm2.Histo2D(TH2D(Form("hnum2_%s", c.c_str()), Form("hnum2_%s", c.c_str()), nBinsY, yArr, nBinsPt, ptArr), "Wrap_preFSR", "Wpt_preFSR", "P"+c+"sq");

        _h2List.push_back(hNumerator);
        _h2List.push_back(hP2);
    
    }

    return dArm;
    
}

std::vector<ROOT::RDF::RResultPtr<TH1D>> AngCoeff::getTH1(){ 
    return _h1List;
}
std::vector<ROOT::RDF::RResultPtr<TH2D>> AngCoeff::getTH2(){ 
    return _h2List;
}
std::vector<ROOT::RDF::RResultPtr<TH3D>> AngCoeff::getTH3(){ 
    return _h3List;
}

void AngCoeff::reset(){
    
    _h1List.clear();
    _h2List.clear();
    _h3List.clear();

}