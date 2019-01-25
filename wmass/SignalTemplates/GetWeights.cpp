#include "GetWeights.h"


RNode GetWeights::run(RNode d){

    TFile *fPlus = TFile::Open("coeffWPlus.root");
    TFile *fMinus = TFile::Open("coeffWMinus.root");

    std::vector<TH2D> hPlus;
    std::vector<TH2D> hMinus;

    TIter next(fPlus->GetListOfKeys());
    TKey *key;

    while ((key = (TKey*)next())) {

        TString name = key.GetName();
        TH2 *hP = (TH1*) fPlus->Get(name);
        TH2 *hM = (TH1*) fMinus->Get(name);

        hPlus.push_back(hP);
        hMinus.push_back(hM);

    }

    auto getNorm = [hPlus,hMinus](float Wpt, float Wrap, int sign, float P0, float P1, float P2, float P3, float P4, float P5, float P6, float P7, float PUL){

        float norm = PUL;
        std::vector<float> arm;

        arm.push_back(P0);
        arm.push_back(P1);
        arm.push_back(P2);
        arm.push_back(P3);
        arm.push_back(P4);
        arm.push_back(P5);
        arm.push_back(P6);
        arm.push_back(P7);

        if(sign>0){ // W minus

            for(unsigned int i=0; i<hMinus.size(); i++){ //loop over angular coefficients

                int binPt = hMinus[i]->GetYaxis()->FindBin(Wpt);
                int binY = hMinus[i]->GetXaxis()->FindBin(Wrap);

                norm+=hMinus[i]->GetBinContent(binY,binPt)*arm[i]; //sum Ai*Pi

            }

        } 
        else{

           for(unsigned int i=0; i<hPlus.size(); i++){ //loop over angular coefficients

            int binPt = hPlus[i]->GetYaxis()->FindBin(Wpt);
            int binY = hPlus[i]->GetXaxis()->FindBin(Wrap);

                norm+=hPlusus[i]->GetBinContent(binY,binPt)*arm[i]; //sum Ai*Pi

            } 
        }




        return norm;

    };

    auto getWeight = [](float norm, float P, float gen){

        return (P/norm)*gen;

    };

    auto dPw = d.Define("Pnorm", getNorm, {"Wpt_preFSR", "Wrap_preFSR", "GenPart_pdgId[GenPart_preFSRMuonIdx]", "P0", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "PUL"})
    .Define("Pweight0", getWeight, {"Pnorm", "P0", "Generator_weight_norm"})
    .Define("Pweight1", getWeight, {"Pnorm", "P1", "Generator_weight_norm"})
    .Define("Pweight2", getWeight, {"Pnorm", "P2", "Generator_weight_norm"})
    .Define("Pweight3", getWeight, {"Pnorm", "P3", "Generator_weight_norm"})
    .Define("Pweight4", getWeight, {"Pnorm", "P4", "Generator_weight_norm"})
    .Define("Pweight5", getWeight, {"Pnorm", "P5", "Generator_weight_norm"})
    .Define("Pweight6", getWeight, {"Pnorm", "P6", "Generator_weight_norm"})
    .Define("Pweight7", getWeight, {"Pnorm", "P7", "Generator_weight_norm"})
    .Define("PweightUL", getWeight, {"Pnorm", "PUL", "Generator_weight_norm"});    

    return dPw;
    
}
