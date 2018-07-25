// -*- C++ -*-
//
// Package:    trackJet/NNPixSeedInput
// Class:      NNPixSeedInput
//
/**\class NNPixSeedInput NNPixSeedInput.cc trackJet/NNPixSeedInput/plugins/NNPixSeedInput.cc

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



#include "TTree.h"


//
// class declaration
//

// If the analyzer does not use TFileService, please remove
// the template argument to the base class so the class inherits
// from  edm::one::EDAnalyzer<> and also remove the line from
// constructor "usesResource("TFileService");"
// This will improve performance in multithreaded jobs.

class NNPixSeedInput : public edm::one::EDProducer<edm::one::SharedResources>  {
   public:
      explicit NNPixSeedInput(const edm::ParameterSet&);
      ~NNPixSeedInput();

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

  TFile* NNPixSeedInput_out;
  TTree* NNPixSeedInputTree;
  static const int jetDimX =200;
  static const int jetDimY =200;
  static const int Nlayer =4;
  static const int Ntrack = 100;
  static const int Npar = 4;
  static const int Nover = 3;
  double clusterMeas[jetDimX][jetDimY][Nlayer];
  double trackPar[jetDimX][jetDimY][Nover][Npar+1];
  double trackProb[jetDimX][jetDimY][Nover];
  double clusterSplit[Ntrack][Nlayer][jetDimX][jetDimY];
  double track_pt[Ntrack] = {0.0};
  double track_pz[Ntrack] = {0.0};
  double track_eta[Ntrack] = {0.0};
  double track_phi[Ntrack] = {0.0};
  double jet_pt;
  double jet_eta;
  double jet_phi;
  double jet_Ntrack = 0;

  // int minLayer = 1;
  // int maxLayer = 4;

  double pitchX = 0.01;
  double pitchY = 0.015;
  static const int distThr = 2;//4


  int jetnum =0;

  bool print = false;
  bool print2 = false;

  int evt_counter =0;



  // int eventNum;
  // int layerNum;
  // int pixelRow;
  // int pixelCol;
  // double pixelSig;

   private:
      virtual void beginJob() override;
      virtual void produce( edm::Event&, const edm::EventSetup&) override;
      virtual void endJob() override;


      // ----------member data ---------------------------
  std::string propagatorName_;
  edm::ESHandle<MagneticField>          magfield_;
  //edm::ESHandle<GlobalTrackingGeometry> geometry_;
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
  //edm::EDGetTokenT<std::vector<G4SimTrack> > g4simtracksToken;
  edm::EDGetTokenT<std::vector<SimTrack> > simtracksToken;
  edm::EDGetTokenT<std::vector<SimVertex> > simvertexToken;


  std::map<int, double [Nlayer][jetDimX][jetDimY]> trackMap;

  double ptMin_;
  // double deltaR_;
  std::string pixelCPE_;


  std::pair<bool, Basic3DVector<float>> findIntersection(const GlobalVector & , const reco::Candidate::Point & ,const GeomDet*);

  void fillPixelMatrix(const SiPixelCluster &, int, auto, const GeomDet*);

  void fillPixelTrackMap(int, const SiPixelCluster &, int, auto, const GeomDet*);

  void fillPixelTrackMatrix(const std::vector<SimTrack>* const &);

  std::map<int,SiPixelCluster> splitClusterInTracks(const SiPixelCluster &, const DetId &);

  std::pair<int,int> local2Pixel(double, double, const GeomDet*);
  LocalPoint pixel2Local(int, int, const GeomDet*);

  int pixelFlipper(const GeomDet*);

  GlobalVector recenter(const reco::Candidate&, GlobalVector, const reco::Vertex&, const TrackerTopology* const, const PixelClusterParameterEstimator*);

  void fillTrackInfo(const reco::Candidate&, const std::set<int>, const auto &,  const auto &, auto, auto, auto, const GeomDet*, std::vector<std::map<int,SiPixelCluster>>, const PixelClusterParameterEstimator*, const GeomDetUnit*);

  const GeomDet* DetectorSelector(int ,const reco::Candidate& jet, GlobalVector,  const reco::Vertex& jetVertex, const TrackerTopology* const, const PixelClusterParameterEstimator*, const auto &);


  // template<typename Cluster>
  // std::unique_ptr<edmNew::DetSetVector<Cluster> >
  // splitClusters(const std::map<uint32_t,
	// 	boost::sub_range<std::vector<ClusterWithTracks<Cluster> > > > &input,
	// 	const reco::Vertex &vtx) const ;
  //
  // template<typename Cluster>
  // void splitCluster(const ClusterWithTracks<Cluster> &cluster,
	// 	    typename edmNew::DetSetVector<Cluster>::FastFiller &output) const ;

};

//
// constants, enums and typedefs
//

//
// static data member definitions
//

//
// constructors and destructor
//
NNPixSeedInput::NNPixSeedInput(const edm::ParameterSet& iConfig) :

      vertices_(consumes<reco::VertexCollection>(iConfig.getParameter<edm::InputTag>("vertices"))),
      pixelClusters_(consumes<edmNew::DetSetVector<SiPixelCluster> >(iConfig.getParameter<edm::InputTag>("pixelClusters"))),
      pixeldigisimlinkToken(consumes< edm::DetSetVector<PixelDigiSimLink> >(edm::InputTag("simSiPixelDigis"))),
      cores_(consumes<edm::View<reco::Candidate> >(iConfig.getParameter<edm::InputTag>("cores"))),
      simtracksToken(consumes<std::vector<SimTrack> >(iConfig.getParameter<edm::InputTag>("simTracks"))),
      simvertexToken(consumes<std::vector<SimVertex> >(iConfig.getParameter<edm::InputTag>("simVertex"))),
      ptMin_(iConfig.getParameter<double>("ptMin")),
      pixelCPE_(iConfig.getParameter<std::string>("pixelCPE"))

      //cores_(consumes<edm::View<reco::Candidate> >(iConfig.getParameter<edm::InputTag>("cores")))

//     //  pixelClusters_ = consumes<edmNew::DetSetVector<SiPixelCluster> >(iConfig.getParameter<edm::InputTag>("pixelClusters"));
      // deltaR_(iConfig.getParameter<double>("deltaRmax")),

{
   //now do what ever initialization is needed
   usesResource("TFileService");
  // pixelClusters_ = consumes<edmNew::DetSetVector<SiPixelCluster> >(iConfig.getParameter<edm::InputTag>("pixelClusters"));


   edm::Service<TFileService> fileService;

   //pxdMap_out =new TFile("pxdMap_out.root", "RECREATE");
  // NNPixSeedInputTree= new TTree("NNPixSeedInputTree","NNPixSeedInputTree");
   NNPixSeedInputTree= fileService->make<TTree>("NNPixSeedInputTree","NNPixSeedInputTree");
  //  NNPixSeedInputTree->SetAutoFlush(10000);
   NNPixSeedInputTree->Branch("cluster_measured",clusterMeas,"cluster_measured[200][200][4]/D");
   NNPixSeedInputTree->Branch("trackPar", trackPar, "trackPar[200][200][3][5]/D");
   NNPixSeedInputTree->Branch("trackProb", trackProb, "trackProb[200][200][3]/D");
  //  NNPixSeedInputTree->Branch("cluster_splitted",clusterSplit,"cluster_splitted[100][4][100][100]/D");
   NNPixSeedInputTree->Branch("jet_eta",&jet_eta);
   NNPixSeedInputTree->Branch("jet_pt",&jet_pt);
   NNPixSeedInputTree->Branch("jet_phi",&jet_phi);
   NNPixSeedInputTree->Branch("jet_Ntrack",&jet_Ntrack);
   NNPixSeedInputTree->Branch("track_pt",track_pt,"track_pt[100]/D");
   NNPixSeedInputTree->Branch("track_pz",track_pz,"track_pz[100]/D");
   NNPixSeedInputTree->Branch("track_eta",track_eta,"track_eta[100]/D");
   NNPixSeedInputTree->Branch("track_phi",track_phi,"track_phi[100]/D");

   // //sto usando fileservice quindi non servono in fondo
   // //pxdMap_out->cd();
   // //NNPixSeedInputTree->Write();
   // //pxdMap_out->Close();


   /// dichiarare cosa produce  produces<asd

   for(int i=0; i<Npar+1; i++){
     for(int j=0; j<jetDimX; j++){
       for(int k=0; k<jetDimY; k++){
         if(j<jetDimX && k<jetDimY && i< Nlayer) clusterMeas[j][k][i] = 0.0;
         for(int m=0; m<Nover; m++){
           if(j<jetDimX && k<jetDimY && i< Npar && m<Nover) trackPar[j][k][m][i] =0.0;
           if(j<jetDimX && k<jetDimY && m<Nover) trackProb[j][k][m] =0.0;
         }
       }
     }
   }

}


NNPixSeedInput::~NNPixSeedInput()
{

   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called for each event  ------------
#define foreach BOOST_FOREACH


void NNPixSeedInput::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
  evt_counter++;

  // for(jet){ //soglia pt 500 Gev
  //   save(jet->pt,eta)
  //   for(layer){
  //     find(inter = intersezione jet-layer)
  //     for(cluster on layer){
  //       if(cluser in finestra 30x30 intorno a inter){
  //         save(cluster->sig in posizione x,y,layer)
  //         (trackcluster[n],tracks[n])=split(cluster)
  //         for(trackcluster){ //cioè per ogni traccia che ha originato cluser
  //           save(trackcluster->sig in posizione x,y,layer,track)//con ampiezza tot cluster/Ntrack?
  //           save(trackcluster->track pt,eta,phi) //geom det, specific surface
  //         }
  //       }
  //     }
  //
  //   }
  // }



  using namespace edm;

  iSetup.get<IdealMagneticFieldRecord>().get( magfield_ );
  iSetup.get<GlobalTrackingGeometryRecord>().get(geometry_);
  iSetup.get<TrackingComponentsRecord>().get( "AnalyticalPropagator", propagator_ );

  iEvent.getByToken(pixelClusters_, inputPixelClusters);
  allSiPixelClusters.clear(); siPixelDetsWithClusters.clear();
  allSiPixelClusters.reserve(inputPixelClusters->dataSize()); // this is important, otherwise push_back invalidates the iterators

  edm::Handle<std::vector<SimTrack> > simtracks;
  iEvent.getByToken(simtracksToken, simtracks);

  edm::Handle<std::vector<SimVertex> > simvertex;
  iEvent.getByToken(simvertexToken, simvertex);

  Handle<std::vector<reco::Vertex> > vertices;
  iEvent.getByToken(vertices_, vertices);
  //const reco::Vertex& pv = (*vertices)[0];

  Handle<edm::View<reco::Candidate> > cores;
  iEvent.getByToken(cores_, cores);

  iEvent.getByToken(pixeldigisimlinkToken, pixeldigisimlink);

  // edm::ESHandle<PixelClusterParameterEstimator> pe;
  // const PixelClusterParameterEstimator* pp;
  // iSetup.get<TkPixelCPERecord>().get(pixelCPE_, pe);
  // pp = pe.product();

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
  //std::cout << "jet tot number =" << cores->size() << std::endl;
  for (unsigned int ji = 0; ji < cores->size(); ji++) { //loop jet

    if ((*cores)[ji].pt() > ptMin_) {
      // std::cout << " __________________________________________________________" <<std::endl;
       std::cout << "|____________________NEW JET_______________________________|" <<std::endl;
      //
      // std::cout << "jet number " << jetnum << std::endl;
      //if(ji==1) print = true;
      //  if(print2)std::cout << "|____________________NEW JET_______________________________|" <<std::endl;

      const reco::Candidate& jet = (*cores)[ji];

      std::set<int> trkIDset;
      LocalPoint jetInter(0,0,0);
      // const GeomDet* globDet = (GeomDet*)0; //fuffa assigment to allow to compile

      const auto & simtracksVector = simtracks.product();
      const auto & simvertexVector = simvertex.product();

      jet_pt = jet.pt();
      jet_eta = jet.eta();
      jet_phi = jet.phi();
      GlobalVector jetDir(jet.px(), jet.py(), jet.pz());
      //GlobalVector jetVertex(jet.vertex());

      const reco::Vertex& jetVertex = (*vertices)[0];
      auto jetVert = jetVertex; //trackInfo filling
      std::vector<std::map<int,SiPixelCluster>> clusterMapVector;
      const GeomDetUnit* detUnit = (GeomDetUnit*)0; //fuffa assigment to allow to compile;

      // std::cout << "jetdirection=" << jetDir << std::endl;

      // jetDir=recenter(jet, jetDir, jetVertex, tTopo, pp);

      // std::cout << "jetdirection corrected=" << jetDir << std::endl;

      //reco::Candidate::Point jetVertex = jet.vertex(); //probably equivalent
      edmNew::DetSetVector<SiPixelCluster>::const_iterator detIt = inputPixelClusters->begin();

      const GeomDet* globDet = DetectorSelector(2, jet, jetDir, jetVertex, tTopo,pp, simtracksVector);
      if(globDet == 0) continue;

      const GeomDet* goodDet1 = DetectorSelector(1, jet, jetDir, jetVertex, tTopo,pp, simtracksVector);
      const GeomDet* goodDet3 = DetectorSelector(3, jet, jetDir, jetVertex, tTopo,pp, simtracksVector);
      const GeomDet* goodDet4 = DetectorSelector(4, jet, jetDir, jetVertex, tTopo,pp, simtracksVector);



      for (; detIt != inputPixelClusters->end(); detIt++) { //loop deset
        //edmNew::DetSetVector<SiPixelCluster>::FastFiller filler(*output,detIt->id()); //A CHE SERVE?
        const edmNew::DetSet<SiPixelCluster>& detset = *detIt;
        const GeomDet* det = geometry_->idToDet(detset.id()); //lui sa il layer con cast a  PXBDetId (vedi dentro il layer function)
        //std::cout << "detset size = " << detset.size() << std::endl;
        // if(det!=globDet) continue;
        for (auto cluster = detset.begin(); cluster != detset.end(); cluster++) { //loop cluster
          // std::cout << " ---- new cluster ----" << std::endl;

          const SiPixelCluster& aCluster = *cluster;
          det_id_type aClusterID= detset.id();

          // if(aClusterID.subdetId()!=1) continue;
          if(DetId(aClusterID).subdetId()!=1) continue;

          // PXBDetId detPX = (PXBDetId)detset.id();
          //int lay = detPX.layer();
          int lay = tTopo->layer(det->geographicalId());

          std::pair<bool, Basic3DVector<float>> interPair = findIntersection(jetDir,(reco::Candidate::Point)jetVertex.position(), det);

          if(interPair.first==false) continue;

          Basic3DVector<float> inter = interPair.second;


          auto localInter = det->specificSurface().toLocal((GlobalPoint)inter);


          GlobalPoint pointVertex(jetVertex.position().x(), jetVertex.position().y(), jetVertex.position().z());

           //--------------------------debuging lines ---------------------//

          //auto deltaR_loc = Geom::deltaR(jetDir, localInter);
        //  auto deltaR_glob = Geom::deltaR(jetDir, inter);
          GlobalPoint cPos = det->surface().toGlobal(pp->localParametersV(aCluster,(*geometry_->idToDetUnit(detIt->id())))[0].first);
          LocalPoint cPos_local = pp->localParametersV(aCluster,(*geometry_->idToDetUnit(detIt->id())))[0].first;

          //useful lines only if print =.=
            GlobalVector intersectionDir = (GlobalPoint) inter - pointVertex;
            auto deltaR_glob = Geom::deltaR(jetDir, intersectionDir);
            GlobalVector clusterDir = cPos - pointVertex;
            auto deltaR_clust = Geom::deltaR(jetDir, clusterDir);
        //end of =.=

          //--------------------------end---------------------//


          if(std::abs(cPos_local.x()-localInter.x())/pitchX<=jetDimX/2 && std::abs(cPos_local.y()-localInter.y())/pitchY<=jetDimY/2){ // per ora preso baricentro, da migliorare

            if(det==goodDet1 || det==goodDet3 || det==goodDet4 || det==globDet) {
              // std::cout << ">>>>>>>>>>>>>>>>>>>>>>>> Another Det, det==" << det << "layer=" << lay <<std::endl;
              fillPixelMatrix(aCluster,lay,localInter, det);
              }

            if(lay==2 && det==globDet) {

              if(jetInter.x()==0 && jetInter.y()==0 && jetInter.z()==0) jetInter = localInter; //filling infoTracks
              // if(globDet ==(GeomDet*)0){//filling infoTracks
                //  globDet = det;
              detUnit = geometry_->idToDetUnit(detIt->id());
              //  }

              // if(det!=globDet) continue;

              std::map<int,SiPixelCluster> splittedCluster = splitClusterInTracks(aCluster,aClusterID); //accesso/assegnazione splittedClister[id]=cluser
              clusterMapVector.push_back(splittedCluster);
              for(std::map<int,SiPixelCluster>::iterator track_iter= splittedCluster.begin(); track_iter!=splittedCluster.end(); track_iter++){
                trkIDset.insert(track_iter->first); //trackID

              fillPixelTrackMap(track_iter->first, track_iter->second,lay,localInter, det);
              //aggiungere salvataggio info traccia (pt eta ecc) usando trackID
              }//tracks in cluster
          }
          } //cluster in ROI
        } //cluster
      } //detset
    //  jetnum++;


    // int lay = tTopo->layer(globDet->geographicalId());
    // std::cout << "layer filled=" << lay << std::endl;
    // if(globDet == 0) continue;
    fillTrackInfo(jet, trkIDset, simtracksVector, simvertexVector, jetInter, jetDir, jetVert, globDet, clusterMapVector, pp, detUnit);
    clusterMapVector.clear();
    NNPixSeedInputTree->Fill();
    std::cout << "FILL!" << std::endl;

    for(int i=0; i<Npar+1; i++){
      for(int j=0; j<jetDimX; j++){
        for(int k=0; k<jetDimY; k++){
          if(j<jetDimX && k<jetDimY && i< Nlayer) clusterMeas[j][k][i] = 0.0;
          for(int m=0; m<Nover; m++){
            if(trackPar[j][k][m][i]!=0 && j<jetDimX && k<jetDimY && i< Npar+1 && m<Nover) trackPar[j][k][m][i] =0.0;
            if(trackProb[j][k][m]!=0 && j<jetDimX && k<jetDimY && m<Nover) trackProb[j][k][m] =0.0;
          }
          for(int h=0; h<Ntrack; h++){
            if(h<Ntrack) track_pt[h] = 0.0;
            if(h<Ntrack) track_pz[h] = 0.0;
            if(h<Ntrack) track_eta[h] = 0.0;
            if(h<Ntrack) track_phi[h] = 0.0;
          }
        }
      }
    }
    trkIDset.clear();
  } //jet > pt
 } //jet
//  print = false;
std::cout << "event number=" << evt_counter<< std::endl;
trackMap.clear();
}













  std::pair<bool, Basic3DVector<float>> NNPixSeedInput::findIntersection(const GlobalVector & dir,const  reco::Candidate::Point & vertex, const GeomDet* det){
     StraightLinePlaneCrossing vertexPlane(Basic3DVector<float>(vertex.x(),vertex.y(),vertex.z()), Basic3DVector<float>(dir.x(),dir.y(),dir.z()));

     std::pair<bool, Basic3DVector<float>> pos = vertexPlane.position(det->specificSurface());

     return pos;
  }



  std::pair<int,int> NNPixSeedInput::local2Pixel(double locX, double locY, const GeomDet* det){
    LocalPoint locXY(locX,locY);
    float pixX=(dynamic_cast<const PixelGeomDetUnit*>(det))->specificTopology().pixel(locXY).first;
    float pixY=(dynamic_cast<const PixelGeomDetUnit*>(det))->specificTopology().pixel(locXY).second;
    std::pair<int, int> out(pixX,pixY);
    return out;
  }

  LocalPoint NNPixSeedInput::pixel2Local(int pixX, int pixY, const GeomDet* det){
    float locX=(dynamic_cast<const PixelGeomDetUnit*>(det))->specificTopology().localX(pixX);
    float locY=(dynamic_cast<const PixelGeomDetUnit*>(det))->specificTopology().localY(pixY);
    LocalPoint locXY(locX,locY);
    return locXY;
  }

  int NNPixSeedInput::pixelFlipper(const GeomDet* det){
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


  GlobalVector NNPixSeedInput::recenter(const reco::Candidate& jet, GlobalVector dir, const reco::Vertex& jetVertex, const TrackerTopology* const tTopo, const PixelClusterParameterEstimator* pp){

    int layNum=4;
    int jetCore = 40;
    // std::vector<std::pair<double,double>> baricenter;
    double baricenter_x[layNum]={0.0};
    double baricenter_y[layNum]={0.0};
    double charge[layNum]={0.0};
    GlobalPoint baricenter_global;

    // std::cout<<"deb1="<<baricenter_y[0] <<std::endl;



    for(int llay=0; llay<layNum;llay++){
      if(llay<layNum) baricenter_x[llay]=0.0;
      if(llay<layNum) baricenter_y[llay]=0.0;
      // std::cout<<"deb1="<<baricenter_y[0] <<std::endl;

      edmNew::DetSetVector<SiPixelCluster>::const_iterator detIt = inputPixelClusters->begin(); //forse non lo ha !!!!!

      for (; detIt != inputPixelClusters->end(); detIt++) { //loop deset

        edmNew::DetSetVector<SiPixelCluster>::const_iterator detfound;

        const edmNew::DetSet<SiPixelCluster>& detset = *detIt;
        const GeomDet* det = geometry_->idToDet(detset.id());

        for (auto cluster = detset.begin(); cluster != detset.end(); cluster++) { //loop cluster

          const SiPixelCluster& aCluster = *cluster;
          auto aClusterID= detset.id();
          if(DetId(aClusterID).subdetId()!=1) continue;

          int lay = tTopo->layer(det->geographicalId());
          // if(lay==0)std::cout<<"layer 0????"<< std::endl;
          if(lay!=llay+1) continue;

          std::pair<bool, Basic3DVector<float>> interPair = findIntersection(dir,(reco::Candidate::Point)jetVertex.position(), det);
          if(interPair.first==false) continue;
          Basic3DVector<float> inter = interPair.second;
          auto localInter = det->specificSurface().toLocal((GlobalPoint)inter);
          //GlobalPoint pointVertex(jetVertex.position().x(), jetVertex.position().y(), jetVertex.position().z());
          //GlobalPoint cPos = det->surface().toGlobal(pp->localParametersV(aCluster,(*geomscretry_->idToDetUnit(detIt->id())))[0].first);
          LocalPoint cPos_local = pp->localParametersV(aCluster,(*geometry_->idToDetUnit(detIt->id())))[0].first;

          if(std::abs(cPos_local.x()-localInter.x())/pitchX<=jetCore/2 && std::abs(cPos_local.y()-localInter.y())/pitchY<=jetCore/2){ // per ora preso baricentro, da migliorare


            if(llay<layNum) baricenter_x[llay] += (cPos_local.x())*(aCluster.charge());
            if(llay<layNum) baricenter_y[llay] += (cPos_local.y())*(aCluster.charge());

            if(llay<layNum) charge[llay] += aCluster.charge();

           detfound=detIt;


          } //cluster in ROI
      } //cluster
      // std::cout<<"charge"<<charge[0] << std::endl;

      if(detfound==detIt){
        const edmNew::DetSet<SiPixelCluster>& detset = *detIt;
        // std::cout << "enter in det==" << detset.id();
        // std::cout << "     with lay = " << llay << std::endl;
        if(llay<layNum) baricenter_x[llay] /= charge[llay];
        if(llay<layNum) baricenter_y[llay] /= charge[llay];

      LocalPoint baricenter_local(baricenter_x[0],baricenter_y[0], 0.0);
      // std::cout<<"baricenter_local="<<baricenter_local << std::endl;
      baricenter_global = det->surface().toGlobal(baricenter_local);
      }
    } //detset

  } //layer
  //std::cout<<"baricenter_global="<<baricenter_global << std::endl;
  GlobalPoint pointv(jetVertex.position().x(), jetVertex.position().y(), jetVertex.position().z());
  //GlobalPoint nothing(0,0,0);
  GlobalVector out = baricenter_global - pointv;
  return out;

}


  void NNPixSeedInput::fillPixelMatrix(const SiPixelCluster & cluster, int layer, auto inter, const GeomDet* det){
    // if(print){std::cout << "----- cluster filled-------" << std::endl;
    // std::cout << "cluser layer" << layer << std::endl;}
     if(print){std::cout << "--------new cluster----------" <<std::endl;
    std::cout << "layer=" << layer << std::endl;}
    if(layer==0) std::cout << "LAYER 0!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" << std::endl;

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
        if(nx<jetDimX && ny<jetDimY && layer-1< Nlayer && layer-1>=0 && nx>=0 && ny>=0) clusterMeas[nx][ny][layer-1] += pix.adc;

        if(print){std::cout << "x position pixel " << nx-jetDimX/2 <<std::endl;
        std::cout << "y position pixel " << ny-jetDimY/2 <<std::endl;
        std::cout << "charge " << pix.adc <<std::endl;}

        if(0){std::cout << "---------INPUT debug -------- det=" <<det->gdetIndex()<< std::endl;
        std::cout<< "x=" << nx << ", y=" << ny << "("<<nx-jetDimX/2 << ", " << ny-jetDimY/2 << ")" << std::endl;
        std::cout << "jetInter X="<< pixInter.first <<", Y=" << pixInter.second << std::endl;
        std::cout << "trkInter X="<< pix.x <<", Y=" << pix.y << std::endl;
      }
      }
    }

  }

  void NNPixSeedInput::fillPixelTrackMap(int trackID, const SiPixelCluster & cluster, int layer, auto inter, const GeomDet* det){

    int flip = pixelFlipper(det); // 1=not flip, -1=flip

    for(int i=0; i<cluster.size();i++){
      SiPixelCluster::Pixel pix = cluster.pixel(i);

      std::pair<int,int> pixInter = local2Pixel(inter.x(),inter.y(),det);
      int nx = pix.x-pixInter.first;
      int ny = pix.y-pixInter.second;
      nx=flip*nx;

      if(abs(nx)<jetDimX/2 && abs(ny)<jetDimY/2){
        nx = nx+jetDimX/2;
        ny = ny+jetDimY/2;
        if(0){std::cout << "---------cluster splitting debug --------" << std::endl;
        std::cout<< "trackID=" << trackID << ", x=" << nx << ", y=" << ny << std::endl;
        std::cout << "jetInter X="<< pixInter.first <<", Y=" << pixInter.second << std::endl;
        std::cout << "trkInter X="<< pix.x <<", Y=" << pix.y << std::endl;
        LocalPoint pix2loc = pixel2Local(pix.x,pix.y,det);
        std::cout << "local jetInter X="<< inter.x() <<", Y=" << inter.y() << std::endl;
        std::cout << "local trkInter X="<< pix2loc.x() <<", Y=" << pix2loc.y() << std::endl;
        std::cout << "DETid" << det->gdetIndex() << std::endl;}
        if(layer-1<Nlayer && layer-1>=0 && nx<jetDimX && ny<jetDimY && nx>=0 && ny>=0) trackMap[trackID][layer-1][nx][ny] += pix.adc;
      }
    }
  }

  void NNPixSeedInput::fillPixelTrackMatrix(const std::vector<SimTrack>* const & stVector){
    int trk = 0;
    double trackFlag[Ntrack] = {0.0};
    for(std::map<int, double [Nlayer][jetDimX][jetDimY]>::iterator it=trackMap.begin(); it!=trackMap.end(); it++){
      if(trk<Ntrack) trackFlag[trk] = it->first;
      if(print2){std::cout << "trk="<< trk;
      std::cout << " -- trackID=" << trackFlag[trk] << std::endl;}
    //for(int trk =0; trk<=std::min(trackMap.size(),NTrack); trk++)
      if(trk>=Ntrack) continue;
      for(int lay =0; lay<Nlayer; lay++){
        for(int dimx =0; dimx<jetDimX; dimx++){
          for(int dimy =0; dimy<jetDimY; dimy++){
            if(trk< Ntrack && lay<Nlayer && dimx<jetDimX && dimy<jetDimY) clusterSplit[trk][lay][dimx][dimy] = trackMap[it->first][lay][dimx][dimy];

            if(trackMap[it->first][lay][dimx][dimy]>100){
              if(print2){std::cout << "filled hit in track (trk), " << trk;
              std::cout << " -- filled lay=" << lay;
              std::cout << " -- filled dimx=" << dimx;
              std::cout << " -- filled dimy=" << dimy <<std::endl;}
            }
          }
        }
      }

      for(uint j=0; j<stVector->size(); j++){
          SimTrack st = stVector->at(j);
          if((int)st.trackId()==it->first) {

            if(trk<Ntrack) track_pt[trk] = st.momentum().Pt();
            if(trk<Ntrack) track_pz[trk] = st.momentum().Pz();
            if(trk<Ntrack) track_eta[trk] = st.momentum().Eta();
            if(trk<Ntrack) track_phi[trk] = st.momentum().Phi();

            if(print2){std:: cout << "pt=" << track_pt[trk];
            std:: cout << " --- eta=" << track_eta[trk] << std::endl;}

          }
        }


      trk++;
      if(print2) std::cout << "------------------------------" << std::endl;
    }
    trackMap.clear();
  }




  void NNPixSeedInput::fillTrackInfo(const reco::Candidate& jet, const std::set<int> setTrkID, const auto & stVector,  const auto & svVector, auto jti, auto jetDir, auto jVert, const GeomDet* det, std::vector<std::map<int,SiPixelCluster>> clusterVector, const PixelClusterParameterEstimator* cpe, const GeomDetUnit* detUnit){

    struct trkInfoObj
    {
      int prob;
      double dist;
      double xpos;
      double ypos;
      double xangle;
      double yangle;
      double zero_flag; //useful for CNN training only: 0 if x,y,eta,phi==0
      // double jEta;
      // double jPt;
      // double xdist;
      // double ydist;
      // double trknum;
      trkInfoObj(int pp, double dd, double xx, double yy, double tx, double ty, int zf) : //, double jeta, double jpt) : // double xd, double yd, double n) :
        prob(pp),
        dist(dd),
        xpos(xx),
        ypos(yy),
        xangle(tx),
        yangle(ty),
        zero_flag(zf) {}
        // jEta(jeta),
        // jPt(jpt) {}
        // xdist(xd),
        // ydist(yd),
        // trknum(n) {}

      bool operator < (const trkInfoObj& trk) const
      {
        return (dist < trk.dist);
      }
    };

   std::vector<SimTrack> goodSimTrk;
   std::vector<SimVertex> goodSimVtx;



    int trk =0;
    for(uint j=0; j<stVector->size(); j++){ //matched tracks selection and vertex assigment
      for(std::set<int>::iterator it=setTrkID.begin(); it!=setTrkID.end(); ++it) {
        SimTrack st = stVector->at(j);
        if((int)st.trackId()==*it) {
          // if(st.momentum().Pt()>100){
          goodSimTrk.push_back(st);
          for(uint v =0; v<svVector->size(); v++) {
            SimVertex sv = svVector->at(v);
            if((int)sv.vertexId()==(int)st.vertIndex()){
              // if(st.vertIndex()==-1) goodSimVtx.push_back((SimVertex)jVert);
              //else
               goodSimVtx.push_back(sv);
            }
          }
          // if(trk<100){
          //   track_pt[trk] = st.momentum().Pt();
          //   track_pz[trk] = st.momentum().Pz();
          //   track_eta[trk] = st.momentum().Eta();
          //   track_phi[trk] = st.momentum().Phi();
          // }
          // trk++;
        // }
        }
      }
    }
    jet_Ntrack=goodSimTrk.size();
    for(uint j=0; j<goodSimTrk.size(); j++){
      SimTrack st = goodSimTrk.at(j);
      if(j<100){
        if(trk<Ntrack) track_pt[j] = st.momentum().Pt();
        if(trk<Ntrack) track_pz[j] = st.momentum().Pz();
        if(trk<Ntrack) track_eta[j] = st.momentum().Eta();
        if(trk<Ntrack) track_phi[j] = st.momentum().Phi();
      }
      // //--------------debug lines -------------
      // SimVertex sv = goodSimVtx.at(j);
      // GlobalVector trkMom(st.trackerSurfaceMomentum().x(),st.trackerSurfaceMomentum().y(), st.trackerSurfaceMomentum().z());
      // GlobalPoint trkPos(sv.position().x(),sv.position().y(), sv.position().z());
      // GlobalPoint trkPosJet(jVert.position().x(),jVert.position().y(), jVert.position().z());
      // std::pair<bool, Basic3DVector<float>> trkInterPair;
      // trkInterPair = findIntersection(trkMom,(reco::Candidate::Point)trkPos, det);
      // //trkInterPair = findIntersection(trkMom,(reco::Candidate::Point)trkPosJet, det);
      // if(trkInterPair.first==false) continue;
      // Basic3DVector<float> trkInter = trkInterPair.second;
      // // auto localTrkInter = det->specificSurface().toLocal((GlobalPoint)trkInter);
      //
      // //--------new intesection method------//
      // // GlobalPoint cPos = det->surface().toGlobal(pp->localParametersV(aCluster,(*geometry_->idToDetUnit(detIt->id())))[0].first);
      // SiPixelCluster theCluster;
      // for(uint t=0; t<clusterVector.size(); t++){
      //   for(std::map<int,SiPixelCluster>::iterator track_iter= clusterVector.at(t).begin(); track_iter!=clusterVector.at(t).end(); track_iter++){
      //     if(track_iter->first==(int)st.trackId() ){
      //       theCluster = track_iter->second;
      //     }
      //   }
      //
      // }
      // // //debug lines ........
      // // for(int i=0; i<theCluster.size();i++){
      // //   SiPixelCluster::Pixel pix = theCluster.pixel(i);
      // //   std::cout << ".............................CLUSTER DEBUG: ";
      // //   std::cout << "pixel x=" << pix.x << ", y=" << pix.y << ", adc=" << pix.adc<< std::endl;
      // // }
      // // std::cout << "cluster baricenter" << "x=" <<  theCluster.x() << ", y="<< theCluster.y() << std::endl;
      //
      // LocalPoint localTrkInter = std::get<0>(cpe->getParameters(theCluster,*detUnit));
      //
      //
      // int flip = pixelFlipper(det);
      // std::pair<int,int> pixJInter = local2Pixel(jti.x(),jti.y(),det);
      // std::pair<int,int> pixTrkInter = local2Pixel(localTrkInter.x(),localTrkInter.y(),det);
      // LocalPoint reloc = pixel2Local(pixTrkInter.first, pixTrkInter.second, det);
      // std::cout << "TRACK DEBUG: " << j << " trackiD=" << (int)st.trackId() << std::endl;
      // std::cout << "Inter track glob: " << trkInter << std::endl;
      // std::cout << "Inter track loc: " << localTrkInter << std::endl;
      // std::cout << "Inter jet loc: " << jti << std::endl;
      // std::cout << "Inter track pix X: " << pixTrkInter.first;
      // std::cout << "  Y: " << pixTrkInter.second << std::endl;
      // std::cout << "Inter jet pix X: " << pixJInter.first;
      // std::cout << "  Y: " << pixJInter.second << std::endl;
      // std::cout << "diff pix x " << flip*(-pixJInter.first + pixTrkInter.first)+jetDimX/2;
      // std::cout << "    Y: " << -pixJInter.second + pixTrkInter.second+jetDimY/2 << ", flip=" << flip << std::endl;
      // // std::cout << "reconversion in pos, X:" << pixTrkInter.first*pitchX << ",    Y="<< pixTrkInter.second*pitchY << std::endl;
      // std::cout << "reconversion in pos, reloc:" << reloc << std::endl;
      // std::cout << "DETid" << det->gdetIndex() << std::endl;
      //
      //  std::cout << "-----------" << std::endl;
      //
      // //--------------END OF debug lines -------------

    }
    // std::cout << "New Info filling, track Number="<< goodSimTrk.size() << " det=" << det << std::endl;
    for(int x=0; x<jetDimX; x++){
      for(int y=0; y<jetDimY; y++){
        // int flipp= pixelFlipper(det); //-----LINEA DEMMERDA INCRIMINATA
        // std::cout << flipp << std::endl;
        // flipp=-1;
        // LocalPoint Jinter(flipp*jti.x(),jti.y(),jti.z());
        // std::cout << "x=" << x << ", y=" << y << std::endl;
        // std::vector<double *> tracksInfo
        std::vector<trkInfoObj> tracksInfo;
        for(uint j=0; j<goodSimTrk.size(); j++){
          // std::cout << "------------------------------:track,x,y" << x << y << std::endl;
          SimTrack st = goodSimTrk.at(j);
          // SimVertex sv = goodSimVtx.at(j);
          GlobalVector trkMom(st.trackerSurfaceMomentum().x(),st.trackerSurfaceMomentum().y(), st.trackerSurfaceMomentum().z());
          // std::cout << "trkMom" <<trkMom<< std::endl;
          // GlobalPoint * trkPos;
          // if(st.vertIndex()==-1) trkPos = new GlobalPoint(jVert.position().x(),jVert.position().y(), jVert.position().z());
          // else trkPos = new GlobalPoint(sv.position().x(),sv.position().y(), sv.position().z());
          // GlobalPoint trkPos(sv.position().x(),sv.position().y(), sv.position().z());
          // GlobalPoint trkPosJet(jVert.position().x(),jVert.position().y(), jVert.position().z());
          // std::cout << "trkPos" <<trkPos<< std::endl;
          // std::pair<bool, Basic3DVector<float>> trkInterPair;
          // if(st.vertIndex()==-1) {
            // trkInterPair = findIntersection(trkMom,(reco::Candidate::Point)trkPosJet, det);
            // std::cout << "no track vertex" <<std::endl;
          // }
          // else  trkInterPair = findIntersection(trkMom,(reco::Candidate::Point)trkPos, det);
          //SISTEMA intersezione per verso opposto

          // if(trkInterPair.first==false) continue;
          // Basic3DVector<float> trkInter = trkInterPair.second;
          int flip = pixelFlipper(det); // 1=not flip, -1=flip

          // std::cout << "global track inter=" <<trkInter << std::endl;

          //////////////////////////////////auto localTrkInter = det->specificSurface().toLocal((GlobalPoint)trkInter);

          // std::cout << "local track inter=" <<localTrkInter << std::endl;
          // std::cout << "local jet inter=" <<Jinter << std::endl;
          SiPixelCluster theCluster;
          for(uint t=0; t<clusterVector.size(); t++){
            for(std::map<int,SiPixelCluster>::iterator track_iter= clusterVector.at(t).begin(); track_iter!=clusterVector.at(t).end(); track_iter++){
              if(track_iter->first==(int)st.trackId()){
                theCluster = track_iter->second;
              }
            }

          }

          //LocalPoint localTrkInter = std::get<0>(cpe->getParameters(theCluster,*detUnit));
          LocalPoint localTrkInter(flip*(std::get<0>(cpe->getParameters(theCluster,*detUnit))).x(),(std::get<0>(cpe->getParameters(theCluster,*detUnit))).y(),(std::get<0>(cpe->getParameters(theCluster,*detUnit))).z());
          // localTrkInter = flip*localTrkInter;
          // Jinter = flip*Jinter;
          LocalPoint Jinter(flip*jti.x(),jti.y(),jti.z());


          std::pair<int,int> pixJInter = local2Pixel(Jinter.x(),Jinter.y(),det);
          std::pair<int,int> pixTrkInter = local2Pixel(localTrkInter.x(),localTrkInter.y(),det);

          int pixX = (pixTrkInter.first-pixJInter.first);
          int pixY = (pixTrkInter.second-pixJInter.second);

          pixX=pixX;
          pixX = pixX+jetDimX/2;
          pixY = pixY+jetDimY/2;

          // double info[9] = {0,0,0,0,0,0,0,0,-1};
          double info[7] = {0.0,0.0,0.0,0.0,0.0,0.0,0.0};

          if (x==pixX && y==pixY) {
            // if(flagOver[x][y] < Nover){
            //   trackProb[x][y][flagOver[x][y]] = 1;
            //   flagOver[x][y]=flagOver[x][y]+1;
            // }
            // std::cout << "-----------" <<std::endl;
            // std::cout << "trk num " << j << ", flip=" << flip << std::endl;
            // std::cout << "prob1,  x=" << x << "  y=" << y << std::endl;
            info[0]= 1;
            // std::cout << "pixel Xj=" << pixJInter.first << std::endl;
            // std::cout << "pixel Xtrk=" << pixTrkInter.first << std::endl;
            // std::cout << "pixel Yj=" << pixJInter.second << std::endl;
            // std::cout << "pixel Ytrk=" << pixTrkInter.second << std::endl;
          }

          // double distX = flip*(Jinter.x()-localTrkInter.x())-(x+0.5)*pitchX;
          // double distY = Jinter.y()-localTrkInter.y()-(x+0.5)*pitchY;
          //  double distX = flip*(localTrkInter.x())-(pixTrkInter.first+0.5)*pitchX;
          //  double distY = localTrkInter.y()-(pixTrkInter.second+0.5)*pitchY;
        //   LocalPoint pix2loc = pixel2Local(pixTrkInter.first,pixTrkInter.second,det);
          //  double distX = localTrkInter.x()-pix2loc.x()-0.5*pitchX;
          //  double distY = localTrkInter.y()-pix2loc.y()-0.5*pitchY;
          LocalPoint pix2loc = pixel2Local(x+pixJInter.first-jetDimX/2,y+pixJInter.second-jetDimY/2,det);
          double distX =  localTrkInter.x()-pix2loc.x()-0.5*pitchX;
          double distY =  localTrkInter.y()-pix2loc.y()-0.5*pitchY;

           if(distX<0.000001 && distX> -0.000001) {
            //  std::cout << "distX="<< distX << std::endl;
             distX = 0.0;
           }
           if(distY<0.000001 && distY> - 0.000001){
            //  std::cout << "distY="<< distY << std::endl;
             distY = 0.0;
           }

          info[1] = sqrt(distX*distX+distY*distY);
          // info[6] = distX;
          // info[7] = distY;
          if(info[0]== 1 && 0){
            std::cout << "2ddist=" << info[1] << std::endl;
            std::cout << "distX=" << distX <<", distY="<<distY<<std::endl;
            std::cout << "pixel Xj=" << pixJInter.first << std::endl;
            std::cout << "pixel Xtrk=" << pixTrkInter.first << std::endl;
            std::cout << "pixel Yj=" << pixJInter.second << std::endl;
            std::cout << "pixel Ytrk=" << pixTrkInter.second << std::endl;
            std::cout << "Inter track loc: " << localTrkInter.y() << std::endl;
            std::cout << "Inter jet loc: " << Jinter << std::endl;
            std::cout << "pix2loc=" << pix2loc.y() << std::endl;
            std::cout<< "difference:" << (float)(localTrkInter.y())-(float)(pix2loc.y())-0.5*(float)pitchY << std::endl;


          }

          if(fabs(distX)<distThr*pitchX && fabs(distY)<distThr*pitchY){ //////////////////////////////////////////---GOOD WAY
          //if(x==pixX && y==pixY)
            info[2] = distX;
            info[3] = distY;
            //----debug lines ---- //
            if(info[0]== 1 && 0 ) {
              std::cout << "x=" << x << ", y=" << y << std::endl;
              std::cout << "Jinter=" << Jinter << std::endl;
              std::cout << "localTrkInter=" << localTrkInter << std::endl;
              std::cout << "dist, distX=" << distX <<", distY=" << distY<< std::endl;
            }
            //----debug lines ----END


            // auto localJetDir = det->specificSurface().toLocal((GlobalVector)jetDir);
            // auto localTrkDir = det->specificSurface().toLocal(trkMom);
            //
            // info[4] = atan(localJetDir.x()/localJetDir.z())-atan(localTrkDir.x()/localTrkDir.z());
            // info[5] = atan(localJetDir.y()/localJetDir.z())-atan(localTrkDir.y()/localTrkDir.z());
            info[4] = st.momentum().Eta()-jet.eta();
            info[5] = deltaPhi(st.momentum().Phi(),jet.phi());
            // info[6] = jet.eta();
            // info[7] = jet.pt();


          }
          else{
          if(info[0]== 1) {
            std::cout <<"?????????????out???" << std::endl;

          }
          info[2] = 99999999;
          info[3] = 99999999;
          }
          // info[8]=j;
          if(info[0]==1 && 0) std::cout << "inside=" << info[0] << "," << info[1] << "," << info[2] << "," <<info[3] << "," <<info[4] << "," << info[5] << "," << std::endl;

          if(info[0]==0 && info[2]==0.0 && info[3]==0.0 && info[4]==0.0 && info[5]==0.0) {
            info[6] = 0;
            // std::cout << "0-flag=" << info[0] << "," << info[1] << "," << info[2] << "," <<info[3] << "," <<info[4] << "," << info[5] << "," << std::endl;
          }
          else if(info[2] > 9999999 && info[3] > 9999999) {
            info[6] = 0;
            // std::cout << "0-flag=" << info[0] << "," << info[1] << "," << info[2] << "," <<info[3] << "," <<info[4] << "," << info[5] << "," << std::endl;

          }
          else{
             info[6]=1;
            // std::cout << "1-flag=" << "x="<< x << ", y=" << y<< ", " << info[0] << "," << info[1] << "," << info[2] << "," <<info[3] << "," <<info[4] << "," << info[5] << "," << std::endl;
           }

          tracksInfo.push_back(trkInfoObj(info[0],info[1],info[2],info[3],info[4],info[5],info[6]));//,info[6],info[7]));//info[6],info[7],info[8]));
          // if(info[0]== 1) std::cout << tracksInfo.at(tracksInfo.size()-1).prob << std::endl;

          //---debug lines
          // for(uint k=0; k<tracksInfo.size(); k++){
          //   if(info[0]== 1){
          //     std::cout << "track info vector, prob:"<<tracksInfo.at(k).prob << ",    dist:"<<tracksInfo.at(k).dist  << ", distX="<<tracksInfo.at(k).xdist << ", distY="<< tracksInfo.at(k).ydist << ", pixX="<<  local2Pixel(tracksInfo.at(k).xdist,tracksInfo.at(k).ydist,det).first << ", pixY="<< local2Pixel(tracksInfo.at(k).xdist,tracksInfo.at(k).ydist,det).second<< std::endl;
          //   }
          // }
          // //end of debug

        }//good tracks
        // std::cout << "prob0=" << tracksInfo.at(0).prob << ", prob1=" << tracksInfo.at(1).prob << ", prob2="<<tracksInfo.at(2).prob << std::endl;
        int fl=0;
        for(uint k=0; k<tracksInfo.size(); k++){
          if(tracksInfo.at(k).prob== 1){
            fl=1;
          }
        }
        if(fl==1) {
          //---debug lines
          for(uint k=0; k<tracksInfo.size(); k++){
            //std::cout << "track info vector, OUT, prob:"<<tracksInfo.at(k).prob << ",    dist:"<<tracksInfo.at(k).dist   <<std::endl;


            //if(tracksInfo.at(trk).prob==1) std::cout << "track info vector, OUT, prob:"<<tracksInfo.at(k).prob << ",    dist:"<<tracksInfo.at(k).dist  << ", distX="<<tracksInfo.at(k).xpos << ", distY="<< tracksInfo.at(k).ypos<<std::endl; //<< ", pixX="<<  local2Pixel(tracksInfo.at(k).xpos,tracksInfo.at(k).ypos,det).first << ", pixY="<< local2Pixel(tracksInfo.at(k).xpos,tracksInfo.at(k).ypos,det).second<< std::endl;//<< "tracknumber="<<tracksInfo.at(k).trknum<< std::endl;
            if(tracksInfo.size()>1 && 0) std::cout << "track info vector, OUT, prob:"<<tracksInfo.at(k).prob << ",    dist:"<<tracksInfo.at(k).dist  << ", distX="<<tracksInfo.at(k).xpos << ", distY="<< tracksInfo.at(k).ypos<<std::endl; //<< ", pixX="<<  local2Pixel(tracksInfo.at(k).xpos,tracksInfo.at(k).ypos,det).first << ", pixY="<< local2Pixel(tracksInfo.at(k).xpos,tracksInfo.at(k).ypos,det).second<< std::endl;//<< "tracknumber="<<tracksInfo.at(k).trknum<< std::endl;

          }
        }
          //end of debug


        // if(tracksInfo.at(0).prob== 1) std::cout << "size trackinfo presort="  << tracksInfo.size() << std::endl;

        std::sort(tracksInfo.begin(), tracksInfo.end());

        if(fl==1) {
          //---debug lines
          for(uint k=0; k<tracksInfo.size(); k++){
            // std::cout << "track info vector, SORT, prob:"<<tracksInfo.at(k).prob << ",    dist:"<<tracksInfo.at(k).dist   <<std::endl;


            //if(tracksInfo.at(trk).prob==1)
            if(tracksInfo.size()>1 && 0)  std::cout << "track info vector, SORT, prob:"<<tracksInfo.at(k).prob << ",    dist:"<<tracksInfo.at(k).dist  << ", distX="<<tracksInfo.at(k).xpos << ", distY="<< tracksInfo.at(k).ypos <<std::endl;//", pixX="<<  local2Pixel(tracksInfo.at(k).xpos,tracksInfo.at(k).ypos,det).first << ", pixY="<< local2Pixel(tracksInfo.at(k).xpos,tracksInfo.at(k).ypos,det).second<< std::endl;//<< "tracknumber="<<tracksInfo.at(k).trknum<< std::endl;

          }
        }
        int trkLim=Nover;
        // if(tracksInfo.at(0).prob== 1)  std::cout << "size trackinfo postsort="  << tracksInfo.size() << std::endl;
        if (tracksInfo.size()<3) trkLim = tracksInfo.size();

        if(trackPar[x][y][2][4]!=0 && 0) std::cout << "out!!!!!!!!!-----------------------------------------------" << std::endl;
        for(trk=0; trk<trkLim; trk++){
          if(x<jetDimX && y<jetDimY && trk<Nover && x>=0 && y>=0) {
            if(tracksInfo.at(trk).xpos!=99999999) trackPar[x][y][trk][0]=tracksInfo.at(trk).xpos;
            else trackPar[x][y][trk][0]=0.0;
            if(tracksInfo.at(trk).ypos!=99999999) trackPar[x][y][trk][1]=tracksInfo.at(trk).ypos;
            else trackPar[x][y][trk][1]=0.0;
            trackPar[x][y][trk][2]=tracksInfo.at(trk).xangle;
            trackPar[x][y][trk][3]=tracksInfo.at(trk).yangle;
            trackPar[x][y][trk][4]=tracksInfo.at(trk).zero_flag;
            //  trackPar[x][y][trk][4]=tracksInfo.at(trk).jEta;
            //  trackPar[x][y][trk][5]=tracksInfo.at(trk).jPt;
            trackProb[x][y][trk]=tracksInfo.at(trk).prob;

            //-----------debug lines ---------------//

            if(tracksInfo.at(trk).zero_flag!=0 && 0){
              std::cout <<"Filling trakck=" << trk << ", prob="<<tracksInfo.at(trk).prob<< ", x="<< x << ", y=" << y<< ", "<<  "xpos=" << tracksInfo.at(trk).xpos << " ypos=" << tracksInfo.at(trk).ypos << std::endl;
            }

            if(tracksInfo.at(trk).prob==1 && 0){
              std::cout << "xpos=" << tracksInfo.at(trk).xpos << " ypos=" << tracksInfo.at(trk).ypos << "("<<trackPar[x][y][trk][0] << "," << trackPar[x][y][trk][1] <<")" << std::endl;
            }
         }
         if(trackPar[x][y][2][4]!=0 && 0) std::cout << "-------------------------------------------------" << ", prob="<<trackProb[x][y][2]<< ", x="<< x << ", y=" << y<< ", "<<  "xpos=" << trackPar[x][y][2][0] << " ypos=" << trackPar[x][y][2][1] << "par2="<< trackPar[x][y][2][2] << "par3="<<trackPar[x][y][2][3]<< "flag="<<trackPar[x][y][2][4]<< std::endl;
          //----debug lines ----
          if(tracksInfo.at(trk).prob==1 && 0 ){
            std::cout << " NEW TRACK: " << std::endl;
            std::cout << " x position:" << tracksInfo.at(trk).xpos << std::endl;
            std::cout << " y position:" << tracksInfo.at(trk).ypos << std::endl;
            std::cout << " x bin:" << x << std::endl;
            std::cout << " y bin:" << y << std::endl;
          }
          //----debug lines ----END

        }//trk (filling)
      tracksInfo.clear();
    } // y
    }//x
    goodSimTrk.clear();
    goodSimVtx.clear();
  }






    // for(std::map<int, double [Nlayer][jetDimX][jetDimY]>::iterator it=trackMap.begin(); it!=trackMap.end(); it++){ //sistema: loop solo su simtrack associati a cluster
    //   for(uint j=0; j<stVector->size(); j++){
    //     SimTrack st = stVector->at(j);
    //     if((int)st.trackId()==it->first) {
    //       std::pair<bool, Basic3DVector<float>> trkInterPair = findIntersection(st.trackerSurfaceMomentum(),(reco::Candidate::Point)st.trackerSurfacePosition(), det); //sistema tipo argomenti + local global ecc
    //       if(trkInterPair.first==false) continue;
    //       Basic3DVector<float> trkInter = trkInterPair.second;
    //       auto localTrkInter = det->specificSurface().toLocal((GlobalPoint)inter);
    //       for(int i=0; i<jetDimX; i++){
    //         for(int k=0; k<jetDimY; k++){
    //
    //         }
    //       }
    //
    //     }
    //   }
    // }






  std::map<int,SiPixelCluster> NNPixSeedInput::splitClusterInTracks(const SiPixelCluster & cluster, const DetId & clusterID){ //devo passargli anche detset?

    std::map<int,SiPixelCluster> output;

    int minPixelRow = cluster.minPixelRow();
    int maxPixelRow = cluster.maxPixelRow();
    int minPixelCol = cluster.minPixelCol();
    int maxPixelCol = cluster.maxPixelCol();
    int dsl = 0; // number of digisimlinks

    // std::cout << "detID=" << (int)clusterID << std::endl;

    edm::DetSetVector<PixelDigiSimLink>::const_iterator isearch = pixeldigisimlink->find(clusterID);
    if (isearch != pixeldigisimlink->end()){
      // std::cout << "search ok" << std::endl;

       edm::DetSet<PixelDigiSimLink> digiLink = (*isearch);
       edm::DetSet<PixelDigiSimLink>::const_iterator linkiter = digiLink.data.begin();


        //create a vector for the track ids in the digisimlinks
       std::vector<int> simTrackIdV;
       simTrackIdV.clear();
       //create a vector for the new splittedClusters
       std::vector<SiPixelCluster> splittedCluster;
       splittedCluster.clear();

      for ( ; linkiter != digiLink.data.end(); linkiter++)
       { // loop over all digisimlinks
        //  std::cout << "inside for" << std::endl;

          dsl++;
          std::pair<int,int> pixel_coord = PixelDigi::channelToPixel(linkiter->channel());

           // is the digisimlink inside the cluster boundaries?
          if ( pixel_coord.first  <= maxPixelRow &&
              pixel_coord.first  >= minPixelRow &&
              pixel_coord.second <= maxPixelCol &&
              pixel_coord.second >= minPixelCol )
          {
              bool inStock(false); // did we see this simTrackId before?

              SiPixelCluster::PixelPos newPixelPos(pixel_coord.first, pixel_coord.second); // coordinates to the pixel

              //loop over the pixels from the cluster to get the charge in this pixel
              int newPixelCharge(0); //fraction times charge in the original cluster pixel

             const std::vector<SiPixelCluster::Pixel>& pixvector = (cluster).pixels();

             for(std::vector<SiPixelCluster::Pixel>::const_iterator itPix = pixvector.begin(); itPix != pixvector.end(); itPix++)
               {

                   if (((int) itPix->x) == ((int) pixel_coord.first)&&(((int) itPix->y) == ((int) pixel_coord.second)))
                     {

                          newPixelCharge = (int) (linkiter->fraction()*itPix->adc);

                     }
               }

              if ( newPixelCharge < 2500 ){
                // std::cout << "poca carica" <<std::endl;
                continue;
              }

              //add the pixel to an already existing cluster if the charge is above the threshold
              int clusVecPos = 0;
              std::vector<int>::const_iterator sTIter =  simTrackIdV.begin();

              for ( ; sTIter < simTrackIdV.end(); sTIter++)
                {

                    if (((*sTIter)== (int) linkiter->SimTrackId()))
                      {
                          inStock=true; // now we saw this id before
                            // 	  //		  std::cout << " adding a pixel to the cluster " << (int) (clusVecPos) <<std::endl;;
                            // 	  //		    std::cout << "newPixelCharge " << newPixelCharge << std::endl;;
                          splittedCluster.at(clusVecPos).add(newPixelPos,newPixelCharge); // add the pixel to the cluster

                          //-----debug lines -----//
                        //
                        //   if(linkiter->SimTrackId()==131) {
                        //     std::cout << "TRACK 131:" <<std::endl;
                        //     SiPixelCluster theCluster = SiPixelCluster(newPixelPos,newPixelCharge);
                        //     for(int i=0; i<theCluster.size();i++){
                        //     SiPixelCluster::Pixel pix = theCluster.pixel(i);
                        //     std::cout << "pixel x=" << pix.x << ", y=" << pix.y << ", adc=" << pix.adc<< std::endl;
                        //   }
                        // }


                     }
                    clusVecPos++;

                }

            //look if the splitted cluster was already made before, if not create one
            // std::cout << "pre instock" << std::endl;

            if ( !inStock )
              {
                  //		std::cout << "creating a new cluster " << std::endl;;
                simTrackIdV.push_back(linkiter->SimTrackId()); // add the track id to the vector
                // std::cout << "trackID in splitter=" << linkiter->SimTrackId() << std::endl;
                splittedCluster.push_back(SiPixelCluster(newPixelPos,newPixelCharge)); // add the cluster to the vector

                // //-----debug lines -----//
                // if(linkiter->SimTrackId()==131) {
                //   std::cout << "TRACK 131:" <<std::endl;
                //   SiPixelCluster theCluster = SiPixelCluster(newPixelPos,newPixelCharge);
                //   for(int i=0; i<theCluster.size();i++){
                //   SiPixelCluster::Pixel pix = theCluster.pixel(i);
                //   std::cout << "pixel x=" << pix.x << ", y=" << pix.y << ", adc=" << pix.adc<< std::endl;
                // }
                // }


              }
        }
      }

    //    std::cout << "will add clusters : simTrackIdV.size() " << simTrackIdV.size() << std::endl;;

     if ( ( ( (int)simTrackIdV.size() ) == 1 ) || cluster.size()==1 )
      {
        // std::cout << "size trackID o clustersize=1" << std::endl;
	       if(simTrackIdV.size()  == 1) {
         //	    cout << "putting in this cluster" << endl;
          //output.push_back(cluster);
          output[simTrackIdV.at(0)] = cluster;
          // std::cout << "size trackID=1" << std::endl;

        }
        //      std::cout << "cluster added " << output.size() << std::endl;;
      }
    else
     {
        //for (std::vector<SiPixelCluster>::const_iterator cIter = splittedCluster.begin(); cIter != splittedCluster.end(); cIter++ )
        //for(SiPixelCluster & clust : splittedCluster)
        // std::cout << "inside else" << std::endl;

        for(uint j=0; j<splittedCluster.size(); j++)
         {
            //output.push_back( (*cIter) );

            output[simTrackIdV.at(j)]=splittedCluster.at(j);
            // std::cout << "size cluser!=1, element=" << j << std::endl;


         }
    }

      simTrackIdV.clear();
      splittedCluster.clear();
    }//if (isearch != pixeldigisimlink->end())
    // std::cout << "arrivo a pre-return" << std::endl;

    return output;
  }

const GeomDet* NNPixSeedInput::DetectorSelector(int llay, const reco::Candidate& jet, GlobalVector jetDir, const reco::Vertex& jetVertex, const TrackerTopology* const tTopo, const PixelClusterParameterEstimator* pp, const auto & simtracksVector){

  struct trkNumCompare {
  bool operator()(std::pair<int,const GeomDet*> x, std::pair<int,const GeomDet*> y) const
  {return x.first > y.first;}
  };

  std::set<std::pair<int,const GeomDet*>, trkNumCompare> track4detSet;

  LocalPoint jetInter(0,0,0);
  // const GeomDet* globDet = (GeomDet*)0; //fuffa assigment to allow to compile
  // const GeomDetUnit* detUnit = (GeomDetUnit*)0; //fuffa assigment to allow to compile;

  // jet_pt = jet.pt();
  // jet_eta = jet.eta();
  // jet_phi = jet.phi();

  // const reco::Vertex& jetVertex = (*vertices)[0];
  // auto jetVert = jetVertex; //trackInfo filling
  // std::vector<std::map<int,SiPixelCluster>> clusterMapVector;

  edmNew::DetSetVector<SiPixelCluster>::const_iterator detIt = inputPixelClusters->begin();

  for (; detIt != inputPixelClusters->end(); detIt++) { //loop deset

    std::set<int> trkIDset;
    const edmNew::DetSet<SiPixelCluster>& detset = *detIt;
    const GeomDet* det = geometry_->idToDet(detset.id()); //lui sa il layer con cast a  PXBDetId (vedi dentro il layer function)
    for (auto cluster = detset.begin(); cluster != detset.end(); cluster++) { //loop cluster

      const SiPixelCluster& aCluster = *cluster;
      // det_id_type aClusterID= detset.id();
      auto aClusterID= detset.id();

      if(DetId(aClusterID).subdetId()!=1) continue;

      int lay = tTopo->layer(det->geographicalId());

      std::pair<bool, Basic3DVector<float>> interPair = findIntersection(jetDir,(reco::Candidate::Point)jetVertex.position(), det);

      if(interPair.first==false) continue;

      Basic3DVector<float> inter = interPair.second;

      auto localInter = det->specificSurface().toLocal((GlobalPoint)inter);

      // GlobalPoint pointVertex(jetVertex.position().x(), jetVertex.position().y(), jetVertex.position().z());

      // GlobalPoint cPos = det->surface().toGlobal(pp->localParametersV(aCluster,(*geometry_->idToDetUnit(detIt->id())))[0].first);
      LocalPoint cPos_local = pp->localParametersV(aCluster,(*geometry_->idToDetUnit(detIt->id())))[0].first;

      if(std::abs(cPos_local.x()-localInter.x())/pitchX<=jetDimX/2 && std::abs(cPos_local.y()-localInter.y())/pitchY<=jetDimY/2){ // per ora preso baricentro, da migliorare

        // fillPixelMatrix(aCluster,lay,localInter, det);
        if(lay==llay) {

          // if(jetInter.x()==0 && jetInter.y()==0 && jetInter.z()==0) jetInter = localInter; //filling infoTracks

          // if(globDet ==(GeomDet*)0){//filling infoTracks
          //    globDet = det;
          //    detUnit = geometry_->idToDetUnit(detIt->id());
          //  }

          // if(det!=globDet) continue;

          std::map<int,SiPixelCluster> splittedCluster = splitClusterInTracks(aCluster,aClusterID); //accesso/assegnazione splittedClister[id]=cluser
          // clusterMapVector.push_back(splittedCluster);
          for(std::map<int,SiPixelCluster>::iterator track_iter= splittedCluster.begin(); track_iter!=splittedCluster.end(); track_iter++){
            for(uint j=0; j<simtracksVector->size(); j++){
              SimTrack st = simtracksVector->at(j);
              if((int)st.trackId()==track_iter->first) {
                // std::cout << "1 track, det" << det << ", trackID="<< track_iter->first<< std::endl;
                trkIDset.insert(track_iter->first); //trackID
              }
            }
          //fillPixelTrackMap(track_iter->first, track_iter->second,lay,localInter, det);
          //aggiungere salvataggio info traccia (pt eta ecc) usando trackID
          }//tracks in cluster
      }
      } //cluster in ROI
    } //cluster
    int siz = trkIDset.size();
    // if(siz>0) std::cout << "SIZE=" << siz << std::endl;
    std::pair<int,const GeomDet*> track4det(siz, det);
    if(siz>0) track4detSet.insert(track4det);
  } //detset

  std::cout << "Selected det=" << track4detSet.begin()->second << ", trk number=" << track4detSet.begin()->first << std::endl;
  // for(std::set<std::pair<int,const GeomDet*>, trkNumCompare>::iterator track_iter= track4detSet.begin(); track_iter!=track4detSet.end(); track_iter++){
  //   std::cout << "det=" << track_iter->second << ", trk number=" << track_iter->first << std::endl;
  // }
  // std::cout << "---------" << std::endl;

  if(track4detSet.size()==0) return (GeomDet*)0;
  else return track4detSet.begin()->second;
}



//
// #ifdef THIS_IS_AN_EVENT_EXAMPLE
//    Handle<ExampleData> pIn;
//    iEvent.getByLabel("example",pIn);
// #endif
//
// #ifdef THIS_IS_AN_EVENTSETUP_EXAMPLE
//    ESHandle<SetupData> pSetup;
//    iSetup.get<SetupRecord>().get(pSetup);
// #endif




// ------------ method called once each job just before starting event loop  ------------
void
NNPixSeedInput::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void
NNPixSeedInput::endJob()
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
NNPixSeedInput::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(NNPixSeedInput);
