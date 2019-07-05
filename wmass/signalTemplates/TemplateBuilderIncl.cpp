#include "TemplateBuilderIncl.h"


RNode TemplateBuilderIncl::run(RNode d){
	

	TH2::SetDefaultSumw2(true);

  float yArr[] = {-6.0, -3.0, -2.5, -2.0, -1.6, -1.2, -0.8, -0.4, 0, 0.4, 0.8, 1.2 ,1.6, 2.0, 2.5, 3.0, 6.0};
  float qtArr[] = {0., 4., 8., 12., 16., 20., 24., 32., 40., 60., 100., 200.};

  const int nBinsY = 16;
  const int nBinsQt = 11;

  const int nBinsEta = 100;
  const int nBinsPt = 80;

  float etaArr[nBinsEta+1] = {0};
  float ptArr[nBinsPt+1] = {0};

  for(int i=0; i<nBinsEta+1; i++){

    float binSize = 5.0/nBinsEta;
    etaArr[i] = -2.5 + i*binSize;

  }

  for(int i=0; i<nBinsPt+1; i++){

    float binSize = (65.-25.)/nBinsPt;
    ptArr[i] = 25. + i*binSize;

  }

  auto getFromIdx = [](rvec_f v, int idx){ return v[idx];};

  auto d1 = d.Filter("GenPart_pdgId[GenPart_preFSRMuonIdx]<0").Define("Mupt_preFSR", getFromIdx, {"GenPart_pt", "GenPart_preFSRMuonIdx"}).Define("Mueta_preFSR", getFromIdx, {"GenPart_eta", "GenPart_preFSRMuonIdx"})\
  .Define("Generator_weight_norm", [](float w)-> float{ return w/abs(w);}, {"Generator_weight"});

  // fake histogram just to define filters
  auto h = new TH2F("h", "h", nBinsY, yArr, nBinsQt, qtArr);

    for(int j=1; j<h->GetNbinsY()+1; j++){ // for each W pt bin

    	float lowEdgePt = h->GetYaxis()->GetBinLowEdge(j);
    	float upEdgePt = h->GetYaxis()->GetBinUpEdge(j);


      auto sel = [lowEdgePt, upEdgePt](float pt) { return (pt >lowEdgePt && pt<upEdgePt);};

      auto tmp = d1.Filter(sel, {"Wpt_preFSR"}).Histo3D(TH3D(Form("pt_%i", j), Form("pt_%i", j), nBinsEta, etaArr, nBinsPt, ptArr, nBinsY, yArr), "Mueta_preFSR" ,"Mupt_preFSR", "Wrap_preFSR");

      _h3List.push_back(tmp);

      }

  //pseudodata

    auto pseudodata = d1.Histo2D(TH2D("pseudodata", "pseudodata", nBinsEta, etaArr, nBinsPt, ptArr),"Mueta_preFSR" ,"Mupt_preFSR");    
    _h2List.push_back(pseudodata);
    
    return d1;


  }

std::vector<ROOT::RDF::RResultPtr<TH1D>> TemplateBuilderIncl::getTH1(){ 
    return _h1List;
}
std::vector<ROOT::RDF::RResultPtr<TH2D>> TemplateBuilderIncl::getTH2(){ 
    return _h2List;
}
std::vector<ROOT::RDF::RResultPtr<TH3D>> TemplateBuilderIncl::getTH3(){ 
    return _h3List;
}
void  TemplateBuilderIncl::reset(){
  
  _h1List.clear();
  _h2List.clear();
  _h3List.clear();

}
