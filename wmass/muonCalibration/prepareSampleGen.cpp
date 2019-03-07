#include "prepareSampleGen.h"


RNode prepareSampleGen::run(RNode d){

    // define scale, resolution and rapidity

 auto rapidity = [](float pt1, float pt2, float eta1, float eta2, float phi1, float phi2){


  TLorentzVector v1(1,1,1,1);
  TLorentzVector v2(1,1,1,1);

  v1.SetPtEtaPhiM(pt1,eta1,phi1,0.105);
  v2.SetPtEtaPhiM(pt2,eta2,phi2,0.105);
  auto rapidity =(v1+v2).Rapidity();

  return rapidity;
};

auto ptResonance = [](float pt1, float pt2, float eta1, float eta2, float phi1, float phi2){

  TLorentzVector v1(1,1,1,1);
  TLorentzVector v2(1,1,1,1);

  v1.SetPtEtaPhiM(pt1,eta1,phi1,0.105);
  v2.SetPtEtaPhiM(pt2,eta2,phi2,0.105);
  float ptRes =(v1+v2).Pt();

  return ptRes;
};

TRandom3 *random_ = new TRandom3(10101982);

auto smear = [random_](float mass, float massErr){

  //std::cout << " random " << std::endl;

  float smeared = random_->Gaus(0,massErr);
  
  return mass+smeared;

};


auto d1 = d.Filter(_myString).Define("rapidity", rapidity, {"mcpt1","mcpt2","eta1","eta2","phi1","phi2"}).Define("ptRes", ptResonance, {"mcpt1","mcpt2","eta1","eta2","phi1","phi2"}).Filter("fabs(rapidity)<2.4")
.Define("genMassSmeared", smear, {"genMass", "massErr"});

auto h = d1.Histo1D(TH1D("ptRes", "ptRes", 200, 0, 100), "ptRes");

_h1List.push_back(h);


return d1;


}

std::vector<ROOT::RDF::RResultPtr<TH1D>> prepareSampleGen::getTH1(){ 
  return _h1List;
}
std::vector<ROOT::RDF::RResultPtr<TH2D>> prepareSampleGen::getTH2(){ 
  return _h2List;
}
std::vector<ROOT::RDF::RResultPtr<TH3D>> prepareSampleGen::getTH3(){ 
  return _h3List;
}
bool prepareSampleGen::triggerLoop(){
  return _trigLoop;
}
