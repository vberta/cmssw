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

    std::vector<ROOT::RDF::RResultPtr<TH2D>> test;
    auto dw = d.Filter("GenPart_pdgId[GenPart_preFSRMuonIdx]<0").Histo1D("Wrap_preFSR");

    _h1List.push_back(dw);

    return d;


    /*
    // first normalise generator weights

    auto dw = d.Filter("GenPart_pdgId[GenPart_preFSRMuonIdx]<0").Define("Generator_weight_norm", [](float w)-> float{ return w/abs(w);}, {"Generator_weight"});

    auto dArm = defineArmonics(dw);
    
    float yArr[] = {-3.5, -3.0, -2.5, -2.0, -1.6, -1.2, -0.8, -0.4, 0, 0.4, 0.8, 1.2 ,1.6, 2.0, 2.5, 3.0, 3.5};
    float ptArr[] = {0., 4., 8., 12., 16., 20., 24., 32., 40., 60.};
    
    int nBinsY = 16;
    int nBinsPt = 9;

    std::vector<std::string> coeff = {"0", "1", "2", "3", "4", "5", "6", "7"};

    std::vector<ROOT::RDF::RResultPtr<TH2D>> h2Num;
    std::vector<ROOT::RDF::RResultPtr<TH2D>> h2Num2;

    // only once 
    auto hDenominator = dArm.Histo2D(TH2D("hdenom", "hdenom", nBinsY, yArr, nBinsPt, ptArr), "Wrap_preFSR", "Wpt_preFSR", "Generator_weight_norm");
    
    for(auto c:coeff){

        auto dArm2 = defineArmonicsSqAndW(dArm, c);
        auto hNumerator = dArm2.Histo2D(TH2D(Form("A%s", c.c_str()), Form("A%s", c.c_str()), nBinsY, yArr, nBinsPt, ptArr), "Wrap_preFSR", "Wpt_preFSR", "P"+c+"w");
        auto hP2 =  dArm2.Histo2D(TH2D(Form("hnum2_%s", c.c_str()), Form("hnum2_%s", c.c_str()), nBinsY, yArr, nBinsPt, ptArr), "Wrap_preFSR", "Wpt_preFSR", "P"+c+"sq");

        h2Num.push_back(hNumerator);
        h2Num2.push_back(hP2);
    
    }
    

    for(std::size_t h=0; h < h2Num.size(); h++){    

        for(int j=1; j<h2Num[h]->GetNbinsY()+1; j++){ // for each pt bin

            for(int i=1; i<h2Num[h]->GetNbinsX()+1; i++){ // for each y bin

                h2Num[h]->SetBinContent(i,j, h2Num[h]->GetBinContent(i,j)/hDenominator->GetBinContent(i,j));
                
                float stdErr2 = h2Num2[h]->GetBinContent(i,j)/hDenominator->GetBinContent(i,j) - h2Num[h]->GetBinContent(i,j)*h2Num[h]->GetBinContent(i,j);
                float sqrtneff = hDenominator->GetBinContent(i,j)/hDenominator->GetBinError(i,j);
                float coeff_err = TMath::Sqrt(stdErr2)/(sqrtneff);
                    
                h2Num[h]->SetBinError(i,j, coeff_err);

                // rescale with the right coefficient

                float cont = h2Num[h]->GetBinContent(i,j);
                float err = h2Num[h]->GetBinError(i,j);
                    
                if(h == 0){        
                    h2Num[h]->SetBinContent(i,j, 20./3.*cont + 2./3.);
                    h2Num[h]->SetBinError(i,j, 20./3.*err);
                }
                else if(h == 1 || h == 5 || h == 6){        
                    h2Num[h]->SetBinContent(i,j, 5*cont);
                    h2Num[h]->SetBinError(i,j, 5*err);
                }
                else if(h == 2){         
                    h2Num[h]->SetBinContent(i,j, 10*cont);
                    h2Num[h]->SetBinError(i,j, 10*err);
                }
                else{       
                    h2Num[h]->SetBinContent(i,j, 4*cont);
                    h2Num[h]->SetBinError(i,j, 4*err);
                }
                
            }


        }

        //_h2List.push_back(h2Num[h]);
        test.push_back(h2Num[h]);

    }   

    auto getNorm = [this](float Wpt, float Wrap, float P0, float P1, float P2, float P3, float P4, float P5, float P6, float P7, float PUL){

        float norm = 0.;
        std::vector<float> arm;

        arm.push_back(P0);
        arm.push_back(P1);
        arm.push_back(P2);
        arm.push_back(P3);
        arm.push_back(P4);
        arm.push_back(P5);
        arm.push_back(P6);
        arm.push_back(P7);
        arm.push_back(PUL);


        for(unsigned int i=0; i<_h2List.size(); i++){ //loop over angular coefficients

            int binPt = _h2List[i]->GetYaxis()->FindBin(Wpt);
            int binY = _h2List[i]->GetXaxis()->FindBin(Wrap);

            norm+=_h2List[i]->GetBinContent(binY,binPt)*arm[i]; //sum Ai*Pi

        }

        return norm;

    };

    auto getWeight = [this](float norm, float P){

        return P/norm;

    };

    auto dPw = dArm.Define("Pnorm", getNorm, {"Wpt_preFSR", "Wrap_preFSR", "P0", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "PUL"}).Define("Pweight0", getWeight, {"Pnorm", "P0"}).Define("Pweight1", getWeight, {"Pnorm", "P1"}).Define("Pweight2", getWeight, {"Pnorm", "P2"})
    .Define("Pweight3", getWeight, {"Pnorm", "P3"}).Define("Pweight4", getWeight, {"Pnorm", "P4"}).Define("Pweight5", getWeight, {"Pnorm", "P5"}).Define("Pweight6", getWeight, {"Pnorm", "P6"}).Define("Pweight7", getWeight, {"Pnorm", "P7"}).Define("PweightUL", getWeight, {"Pnorm", "PUL"});

    auto prova = dPw.Histo2D(TH2D("hdenom2", "hdenom2", nBinsY, yArr, nBinsPt, ptArr), "Wrap_preFSR", "Wpt_preFSR", "Generator_weight_norm");
    _h2List.push_back(prova);
    
    
    return dPw;
    */
}

std::vector<ROOT::RDF::RResultPtr<TH1D>> AngCoeff::getTH1(){

    return _h1List;
}

std::vector<ROOT::RDF::RResultPtr<TH2D>> AngCoeff::getTH2(){

    return _h2List;
}







    