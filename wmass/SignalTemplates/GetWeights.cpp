#include "GetWeights.h"


RNode GetWeights::run(RNode d){

    TFile *f = TFile::Open(_myString.c_str());

    TIter next(f->GetListOfKeys());
    TKey *key;

    std::vector<TH2D*> hlist;

    while ((key = (TKey*)next())) {

        TString name = key->GetName();
        TH2D *h = (TH2D*) f->Get(name);

        hlist.push_back(h);

    }

    auto getNorm = [hlist](float Wpt, float Wrap, float P0, float P1, float P2, float P3, float P4, float P5, float P6, float P7, float PUL){

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

        for(unsigned int i=0; i<hlist.size(); i++){ //loop over angular coefficients

                int binPt = hlist[i]->GetYaxis()->FindBin(Wpt);
                int binY = hlist[i]->GetXaxis()->FindBin(Wrap);

                norm+=hlist[i]->GetBinContent(binY,binPt)*arm[i]; //sum Ai*Pi

        }

        return norm;

    };

    auto getWeight = [](float norm, float P, float gen){

        return (P/norm)*gen;

    };

    auto dPw = d.Define("Pnorm", getNorm, {"Wpt_preFSR", "Wrap_preFSR", "P0", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "PUL"})
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

std::vector<ROOT::RDF::RResultPtr<TH1D>> GetWeights::getTH1(){ 
    return _h1List;
}
std::vector<ROOT::RDF::RResultPtr<TH2D>> GetWeights::getTH2(){ 
    return _h2List;
}
std::vector<ROOT::RDF::RResultPtr<TH3D>> GetWeights::getTH3(){ 
    return _h3List;
}
bool GetWeights::triggerLoop(){
    return _trigLoop;
}
