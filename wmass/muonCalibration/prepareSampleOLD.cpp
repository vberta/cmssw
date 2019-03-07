#include "prepareSample.h"


RNode prepareSample::run(RNode d){

    // define scale, resolution and rapidity

  std::string s = "&&J";

  float trueMass = -1;

  if (_myString.find(s) != std::string::npos) {

   trueMass = 3.095;
 }

 else trueMass = 90.851;


 auto scale = [&trueMass](float mass){ return mass/trueMass;};
 auto resolution = [&trueMass](float massErr){ return massErr/trueMass;};

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


auto d1 = d.Define("J", [](){return 1;}).Filter(_myString).Define("scale", scale, {"mass"}).Define("resolution", resolution, {"massErr"});

auto d2 = d1.Define("rapidity", rapidity, {"pt1","pt2","eta1","eta2","phi1","phi2"}).Define("ptRes", ptResonance, {"pt1","pt2","eta1","eta2","phi1","phi2"}).Filter("fabs(rapidity)<2.4");

auto h = d2.Histo1D(TH1D("ptRes", "ptRes", 200, 0, 100), "ptRes");

_h1List.push_back(h);


return d2;


}

std::vector<ROOT::RDF::RResultPtr<TH1D>> prepareSample::getTH1(){ 
  return _h1List;
}
std::vector<ROOT::RDF::RResultPtr<TH2D>> prepareSample::getTH2(){ 
  return _h2List;
}
std::vector<ROOT::RDF::RResultPtr<TH3D>> prepareSample::getTH3(){ 
  return _h3List;
}
bool prepareSample::triggerLoop(){
  return _trigLoop;
}
