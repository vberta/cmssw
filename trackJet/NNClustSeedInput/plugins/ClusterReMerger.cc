#include "FWCore/Framework/interface/stream/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "DataFormats/Common/interface/Handle.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "DataFormats/SiPixelCluster/interface/SiPixelCluster.h"
#include "DataFormats/Common/interface/DetSetVectorNew.h"

#include "RecoLocalTracker/ClusterParameterEstimator/interface/PixelClusterParameterEstimator.h"
#include "RecoLocalTracker/Records/interface/TkPixelCPERecord.h"

#include "Geometry/CommonDetUnit/interface/GlobalTrackingGeometry.h"
#include "Geometry/Records/interface/GlobalTrackingGeometryRecord.h"
#include "DataFormats/GeometryVector/interface/VectorUtil.h"

#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include "DataFormats/JetReco/interface/Jet.h"

#include <algorithm>
#include <vector>
#include <utility>

class ClusterReMerger : public edm::stream::EDProducer<> {
 public:
  ClusterReMerger(const edm::ParameterSet& iConfig);
  ~ClusterReMerger() override;
  void produce(edm::Event& iEvent, const edm::EventSetup& iSetup) override;
  bool touch(SiPixelCluster & a, SiPixelCluster & b);
  void merge(size_t i,size_t j, std::vector<SiPixelCluster> & clusters);
 private:
  edm::EDGetTokenT<edmNew::DetSetVector<SiPixelCluster> > pixelClusters_;
};

ClusterReMerger::ClusterReMerger(const edm::ParameterSet& iConfig):
      pixelClusters_(consumes<edmNew::DetSetVector<SiPixelCluster> >(
          iConfig.getParameter<edm::InputTag>("pixelClusters")))

{
  produces<edmNew::DetSetVector<SiPixelCluster> >();
}

ClusterReMerger::~ClusterReMerger() {}

bool ClusterReMerger::touch( SiPixelCluster & a, SiPixelCluster & b){
    for(int i=0;i<a.size();i++)
     for(int  j=0;j<b.size();j++)
	{
 	  auto ap=a.pixel(i); auto bp=b.pixel(j);
	  if( abs(ap.x - bp.x) <=1 and  abs(ap.y-bp.y) <=1 ) return true;
	}
    return false;
}

void ClusterReMerger::merge(size_t i,size_t j, std::vector<SiPixelCluster> & clusters)
{
 std::map<std::pair<uint16_t,uint16_t>,uint16_t> pixels;
 for(int k=0;k<clusters[i].size();k++){
	pixels[std::pair<uint16_t,uint16_t>(clusters[i].pixel(k).x,clusters[i].pixel(k).y)]+=clusters[i].pixel(k).adc;
 }
 for(int k=0;k<clusters[j].size();k++){
	pixels[std::pair<uint16_t,uint16_t>(clusters[j].pixel(k).x,clusters[j].pixel(k).y)]+=clusters[j].pixel(k).adc;
 }
 uint16_t vx[1000],vy[1000],vadc[1000];
 size_t k=0;
 for(auto it=pixels.begin(); it!=pixels.end();it++,k++){
	vx[k]=it->first.first;
	vy[k]=it->first.second;
	vadc[k]=it->second;
	if(k==1000){std::cerr << "More than 1000 pixels!!!" << std::endl; break;}
 }
 // std::cout << "Merging" << pixels.size() ;
 // for(size_t l=0;l<pixels.size();l++) std::cout << " " << vadc[l] ;
 // std::cout << std::endl;
 SiPixelCluster newcluster(pixels.size(),vadc,vx,vy,
	std::min(clusters[i].minPixelRow(),clusters[j].minPixelRow()),
	std::min(clusters[i].minPixelCol(),clusters[j].minPixelCol()));
 clusters[i]=newcluster;
}


void ClusterReMerger::produce(edm::Event& iEvent,
                                     const edm::EventSetup& iSetup) {
  using namespace edm;

  Handle<edmNew::DetSetVector<SiPixelCluster> > inputPixelClusters;
  iEvent.getByToken(pixelClusters_, inputPixelClusters);


  auto output = std::make_unique<edmNew::DetSetVector<SiPixelCluster>>();
  edmNew::DetSetVector<SiPixelCluster>::const_iterator detIt =
      inputPixelClusters->begin();
  for (; detIt != inputPixelClusters->end(); detIt++) {
    edmNew::DetSetVector<SiPixelCluster>::FastFiller filler(*output,
                                                            detIt->id());
    std::vector<SiPixelCluster> clusters;
    const edmNew::DetSet<SiPixelCluster>& detset = *detIt;
    for (auto cluster = detset.begin(); cluster != detset.end(); cluster++) clusters.push_back(*cluster);

    size_t i=0;
    while(i <clusters.size())
    {
	    size_t j=i+1;
	     for(;j<clusters.size();j++)
        	{
	        if(touch(clusters[i],clusters[j]) ) {
	         	 merge(i,j,clusters);
		         clusters.erase(clusters.begin()+j);
		          break;
	   }
	}
	if(j==clusters.size()){ i++; }//nothing to merge, go to next
    } //while
    for(size_t i=0;i<clusters.size(); i++)  {
	filler.push_back(clusters[i]);
        std::push_heap(filler.begin(),filler.end(),
          [](SiPixelCluster const & cl1,SiPixelCluster const & cl2) { return cl1.minPixelRow() < cl2.minPixelRow();});
      }
      // if(clusters.size()!=detset.size()) std::cout << "Merged "<< -clusters.size()+detset.size() <<std::endl;
 } //det
   iEvent.put(std::move(output));
}


#include "FWCore/PluginManager/interface/ModuleDef.h"
#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(ClusterReMerger);
