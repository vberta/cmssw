#include "TemplateBuilder.h"


RNode TemplateBuilder::doSomething(RNode d){

    return d;

    /*
	
	TH2::SetDefaultSumw2(true);


	float yArr[] = {-3.5, -3.0, -2.5, -2.0, -1.6, -1.2, -0.8, -0.4, 0, 0.4, 0.8, 1.2 ,1.6, 2.0, 2.5, 3.0, 3.5};
	float ptArr[] = {0., 4., 8., 12., 16., 20., 24., 32., 40., 60.};

	int nBinsY = 16;
	int nBinsPt = 9;

	std::vector<std::string> coeff = {"0", "1", "2", "3", "4", "5", "6", "7", "UL"};
	std::vector<ROOT::RDF::RResultPtr<TH2D>> templList;

	auto getFromIdx = [](rvec_f v, int idx){ return v[idx];};
	auto getFromIdxStd = [](std::vector<float> v, int idx){ return v[idx];};

	auto d1 = d.Define("Mupt_preFSR", getFromIdx, {"GenPart_pt", "GenPart_preFSRMuonIdx"}).Define("Mueta_preFSR", getFromIdx, {"GenPart_eta", "GenPart_preFSRMuonIdx"});


    // fake histogram just to define filters
	auto h = new TH2F("h", "h", nBinsY, yArr, nBinsPt, ptArr);

    for(int j=1; j<h->GetNbinsY()+1; j++){ // for each pt bin

    	float lowEdgePt = h->GetYaxis()->GetBinLowEdge(j+1);
    	float upEdgePt = h->GetYaxis()->GetBinUpEdge(j+1);

            for(int i=1; i<h->GetNbinsX()+1; i++){ // for each y bin

            	float lowEdgeY = h->GetXaxis()->GetBinLowEdge(i+1);
            	float upEdgeY = h->GetXaxis()->GetBinUpEdge(i+1);

            	auto sel = [lowEdgePt, upEdgePt, lowEdgeY, upEdgeY](float pt, float rap) { return (pt >lowEdgePt && pt<upEdgePt && rap >lowEdgeY && rap<upEdgeY);};

            	for(auto c:coeff){

            		auto tmp = d1.Filter(sel, {"Wpt_preFSR", "Wrap_preFSR"}).Histo2D(TH2D(Form("A%s_pt%.2f_to_%.2f_rap%.2f_to_%.2f", c.c_str(), lowEdgePt, upEdgePt, lowEdgeY, upEdgeY), Form("A%s_pt%.2f_to_%.2f_rap%.2f_to%.2f", c.c_str(), lowEdgePt, upEdgePt, lowEdgeY, upEdgeY), 50, -2.5, 2.5, 40, 20, 60), "Mueta_preFSR" ,"Mupt_preFSR", "Pweight"+c);

            		templList.push_back(tmp);

            	}


            }


        }

    TFile *ftempl = new TFile("templates.root", "recreate");

    ftempl->cd();

    for(std::size_t i=0; i<templList.size(); i++){
        	/*
        	if(i%8!=0){

        		for(int j=1; j<h->GetNbinsY()+1; j++){ // for each pt bin
        			for(int i=1; i<h->GetNbinsX()+1; i++){ // for each y bin

        				std::cout<< int(i/8)+8 << std::endl;
        				templList[i]->SetBinContent(i,j,templList[i]->GetBinContent(i,j)+templList[int(i/8)*8+8]->GetBinContent(i,j));
        				templList[i]->SetBinError(i,j, sqrt(templList[i]->GetBinError(i,j)*templList[i]->GetBinError(i,j) + templList[int(i/8)+8]->GetBinError(i,j)*templList[int(i/8)+8]->GetBinError(i,j)));	
        			}

        		}
        	}
			
        	templList[i]->Write();
    } 

    return d;

    */

}

std::vector<ROOT::RDF::RResultPtr<TH1D>> TemplateBuilder::getTH1(){ 

    	return _h1List;

}

std::vector<ROOT::RDF::RResultPtr<TH2D>> TemplateBuilder::getTH2(){ 

    	return _h2List;


}
