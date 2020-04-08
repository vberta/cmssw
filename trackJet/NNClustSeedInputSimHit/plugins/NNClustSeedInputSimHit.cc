// -*- C++ -*-
//
// Package:    trackJet/NNClustSeedInputSimHit
// Class:      NNClustSeedInputSimHit
//
/**\class NNClustSeedInputSimHit NNClustSeedInputSimHit.cc trackJet/NNClustSeedInputSimHit/plugins/NNClustSeedInputSimHit.cc

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
#include "SimDataFormats/TrackingHit/interface/PSimHit.h"

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

#include "SimG4Core/Notification/interface/G4SimTrack.h"
#include "SimDataFormats/Track/interface/SimTrack.h"

// #include "SimDataFormats/Vertex/interface/SimVertex.h"


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

class NNClustSeedInputSimHit : public edm::one::EDProducer<edm::one::SharedResources>  {
   public:
      explicit NNClustSeedInputSimHit(const edm::ParameterSet&);
      ~NNClustSeedInputSimHit();

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

  TFile* NNClustSeedInputSimHit_out;
  TTree* NNClustSeedInputSimHitTree;
  static const int jetDimX =30;//30
  static const int jetDimY =30;//30
  static const int Nlayer =7;//4;
  static const int Ntrack = 100;
  static const int Npar = 5; //added 1/pt
  static const int Nover = 3;
  static const int NClust = 5;
  double clusterMeas[jetDimX][jetDimY][Nlayer];
  double trackPar[jetDimX][jetDimY][Nover][Npar+1]; //NOFLAG
  double trackProb[jetDimX][jetDimY][Nover];
  double clusterSplit[Ntrack][Nlayer][jetDimX][jetDimY];
  double track_pt[Ntrack] = {0.0};
  double track_pz[Ntrack] = {0.0};
  double track_eta[Ntrack] = {0.0};
  double track_phi[Ntrack] = {0.0};
  double jet_pt;
  double jet_p;
  double jet_eta;
  double jet_phi;
  double jet_Ntrack = 0;
  // int NPixL4=0;
  // int NPixL5=0;
  // int NPixL6=0;
  int NPixLay[Nlayer] = {0};


  int eventID;

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
  // edm::EDGetTokenT<std::vector<SimVertex> > simvertexToken;
  edm::EDGetTokenT<std::vector<PSimHit> > PSimHitToken;
  edm::Handle<std::vector<PSimHit> > simhits;
  edm::EDGetTokenT<std::vector<PSimHit> > PSimHitECToken;
  edm::Handle<std::vector<PSimHit> > simhitsEC;



  std::map<int, double [Nlayer][jetDimX][jetDimY]> trackMap;

  double ptMin_;
  double deltaR_;
  double chargeFracMin_;
  double centralMIPCharge_;
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

  void fillTrackInfo(const reco::Candidate&, const auto &, auto, auto, auto, const GeomDet*, const PixelClusterParameterEstimator*, std::vector<PSimHit>, const TrackerTopology* const);

  const GeomDet* DetectorSelector(int ,const reco::Candidate& jet, GlobalVector,  const reco::Vertex& jetVertex, const TrackerTopology* const, const PixelClusterParameterEstimator*, const auto &);

  std::vector<GlobalVector> splittedClusterDirections(const reco::Candidate&, const TrackerTopology* const, auto pp, const reco::Vertex& jetVertex, int );


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
NNClustSeedInputSimHit::NNClustSeedInputSimHit(const edm::ParameterSet& iConfig) :

      vertices_(consumes<reco::VertexCollection>(iConfig.getParameter<edm::InputTag>("vertices"))),
      pixelClusters_(consumes<edmNew::DetSetVector<SiPixelCluster> >(iConfig.getParameter<edm::InputTag>("pixelClusters"))),
      pixeldigisimlinkToken(consumes< edm::DetSetVector<PixelDigiSimLink> >(edm::InputTag("simSiPixelDigis"))),
      cores_(consumes<edm::View<reco::Candidate> >(iConfig.getParameter<edm::InputTag>("cores"))),
      simtracksToken(consumes<std::vector<SimTrack> >(iConfig.getParameter<edm::InputTag>("simTracks"))),
      // simvertexToken(consumes<std::vector<SimVertex> >(iConfig.getParameter<edm::InputTag>("simVertex"))),
      PSimHitToken(consumes<std::vector<PSimHit> >(iConfig.getParameter<edm::InputTag>("simHit"))),
      PSimHitECToken(consumes<std::vector<PSimHit> >(iConfig.getParameter<edm::InputTag>("simHitEC"))),
      ptMin_(iConfig.getParameter<double>("ptMin")),
      deltaR_(iConfig.getParameter<double>("deltaR")),
      chargeFracMin_(iConfig.getParameter<double>("chargeFractionMin")),
      centralMIPCharge_(iConfig.getParameter<double>("centralMIPCharge")),
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
  // NNClustSeedInputSimHitTree= new TTree("NNClustSeedInputSimHitTree","NNClustSeedInputSimHitTree");
   NNClustSeedInputSimHitTree= fileService->make<TTree>("NNClustSeedInputSimHitTree","NNClustSeedInputSimHitTree");
  //  NNClustSeedInputSimHitTree->SetAutoFlush(10000);
   NNClustSeedInputSimHitTree->Branch("cluster_measured",clusterMeas,"cluster_measured[30][30][7]/D");
   NNClustSeedInputSimHitTree->Branch("trackPar", trackPar, "trackPar[30][30][3][6]/D"); //NOFLAG
   NNClustSeedInputSimHitTree->Branch("trackProb", trackProb, "trackProb[30][30][3]/D");
  //  NNClustSeedInputSimHitTree->Branch("cluster_splitted",clusterSplit,"cluster_splitted[100][4][100][100]/D");
   NNClustSeedInputSimHitTree->Branch("jet_eta",&jet_eta);
   NNClustSeedInputSimHitTree->Branch("jet_pt",&jet_pt);
   NNClustSeedInputSimHitTree->Branch("jet_p",&jet_p);
   NNClustSeedInputSimHitTree->Branch("jet_phi",&jet_phi);
   NNClustSeedInputSimHitTree->Branch("jet_Ntrack",&jet_Ntrack);
   NNClustSeedInputSimHitTree->Branch("track_pt",track_pt,"track_pt[100]/D");
   NNClustSeedInputSimHitTree->Branch("track_pz",track_pz,"track_pz[100]/D");
   NNClustSeedInputSimHitTree->Branch("track_eta",track_eta,"track_eta[100]/D");
   NNClustSeedInputSimHitTree->Branch("track_phi",track_phi,"track_phi[100]/D");
   NNClustSeedInputSimHitTree->Branch("event_ID",&eventID);

   //debug branches
   NNClustSeedInputSimHitTree->Branch("NPixLay",NPixLay, "NPixLay[7]/I");
   // NNClustSeedInputSimHitTree->Branch("NPixL5",&NPixL5);
   // NNClustSeedInputSimHitTree->Branch("NPixL6",&NPixL6);



   // //sto usando fileservice quindi non servono in fondo
   // //pxdMap_out->cd();
   // //NNClustSeedInputSimHitTree->Write();
   // //pxdMap_out->Close();


   /// dichiarare cosa produce  produces<asd
     for(int i=0; i<Nlayer; i++){ //NOFLAG
       for(int j=0; j<jetDimX; j++){
         for(int k=0; k<jetDimY; k++){
           if(j<jetDimX && k<jetDimY && i< Nlayer) clusterMeas[j][k][i] = 0.0;
           for(int m=0; m<Nover; m++){
             if(j<jetDimX && k<jetDimY && i< Npar+1 && m<Nover) trackPar[j][k][m][i] =0.0;
             if(j<jetDimX && k<jetDimY && m<Nover) trackProb[j][k][m] =0.0;
           }
         }
       }
     }


}


NNClustSeedInputSimHit::~NNClustSeedInputSimHit()
{

   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called for each event  ------------
#define foreach BOOST_FOREACH


void NNClustSeedInputSimHit::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{

  evt_counter++;
  std::cout << "event number (iterative)=" << evt_counter<< ", event number (id)="<< iEvent.id().event() << std::endl;


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
  //
  // edm::Handle<std::vector<SimVertex> > simvertex;
  // iEvent.getByToken(simvertexToken, simvertex);

  Handle<std::vector<reco::Vertex> > vertices;
  iEvent.getByToken(vertices_, vertices);
  //const reco::Vertex& pv = (*vertices)[0];

  iEvent.getByToken(PSimHitToken, simhits);
  iEvent.getByToken(PSimHitECToken, simhitsEC);


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
  int jet_number = 0;
  std::cout << " ---------------------NEW EVENT: N of jets in the event =" << cores->size() << std::endl;
  std::cout << "THIS IS A ENDCAP-ONLY TRAINING NTUPLE!!!!"<< std::endl;






  for (unsigned int ji = 0; ji < cores->size(); ji++) { //loop jet
    // continue;
    jet_number++;

    // if(iEvent.id().event()!=4807889) continue;


    if(std::abs((*cores)[ji].eta())<1.4 || std::abs((*cores)[ji].eta())>2.1) continue; //TRAINING ON ENDCAP ONLY;//DEBUGGGG
    std:: cout << "good eta!" << (*cores)[ji].eta()<< ", p="<< (*cores)[ji].p()  << std::endl;
    if ((*cores)[ji].p() > ptMin_ ) { //NB: the cut is on PT!!!, if you want p-->(*cores)[ji].p()
      // std::cout << " __________________________________________________________" <<std::endl;
       std::cout << "|____________________NEW JET_______________________________| jet number=" << jet_number  << ", pt= "<< (*cores)[ji].pt() << ", eta=" << (*cores)[ji].eta() << std::endl;

      //
      // std::cout << "jet number " << jetnum << std::endl;
      //if(ji==1) print = true;
      //  if(print2)std::cout << "|____________________NEW JET_______________________________|" <<std::endl;
      if(std::abs((*cores)[ji].eta())>1.4) std::cout << "ENDCAP JET, eta="<<(*cores)[ji].eta() << std::endl;
      else std::cout << "BARREL JET, eta="<<(*cores)[ji].eta() << std::endl;

      const reco::Candidate& jet = (*cores)[ji];
      const reco::Vertex& jetVertex = (*vertices)[0];
      GlobalVector jetDirection(jet.px(), jet.py(), jet.pz());

      // // DEBUGG LINES /////
      // jet_pt = jet.pt();
      // jet_p = jet.p();
      // jet_eta = jet.eta();
      // jet_phi = jet.phi();
      // eventID= iEvent.id().event();
      // NNClustSeedInputSimHitTree->Fill();
      // continue;
      // END OF DEBUGGGG///////

      std::vector<GlobalVector> splitClustDirSet = splittedClusterDirections(jet, tTopo, pp, jetVertex, 1);
      std::cout << "numero of cluster da splittare:" << splitClustDirSet.size() << "+jetDir" << std::endl;
      if(splitClustDirSet.size()==0) {//if layer 1 is broken find direcitons on layer 2
        splitClustDirSet = splittedClusterDirections(jet, tTopo, pp, jetVertex, 2);
        std::cout << "split on lay2, in numero=" << splitClustDirSet.size() << "+jetDir" << std::endl;
      }
      splitClustDirSet.push_back(jetDirection);

      for(int cc=0; cc<(int)splitClustDirSet.size(); cc++){
      int counterPX=0;
      // NPixL4=0;
      // NPixL5=0;
      // NPixL6=0;
      for(int lp=0; lp<Nlayer; lp++) NPixLay[lp] = 0;



      GlobalVector bigClustDir = splitClustDirSet.at(cc);

      std::set<int> trkIDset;
      LocalPoint jetInter(0,0,0);
      // const GeomDet* globDet = (GeomDet*)0; //fuffa assigment to allow to compile

      const auto & simtracksVector = simtracks.product();
      // const auto & simvertexVector = simvertex.product();

      jet_pt = jet.pt();
      jet_p = jet.p();
      jet_eta = jet.eta();
      jet_phi = jet.phi();
      eventID= iEvent.id().event();
      // std::cout <<"pt="<< jet_pt <<",   p="<< jet_p << ", eta=" << jet_eta << std::endl;


      // GlobalVector jetDir(jet.px(), jet.py(), jet.pz());

      //GlobalVector jetVertex(jet.vertex());

      auto jetVert = jetVertex; //trackInfo filling


      std::vector<std::map<int,SiPixelCluster>> clusterMapVector;
      std::vector<PSimHit> goodSimHit;
      // const GeomDetUnit* detUnit = (GeomDetUnit*)0; //fuffa assigment to allow to compile;

      // std::cout << "jetdirection=" << jetDir << std::endl;
      // jetDir=recenter(jet, jetDir, jetVertex, tTopo, pp);
      // std::cout << "jetdirection corrected=" << jetDir << std::endl;
      //reco::Candidate::Point jetVertex = jet.vertex(); //probably equivalent

      edmNew::DetSetVector<SiPixelCluster>::const_iterator detIt = inputPixelClusters->begin();
      // std::cout << "DEBUG 1, pre detsel" << std::endl;

      const GeomDet* globDet = DetectorSelector(2, jet, bigClustDir, jetVertex, tTopo,pp, simtracksVector); //select detector mostly hitten by the jet
      // if(globDet == 0) continue;
      // const GeomDet* goodDet1 = DetectorSelector(1, jet, bigClustDir, jetVertex, tTopo,pp, simtracksVector);
      // const GeomDet* goodDet3 = DetectorSelector(3, jet, bigClustDir, jetVertex, tTopo,pp, simtracksVector);
      // const GeomDet* goodDet4 = DetectorSelector(4, jet, bigClustDir, jetVertex, tTopo,pp, simtracksVector);

      //fill the good det vector
      std::vector<const GeomDet*> goodDets;
      for(int l=1; l<8; l++){
        // std::cout << "DEBUG 1.5, inside pre detsel, l=" << l<<std::endl;

        const GeomDet* goodDet = DetectorSelector(l, jet, bigClustDir, jetVertex, tTopo,pp, simtracksVector);
        // std::cout << "layer=" << l << " det="<< goodDet << std::endl;
        goodDets.push_back(goodDet);
        // std::cout << "DEBUG 1.5, inside post detsel, l=" << l<<std::endl;

      }

      // std::cout << "DEBUG 2, post detsel" << std::endl;


      for (; detIt != inputPixelClusters->end(); detIt++) { //loop deset
        //edmNew::DetSetVector<SiPixelCluster>::FastFiller filler(*output,detIt->id()); //A CHE SERVE?
        const edmNew::DetSet<SiPixelCluster>& detset = *detIt;
        const GeomDet* det = geometry_->idToDet(detset.id()); //lui sa il layer con cast a  PXBDetId (vedi dentro il layer function)
        //std::cout << "detset size = " << detset.size() << std::endl;
        // if(det!=globDet) continue;

        bool goodDetBool = false;
        for(int l=0; l<(int)goodDets.size(); l++){
          if(goodDets.at(l)==det) goodDetBool = true;
        }

        for (auto cluster = detset.begin(); cluster != detset.end(); cluster++) { //loop cluster
          // std::cout << " ---- new cluster ----" << std::endl;

          const SiPixelCluster& aCluster = *cluster;
          det_id_type aClusterID= detset.id();

          // if(aClusterID.subdetId()!=1) continue;
          // if(DetId(aClusterID).subdetId()!=1) continue; #select only  barrel clusters

          // PXBDetId detPX = (PXBDetId)detset.id();
          //int lay = detPX.layer();
          int lay = tTopo->layer(det->geographicalId());
          // std::cout << "lay" << lay << ", subdetID="<< det->geographicalId().subdetId() << ", Endcap detID=" << PixelSubdetector::PixelEndcap << std::endl;
          if(det->geographicalId().subdetId()==PixelSubdetector::PixelEndcap) {
            lay=lay+4; //endcap layer counting = 5,6,7
            // std::cout << ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>endcap layer"<< lay << std::endl;
            }

          std::pair<bool, Basic3DVector<float>> interPair = findIntersection(bigClustDir,(reco::Candidate::Point)jetVertex.position(), det);

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
            auto deltaR_glob = Geom::deltaR(bigClustDir, intersectionDir);
            GlobalVector clusterDir = cPos - pointVertex;
            auto deltaR_clust = Geom::deltaR(bigClustDir, clusterDir);
        //end of =.=

          //--------------------------end---------------------//

          // if(lay>4) std::cout << "layer" << lay << "  cPos_local.x()-localInter.x()/pitchX" << cPos_local.x()-localInter.x()/pitchX << "   cPos_local.y()-localInter.y())/pitchY" << cPos_local.y()-localInter.y()/pitchY<<std::endl;
          if(std::abs(cPos_local.x()-localInter.x())/pitchX<=jetDimX/2 && std::abs(cPos_local.y()-localInter.y())/pitchY<=jetDimY/2){ // per ora preso baricentro, da migliorare
            if(lay>4) {
              counterPX++;
            //   if(lay==5) NPixL4++;
            //   if(lay==6) NPixL5++;
            //   if(lay==7) NPixL6++;
              }
            NPixLay[lay-1]= NPixLay[lay-1]+1;
            // std::cout <<"npixlay=" <<NPixLay[lay-1] << ", l="<<lay << std::endl;
            // if(det==goodDet1 || det==goodDet3 || det==goodDet4 || det==globDet)
            if(goodDetBool) {
              // std::cout << ">>>>>>>>>>>>>>>>>>>>>>>> Another Det, det==" << det << "layer=" << lay <<std::endl;

              // if(lay>4) std::cout << ">>>>>>>>>>>>>>>>>>>>>>>> DEBUGG --- layer=" << lay << std::endl;
              fillPixelMatrix(aCluster,lay,localInter, det);
              }

            if(lay==2 && det==globDet) {

              // if(globDet ==(GeomDet*)0){//filling infoTracks
                //  globDet = det;
              // detUnit = geometry_->idToDetUnit(detIt->id());
              //  }

              // if(det!=globDet) continue;
              // std::cout << "DEBUG 5, inside lay2" << std::endl;

              std::map<int,SiPixelCluster> splittedCluster = splitClusterInTracks(aCluster,aClusterID); //accesso/assegnazione splittedClister[id]=cluser
              clusterMapVector.push_back(splittedCluster);//(non è davvero usato questo, è old)
              // for(uint sh=0; sh<simhits->size(); sh++){ //CAMBIARE QUI E METTERE DOPO
              //   for(std::map<int,SiPixelCluster>::iterator track_iter= splittedCluster.begin(); track_iter!=splittedCluster.end(); track_iter++){
              //     if((*simhits)[sh].trackId()==(uint)track_iter->first){
              //       goodSimHit.push_back((*simhits)[sh]);
              //     }
              //   }
              // }
              for(std::map<int,SiPixelCluster>::iterator track_iter= splittedCluster.begin(); track_iter!=splittedCluster.end(); track_iter++){ //not rused:old implementation
                trkIDset.insert(track_iter->first); //trackID
                fillPixelTrackMap(track_iter->first, track_iter->second,lay,localInter, det);
                // std::cout << "DEBUG 6, post fill pixeltrakcpmap" << std::endl;

                //aggiungere salvataggio info traccia (pt eta ecc) usando trackID
              }//tracks in cluster
          }
          }
          // else {if(lay>4) std::cout << "FAIL" << std::endl;} //cluster in ROI
        } //cluster
      } //detset


      // ------------------------  good sim hit selection (hit inside window) --------------------------------------//
      std::vector<PSimHit> simhitsALL;
      std::vector<PSimHit>::const_iterator shItB = simhits->begin();
      for (; shItB != simhits->end(); shItB++) { //loop on simit to find correspondent det (barrel)
        simhitsALL.push_back((*shItB));
      }
      // std::vector<PSimHit>::const_iterator shItEC = simhitsEC->begin();
      // for (; shItEC != simhitsEC->end(); shItEC++) { //loop on simit to find correspondent det (endCaps)
      //   simhitsALL.push_back((*shItEC));
      // }

      std::vector<PSimHit>::const_iterator shIt = simhitsALL.begin();
      // std::set<const GeomDet*> simhitsDetSet;
      for (; shIt != simhitsALL.end(); shIt++) { //loop deset
        // const edmNew::DetSet<PSimHit>& detset = *shIt;
        const GeomDet* det = geometry_->idToDet((*shIt).detUnitId());
        // if(det!=goodDet1 && det!=goodDet3 && det!=goodDet4 && det!=globDet) continue;
        if(det!=globDet) continue;
        std::pair<bool, Basic3DVector<float>> interPair = findIntersection(bigClustDir,(reco::Candidate::Point)jetVertex.position(), det);
        if(interPair.first==false) continue;
        Basic3DVector<float> inter = interPair.second;
        auto localInter = det->specificSurface().toLocal((GlobalPoint)inter);
        if(jetInter.x()==0 && jetInter.y()==0 && jetInter.z()==0) jetInter = localInter; //filling infoTracks

        // int flip = pixelFlipper(det);
        if(std::abs(((*shIt).localPosition()).x()-localInter.x())/pitchX<=jetDimX/2 && std::abs(((*shIt).localPosition()).y()-localInter.y())/pitchY<=jetDimY/2){
          // std::cout << "good sim hit on MAIN LAYER,  track ID" << (*shIt).trackId()<< std::endl;
          goodSimHit.push_back((*shIt));

        }
      }


      //------ DEBUG ENDCAP ------------------------//
      std::vector<PSimHit> goodSimHitEC;
      std::vector<PSimHit>::const_iterator shItEC = simhitsEC->begin();
      for (; shItEC != simhitsEC->end(); shItEC++) { //loop deset
        // const edmNew::DetSet<PSimHit>& detset = *shItEC;
        const GeomDet* det = geometry_->idToDet((*shItEC).detUnitId());
        // if(det!=goodDet1 && det!=goodDet3 && det!=goodDet4 && det!=globDet) continue;
        bool goodDetBoolEC = false;
        for(int l=0; l<(int)goodDets.size(); l++){
          if(goodDets.at(l)==det) {
          goodDetBoolEC = true;
          // std::cout <<  "layer ok="<< l+1 << std::endl;
          }
        }
        // if(det!=goodDets.at(6)) continue;
        if(goodDetBoolEC==false) continue;
        std::pair<bool, Basic3DVector<float>> interPair = findIntersection(bigClustDir,(reco::Candidate::Point)jetVertex.position(), det);
        if(interPair.first==false) continue;
        Basic3DVector<float> inter = interPair.second;
        auto localInter = det->specificSurface().toLocal((GlobalPoint)inter);
        if(jetInter.x()==0 && jetInter.y()==0 && jetInter.z()==0) jetInter = localInter; //filling infoTracks

        // int flip = pixelFlipper(det);
        if(std::abs(((*shItEC).localPosition()).x()-localInter.x())/pitchX<=jetDimX/2 && std::abs(((*shItEC).localPosition()).y()-localInter.y())/pitchY<=jetDimY/2){
          int lay = tTopo->layer(det->geographicalId());
          if(det->geographicalId().subdetId()==PixelSubdetector::PixelEndcap) lay=lay+4;
          // std::cout << "good sim hit on lay=" <<lay << ", track ID="<<(*shItEC).trackId()<< std::endl;

          goodSimHitEC.push_back((*shItEC));
        }
      }
      // std::cout <<  "=====================================================>>counting numer of good hits" << goodSimHitEC.size();

      // const auto & simtracksVector2 = simtracks.product();
      //   for(uint j=0; j<simtracksVector2->size(); j++){
      //     for(std::vector<PSimHit>::const_iterator it=simhitsEC->begin(); it!=simhitsEC->end(); ++it) {
      //       SimTrack st = simtracksVector2->at(j);
      //       if(st.trackId()==(*it).trackId()) {
      //         const GeomDet* det = geometry_->idToDet((*it).detUnitId());
      //         int lay = tTopo->layer(det->geographicalId());
      //         if(det->geographicalId().subdetId()==PixelSubdetector::PixelEndcap) {
      //           lay=lay+4; //endcap layer counting = 5,6,7
      //           std::cout << "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!endcap layer"<< lay << "   det" << det->gdetIndex() << std::endl;
      //           }
      //         // else  std::cout << "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!barrel layer"<< lay << "   det" << det->gdetIndex() << std::endl;
      //
      //       }
      //     }
      //
      //   }







        //------ DEBUG ENDCAP ------------------------//




      // ------------------------  End good sim hit selection --------------------------------------//
      // std::cout << "size sim hit in window" << goodSimHit.size() << std::endl;

    // int lay = tTopo->layer(globDet->geographicalId());
    // std::cout << "layer filled=" << lay << std::endl;
    // if(globDet == 0) continue;
    // std::cout << "DEBUG 7, pre filltrakcinfo" << std::endl;

    //debug endcap ------

    // std::vector<PSimHit> simhitsEC_copy;
    //
    // std::vector<PSimHit>::const_iterator shItEC = simhitsEC->begin();
    // for (; shItEC != simhitsEC->end(); shItEC++) { //loop on simit to find correspondent det (endCaps)
    //   simhitsEC_copy.push_back((*shItEC));
    // }
    //end of debug endcap ------

    fillTrackInfo(jet, simtracksVector, jetInter, bigClustDir, jetVert, globDet, pp, goodSimHit,tTopo);
    // std::cout << "DEBUG 8, post filltrakcinfo" << std::endl;



    clusterMapVector.clear();
    NNClustSeedInputSimHitTree->Fill();
    std::cout << "FILL!" << std::endl;
    std::cout << ">>> counterPX_EC=" <<counterPX << ", 0=" <<NPixLay[0] << ", 1=" <<NPixLay[1] <<", 2=" <<NPixLay[1] << ", 3=" <<NPixLay[2]<<", 4=" <<NPixLay[4] <<", 5=" <<NPixLay[5] << ", 6=" <<NPixLay[6]<<std::endl;



    for(int i=0; i<Nlayer; i++){
      for(int j=0; j<jetDimX; j++){
        for(int k=0; k<jetDimY; k++){
          if(j<jetDimX && k<jetDimY && i< Nlayer) clusterMeas[j][k][i] = 0.0;
          for(int m=0; m<Nover; m++){
            if(trackPar[j][k][m][i]!=0 && j<jetDimX && k<jetDimY && i< Npar+1 && m<Nover) trackPar[j][k][m][i] =0.0; //NOFLAG
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
  } //bigcluster
  } //jet > pt
 } //jet
//  print = false;
trackMap.clear();
}













  std::pair<bool, Basic3DVector<float>> NNClustSeedInputSimHit::findIntersection(const GlobalVector & dir,const  reco::Candidate::Point & vertex, const GeomDet* det){
     StraightLinePlaneCrossing vertexPlane(Basic3DVector<float>(vertex.x(),vertex.y(),vertex.z()), Basic3DVector<float>(dir.x(),dir.y(),dir.z()));

     std::pair<bool, Basic3DVector<float>> pos = vertexPlane.position(det->specificSurface());

     return pos;
  }



  std::pair<int,int> NNClustSeedInputSimHit::local2Pixel(double locX, double locY, const GeomDet* det){
    LocalPoint locXY(locX,locY);
    float pixX=(dynamic_cast<const PixelGeomDetUnit*>(det))->specificTopology().pixel(locXY).first;
    float pixY=(dynamic_cast<const PixelGeomDetUnit*>(det))->specificTopology().pixel(locXY).second;
    std::pair<int, int> out(pixX,pixY);
    return out;
  }

  LocalPoint NNClustSeedInputSimHit::pixel2Local(int pixX, int pixY, const GeomDet* det){
    float locX=(dynamic_cast<const PixelGeomDetUnit*>(det))->specificTopology().localX(pixX);
    float locY=(dynamic_cast<const PixelGeomDetUnit*>(det))->specificTopology().localY(pixY);
    LocalPoint locXY(locX,locY);
    return locXY;
  }

  int NNClustSeedInputSimHit::pixelFlipper(const GeomDet* det){
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


  GlobalVector NNClustSeedInputSimHit::recenter(const reco::Candidate& jet, GlobalVector dir, const reco::Vertex& jetVertex, const TrackerTopology* const tTopo, const PixelClusterParameterEstimator* pp){

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


  void NNClustSeedInputSimHit::fillPixelMatrix(const SiPixelCluster & cluster, int layer, auto inter, const GeomDet* det){
    // if(print){std::cout << "----- cluster filled-------" << std::endl;
    // std::cout << "cluser layer" << layer << std::endl;}
     if(layer==1 && 0){std::cout << "--------new cluster----------cluster size=" <<cluster.size() <<std::endl;
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
        if(nx<jetDimX && ny<jetDimY && layer-1< Nlayer && layer-1>=0 && nx>=0 && ny>=0) clusterMeas[nx][ny][layer-1] += (pix.adc)/(float)(14000);

        if(layer>4 && 0){std::cout << "x position pixel " << nx-jetDimX/2 <<std::endl;
        std::cout << "y position pixel " << ny-jetDimY/2 <<std::endl;
        std::cout << "charge " << pix.adc <<std::endl;}

        if(layer>4 && 0){std::cout << "---------INPUT debug -------- det=" <<det->gdetIndex()<< ", layer="<< layer<< std::endl;
        std::cout<< "x=" << nx << ", y=" << ny << "("<<nx-jetDimX/2 << ", " << ny-jetDimY/2 << ")" << std::endl;
        std::cout << "jetInter X="<< pixInter.first <<", Y=" << pixInter.second << std::endl;
        std::cout << "trkInter X="<< pix.x <<", Y=" << pix.y << std::endl;
      }
      }
    }

  }

  void NNClustSeedInputSimHit::fillPixelTrackMap(int trackID, const SiPixelCluster & cluster, int layer, auto inter, const GeomDet* det){

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

  void NNClustSeedInputSimHit::fillPixelTrackMatrix(const std::vector<SimTrack>* const & stVector){
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




  void NNClustSeedInputSimHit::fillTrackInfo(const reco::Candidate& jet, const auto & stVector, auto jti, auto jetDir, auto jVert, const GeomDet* det, const PixelClusterParameterEstimator* cpe,  std::vector<PSimHit> goodSimHit, const TrackerTopology* const tTopo){

    bool oneHitInfo = false;

    struct trkInfoObj
    {
      int prob;
      double dist;
      double xpos;
      double ypos;
      double xangle;
      double yangle;
      int zero_flag; //useful for CNN training only: 0 if x,y,eta,phi==0
      double one_over_pt;
      // double jEta;
      // double jPt;
      // double xdist;
      // double ydist;
      // double trknum;
      trkInfoObj(int pp, double dd, double xx, double yy, double tx, double ty, int zf, double ptInv) : //, double jeta, double jpt) : // double xd, double yd, double n) :
        prob(pp),
        dist(dd),
        xpos(xx),
        ypos(yy),
        xangle(tx),
        yangle(ty),
        zero_flag(zf),
        one_over_pt(ptInv) {}
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
  //  std::vector<SimVertex> goodSimVtx;



    int trk =0;
    for(uint j=0; j<stVector->size(); j++){ //matched tracks selection and vertex assigment
      for(std::vector<PSimHit>::const_iterator it=goodSimHit.begin(); it!=goodSimHit.end(); ++it) {
        SimTrack st = stVector->at(j);
        if(st.trackId()==(*it).trackId()) {
          // std::cout << "matched track " << st.trackId() << std::endl;
          // if(st.momentum().Pt()>100){
          if(st.momentum().Pt()<1 or st.momentum().Pt()>100000) continue; //Pt CUT ON TRACKS!!!!!!!! (1 GeV)
          goodSimTrk.push_back(st);
          // for(uint v =0; v<svVector->size(); v++) {
          //   SimVertex sv = svVector->at(v);
          //   if((int)sv.vertexId()==(int)st.vertIndex()){
          //     // if(st.vertIndex()==-1) goodSimVtx.push_back((SimVertex)jVert);
          //     //else
          //      goodSimVtx.push_back(sv);
          //   }
          // }
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

    //debugging for endcap------------------------
    for(uint j=0; j<goodSimTrk.size(); j++){
      SimTrack st = goodSimTrk.at(j);
      for(std::vector<PSimHit>::const_iterator it=simhitsEC->begin(); it!=simhitsEC->end(); ++it) {
        if(st.trackId()==(*it).trackId()){
          // const GeomDet* det = *detIt;

          const GeomDet* det = geometry_->idToDet((*it).detUnitId());
          int layy = tTopo->layer(det->geographicalId());
          if(det->geographicalId().subdetId()==PixelSubdetector::PixelEndcap) {
            layy=layy+4; //endcap layer counting = 5,6,7
          }
          int detIID = det->gdetIndex();
          // std::cout << "track ID=" << st.trackId() << ", layer=" << layy << ", detID=" << detIID << std::endl;
        }
      }
    }
    //end of debuggin for endcap------------------------


    // std::cout << "New Info filling, track Number="<< goodSimTrk.size() << " det=" << det << std::endl;
    for(int x=0; x<jetDimX; x++){
      for(int y=0; y<jetDimY; y++){
        // int flipp= pixelFlipper(det); //-----LINEA DEMMERDA INCRIMINATA
        // std::cout << flipp << std::endl;
        // flipp=-1;
        // LocalPoint Jinter(flipp*jti.x(),jti.y(),jti.z());
        // if (evt_counter==9 && ((jet_pt-2001)<3))std::cout << "x=" << x << ", y=" << y << std::endl;
        // std::vector<double *> tracksInfo
        std::vector<trkInfoObj> tracksInfo;
        for(uint j=0; j<goodSimTrk.size(); j++){
          // std::cout << "IN THE LOOP ---------------------------------------- O_O_O_O_" << std::endl;
          // if (evt_counter==9 && ((jet_pt-2001)<3))std::cout << "------------------------------:track,x,y" << x << y << std::endl;
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
          // SiPixelCluster theCluster;
          // for(uint t=0; t<clusterVector.size(); t++){
          //   for(std::map<int,SiPixelCluster>::iterator track_iter= clusterVector.at(t).begin(); track_iter!=clusterVector.at(t).end(); track_iter++){
          //     if(track_iter->first==(int)st.trackId()){
          //       theCluster = track_iter->second;
          //     }
          //   }
          //
          // }

          PSimHit theSimHit;
          for(uint sh=0; sh<goodSimHit.size(); sh++){
            if(goodSimHit[sh].trackId()==st.trackId() && (int)goodSimHit[sh].detUnitId()==(int)det->geographicalId()){
              theSimHit = goodSimHit[sh];
              // if (evt_counter==9 && ((jet_pt-2001)<3)) std::cout << "found: detsimHit="<<goodSimHit[sh].detUnitId() << " detID_layer2=" << (int)det->geographicalId()  << std::endl;
              // if (evt_counter==9 && ((jet_pt-2001)<3)) std::cout << "found: detsimHit="<<goodSimHit[sh].detUnitId() << " trackID=" << st.trackId() << std::endl;
            }
          }

          //LocalPoint localTrkInter = std::get<0>(cpe->getParameters(theCluster,*detUnit));
          // LocalPoint localTrkInter_cpe(flip*(std::get<0>(cpe->getParameters(theCluster,*detUnit))).x(),(std::get<0>(cpe->getParameters(theCluster,*detUnit))).y(),(std::get<0>(cpe->getParameters(theCluster,*detUnit))).z());

          LocalPoint localTrkInter(flip*(theSimHit.localPosition()).x(),(theSimHit.localPosition()).y(),(theSimHit.localPosition()).z());

          //std::cout << "simHitPoint=" << localTrkInter << ", cpe_point=" << localTrkInter_cpe << std::endl;

          // localTrkInter = flip*localTrkInter;
          // Jinter = flip*Jinter;
          LocalPoint Jinter(flip*jti.x(),jti.y(),jti.z());


          std::pair<int,int> pixJInter = local2Pixel(Jinter.x(),Jinter.y(),det);
          std::pair<int,int> pixTrkInter = local2Pixel(localTrkInter.x(),localTrkInter.y(),det); //ADDED PITCH

          int pixX = (pixTrkInter.first-pixJInter.first);
          int pixY = (pixTrkInter.second-pixJInter.second);

          // if (evt_counter==9 && ((jet_pt-2001)<3)) std::cout << "localTrkInter=" << localTrkInter << ", Jinter=" << Jinter << ", pixJInter=" << pixJInter << ", pixTrkInter" << pixTrkInter <<std:endl;

          // if (evt_counter==9 && ((jet_pt-2001)<3)) std::cout << "Jinter.x()=" << Jinter.x() << ",Jinter.y()=" << Jinter.y();
          // if (evt_counter==9 && ((jet_pt-2001)<3)) std::cout << ", localTrkInter.x()=" << localTrkInter.x() << ",localTrkInter.y()=" << localTrkInter.y();
          // if (evt_counter==9 && ((jet_pt-2001)<3)) std::cout << ", pixel Xj=" << pixJInter.first ;
          // if (evt_counter==9 && ((jet_pt-2001)<3)) std::cout << ", pixel Xtrk=" << pixTrkInter.first ;
          // if (evt_counter==9 && ((jet_pt-2001)<3)) std::cout << ", pixel Yj=" << pixJInter.second ;
          // if (evt_counter==9 && ((jet_pt-2001)<3)) std::cout << ", pixel Ytrk=" << pixTrkInter.second << std::endl;

          // pixX=pixX;
          pixX = pixX+jetDimX/2;
          pixY = pixY+jetDimY/2;
          // if (evt_counter==9 && ((jet_pt-2001)<3)) std::cout << "PIX x = " << pixX << ", PIX y=" << pixY << std::endl;

          // double info[9] = {0,0,0,0,0,0,0,0,-1};
          double info[8] = {0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0};

          if (x==pixX && y==pixY) {
            // if(theCluster.sizeX()==1) std::cout << "PROB1 " << "size x="<< theCluster.sizeX()<< ", size Y="<< theCluster.sizeY()<<", local x ="<<localTrkInter.x()<< ", local y="<<localTrkInter.y() << ", divided by pitch X=" << localTrkInter.x()/pitchX << ", divided by pitch Y=" << localTrkInter.y()/pitchY << ", flipped=" << flip << ", pixel num=" << theCluster.minPixelRow() << "," << theCluster.minPixelCol() << std::endl;
            // std::cout << "PROB1 " << ", local x ="<<localTrkInter.x()<< ", local y="<<localTrkInter.y() << ", divided by pitch X=" << localTrkInter.x()/pitchX << ", divided by pitch Y=" << localTrkInter.y()/pitchY << ", flipped=" << flip << std::endl;

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
          else info[0] = 0;

          // double distX = flip*(Jinter.x()-localTrkInter.x())-(x+0.5)*pitchX;
          // double distY = Jinter.y()-localTrkInter.y()-(x+0.5)*pitchY;
          //  double distX = flip*(localTrkInter.x())-(pixTrkInter.first+0.5)*pitchX;
          //  double distY = localTrkInter.y()-(pixTrkInter.second+0.5)*pitchY;
        //   LocalPoint pix2loc = pixel2Local(pixTrkInter.first,pixTrkInter.second,det);
          //  double distX = localTrkInter.x()-pix2loc.x()-0.5*pitchX;
          //  double distY = localTrkInter.y()-pix2loc.y()-0.5*pitchY;
          LocalPoint pix2loc = pixel2Local(x+pixJInter.first-jetDimX/2,y+pixJInter.second-jetDimY/2,det);
          double distX =  localTrkInter.x()-pix2loc.x()-0.5*pitchX;//ADDED PITCH
          double distY =  localTrkInter.y()-pix2loc.y()-0.5*pitchY;

           if(distX<0.000001 && distX> -0.000001) {
            // std::cout << "Xclust=" << theCluster.sizeX()<< ", distX="<< distX << ", localTrkInter x=" <<localTrkInter.x()/pitchX << ", pix2loc x=" << pix2loc.x() << std::endl;
             distX = 0.0;
           }
           if(distY<0.000001 && distY> - 0.000001){
            //  std::cout << "Yclust=" << theCluster.sizeY() << ", distY="<< distY << ", localTrkInter y=" <<localTrkInter.y()/pitchY << ", pix2loc y=" << pix2loc.y() << std::endl;
             distY = 0.0;
           }

          info[1] = sqrt(distX*distX+distY*distY);
          // info[6] = distX;
          // info[7] = distY;
          if(info[0]== 1 && 0 ){
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
            info[4] = st.momentum().Eta()-jetDir.eta();
            info[5] = deltaPhi(st.momentum().Phi(),jetDir.phi());
            info[7] = 1/st.momentum().Pt();
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

          tracksInfo.push_back(trkInfoObj(info[0],info[1],info[2],info[3],info[4],info[5],info[6],info[7]));//,info[6],info[7]));//info[6],info[7],info[8]));
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
            if(tracksInfo.at(trk).xpos!=99999999) trackPar[x][y][trk][0]=100*tracksInfo.at(trk).xpos;
            else trackPar[x][y][trk][0]=0.0;
            if(tracksInfo.at(trk).ypos!=99999999) trackPar[x][y][trk][1]=100*tracksInfo.at(trk).ypos;
            else trackPar[x][y][trk][1]=0.0;
            trackPar[x][y][trk][2]=100*tracksInfo.at(trk).xangle;
            trackPar[x][y][trk][3]=100*tracksInfo.at(trk).yangle;
            // if(tracksInfo.at(trk).zero_flag!=0 && tracksInfo.at(trk).zero_flag!=1) std::cout << "zero_flag=" << tracksInfo.at(trk).zero_flag << std::endl;
            trackPar[x][y][trk][5]=tracksInfo.at(trk).zero_flag; //NOFLAG
            // if(tracksInfo.at(trk).zero_flag!=0 && tracksInfo.at(trk).zero_flag!=1) std::cout << "assigned zero_flag=" << trackPar[x][y][trk][5]<< std::endl;
            trackPar[x][y][trk][4]=tracksInfo.at(trk).one_over_pt;
            //  trackPar[x][y][trk][4]=tracksInfo.at(trk).jEta;
            //  trackPar[x][y][trk][5]=tracksInfo.at(trk).jPt;
            trackProb[x][y][trk]=tracksInfo.at(trk).prob;
            // for(int q=0; q<6; q++){
              // if(trackPar[x][y][trk][q]>10000) {
                // std::cout << "we have a problem with par " << q << ". value=" << trackPar[x][y][trk][q] << std::endl;
                // if(q==0) std::cout << "internal="<< tracksInfo.at(trk).xpos << std::endl;
                // if(q==1) std::cout << "internal="<< tracksInfo.at(trk).ypos << std::endl;
                // if(q==2) std::cout << "internal="<< tracksInfo.at(trk).xangle << std::endl;
                // if(q==3) std::cout << "internal="<< tracksInfo.at(trk).yangle << std::endl;
                // if(q==4) std::cout << "internal="<< tracksInfo.at(trk).one_over_pt << std::endl;
                // if(q==5) std::cout << "internal="<< tracksInfo.at(trk).zero_flag << std::endl;
              // }
            // }

            if(oneHitInfo){
              if(trackProb[x][y][trk]==0) {
                for(int pp=0; pp<Npar+1; pp++){ //NOFLAG
                  trackPar[x][y][trk][pp] = 0.0;
                }
              }
            }

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
          if(tracksInfo.at(trk).prob==1 && 0){
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
    // goodSimVtx.clear();
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






  std::map<int,SiPixelCluster> NNClustSeedInputSimHit::splitClusterInTracks(const SiPixelCluster & cluster, const DetId & clusterID){ //devo passargli anche detset?

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


  const GeomDet* NNClustSeedInputSimHit::DetectorSelector(int llay, const reco::Candidate& jet, GlobalVector jetDir, const reco::Vertex& jetVertex, const TrackerTopology* const tTopo, const PixelClusterParameterEstimator* pp, const auto & simtracksVector){

    struct distCompare {
    bool operator()(std::pair<double,const GeomDet*> x, std::pair<double,const GeomDet*> y) const
    {return x.first < y.first;} // changed <, now the smaller!
    };

    std::set<std::pair<double,const GeomDet*>, distCompare> distDetSet;//distance square from center of det

    LocalPoint jetInter(0,0,0);
    // const GeomDet* globDet = (GeomDet*)0; //fuffa assigment to allow to compile
    // const GeomDetUnit* detUnit = (GeomDetUnit*)0; //fuffa assigment to allow to compile;

    // jet_pt = jet.pt();
    // jet_eta = jet.eta();
    // jet_phi = jet.phi();

    // const reco::Vertex& jetVertex = (*vertices)[0];
    // auto jetVert = jetVertex; //trackInfo filling
    // std::vector<std::map<int,SiPixelCluster>> clusterMapVector;
    // std::cout << "DEBUG DETSEL, pre loops" << std::endl;

    std::vector<PSimHit>::const_iterator shIt = simhits->begin();
    std::vector<PSimHit>::const_iterator shItEC = simhitsEC->begin();

    std::set<const GeomDet*> simhitsDetSet;

    for (; shIt != simhits->end(); shIt++) { //loop on simit to find correspondent det (barrel)
      // const edmNew::DetSet<PSimHit>& detset = *shIt;
      const GeomDet* det = geometry_->idToDet((*shIt).detUnitId());

      simhitsDetSet.insert(det);
    }

    // std::cout << "DEBUG DETSEL, between loops" << std::endl;


    for (; shItEC != simhitsEC->end(); shItEC++) { //loop on simit to find correspondent det (endCaps)
      // const edmNew::DetSet<PSimHit>& detset = *shIt;
      // std::cout << "DEBUG DETSEL, pre ECdet" << std::endl;

      const GeomDet* det = geometry_->idToDet((*shItEC).detUnitId());
      // std::cout << "DEBUG DETSEL,post ECdet" << std::endl;

      simhitsDetSet.insert(det);
      // std::cout << "DEBUG DETSEL,inserted ECdet" << std::endl;

    }

    // std::cout << "DEBUG DETSEL, post loops" << std::endl;

    // edmNew::DetSetVector<SiPixelCluster>::const_iterator detIt = simhits->begin();

    for (std::set<const GeomDet*>::iterator detIt=simhitsDetSet.begin(); detIt != simhitsDetSet.end(); detIt++) { //loop deset
      // std::cout << "DEBUG DETSEL, in iteration" << std::endl;

      // std::set<int> trkIDset;
      // std::set<double> distSet; //distance square from center of det

      const GeomDet* det = *detIt;
      // for (auto cluster = detset.begin(); cluster != detset.end(); cluster++) { //loop cluster

        // const SiPixelCluster& aCluster = *cluster;
        // det_id_type aClusterID= detset.id();
        // auto aClusterID= detset.id();

        // if(DetId(aClusterID).subdetId()!=1) continue;

        int lay = tTopo->layer(det->geographicalId());
        if(det->geographicalId().subdetId()==PixelSubdetector::PixelEndcap){
           lay=lay+4; //endcap layer counting = 5,6,7
          //  std::cout << "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< endcap detector" << std::endl;
        }
        std::pair<bool, Basic3DVector<float>> interPair = findIntersection(jetDir,(reco::Candidate::Point)jetVertex.position(), det);
        if(interPair.first==false) continue;
        Basic3DVector<float> inter = interPair.second;
        auto localInter = det->specificSurface().toLocal((GlobalPoint)inter);

        // GlobalPoint pointVertex(jetVertex.position().x(), jetVertex.position().y(), jetVertex.position().z());

        // GlobalPoint cPos = det->surface().toGlobal(pp->localParametersV(aCluster,(*geometry_->idToDetUnit(detIt->id())))[0].first);
        // LocalPoint cPos_local = pp->localParametersV(aCluster,(*geometry_->idToDetUnit(detIt->id())))[0].first;

        // if(std::abs(cPos_local.x()-localInter.x())/pitchX<=jetDimX/2 && std::abs(cPos_local.y()-localInter.y())/pitchY<=jetDimY/2){ // per ora preso baricentro, da migliorare

          // fillPixelMatrix(aCluster,lay,localInter, det);
          if(lay==llay) {
            double dist2 = localInter.x()*localInter.x()+localInter.y()*localInter.y();
            // std::cout << "lay=" << lay << " dist=" << dist2 << " det="<< det->gdetIndex() << std::endl;
            std::pair<double,const GeomDet*> distDet(dist2, det);
            distDetSet.insert(distDet);
          }

            // if(jetInter.x()==0 && jetInter.y()==0 && jetInter.z()==0) jetInter = localInter; //filling infoTracks

            // if(globDet ==(GeomDet*)0){//filling infoTracks
            //    globDet = det;
            //    detUnit = geometry_->idToDetUnit(detIt->id());
            //  }

            // if(det!=globDet) continue;

            // std::map<int,SiPixelCluster> splittedCluster = splitClusterInTracks(aCluster,aClusterID); //accesso/assegnazione splittedClister[id]=cluser
            // clusterMapVector.push_back(splittedCluster);
            // for(std::map<int,SiPixelCluster>::iterator track_iter= splittedCluster.begin(); track_iter!=splittedCluster.end(); track_iter++){
              // for(uint j=0; j<simtracksVector->size(); j++){
                // SimTrack st = simtracksVector->at(j);
                // if((int)st.trackId()==track_iter->first) {
                  // std::cout << "1 track, det" << det << ", trackID="<< track_iter->first<< std::endl;
                  // trkIDset.insert(track_iter->first); //trackID
                // }
              // }
            //fillPixelTrackMap(track_iter->first, track_iter->second,lay,localInter, det);
            //aggiungere salvataggio info traccia (pt eta ecc) usando trackID
            // }//tracks in cluster
          // }
        // } //cluster in ROI
      //} //cluster

      // int siz = trkIDset.size();
      // if(siz>0) std::cout << "SIZE=" << siz << std::endl;

    } //detset

    if(distDetSet.size()!=0 && 0) std::cout << "layer ="<< llay << "  det=" << distDetSet.begin()->second->gdetIndex() << ", distance =" << distDetSet.begin()->first << std::endl;
    // for(std::set<std::pair<double,const GeomDet*>, distCompare>::iterator track_iter= distDetSet.begin(); track_iter!=distDetSet.end(); track_iter++){
    //   std::cout << "det=" << track_iter->second << ", trk number=" << track_iter->first << std::endl;
    // }
    // std::cout << "---------" << std::endl;
    // if(distDetSet.size()==0) std::cout << "VUOTAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" << std::endl;
    if(distDetSet.size()==0) return (GeomDet*)0;
    else {

    //start debug EC-------------------------------
    // int   NTracksCounter = 0;
    // std::map<int, int> mapCount;
    //     for(uint j=0; j<simtracksVector->size(); j++){
    //       for(std::vector<PSimHit>::const_iterator it=simhitsEC->begin(); it!=simhitsEC->end(); ++it) {
    //         SimTrack st = simtracksVector->at(j);
    //         if(st.trackId()==(*it).trackId()) {
    //           const GeomDet* det = geometry_->idToDet((*it).detUnitId());
    //           int lay = tTopo->layer(det->geographicalId());
    //           if(det->geographicalId().subdetId()==PixelSubdetector::PixelEndcap) {
    //             lay=lay+4; //endcap layer counting = 5,6,7
    //           }
    //             // std::cout << "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!endcap layer"<< lay << "   det" << det->gdetIndex() << std::endl;
    //             if(det == distDetSet.begin()->second) NTracksCounter++;
    //             if(lay==llay) {
    //               if(mapCount.find(det->gdetIndex())!=mapCount.end()) mapCount[det->gdetIndex()]++;
    //               else   mapCount[det->gdetIndex()]=0;
    //               }
    //           // else  std::cout << "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!barrel layer"<< lay << "   det" << det->gdetIndex() << std::endl;
    //
    //         }
    //       }
    //     }
    // for(uint j=0; j<simtracksVector->size(); j++){
    //
    //       for(std::vector<PSimHit>::const_iterator it=simhits->begin(); it!=simhits->end(); ++it) {
    //         SimTrack st = simtracksVector->at(j);
    //         if(st.trackId()==(*it).trackId()) {
    //           const GeomDet* det = geometry_->idToDet((*it).detUnitId());
    //           int lay = tTopo->layer(det->geographicalId());
    //           if(det->geographicalId().subdetId()==PixelSubdetector::PixelEndcap) {
    //             lay=lay+4; //endcap layer counting = 5,6,7
    //           }
    //             // std::cout << "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!endcap layer"<< lay << "   det" << det->gdetIndex() << std::endl;
    //             if(det == distDetSet.begin()->second) NTracksCounter++;
    //             if(lay==llay) {
    //               if(mapCount.find(det->gdetIndex())!=mapCount.end()) mapCount[det->gdetIndex()]++;
    //               else   mapCount[det->gdetIndex()]=0;
    //               }
    //           // else  std::cout << "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!barrel layer"<< lay << "   det" << det->gdetIndex() << std::endl;
    //
    //         }
    //       }
    //     }
    //     int maxMap = 0;
    //     int detmap=0;
    //     double distMap = 0;
    //     for(auto const & x : mapCount){
    //       if(x.second>maxMap ){
    //          maxMap=x.second;
    //          detmap = x.first;
    //        }
    //     for( auto x : distDetSet){
    //       if(x.second->gdetIndex()==detmap) {
    //         distMap=x.first;
    //       }
    //     }
    //     }
    //
    //       std::cout << ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>lay=" << llay << " dist=" << distDetSet.begin()->first << " det="<< distDetSet.begin()->second->gdetIndex() << "nTracks on it=" <<  NTracksCounter << "  map value=" << maxMap << " map det=" << detmap <<"   distMap=" << distMap <<std::endl;
    //      // if(distDetSet.begin()->second->geographicalId().subdetId()==PixelSubdetector::PixelEndcap) std::cout << "EC det!" << std::endl;

      //End of debug EC-------------------------------




      return distDetSet.begin()->second;
    }
  }





//backup
// const GeomDet* NNClustSeedInputSimHit::DetectorSelector(int llay, const reco::Candidate& jet, GlobalVector jetDir, const reco::Vertex& jetVertex, const TrackerTopology* const tTopo, const PixelClusterParameterEstimator* pp, const auto & simtracksVector){
//
//   struct trkNumCompare {
//   bool operator()(std::pair<int,const GeomDet*> x, std::pair<int,const GeomDet*> y) const
//   {return x.first > y.first;}
//   };
//
//   std::set<std::pair<int,const GeomDet*>, trkNumCompare> track4detSet;
//
//   LocalPoint jetInter(0,0,0);
//   // const GeomDet* globDet = (GeomDet*)0; //fuffa assigment to allow to compile
//   // const GeomDetUnit* detUnit = (GeomDetUnit*)0; //fuffa assigment to allow to compile;
//
//   // jet_pt = jet.pt();
//   // jet_eta = jet.eta();
//   // jet_phi = jet.phi();
//
//   // const reco::Vertex& jetVertex = (*vertices)[0];
//   // auto jetVert = jetVertex; //trackInfo filling
//   // std::vector<std::map<int,SiPixelCluster>> clusterMapVector;
//
//   edmNew::DetSetVector<SiPixelCluster>::const_iterator detIt = inputPixelClusters->begin();
//
//   for (; detIt != inputPixelClusters->end(); detIt++) { //loop deset
//
//     std::set<int> trkIDset;
//     const edmNew::DetSet<SiPixelCluster>& detset = *detIt;
//     const GeomDet* det = geometry_->idToDet(detset.id()); //lui sa il layer con cast a  PXBDetId (vedi dentro il layer function)
//     for (auto cluster = detset.begin(); cluster != detset.end(); cluster++) { //loop cluster
//
//       const SiPixelCluster& aCluster = *cluster;
//       // det_id_type aClusterID= detset.id();
//       auto aClusterID= detset.id();
//
//       if(DetId(aClusterID).subdetId()!=1) continue;
//
//       int lay = tTopo->layer(det->geographicalId());
//
//       std::pair<bool, Basic3DVector<float>> interPair = findIntersection(jetDir,(reco::Candidate::Point)jetVertex.position(), det);
//
//       if(interPair.first==false) continue;
//
//       Basic3DVector<float> inter = interPair.second;
//
//       auto localInter = det->specificSurface().toLocal((GlobalPoint)inter);
//
//       // GlobalPoint pointVertex(jetVertex.position().x(), jetVertex.position().y(), jetVertex.position().z());
//
//       // GlobalPoint cPos = det->surface().toGlobal(pp->localParametersV(aCluster,(*geometry_->idToDetUnit(detIt->id())))[0].first);
//       LocalPoint cPos_local = pp->localParametersV(aCluster,(*geometry_->idToDetUnit(detIt->id())))[0].first;
//
//       if(std::abs(cPos_local.x()-localInter.x())/pitchX<=jetDimX/2 && std::abs(cPos_local.y()-localInter.y())/pitchY<=jetDimY/2){ // per ora preso baricentro, da migliorare
//
//         // fillPixelMatrix(aCluster,lay,localInter, det);
//         if(lay==llay) {
//
//           // if(jetInter.x()==0 && jetInter.y()==0 && jetInter.z()==0) jetInter = localInter; //filling infoTracks
//
//           // if(globDet ==(GeomDet*)0){//filling infoTracks
//           //    globDet = det;
//           //    detUnit = geometry_->idToDetUnit(detIt->id());
//           //  }
//
//           // if(det!=globDet) continue;
//
//           std::map<int,SiPixelCluster> splittedCluster = splitClusterInTracks(aCluster,aClusterID); //accesso/assegnazione splittedClister[id]=cluser
//           // clusterMapVector.push_back(splittedCluster);
//           for(std::map<int,SiPixelCluster>::iterator track_iter= splittedCluster.begin(); track_iter!=splittedCluster.end(); track_iter++){
//             for(uint j=0; j<simtracksVector->size(); j++){
//               SimTrack st = simtracksVector->at(j);
//               if((int)st.trackId()==track_iter->first) {
//                 // std::cout << "1 track, det" << det << ", trackID="<< track_iter->first<< std::endl;
//                 trkIDset.insert(track_iter->first); //trackID
//               }
//             }
//           //fillPixelTrackMap(track_iter->first, track_iter->second,lay,localInter, det);
//           //aggiungere salvataggio info traccia (pt eta ecc) usando trackID
//           }//tracks in cluster
//       }
//       } //cluster in ROI
//     } //cluster
//     int siz = trkIDset.size();
//     // if(siz>0) std::cout << "SIZE=" << siz << std::endl;
//     std::pair<int,const GeomDet*> track4det(siz, det);
//     if(siz>0) track4detSet.insert(track4det);
//   } //detset
//
//   if(track4detSet.size()!=0) std::cout << "layer ="<< llay << " Selected det=" << track4detSet.begin()->second->gdetIndex() << ", trk number=" << track4detSet.begin()->first << std::endl;
//   // for(std::set<std::pair<int,const GeomDet*>, trkNumCompare>::iterator track_iter= track4detSet.begin(); track_iter!=track4detSet.end(); track_iter++){
//   //   std::cout << "det=" << track_iter->second << ", trk number=" << track_iter->first << std::endl;
//   // }
//   // std::cout << "---------" << std::endl;
//
//   if(track4detSet.size()==0) return (GeomDet*)0;
//   else return track4detSet.begin()->second;
// }

std::vector<GlobalVector> NNClustSeedInputSimHit::splittedClusterDirections(const reco::Candidate& jet, const TrackerTopology* const tTopo, auto pp, const reco::Vertex& jetVertex , int layer){
  std::vector<GlobalVector> clustDirs;

  edmNew::DetSetVector<SiPixelCluster>::const_iterator detIt_int = inputPixelClusters->begin();


  for (; detIt_int != inputPixelClusters->end(); detIt_int++) {

    const edmNew::DetSet<SiPixelCluster>& detset_int = *detIt_int;
    const GeomDet* det_int = geometry_->idToDet(detset_int.id());
    int lay = tTopo->layer(det_int->geographicalId());
    if(det_int->geographicalId().subdetId()==PixelSubdetector::PixelEndcap) lay=lay+4; //endcap layer counting = 5,6,7
    // std::cout<< "LAYYYYYYYYYYYY=" << lay <<std::endl;
    if(lay != layer) continue; //NB: saved bigclusetr on all the layers!!

    for (auto cluster = detset_int.begin(); cluster != detset_int.end(); cluster++) {
      const SiPixelCluster& aCluster = *cluster;
      // bool hasBeenSplit = false;
      // bool shouldBeSplit = false;
      GlobalPoint cPos = det_int->surface().toGlobal(pp->localParametersV(aCluster,(*geometry_->idToDetUnit(detIt_int->id())))[0].first);
      GlobalPoint ppv(jetVertex.position().x(), jetVertex.position().y(), jetVertex.position().z());
      GlobalVector clusterDir = cPos - ppv;
      GlobalVector jetDir(jet.px(), jet.py(), jet.pz());
      // std::cout <<"deltaR" << Geom::deltaR(jetDir, clusterDir)<<", jetDir="<< jetDir << ", clusterDir=" <<clusterDir << ", X=" << aCluster.sizeX()<< ", Y=" << aCluster.sizeY()<<std::endl;
      if (Geom::deltaR(jetDir, clusterDir) < deltaR_) {
            // check if the cluster has to be splitted

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
            // std::cout <<"jDir="<< jetDir << ", cDir=" <<clusterDir <<  ", carica=" << aCluster.charge() << ", expChar*cFracMin_=" << expCharge * chargeFracMin_ <<", X=" << aCluster.sizeX()<< ", expSizeX+1=" <<  expSizeX + 1<< ", Y="<<aCluster.sizeY() <<", expSizeY+1="<< expSizeY + 1<< std::endl;
            if (aCluster.charge() > expCharge * chargeFracMin_ && (aCluster.sizeX() > expSizeX + 1 ||  aCluster.sizeY() > expSizeY + 1)) {
              // shouldBeSplit = true;
              std::cout << "trovato cluster con deltaR=" << Geom::deltaR(jetDir, clusterDir)<< ", on layer=" <<lay << std::endl;
              clustDirs.push_back(clusterDir);
            }
          }
        }
      }
      return clustDirs;

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
NNClustSeedInputSimHit::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void
NNClustSeedInputSimHit::endJob()
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
NNClustSeedInputSimHit::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(NNClustSeedInputSimHit);
