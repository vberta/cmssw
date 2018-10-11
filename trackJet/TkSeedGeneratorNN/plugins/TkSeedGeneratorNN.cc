// -*- C++ -*-
//
// Package:    trackJet/TkSeedGeneratorNN
// Class:      TkSeedGeneratorNN
//
/**\class TkSeedGeneratorNN TkSeedGeneratorNN.cc trackJet/TkSeedGeneratorNN/plugins/TkSeedGeneratorNN.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Valerio Bertacchi
//         Created:  Mon, 18 Dec 2017 16:35:04 GMT
//
//


// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "Geometry/CommonDetUnit/interface/GlobalTrackingGeometry.h"
#include "Geometry/Records/interface/GlobalTrackingGeometryRecord.h"
#include "Geometry/CommonDetUnit/interface/GlobalTrackingGeometry.h"
#include "Geometry/Records/interface/TrackerTopologyRcd.h"

#include "DataFormats/TrackerCommon/interface/TrackerTopology.h"
#include "DataFormats/Common/interface/Handle.h"
#include "DataFormats/Common/interface/DetSetVector.h"
#include "DataFormats/Common/interface/DetSet.h"
#include "DataFormats/SiPixelCluster/interface/SiPixelCluster.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include "DataFormats/JetReco/interface/Jet.h"
#include "DataFormats/SiPixelDigi/interface/PixelDigi.h"
#include "DataFormats/GeometryVector/interface/VectorUtil.h"
#include "DataFormats/SiPixelDetId/interface/PXBDetId.h"
#include "DataFormats/Math/interface/Point3D.h"
#include "DataFormats/Math/interface/Vector3D.h"
#include "DataFormats/Candidate/interface/Candidate.h"


#include "RecoLocalTracker/ClusterParameterEstimator/interface/PixelClusterParameterEstimator.h"
#include "RecoLocalTracker/Records/interface/TkPixelCPERecord.h"

#include "SimDataFormats/TrackerDigiSimLink/interface/PixelDigiSimLink.h"

#include "TrackingTools/GeomPropagators/interface/StraightLinePlaneCrossing.h"
#include "TrackingTools/GeomPropagators/interface/Propagator.h"
#include "TrackingTools/Records/interface/TrackingComponentsRecord.h"

#include "MagneticField/Engine/interface/MagneticField.h"
#include "MagneticField/Records/interface/IdealMagneticFieldRecord.h"



#include <boost/range.hpp>
#include <boost/foreach.hpp>
#include "boost/multi_array.hpp"

#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "SimG4Core/Application/interface/G4SimTrack.h"
#include "SimDataFormats/Track/interface/SimTrack.h"

#include "SimDataFormats/Vertex/interface/SimVertex.h"


#include "Geometry/TrackerGeometryBuilder/interface/PixelGeomDetUnit.h"

#include "DataFormats/TrajectorySeed/interface/TrajectorySeedCollection.h"



#include "TTree.h"


//
// class declaration
//

// If the analyzer does not use TFileService, please remove
// the template argument to the base class so the class inherits
// from  edm::one::EDAnalyzer<> and also remove the line from
// constructor "usesResource("TFileService");"
// This will improve performance in multithreaded jobs.

class TkSeedGeneratorNN : public edm::one::EDProducer<edm::one::SharedResources>  {
   public:
      explicit TkSeedGeneratorNN(const edm::ParameterSet&);
      ~TkSeedGeneratorNN();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);
  // A pointer to a cluster and a list of tracks on it
  struct TrackAndState
  {
    TrackAndState(const reco::Track *aTrack, TrajectoryStateOnSurface aState) :
      track(aTrack), state(aState) {}
    const reco::Track*      track;
    TrajectoryStateOnSurface state;
  };


  template<typename Cluster>
  struct ClusterWithTracks
  {
    ClusterWithTracks(const Cluster &c) : cluster(&c) {}
    const Cluster* cluster;
    std::vector<TrackAndState> tracks;
  };

  typedef ClusterWithTracks<SiPixelCluster> SiPixelClusterWithTracks;

  typedef boost::sub_range<std::vector<SiPixelClusterWithTracks> > SiPixelClustersWithTracks;

  TFile* TkSeedGeneratorNN_out;
  TTree* TkSeedGeneratorNNTree;
  static const int jetDimX =30;
  static const int jetDimY =30;
  static const int Nlayer =4;
  double clusterMeas[jetDimX][jetDimY][Nlayer];
  double jet_pt;
  double jet_eta;
  double pitchX = 0.01;
  double pitchY = 0.015;
  bool print = false;
  int evt_counter =0;

   private:
      virtual void beginJob() override;
      virtual void produce( edm::Event&, const edm::EventSetup&) override;
      virtual void endJob() override;


      // ----------member data ---------------------------
  std::string propagatorName_;
  edm::ESHandle<MagneticField>          magfield_;
  edm::ESHandle<GlobalTrackingGeometry> geometry_;
  edm::ESHandle<Propagator>             propagator_;

  edm::EDGetTokenT<std::vector<reco::Vertex> > vertices_;
  edm::EDGetTokenT<edmNew::DetSetVector<SiPixelCluster> > pixelClusters_;
  std::vector<SiPixelClusterWithTracks> allSiPixelClusters;
  std::map<uint32_t, SiPixelClustersWithTracks> siPixelDetsWithClusters;
  edm::Handle< edm::DetSetVector<PixelDigiSimLink> > pixeldigisimlink;
  edm::Handle<edmNew::DetSetVector<SiPixelCluster> > inputPixelClusters;
  edm::EDGetTokenT< edm::DetSetVector<PixelDigiSimLink> > pixeldigisimlinkToken;
  edm::EDGetTokenT<edm::View<reco::Candidate> > cores_;
  edm::EDGetTokenT<std::vector<SimTrack> > simtracksToken;
  edm::EDGetTokenT<std::vector<SimVertex> > simvertexToken;



  double ptMin_;
  double deltaR_;
  double chargeFracMin_;
  double centralMIPCharge_;
  std::string pixelCPE_;


  std::pair<bool, Basic3DVector<float>> findIntersection(const GlobalVector & , const reco::Candidate::Point & ,const GeomDet*);

  void fillPixelMatrix(const SiPixelCluster &, int, auto, const GeomDet*);

  std::pair<int,int> local2Pixel(double, double, const GeomDet*);

  LocalPoint pixel2Local(int, int, const GeomDet*);

  int pixelFlipper(const GeomDet*);

  const GeomDet* DetectorSelector(int ,const reco::Candidate& jet, GlobalVector,  const reco::Vertex& jetVertex, const TrackerTopology* const);

  std::vector<GlobalVector> splittedClusterDirections(const reco::Candidate&, const TrackerTopology* const, auto pp, const reco::Vertex& jetVertex );


};

TkSeedGeneratorNN::TkSeedGeneratorNN(const edm::ParameterSet& iConfig) :

      vertices_(consumes<reco::VertexCollection>(iConfig.getParameter<edm::InputTag>("vertices"))),
      pixelClusters_(consumes<edmNew::DetSetVector<SiPixelCluster> >(iConfig.getParameter<edm::InputTag>("pixelClusters"))),
      // pixeldigisimlinkToken(consumes< edm::DetSetVector<PixelDigiSimLink> >(edm::InputTag("simSiPixelDigis"))),
      cores_(consumes<edm::View<reco::Candidate> >(iConfig.getParameter<edm::InputTag>("cores"))),
      // simtracksToken(consumes<std::vector<SimTrack> >(iConfig.getParameter<edm::InputTag>("simTracks"))),
      // simvertexToken(consumes<std::vector<SimVertex> >(iConfig.getParameter<edm::InputTag>("simVertex"))),
      ptMin_(iConfig.getParameter<double>("ptMin")),
      deltaR_(iConfig.getParameter<double>("deltaR")),
      chargeFracMin_(iConfig.getParameter<double>("chargeFractionMin")),
      centralMIPCharge_(iConfig.getParameter<double>("centralMIPCharge")),
      pixelCPE_(iConfig.getParameter<std::string>("pixelCPE"))

{
  //  usesResource("TFileService");
  produces<TrajectorySeedCollection>();



  //  edm::Service<TFileService> fileService;
   //
  //  TkSeedGeneratorNNTree= fileService->make<TTree>("TkSeedGeneratorNNTree","TkSeedGeneratorNNTree");
  //  TkSeedGeneratorNNTree->Branch("cluster_measured",clusterMeas,"cluster_measured[30][30][4]/D");
  //  TkSeedGeneratorNNTree->Branch("jet_eta",&jet_eta);
  //  TkSeedGeneratorNNTree->Branch("jet_pt",&jet_pt);


     for(int i=0; i<Nlayer; i++){ //NOFLAG
       for(int j=0; j<jetDimX; j++){
         for(int k=0; k<jetDimY; k++){
           if(j<jetDimX && k<jetDimY && i< Nlayer) clusterMeas[j][k][i] = 0.0;
          }
         }
      }



}


TkSeedGeneratorNN::~TkSeedGeneratorNN()
{

}

#define foreach BOOST_FOREACH


void TkSeedGeneratorNN::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
  evt_counter++;
  std::cout << "event number (iterative)=" << evt_counter<< ", event number (id)="<< iEvent.id().event() << std::endl;


  using namespace edm;

  iSetup.get<IdealMagneticFieldRecord>().get( magfield_ );
  iSetup.get<GlobalTrackingGeometryRecord>().get(geometry_);
  iSetup.get<TrackingComponentsRecord>().get( "AnalyticalPropagator", propagator_ );

  iEvent.getByToken(pixelClusters_, inputPixelClusters);
  allSiPixelClusters.clear(); siPixelDetsWithClusters.clear();
  allSiPixelClusters.reserve(inputPixelClusters->dataSize()); // this is important, otherwise push_back invalidates the iterators

  // edm::Handle<std::vector<SimTrack> > simtracks;
  // iEvent.getByToken(simtracksToken, simtracks);

  // edm::Handle<std::vector<SimVertex> > simvertex;
  // iEvent.getByToken(simvertexToken, simvertex);

  Handle<std::vector<reco::Vertex> > vertices;
  iEvent.getByToken(vertices_, vertices);

  Handle<edm::View<reco::Candidate> > cores;
  iEvent.getByToken(cores_, cores);

  // iEvent.getByToken(pixeldigisimlinkToken, pixeldigisimlink);

  //--------------------------debuging lines ---------------------//
  edm::ESHandle<PixelClusterParameterEstimator> pe;
  const PixelClusterParameterEstimator* pp;
  iSetup.get<TkPixelCPERecord>().get(pixelCPE_, pe);
  pp = pe.product();
  //--------------------------end ---------------------//

  edm::ESHandle<TrackerTopology> tTopoHandle;
  iSetup.get<TrackerTopologyRcd>().get(tTopoHandle);
  const TrackerTopology* const tTopo = tTopoHandle.product();

  auto output = std::make_unique<edmNew::DetSetVector<SiPixelCluster>>();

print = false;
int jet_number = 0;
  for (unsigned int ji = 0; ji < cores->size(); ji++) { //loop jet
    jet_number++;

    if ((*cores)[ji].pt() > ptMin_) {
       std::cout << "|____________________NEW JET_______________________________| jet number=" << jet_number  <<std::endl;

      const reco::Candidate& jet = (*cores)[ji];
      const reco::Vertex& jetVertex = (*vertices)[0];

      std::vector<GlobalVector> splitClustDirSet = splittedClusterDirections(jet, tTopo, pp, jetVertex);
      std::cout << "numero of cluster da splittare" << splitClustDirSet.size() << std::endl;;
      for(int cc=0; cc<(int)splitClustDirSet.size(); cc++){
      GlobalVector bigClustDir = splitClustDirSet.at(cc);

      LocalPoint jetInter(0,0,0);

      // const auto & simtracksVector = simtracks.product();
      // const auto & simvertexVector = simvertex.product();

      jet_pt = jet.pt();
      jet_eta = jet.eta();

      auto jetVert = jetVertex; //trackInfo filling


      const GeomDetUnit* detUnit = (GeomDetUnit*)0; //fuffa assigment to allow to compile;

      edmNew::DetSetVector<SiPixelCluster>::const_iterator detIt = inputPixelClusters->begin();

      const GeomDet* globDet = DetectorSelector(2, jet, bigClustDir, jetVertex, tTopo); //select detector mostly hitten by the jet

      if(globDet == 0) continue;

      const GeomDet* goodDet1 = DetectorSelector(1, jet, bigClustDir, jetVertex, tTopo);
      const GeomDet* goodDet3 = DetectorSelector(3, jet, bigClustDir, jetVertex, tTopo);
      const GeomDet* goodDet4 = DetectorSelector(4, jet, bigClustDir, jetVertex, tTopo);



      for (; detIt != inputPixelClusters->end(); detIt++) { //loop deset
        const edmNew::DetSet<SiPixelCluster>& detset = *detIt;
        const GeomDet* det = geometry_->idToDet(detset.id()); //lui sa il layer con cast a  PXBDetId (vedi dentro il layer function)

        for (auto cluster = detset.begin(); cluster != detset.end(); cluster++) { //loop cluster

          const SiPixelCluster& aCluster = *cluster;
          det_id_type aClusterID= detset.id();
          if(DetId(aClusterID).subdetId()!=1) continue;

          int lay = tTopo->layer(det->geographicalId());

          std::pair<bool, Basic3DVector<float>> interPair = findIntersection(bigClustDir,(reco::Candidate::Point)jetVertex.position(), det);
          if(interPair.first==false) continue;
          Basic3DVector<float> inter = interPair.second;
          auto localInter = det->specificSurface().toLocal((GlobalPoint)inter);

          GlobalPoint pointVertex(jetVertex.position().x(), jetVertex.position().y(), jetVertex.position().z());


          // GlobalPoint cPos = det->surface().toGlobal(pp->localParametersV(aCluster,(*geometry_->idToDetUnit(detIt->id())))[0].first);
          LocalPoint cPos_local = pp->localParametersV(aCluster,(*geometry_->idToDetUnit(detIt->id())))[0].first;

          if(std::abs(cPos_local.x()-localInter.x())/pitchX<=jetDimX/2 && std::abs(cPos_local.y()-localInter.y())/pitchY<=jetDimY/2){ // per ora preso baricentro, da migliorare

            if(det==goodDet1 || det==goodDet3 || det==goodDet4 || det==globDet) {
              fillPixelMatrix(aCluster,lay,localInter, det);
              }
          } //cluster in ROI
        } //cluster
      } //detset

    // TkSeedGeneratorNNTree->Fill();

    //HERE SOMEHOW THE NN PRODUCE THE SEED FROM THE FILLED INPUT

    auto result = std::make_unique<TrajectorySeedCollection>();

    LocalTrajectoryParameters lp(LocalPoint(0,0,0), LocalVector(1,1,1), TrackCharge(1));
    long int detId=globDet->geographicalId();
    result->push_back(TrajectorySeed( PTrajectoryStateOnDet (lp, 3., detId, /*surfaceSide*/ 0), edm::OwnVector< TrackingRecHit >() , PropagationDirection::alongMomentum));

    iEvent.put(std::move(result));


    std::cout << "FILL!" << std::endl;

    for(int i=0; i<Nlayer; i++){
      for(int j=0; j<jetDimX; j++){
        for(int k=0; k<jetDimY; k++){
          if(j<jetDimX && k<jetDimY && i< Nlayer) clusterMeas[j][k][i] = 0.0;
        }
      }
    }
  } //bigcluster
  } //jet > pt
 } //jet
//  print = false;
}













  std::pair<bool, Basic3DVector<float>> TkSeedGeneratorNN::findIntersection(const GlobalVector & dir,const  reco::Candidate::Point & vertex, const GeomDet* det){
     StraightLinePlaneCrossing vertexPlane(Basic3DVector<float>(vertex.x(),vertex.y(),vertex.z()), Basic3DVector<float>(dir.x(),dir.y(),dir.z()));

     std::pair<bool, Basic3DVector<float>> pos = vertexPlane.position(det->specificSurface());

     return pos;
  }


  std::pair<int,int> TkSeedGeneratorNN::local2Pixel(double locX, double locY, const GeomDet* det){
    LocalPoint locXY(locX,locY);
    float pixX=(dynamic_cast<const PixelGeomDetUnit*>(det))->specificTopology().pixel(locXY).first;
    float pixY=(dynamic_cast<const PixelGeomDetUnit*>(det))->specificTopology().pixel(locXY).second;
    std::pair<int, int> out(pixX,pixY);
    return out;
  }

  LocalPoint TkSeedGeneratorNN::pixel2Local(int pixX, int pixY, const GeomDet* det){
    float locX=(dynamic_cast<const PixelGeomDetUnit*>(det))->specificTopology().localX(pixX);
    float locY=(dynamic_cast<const PixelGeomDetUnit*>(det))->specificTopology().localY(pixY);
    LocalPoint locXY(locX,locY);
    return locXY;
  }

  int TkSeedGeneratorNN::pixelFlipper(const GeomDet* det){
    int out =1;
    LocalVector locZdir(0,0,1);
    GlobalVector globZdir  = det->specificSurface().toGlobal(locZdir);
    GlobalPoint globDetCenter = det->position();
    float direction = globZdir.x()*globDetCenter.x()+ globZdir.y()*globDetCenter.y()+ globZdir.z()*globDetCenter.z();
    //float direction = globZdir.dot(globDetCenter);
    if(direction<0) out =-1;
    // out=1;
    return out;
   }



  void TkSeedGeneratorNN::fillPixelMatrix(const SiPixelCluster & cluster, int layer, auto inter, const GeomDet* det){
    //  if(layer==1 && 0){std::cout << "--------new cluster----------cluster size=" <<cluster.size() <<std::endl;
    // std::cout << "layer=" << layer << std::endl;}
    // if(layer==0) std::cout << "LAYER 0!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" << std::endl;

    int flip = pixelFlipper(det); // 1=not flip, -1=flip
    //std::cout << "flipped?=" << flip << std::endl;

    for(int i=0; i<cluster.size();i++){
      SiPixelCluster::Pixel pix = cluster.pixel(i);
      std::pair<int,int> pixInter = local2Pixel(inter.x(),inter.y(),det);
      int nx = pix.x-pixInter.first;
      int ny = pix.y-pixInter.second;
      nx=flip*nx;
      // int nx = pix.x-inter.x()/pitchX ;//pitchX;
      // int ny = pix.y-inter.y()/pitchY;//pitchY;

      //PXBDetId detPX  = (PXBDetId)(det->geographicalId());
      //if(detPX.ladder()%2==0) nx=-nx;


      if(abs(nx)<jetDimX/2 && abs(ny)<jetDimY/2){
        nx = nx+jetDimX/2;
        ny = ny+jetDimY/2;
        if(nx<jetDimX && ny<jetDimY && layer-1< Nlayer && layer-1>=0 && nx>=0 && ny>=0) std::cout << "clusterMeas[nx][ny][layer-1] += (pix.adc)/(float)(14000) ="  << (pix.adc)/(float)(14000) << std::endl;;

        // if(layer==1 && 0){std::cout << "x position pixel " << nx-jetDimX/2 <<std::endl;
        // std::cout << "y position pixel " << ny-jetDimY/2 <<std::endl;
        // std::cout << "charge " << pix.adc <<std::endl;}

      //   if(0){std::cout << "---------INPUT debug -------- det=" <<det->gdetIndex()<< std::endl;
      //   std::cout<< "x=" << nx << ", y=" << ny << "("<<nx-jetDimX/2 << ", " << ny-jetDimY/2 << ")" << std::endl;
      //   std::cout << "jetInter X="<< pixInter.first <<", Y=" << pixInter.second << std::endl;
      //   std::cout << "trkInter X="<< pix.x <<", Y=" << pix.y << std::endl;
      // }
      }
    }

  }


const GeomDet* TkSeedGeneratorNN::DetectorSelector(int llay, const reco::Candidate& jet, GlobalVector jetDir, const reco::Vertex& jetVertex, const TrackerTopology* const tTopo){

  struct trkNumCompare {
  bool operator()(std::pair<int,const GeomDet*> x, std::pair<int,const GeomDet*> y) const
  {return x.first > y.first;}
  };

  std::set<std::pair<int,const GeomDet*>, trkNumCompare> track4detSet;

  LocalPoint jetInter(0,0,0);

  edmNew::DetSetVector<SiPixelCluster>::const_iterator detIt = inputPixelClusters->begin();

  double minDist = 0.0;
  GeomDet* output = (GeomDet*)0;

  for (; detIt != inputPixelClusters->end(); detIt++) { //loop deset

    const edmNew::DetSet<SiPixelCluster>& detset = *detIt;
    const GeomDet* det = geometry_->idToDet(detset.id()); //lui sa il layer con cast a  PXBDetId (vedi dentro il layer function)
    for (auto cluster = detset.begin(); cluster != detset.end(); cluster++) { //loop cluster

      const SiPixelCluster& aCluster = *cluster;
      auto aClusterID= detset.id();

      if(DetId(aClusterID).subdetId()!=1) continue;

      int lay = tTopo->layer(det->geographicalId());

      if(lay!=llay) continue;

      std::pair<bool, Basic3DVector<float>> interPair = findIntersection(jetDir,(reco::Candidate::Point)jetVertex.position(), det);

      if(interPair.first==false) continue;

      Basic3DVector<float> inter = interPair.second;

      auto localInter = det->specificSurface().toLocal((GlobalPoint)inter);
      // auto det->position()
      // std::cout << "layer =" << llay << " selected det=" << det->gdetIndex() << " distX=" << localInter.x() << " distY=" << localInter.y() <<std::endl;
      // if(minDist==0.0 || std::fabs(localInter.x())<minDist) {
      //   minDist = std::fabs(localInter.x());
      //   output = (GeomDet*)det;
      //   std::cout << "layer =" << llay << " selected det=" << det->gdetIndex() << std::endl;
      //   }

      // if((minDist==0.0 || (localInter.x()*localInter.x()+localInter.y()*localInter.y())<minDist)) {
      if((minDist==0.0 || std::abs(localInter.x())<minDist) && std::abs(localInter.y())<3.35) {

          // minDist = (localInter.x()*localInter.x()+localInter.y()*localInter.y());
          minDist = std::abs(localInter.x());
          output = (GeomDet*)det;
          // std::cout << "layer =" << llay << " selected det=" << det->gdetIndex() << " distX=" << localInter.x() << " distY=" << localInter.y() << ", center=" << det->position()<< std::endl;
      }
        // if(det->gdetIndex()==3 && llay==1)  std::cout << "layer =" << llay << " selected det=" << det->gdetIndex() << " distX=" << localInter.x() << " distY=" << localInter.y() << ", center=" << det->position()<< std::endl;


    } //cluster
  } //detset
  // std::cout << "OK DET= layer =" << llay << " selected det=" << output->gdetIndex() << std::endl;
  return output;
}

std::vector<GlobalVector> TkSeedGeneratorNN::splittedClusterDirections(const reco::Candidate& jet, const TrackerTopology* const tTopo, auto pp, const reco::Vertex& jetVertex ){
  std::vector<GlobalVector> clustDirs;

  edmNew::DetSetVector<SiPixelCluster>::const_iterator detIt_int = inputPixelClusters->begin();


  for (; detIt_int != inputPixelClusters->end(); detIt_int++) {

    const edmNew::DetSet<SiPixelCluster>& detset_int = *detIt_int;
    const GeomDet* det_int = geometry_->idToDet(detset_int.id());
    int lay = tTopo->layer(det_int->geographicalId());
    if(lay != 1) continue;

    for (auto cluster = detset_int.begin(); cluster != detset_int.end(); cluster++) {
      const SiPixelCluster& aCluster = *cluster;

      GlobalPoint cPos = det_int->surface().toGlobal(pp->localParametersV(aCluster,(*geometry_->idToDetUnit(detIt_int->id())))[0].first);
      GlobalPoint ppv(jetVertex.position().x(), jetVertex.position().y(), jetVertex.position().z());
      GlobalVector clusterDir = cPos - ppv;
      GlobalVector jetDir(jet.px(), jet.py(), jet.pz());
      if (Geom::deltaR(jetDir, clusterDir) < deltaR_) {

            bool isEndCap =
                (std::abs(cPos.z()) > 30.f);  // FIXME: check detID instead!
            float jetZOverRho = jet.momentum().Z() / jet.momentum().Rho();
            if (isEndCap)
              jetZOverRho = jet.momentum().Rho() / jet.momentum().Z();
            float expSizeY =
                std::sqrt((1.3f*1.3f) + (1.9f*1.9f) * jetZOverRho*jetZOverRho);
            if (expSizeY < 1.f) expSizeY = 1.f;
            float expSizeX = 1.5f;
            if (isEndCap) {
              expSizeX = expSizeY;
              expSizeY = 1.5f;
            }  // in endcap col/rows are switched
            float expCharge =
                std::sqrt(1.08f + jetZOverRho * jetZOverRho) * centralMIPCharge_;
            if (aCluster.charge() > expCharge * chargeFracMin_ && (aCluster.sizeX() > expSizeX + 1 ||  aCluster.sizeY() > expSizeY + 1)) {
              std::cout << "trovato cluster con deltaR=" << Geom::deltaR(jetDir, clusterDir)<< std::endl;
              clustDirs.push_back(clusterDir);
            }
          }
        }
      }
      return clustDirs;

}


// ------------ method called once each job just before starting event loop  ------------
void
TkSeedGeneratorNN::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void
TkSeedGeneratorNN::endJob()
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
TkSeedGeneratorNN::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(TkSeedGeneratorNN);
