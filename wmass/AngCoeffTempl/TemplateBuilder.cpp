#include "TemplateBuilder.h"


RNode TemplateBuilder::doSomething(RNode d){
	
   
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


	std::vector<std::string> coeff = {"0", "1", "2", "3", "4", "5", "6", "7", "UL"};
	std::vector<ROOT::RDF::RResultPtr<TH3D>> templList;

	auto getFromIdx = [](rvec_f v, int idx){ return v[idx];};

	auto d1 = d.Define("Mupt_preFSR", getFromIdx, {"GenPart_pt", "GenPart_preFSRMuonIdx"}).Define("Mueta_preFSR", getFromIdx, {"GenPart_eta", "GenPart_preFSRMuonIdx"});


    // fake histogram just to define filters
	auto h = new TH2F("h", "h", nBinsY, yArr, nBinsQt, qtArr);

    for(int j=1; j<h->GetNbinsY()+1; j++){ // for each W pt bin

    	float lowEdgePt = h->GetYaxis()->GetBinLowEdge(j);
    	float upEdgePt = h->GetYaxis()->GetBinUpEdge(j);


        auto sel = [lowEdgePt, upEdgePt](float pt) { return (pt >lowEdgePt && pt<upEdgePt);};

       for(auto c:coeff){

          auto tmp = d1.Filter(sel, {"Wpt_preFSR"}).Histo3D(TH3D(Form("A%s_pt%.2f_to_%.2f", c.c_str(), lowEdgePt, upEdgePt), Form("A%s_pt%.2f_to_%.2f", c.c_str(), lowEdgePt, upEdgePt), nBinsEta, etaArr, nBinsPt, ptArr, nBinsY, yArr), "Mueta_preFSR" ,"Mupt_preFSR", "Wrap_preFSR", "Pweight"+c);

          templList.push_back(tmp);



      }


  }

  TFile *ftempl = new TFile("templates.root", "recreate");

  ftempl->cd();

  for(std::size_t i=0; i<templList.size(); i++){
			 
   templList[i]->Write();
    
    } 

return d;


}

std::vector<ROOT::RDF::RResultPtr<TH1D>> TemplateBuilder::getTH1(){ 

   return _h1List;

}

std::vector<ROOT::RDF::RResultPtr<TH2D>> TemplateBuilder::getTH2(){ 

   return _h2List;


}