#include "AngCoeff.h"


RNode AngCoeff::doSomething(RNode d){


    // first normalise generator weights

    auto dw = d.Define("Generator_weight_norm", [](float w)-> float{ return w/225896;}, {"Generator_weight"});

    auto sq = [](float a)-> float{ return a*a;};

    // angular coefficients as defined in https://arxiv.org/pdf/1609.02536.pdf

    // A0 
    auto d0 = dw.Define("P0w", [](float cos_theta, float phi, float w) -> float{ return 1./2.*(1.-3.*cos_theta*cos_theta)*w;}, {"CStheta_preFSR", "CSphi_preFSR", "Generator_weight_norm"}).Define("P0w2", sq, {"P0w"});
    // A1
    auto d1 = d0.Define("P1w", [](float cos_theta, float phi, float w) -> float{ return (2.*cos_theta*sqrt(1.-cos_theta*cos_theta)*cos(phi))*w;}, {"CStheta_preFSR", "CSphi_preFSR", "Generator_weight_norm"}).Define("P1w2", sq, {"P1w"});
    // A2 
    auto d2 = d1.Define("P2w", [](float cos_theta, float phi, float w) -> float{ return 1./2. *(1.-cos_theta*cos_theta)*cos(2.*phi)*w;}, {"CStheta_preFSR", "CSphi_preFSR", "Generator_weight_norm"}).Define("P2w2", sq, {"P2w"});
    // A3
    auto d3 = d2.Define("P3w", [](float cos_theta, float phi, float w) -> float{ return sqrt(1.-cos_theta*cos_theta)*cos(phi)*w;}, {"CStheta_preFSR", "CSphi_preFSR", "Generator_weight_norm"}).Define("P3w2", sq, {"P3w"});    
    // A4
    auto d4 = d3.Define("P4w", [](float cos_theta, float phi, float w) -> float{ return cos_theta*w;}, {"CStheta_preFSR", "CSphi_preFSR", "Generator_weight_norm"}).Define("P4w2", sq, {"P4w"});    
    // A5
    auto d5 = d4.Define("P5w", [](float cos_theta, float phi, float w) -> float{ return (1.-cos_theta*cos_theta)*sin(2.*phi)*w;}, {"CStheta_preFSR", "CSphi_preFSR", "Generator_weight_norm"}).Define("P5w2", sq, {"P5w"}); 
    // A6
    auto d6 = d5.Define("P6w", [](float cos_theta, float phi, float w) -> float{ return (2.*cos_theta*sqrt(1.-cos_theta*cos_theta)*sin(phi))*w;}, {"CStheta_preFSR", "CSphi_preFSR", "Generator_weight_norm"}).Define("P6w2", sq, {"P6w"}); 
    // A7
    auto d7 = d6.Define("P7w", [](float cos_theta, float phi, float w) -> float{ return (sqrt(1.-cos_theta*cos_theta)*sin(phi))*w;}, {"CStheta_preFSR", "CSphi_preFSR", "Generator_weight_norm"}).Define("P7w2", sq, {"P7w"});

    float yArr[] = {-3.5, -3.0, -2.5, -2.0, -1.6, -1.2, -0.8, -0.4, 0, 0.4, 0.8, 1.2 ,1.6, 2.0, 2.5, 3.0, 3.5};
    float ptArr[] = {0., 4., 8., 12., 16., 20., 24., 32., 40., 60.};
    
    int nBinsY = 16;
    int nBinsPt = 9;

    std::vector<std::string> coeff = {"0", "1", "2", "3", "4", "5", "6", "7"};

    std::vector<ROOT::RDF::RResultPtr<TH2D>> h2Num;
    std::vector<ROOT::RDF::RResultPtr<TH2D>> h2Num2;

    // only once 
    auto hDenominator = d7.Histo2D(TH2D("hdenom", "hdenom", nBinsY, yArr, nBinsPt, ptArr), "Wrap_preFSR", "Wpt_preFSR", "Generator_weight_norm");
    
    for(auto c:coeff){

    auto hNumerator = d7.Histo2D(TH2D(Form("A%s", c.c_str()), Form("A%s", c.c_str()), nBinsY, yArr, nBinsPt, ptArr), "Wrap_preFSR", "Wpt_preFSR", "P"+c+"w");
    auto hP2 =  d7.Histo2D(TH2D(Form("hnum2_%s", c.c_str()), Form("hnum2_%s", c.c_str()), nBinsY, yArr, nBinsPt, ptArr), "Wrap_preFSR", "Wpt_preFSR", "P"+c+"w2");

    h2Num.push_back(hNumerator);
    h2Num2.push_back(hP2);
    
    }
    

    for(std::size_t h=0; h < h2Num.size(); h++){    

        for(int j=1; j<h2Num[h]->GetNbinsY()+1; j++){ // for each pt bin

            for(int i=1; i<h2Num[h]->GetNbinsX()+1; i++){ // for each y bin

                h2Num[h]->SetBinContent(i,j, h2Num[h]->GetBinContent(i,j)/hDenominator->GetBinContent(i,j));
                
                float stdErr2 = h2Num2[h]->GetBinContent(i,j)/hDenominator->GetBinContent(i,j) - h2Num[h]->GetBinContent(i,j)*h2Num[h]->GetBinContent(i,j);
                float sqrtneff = hDenominator->GetBinContent(i,j)/TMath::Sqrt(hDenominator->GetBinError(i,j));
                float coeff_err = TMath::Sqrt(stdErr2*0.5)/sqrtneff;
                    
                h2Num[h]->SetBinError(i,j, coeff_err);
                
                }


            }

            _h2List.push_back(h2Num[h]);

        }   

    
    return d7;

}

std::vector<ROOT::RDF::RResultPtr<TH1D>> AngCoeff::getTH1(){

    return _h1List;
}

std::vector<ROOT::RDF::RResultPtr<TH2D>> AngCoeff::getTH2(){

    return _h2List;
}







    