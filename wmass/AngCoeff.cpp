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

    return d7;

}

RNode AngCoeff::defineArmonicsSqAndWscale(RNode d, int c, int k){

    auto sq = [k](float a, float w, rvec_f wscale)-> float{ return a*a*w*wscale[k];};

    auto d2 = d.Define("P"+std::to_string(c)+ "sq"+ "_scale" +std::to_string(k), sq, {"P"+std::to_string(c), "Generator_weight_norm", "LHEScaleWeight"}).Define("P"+std::to_string(c)+ "w"+"_scale" +std::to_string(k), [k](float p, float w, rvec_f wscale){ return p*w*wscale[k];}, {"P"+std::to_string(c), "Generator_weight_norm", "LHEScaleWeight"});

    return d2;

}

RNode AngCoeff::defineArmonicsSqAndWPDF(RNode d, int c, int k){

    auto sq = [k](float a, float w, rvec_f wscale)-> float{ return a*a*w*wscale[k];};

    auto d2 = d.Define("P"+std::to_string(c)+ "sq"+ "_PDF"+ std::to_string(k), sq, {"P"+std::to_string(c), "Generator_weight_norm", "LHEPdfWeight"}).Define("P"+std::to_string(c)+ "w"+ "_PDF" + std::to_string(k), [k](float p, float w, rvec_f wscale){ return p*w*wscale[k];}, {"P"+std::to_string(c), "Generator_weight_norm", "LHEPdfWeight"});

    return d2;

}

RNode AngCoeff::doSomething(RNode d){


    // first normalise generator weights

    auto dw = d.Filter("GenPart_pdgId[GenPart_preFSRMuonIdx]<0").Define("Generator_weight_norm", [](float w)-> float{ return w/abs(w);}, {"Generator_weight"});

    auto dArm = defineArmonics(dw);
    
    float yArr[] = {-3.5, -3.0, -2.5, -2.0, -1.6, -1.2, -0.8, -0.4, 0, 0.4, 0.8, 1.2 ,1.6, 2.0, 2.5, 3.0, 3.5};
    float ptArr[] = {0., 4., 8., 12., 16., 20., 24., 32., 40., 60.};
    
    int nBinsY = 16;
    int nBinsPt = 9;

    std::vector<int> coeff = {0, 1, 2, 3, 4, 5, 6, 7};

    std::map<int, std::vector<ROOT::RDF::RResultPtr<TH2D>>> h2Num;
    std::map<int, ROOT::RDF::RResultPtr<TH2D>> h2Den;
    std::map<int,std::vector<ROOT::RDF::RResultPtr<TH2D>>> h2Num2;

    std::vector<ROOT::RDF::RResultPtr<TH2D>> temp;
    std::vector<ROOT::RDF::RResultPtr<TH2D>> temp2;


    for(unsigned int k=0; k<111; k++){ // loop on QCD scale and PDF variations (8 + 102 variations)

        if(k<9){
            auto hDenominator = dArm.Define("w_scale"+std::to_string(k), [k](float w, rvec_f wscale){ return w*wscale[k];}, {"Generator_weight_norm", "LHEScaleWeight"}).Histo2D(TH2D("hdenom", "hdenom", nBinsY, yArr, nBinsPt, ptArr), "Wrap_preFSR", "Wpt_preFSR", "w_scale"+std::to_string(k));
            h2Den.insert(std::pair<int, ROOT::RDF::RResultPtr<TH2D>>(k, hDenominator));
        }
        else{
            auto d = k-9;
            auto hDenominator = dArm.Define("w_PDF"+std::to_string(k-9), [d](float w, rvec_f wscale){ return w*wscale[d];}, {"Generator_weight_norm", "LHEPdfWeight"}).Histo2D(TH2D("hdenom", "hdenom", nBinsY, yArr, nBinsPt, ptArr), "Wrap_preFSR", "Wpt_preFSR", "w_PDF"+std::to_string(k-9));
            h2Den.insert(std::pair<int, ROOT::RDF::RResultPtr<TH2D>>(k, hDenominator));
        }

        for(auto c:coeff){

            if(k<9){

                auto dArm2 = defineArmonicsSqAndWscale(dArm, c, k); // function depends on coefficient and scale index
                auto hNumerator = dArm2.Histo2D(TH2D(Form("A%i_scaleVar%i", c,k), Form("A%i_scaleVar%i", c,k), nBinsY, yArr, nBinsPt, ptArr), "Wrap_preFSR", "Wpt_preFSR", "P"+std::to_string(c)+ "w"+"_scale" +std::to_string(k));
                auto hP2 =  dArm2.Histo2D(TH2D(Form("A%i_scaleVar%i", c,k), Form("A%i_scaleVar%i", c,k), nBinsY, yArr, nBinsPt, ptArr), "Wrap_preFSR", "Wpt_preFSR", "P"+std::to_string(c)+ "sq"+ "_scale" +std::to_string(k));

                temp.push_back(hNumerator);
                temp2.push_back(hP2);

            }
            else{

                auto dArm2 = defineArmonicsSqAndWPDF(dArm, c, k-9); // function depends on coefficient and scale index
                auto hNumerator = dArm2.Histo2D(TH2D(Form("A%i_PDFVar%i", c,k-9), Form("A%i_PDFVar%i", c,k-9), nBinsY, yArr, nBinsPt, ptArr), "Wrap_preFSR", "Wpt_preFSR", "P"+std::to_string(c)+ "w"+"_PDF" +std::to_string(k-9));
                auto hP2 =  dArm2.Histo2D(TH2D(Form("A%i_PDFVar%i", c,k-9), Form("A%i_PDFVar%i", c,k-9), nBinsY, yArr, nBinsPt, ptArr), "Wrap_preFSR", "Wpt_preFSR", "P"+std::to_string(c)+ "sq"+ "_PDF" +std::to_string(k-9));

                temp.push_back(hNumerator);
                temp2.push_back(hP2);
            }
            
    }

    h2Num.insert(std::pair<int, std::vector<ROOT::RDF::RResultPtr<TH2D>>>(k, temp)); // all histos with variation k
    h2Num2.insert(std::pair<int, std::vector<ROOT::RDF::RResultPtr<TH2D>>>(k, temp2));

    temp.resize(0);
    temp2.resize(0);
    
}

// now iterate over maps

auto it_h2Num = h2Num.begin();
auto it_h2Den = h2Den.begin();
auto it_h2Num2 = h2Num2.begin();

while (it_h2Num != h2Num.end())
{

    for(std::size_t h=0; h < it_h2Num->second.size(); h++){    


        for(int j=1; j<it_h2Num->second.at(h)->GetNbinsY()+1; j++){ // for each pt bin

            for(int i=1; i<it_h2Num->second.at(h)->GetNbinsX()+1; i++){ // for each y bin

                it_h2Num->second.at(h)->SetBinContent(i,j, it_h2Num->second.at(h)->GetBinContent(i,j)/it_h2Den->second->GetBinContent(i,j));
                
                float stdErr2 = it_h2Num2->second.at(h)->GetBinContent(i,j)/it_h2Den->second->GetBinContent(i,j) - it_h2Num->second.at(h)->GetBinContent(i,j)*it_h2Num->second.at(h)->GetBinContent(i,j);
                float sqrtneff = it_h2Den->second->GetBinContent(i,j)/it_h2Den->second->GetBinError(i,j);
                float coeff_err = TMath::Sqrt(stdErr2)/(sqrtneff);

                it_h2Num->second.at(h)->SetBinError(i,j, coeff_err);

                // rescale with the right coefficient

                float cont = it_h2Num->second.at(h)->GetBinContent(i,j);
                float err = it_h2Num->second.at(h)->GetBinError(i,j);

                if(h == 0){        
                    it_h2Num->second.at(h)->SetBinContent(i,j, 20./3.*cont + 2./3.);
                    it_h2Num->second.at(h)->SetBinError(i,j, 20./3.*err);
                }
                else if(h == 1 || h == 5 || h == 6){        
                    it_h2Num->second.at(h)->SetBinContent(i,j, 5*cont);
                    it_h2Num->second.at(h)->SetBinError(i,j, 5*err);
                }
                else if(h == 2){         
                    it_h2Num->second.at(h)->SetBinContent(i,j, 10*cont);
                    it_h2Num->second.at(h)->SetBinError(i,j, 10*err);
                }
                else{       
                    it_h2Num->second.at(h)->SetBinContent(i,j, 4*cont);
                    it_h2Num->second.at(h)->SetBinError(i,j, 4*err);
                }
                
            }
        }


        _h2List.push_back(it_h2Num->second.at(h));

    }

    ++it_h2Den;
    ++it_h2Num;
    ++it_h2Num2;

}


return d;

}

std::vector<ROOT::RDF::RResultPtr<TH1D>> AngCoeff::getTH1(){

    return _h1List;
}

std::vector<ROOT::RDF::RResultPtr<TH2D>> AngCoeff::getTH2(){

    return _h2List;
}







