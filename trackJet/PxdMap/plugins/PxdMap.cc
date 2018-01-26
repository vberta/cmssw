// -*- C++ -*-
//
// Package:    trackJet/PxdMap
// Class:      PxdMap
//
/**\class PxdMap PxdMap.cc trackJet/PxdMap/plugins/PxdMap.cc

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

#include "TTree.h"


//
// class declaration
//

// If the analyzer does not use TFileService, please remove
// the template argument to the base class so the class inherits
// from  edm::one::EDAnalyzer<> and also remove the line from
// constructor "usesResource("TFileService");"
// This will improve performance in multithreaded jobs.

class PxdMap : public edm::one::EDProducer<edm::one::SharedResources>  {
   public:
      explicit PxdMap(const edm::ParameterSet&);
      ~PxdMap();

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

  TFile* pxdMap_out;
  TTree* PxdMapTree;
  static const int jetDimX =30;
  static const int jetDimY =30;
  static const int Nlayer =4;
  static const int Ntrack = 100;
  double clusterMeas[Nlayer][jetDimX][jetDimY];
  double clusterSplit[Ntrack][Nlayer][jetDimX][jetDimY];
  double track_pt[Ntrack] = {0.0};
  double track_eta[Ntrack] = {0.0};
  double track_phi[Ntrack] = {0.0};
  double jet_pt;
  double jet_eta;
  double jet_phi;

  int minLayer = 1;
  int maxLayer = 4;

  double pitchX = 0.01; //A CASO
  double pitchY = 0.015; //A CASO

  int jetnum =0;




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

  std::map<int, double [Nlayer][jetDimX][jetDimY]> trackMap;

  double ptMin_;
  // double deltaR_;

  Basic3DVector<float> findIntersection(const GlobalVector & , const reco::Candidate::Point & ,const GeomDet*);

  void fillPixelMatrix(const SiPixelCluster &, int, auto);

  void fillPixelTrackMap(int, const SiPixelCluster &, int, auto);

  void fillPixelTrackMatrix();

  std::map<int,SiPixelCluster> splitClusterInTracks(const SiPixelCluster &, const DetId &);


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
PxdMap::PxdMap(const edm::ParameterSet& iConfig) :

      vertices_(consumes<reco::VertexCollection>(iConfig.getParameter<edm::InputTag>("vertices"))),
      pixelClusters_(consumes<edmNew::DetSetVector<SiPixelCluster> >(iConfig.getParameter<edm::InputTag>("pixelClusters"))),
      pixeldigisimlinkToken(consumes< edm::DetSetVector<PixelDigiSimLink> >(edm::InputTag("simSiPixelDigis"))),
      cores_(consumes<edm::View<reco::Candidate> >(iConfig.getParameter<edm::InputTag>("cores"))),
      ptMin_(iConfig.getParameter<double>("ptMin"))
      //cores_(consumes<edm::View<reco::Candidate> >(iConfig.getParameter<edm::InputTag>("cores")))

//     //  pixelClusters_ = consumes<edmNew::DetSetVector<SiPixelCluster> >(iConfig.getParameter<edm::InputTag>("pixelClusters"));
      // deltaR_(iConfig.getParameter<double>("deltaRmax")),

{
   //now do what ever initialization is needed
   usesResource("TFileService");
  // pixelClusters_ = consumes<edmNew::DetSetVector<SiPixelCluster> >(iConfig.getParameter<edm::InputTag>("pixelClusters"));


   edm::Service<TFileService> fileService;

   //pxdMap_out =new TFile("pxdMap_out.root", "RECREATE");
  // PxdMapTree= new TTree("PxdMapTree","PxdMapTree");
   PxdMapTree= fileService->make<TTree>("PxdMapTree","PxdMapTree");
   PxdMapTree->Branch("cluster_measured",clusterMeas,"cluster_measured[4][30][30]/f");
   PxdMapTree->Branch("cluster_splitted",clusterSplit,"cluster_splitted[100][4][30][30]/f");
   PxdMapTree->Branch("jet_eta",&jet_eta);
   PxdMapTree->Branch("jet_pt",&jet_pt);
   PxdMapTree->Branch("jet_phi",&jet_phi);
//   PxdMapTree->Branch("track_eta",&track_eta);
//   PxdMapTree->Branch("track_pt",&track_pt);
//   PxdMapTree->Branch("track_phi",&track_phi);

   // //sto usando fileservice quindi non servono in fondo
   // //pxdMap_out->cd();
   // //PxdMapTree->Write();
   // //pxdMap_out->Close();


  //  PxdMapTree->Branch("event_number",&eventNum);
  //  PxdMapTree->Branch("layer_number",&layerNum);
  //  PxdMapTree->Branch("pixel_row",&pixelRow);
  //  PxdMapTree->Branch("pixel_column",&pixelCol);
  //  PxdMapTree->Branch("pixel_signal",&pixelSig);

   /// dichiarare cosa produce  produces<asd
}


PxdMap::~PxdMap()
{

   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called for each event  ------------
#define foreach BOOST_FOREACH


void PxdMap::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{

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

  auto output = std::make_unique<edmNew::DetSetVector<SiPixelCluster>>();

  for (unsigned int ji = 0; ji < cores->size(); ji++) {

    if ((*cores)[ji].pt() > ptMin_) {
      std::cout << " __________________________________________________________" <<std::endl;
      std::cout << "|____________________NEW JET_______________________________|" <<std::endl;

      std::cout << "jet number " << jetnum << std::endl;
      const reco::Candidate& jet = (*cores)[ji];
      jet_pt = jet.pt();

      jet_eta = jet.eta();
      jet_phi = jet.phi();
      GlobalVector jetDir(jet.px(), jet.py(), jet.pz());
      //GlobalVector jetVertex(jet.vertex());
      reco::Candidate::Point jetVertex = jet.vertex();
      edmNew::DetSetVector<SiPixelCluster>::const_iterator detIt = inputPixelClusters->begin();

      for (; detIt != inputPixelClusters->end(); detIt++) {
        edmNew::DetSetVector<SiPixelCluster>::FastFiller filler(*output,detIt->id()); //A CHE SERVE?
        const edmNew::DetSet<SiPixelCluster>& detset = *detIt;
        const GeomDet* det = geometry_->idToDet(detset.id()); //lui sa il layer con cast a  PXBDetId (vedi dentro il layer function)

        for (auto cluster = detset.begin(); cluster != detset.end(); cluster++) {

          const SiPixelCluster& aCluster = *cluster;
          det_id_type aClusterID= detset.id();
          PXBDetId detPX = (PXBDetId)detset.id();
          int lay = detPX.layer();
          Basic3DVector<float> inter = findIntersection(jetDir,jetVertex, det);
          auto localInter = det->specificSurface().toLocal((GlobalVector)inter);

          //if(abs(aCluster.x()/pitchX-localInter.x())<=jetDimX && abs(aCluster.y()/pitchY-localInter.y())<=jetDimY) // per ora preso baricentro, da migliorare
          std::cout << "REF frame DEB: cluser x =" << aCluster.x() << std::endl;
          std::cout << "REF frame DEB: localinter x =" << localInter.x() << std::endl;
          std::cout << "REF frame DEB: inter x =" << inter.x() << std::endl;
          if(abs(aCluster.x()-localInter.x())<=jetDimX/2 && abs(aCluster.y()-localInter.y())<=jetDimY/2){ // per ora preso baricentro, da migliorare
            //---------------debug lines------------------------------------//
            //if(jetnum==10 && lay==2){
            if(1){
              std::cout << "--------new cluster----------" <<std::endl;
              std::cout << "layer=" << lay << std::endl;
              for(int i=0; i<=aCluster.size();i++){
                SiPixelCluster::Pixel pix = cluster->pixel(i);
                int nx = pix.x-localInter.x() ;//pitchX;
                int ny = pix.y-localInter.y();//pitchY;
                std::cout << "x position pixel " << nx <<std::endl;
                std::cout << "y position pixel " << ny <<std::endl;
              }
            }

            fillPixelMatrix(aCluster,lay,localInter); //da sistemare forse il pitch
            //std::unique_ptr<edmNew::DetSetVector<SiPixelCluster> > newPixelClusters( splitClusters( siPixelDetsWithClusters, vertices->front() ) ); //qualcosa del genere
            std::map<int,SiPixelCluster> splittedCluster = splitClusterInTracks(aCluster,aClusterID); //accesso/assegnazione splittedClister[id]=cluser
            for(std::map<int,SiPixelCluster>::iterator track_iter= splittedCluster.begin(); track_iter!=splittedCluster.end(); track_iter++){
              fillPixelTrackMap(track_iter->first, track_iter->second,lay,localInter);
              fillPixelTrackMatrix();
              //aggiungere salvataggio info traccia (pt eta ecc) usando trackID

            }
          }
        }
      }
      jetnum++;
      PxdMapTree->Fill();
    }
  }

}













  Basic3DVector<float> PxdMap::findIntersection(const GlobalVector & dir,const  reco::Candidate::Point & vertex, const GeomDet* det){
     StraightLinePlaneCrossing vertexPlane(Basic3DVector<float>(vertex.x(),vertex.y(),vertex.z()), Basic3DVector<float>(dir.x(),dir.y(),dir.z()));
     std::pair<bool, Basic3DVector<float>> pos = vertexPlane.position(det->specificSurface());
     return pos.second;
  }

  void PxdMap::fillPixelMatrix(const SiPixelCluster & cluster, int layer, auto inter){
    std::cout << "----- cluster filled-------" << std::endl;
    std::cout << "cluser layer" << layer << std::endl;
    for(int i=0; i<=cluster.size();i++){
      SiPixelCluster::Pixel pix = cluster.pixel(i);
      int nx = pix.x-inter.x() ;//pitchX;
      int ny = pix.y-inter.y();//pitchY;
      std::cout << "x position pixel " << nx <<std::endl;
      std::cout << "y position pixel " << ny <<std::endl;
      if(abs(nx)<jetDimX/2 && abs(ny)<jetDimY/2){
        nx = nx+jetDimX/2;
        ny = ny+jetDimY/2;
        clusterMeas[layer][nx][ny] = pix.adc;
      }
    }
  }

  void PxdMap::fillPixelTrackMap(int trackID, const SiPixelCluster & cluster, int layer, auto inter){
    for(int i=0; i<=cluster.size();i++){
      SiPixelCluster::Pixel pix = cluster.pixel(i);
      int nx = pix.x-inter.x() ;//pitchX;
      int ny = pix.y-inter.y();//pitchY;
      if(abs(nx)<jetDimX/2 && abs(ny)<jetDimY/2){
        // std::map<int, double [Nlayer][jetDimX][jetDimY]>::iterator finder = trackMap.find(trackID);
        // if(finder !=trackMap.end()){
        //   // double temp_track[Nlayer][jetDimX][jetDimY] = trackMap[trackID];
        //   // temp_track[layer][nx][ny] = pix.adc;
        //   // trackMap[trackID] =   temp_track[layer][nx][ny]
        //   trackMap[trackID][layer][nx][ny] = pix.adc;
        // }
        // else {
        //   // double temp_track[Nlayer][jetDimX][jetDimY];
        //   // temp_track[layer][nx][ny] = pix.adc;
        //   // trackMap[trackID] = temp_track;
        //   trackMap[trackID][layer][nx][ny] = pix.adc;
        // }
        nx = nx+jetDimX/2;
        ny = ny+jetDimY/2;
        trackMap[trackID][layer][nx][ny] = pix.adc;

        //trackMap[trackID][layer][nx][ny] = pix.adc;

      }
    }
  }

  void PxdMap::fillPixelTrackMatrix(){
    int trk = 0;
    for(std::map<int, double [Nlayer][jetDimX][jetDimY]>::iterator it=trackMap.begin(); it!=trackMap.end(); it++){
    //for(int trk =0; trk<=std::min(trackMap.size(),NTrack); trk++)
      if(trk>=100) continue;
      for(int lay =0; lay<Nlayer; lay++){
        for(int dimx =0; dimx<jetDimX; dimx++){
          for(int dimy =0; dimy<jetDimY; dimy++){
            clusterSplit[trk][lay][dimx][dimy] = trackMap[it->first][lay][dimx][dimy];
          }
        }
      }
      trk++;
    }
    trackMap.clear();
  }


  std::map<int,SiPixelCluster> PxdMap::splitClusterInTracks(const SiPixelCluster & cluster, const DetId & clusterID){ //devo passargli anche detset?

    std::map<int,SiPixelCluster> output;

    int minPixelRow = cluster.minPixelRow();
    int maxPixelRow = cluster.maxPixelRow();
    int minPixelCol = cluster.minPixelCol();
    int maxPixelCol = cluster.maxPixelCol();
    int dsl = 0; // number of digisimlinks

    edm::DetSetVector<PixelDigiSimLink>::const_iterator isearch = pixeldigisimlink->find(clusterID);
    if (isearch != pixeldigisimlink->end()){

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

              if ( newPixelCharge < 2500 )
                continue;

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
                     }
                    clusVecPos++;

                }

            //look if the splitted cluster was already made before, if not create one

            if ( !inStock )
              {
                  //		std::cout << "creating a new cluster " << std::endl;;
                simTrackIdV.push_back(linkiter->SimTrackId()); // add the track id to the vector
                splittedCluster.push_back(SiPixelCluster(newPixelPos,newPixelCharge)); // add the cluster to the vector
              }
        }
      }

    //    std::cout << "will add clusters : simTrackIdV.size() " << simTrackIdV.size() << std::endl;;

     if ( ( ( (int)simTrackIdV.size() ) == 1 ) || cluster.size()==1 )
      {
	       if(simTrackIdV.size()  == 1) {
         //	    cout << "putting in this cluster" << endl;
          //output.push_back(cluster);
          output[simTrackIdV.at(0)] = cluster;
        }
        //      std::cout << "cluster added " << output.size() << std::endl;;
      }
    else
     {
        //for (std::vector<SiPixelCluster>::const_iterator cIter = splittedCluster.begin(); cIter != splittedCluster.end(); cIter++ )
        //for(SiPixelCluster & clust : splittedCluster)
        for(uint j=0; j<splittedCluster.size(); j++)
         {
            //output.push_back( (*cIter) );

            output[simTrackIdV.at(j)]=splittedCluster.at(j);

         }
    }

      simTrackIdV.clear();
      splittedCluster.clear();
    }//if (isearch != pixeldigisimlink->end())

    return output;
  }







//   edmNew::DetSetVector<SiPixelCluster>::const_iterator detIt = inputPixelClusters->begin();
//   for (; detIt != inputPixelClusters->end(); detIt++) {
//     edmNew::DetSetVector<SiPixelCluster>::FastFiller filler(*output,detIt->id());
//     const edmNew::DetSet<SiPixelCluster>& detset = *detIt;
//     const GeomDet* det = geometry->idToDet(detset.id()); //lui sa il layer con cast a  PXBDetId (vedi dentro il layer function)
//     for (auto cluster = detset.begin();
//          cluster != detset.end(); cluster++) {
//       const SiPixelCluster& aCluster = *cluster;
//       bool hasBeenSplit = false;
//       bool shouldBeSplit = false;
//       GlobalPoint cPos = det->surface().toGlobal(
//           pp->localParametersV(aCluster,
//                                (*geometry->idToDetUnit(detIt->id())))[0].first);
//       GlobalPoint ppv(pv.position().x(), pv.position().y(), pv.position().z());
//       GlobalVector clusterDir = cPos - ppv;
//       for (unsigned int ji = 0; ji < cores->size(); ji++) { //fallo diventare loop più esterno
//         if ((*cores)[ji].pt() > ptMin_) {
//           const reco::Candidate& jet = (*cores)[ji];
//           GlobalVector jetDir(jet.px(), jet.py(), jet.pz());
//           if (Geom::deltaR(jetDir, clusterDir) < deltaR_) {
//             // check if the cluster has to be splitted
//             //PRINT DEL CLUSTER SU MAPPA
//             //SPLITTER USANDO tracks
//             bool isEndCap =
//                 (std::abs(cPos.z()) > 30.f);  // FIXME: check detID instead!
//             float jetZOverRho = jet.momentum().Z() / jet.momentum().Rho();
//             if (isEndCap)
//               jetZOverRho = jet.momentum().Rho() / jet.momentum().Z();
//             float expSizeY =
//                 std::sqrt((1.3f*1.3f) + (1.9f*1.9f) * jetZOverRho*jetZOverRho);
//             if (expSizeY < 1.f) expSizeY = 1.f;
//             float expSizeX = 1.5f;
//             if (isEndCap) {
//               expSizeX = expSizeY;
//               expSizeY = 1.5f;
//             }  // in endcap col/rows are switched
//             float expCharge =
//                 std::sqrt(1.08f + jetZOverRho * jetZOverRho) * centralMIPCharge_;
//
//             if (aCluster.charge() > expCharge * chargeFracMin_ &&
//                 (aCluster.sizeX() > expSizeX + 1 ||
//                  aCluster.sizeY() > expSizeY + 1)) {
//               shouldBeSplit = true;
//               if (split(aCluster, filler, expCharge, expSizeY, expSizeX,
//                         jetZOverRho)) {
//                 hasBeenSplit = true;
//               }
//             }
//           }
//         }
//       }
//       if (!hasBeenSplit) {
//         SiPixelCluster c = aCluster;
//         if (shouldBeSplit) {
//           // blowup the error if we failed to split a splittable cluster (does
//           // it ever happen)
//           c.setSplitClusterErrorX(c.sizeX() * (100.f/3.f));  // this is not really blowing up .. TODO: tune
//           c.setSplitClusterErrorY(c.sizeY() * (150.f/3.f));
//         }
//         filler.push_back(c);
//         std::push_heap(filler.begin(),filler.end(),
//           [](SiPixelCluster const & cl1,SiPixelCluster const & cl2) { return cl1.minPixelRow() < cl2.minPixelRow();});
//
//       }
//     }// loop over clusters
//     std::sort_heap(filler.begin(),filler.end(),
//           [](SiPixelCluster const & cl1,SiPixelCluster const & cl2) { return cl1.minPixelRow() < cl2.minPixelRow();});
//
//   }  // loop over det
//   iEvent.put(std::move(output));
// }
//
//
//
//
//
//
//
// void
// PxdMap::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
// {
//
//    using namespace edm;
//    //allSiPixelClusters.clear(); siPixelDetsWithClusters.clear();
//
//    iSetup.get<GlobalTrackingGeometryRecord>().get(geometry_);
//    iSetup.get<IdealMagneticFieldRecord>().get( magfield_ );
//    iSetup.get<TrackingComponentsRecord>().get( "AnalyticalPropagator", propagator_ );
//
//
//    iEvent.getByToken(pixelClusters_, inputPixelClusters);
//    allSiPixelClusters.clear(); siPixelDetsWithClusters.clear();
//    allSiPixelClusters.reserve(inputPixelClusters->dataSize()); // this is important, otherwise push_back invalidates the iterators
//
//     //  pixelClusters_ = consumes<edmNew::DetSetVector<SiPixelCluster> >(iConfig.getParameter<edm::InputTag>("pixelClusters"));
//     //  produces< edmNew::DetSetVector<SiPixelCluster> >();
//
//
//
//    foreach(const edmNew::DetSet<SiPixelCluster> &ds, *inputPixelClusters)
//   {
//     std::vector<SiPixelClusterWithTracks>::iterator start = allSiPixelClusters.end();
//     allSiPixelClusters.insert(start, ds.begin(), ds.end());
//
//     std::vector<SiPixelClusterWithTracks>::iterator end   = allSiPixelClusters.end();
//     siPixelDetsWithClusters[ds.detId()] = SiPixelClustersWithTracks(start,end);
//   }
//
//   //  const SiPixelClusterWithTracks * clustWT = allSiPixelClusters; //SIAMO SICURI??
//   //   //const GlobalVector &vtx
//   //   edmNew::DetSetVector<SiPixelCluster>::FastFiller &output; //CHE CI METTO?
//   //   //DetId detId; //da aggiungere
//   Handle<std::vector<reco::Vertex> > vertices;
//   iEvent.getByToken(vertices_, vertices);
//   const reco::Vertex& pv = (*vertices)[0];
//
//   Handle<edm::View<reco::Candidate> > cores;
//   // iEvent.getByToken(cores_, cores);
//
//   iEvent.getByToken(pixeldigisimlinkToken, pixeldigisimlink);
//
//   // GlobalPoint cPos = det->surface().toGlobal(
//   //           pp->localParametersV(aCluster,
//   //                                (*geometry->idToDetUnit(detIt->id())))[0].first);
//   //       GlobalPoint ppv(pv.position().x(), pv.position().y(), pv.position().z());
//   //       GlobalVector clusterDir = cPos - ppv;
//   // for (unsigned int ji = 0; ji < cores->size(); ji++) {
//   // if ((*cores)[ji].pt() > ptMin_) {
//   //   const reco::Candidate& jet = (*cores)[ji];
//   //   GlobalVector jetDir(jet.px(), jet.py(), jet.pz());
//   //   if (Geom::deltaR(jetDir, clusterDir) < deltaR_) {
//   //
//   //   }
//
//   std::unique_ptr<edmNew::DetSetVector<SiPixelCluster> > newPixelClusters( splitClusters( siPixelDetsWithClusters, vertices->front() ) );
//   iEvent.put(std::move(newPixelClusters));
//   allSiPixelClusters.clear(); siPixelDetsWithClusters.clear();
//
//   // loop su elementi di oggettoprodotto da newPixelCluser
//   //pixelRow=px->riga;
//   //pixelCol=px->colonna;
//   //pixelSign=px->segnale;
//   //EventNum=iEvent_numero;
//   //layerNum->px->layer;
//   //PxdMapTree->Fill();
//
//
//
// }
//

//
// template<typename Cluster>
// std::unique_ptr<edmNew::DetSetVector<Cluster> >
// PxdMap::splitClusters(const std::map<uint32_t, boost::sub_range<std::vector<ClusterWithTracks<Cluster> > > > &input,
// 				    const reco::Vertex &vtx) const
// {
//   auto output = std::make_unique<edmNew::DetSetVector<Cluster>>();
//   typedef std::pair<uint32_t, boost::sub_range<std::vector<ClusterWithTracks<Cluster> > > > pair;
//
//   foreach(const pair &p, input)
//     {
//       const GeomDet* det = geometry_->idToDet( DetId(p.first) );
//
//       if ( det == nullptr )
//       	{
//       	  edm::LogError("MissingDetId") << "DetIDs " << p.first << " is not in geometry.\n";
// 	         continue;
// 	      }
//
//       // gavril: Pass the PV instead of direction
//       // GlobalVector dir(det->position().x() - vtx.x(), det->position().y() - vtx.y(), det->position().z() - vtx.z());
//       GlobalVector primary_vtx( vtx.x(), vtx.y(), vtx.z() );
//
//       // Create output collection
//       typename edmNew::DetSetVector<Cluster>::FastFiller detset(*output, p.first);
//
//       // fill it
//       foreach(const ClusterWithTracks<Cluster> &clustWT, p.second)
// 	     {
// 	        // splitCluster(c, primary_vtx, detset, DetId(p.first) );
//           splitCluster(clustWT, detset );
//        }
//     }
//
//   return output;
// }
//
//
//
//
//
// template<>
// void PxdMap::splitCluster<SiPixelCluster> (const SiPixelClusterWithTracks &clustWT,
// 							 //const GlobalVector &vtx,
// 							 edmNew::DetSetVector<SiPixelCluster>::FastFiller &output
// 							 //DetId detId
// 							 ) const
//   {
//     // cout << "Cluster splitting using simhits " << endl;
//
//     int minPixelRow = (*clustWT.cluster).minPixelRow();
//     int maxPixelRow = (*clustWT.cluster).maxPixelRow();
//     int minPixelCol = (*clustWT.cluster).minPixelCol();
//     int maxPixelCol = (*clustWT.cluster).maxPixelCol();
//     int dsl = 0; // number of digisimlinks
//
//     edm::DetSetVector<PixelDigiSimLink>::const_iterator isearch = pixeldigisimlink->find(output.id());
//     if (isearch != pixeldigisimlink->end()){
//        edm::DetSet<PixelDigiSimLink> digiLink = (*isearch);
//
//        edm::DetSet<PixelDigiSimLink>::const_iterator linkiter = digiLink.data.begin();
//         //create a vector for the track ids in the digisimlinks
//        std::vector<int> simTrackIdV;
//        simTrackIdV.clear();
//        //create a vector for the new splittedClusters
//        std::vector<SiPixelCluster> splittedCluster;
//        splittedCluster.clear();
//
//       for ( ; linkiter != digiLink.data.end(); linkiter++)
//        { // loop over all digisimlinks
//           dsl++;
//           std::pair<int,int> pixel_coord = PixelDigi::channelToPixel(linkiter->channel());
//
//            // is the digisimlink inside the cluster boundaries?
//           if ( pixel_coord.first  <= maxPixelRow &&
//               pixel_coord.first  >= minPixelRow &&
//               pixel_coord.second <= maxPixelCol &&
//               pixel_coord.second >= minPixelCol )
//           {
//               bool inStock(false); // did we see this simTrackId before?
//
//               SiPixelCluster::PixelPos newPixelPos(pixel_coord.first, pixel_coord.second); // coordinates to the pixel
//
//               //loop over the pixels from the cluster to get the charge in this pixel
//               int newPixelCharge(0); //fraction times charge in the original cluster pixel
//
//              const std::vector<SiPixelCluster::Pixel>& pixvector = (*clustWT.cluster).pixels();
//
//              for(std::vector<SiPixelCluster::Pixel>::const_iterator itPix = pixvector.begin(); itPix != pixvector.end(); itPix++)
//                {
//                    if (((int) itPix->x) == ((int) pixel_coord.first)&&(((int) itPix->y) == ((int) pixel_coord.second)))
//                      {
//                           newPixelCharge = (int) (linkiter->fraction()*itPix->adc);
//                      }
//                }
//
//               if ( newPixelCharge < 2500 )
//                 continue;
//
//               //add the pixel to an already existing cluster if the charge is above the threshold
//               int clusVecPos = 0;
//               std::vector<int>::const_iterator sTIter =  simTrackIdV.begin();
//
//               for ( ; sTIter < simTrackIdV.end(); sTIter++)
//                 {
//                     if (((*sTIter)== (int) linkiter->SimTrackId()))
//                       {
//                           inStock=true; // now we saw this id before
//                             // 	  //		  std::cout << " adding a pixel to the cluster " << (int) (clusVecPos) <<std::endl;;
//                             // 	  //		    std::cout << "newPixelCharge " << newPixelCharge << std::endl;;
//                           splittedCluster.at(clusVecPos).add(newPixelPos,newPixelCharge); // add the pixel to the cluster
//                      }
//                     clusVecPos++;
//                 }
//
//             //look if the splitted cluster was already made before, if not create one
//
//             if ( !inStock )
//               {
//                   //		std::cout << "creating a new cluster " << std::endl;;
//                 simTrackIdV.push_back(linkiter->SimTrackId()); // add the track id to the vector
//                 splittedCluster.push_back(SiPixelCluster(newPixelPos,newPixelCharge)); // add the cluster to the vector
//               }
//         }
//       }
//
//   //    std::cout << "will add clusters : simTrackIdV.size() " << simTrackIdV.size() << std::endl;;
//
//      if ( ( ( (int)simTrackIdV.size() ) == 1 ) || ( *clustWT.cluster).size()==1 )
//       {
//          //	    cout << "putting in this cluster" << endl;
//           output.push_back(*clustWT.cluster );
//         //      std::cout << "cluster added " << output.size() << std::endl;;
//       }
//     else
//      {
//         for (std::vector<SiPixelCluster>::const_iterator cIter = splittedCluster.begin(); cIter != splittedCluster.end(); cIter++ )
//          {
//             output.push_back( (*cIter) );
//          }
//     }
//
//      simTrackIdV.clear();
//     splittedCluster.clear();
//   }//if (isearch != pixeldigisimlink->end())
// }





//Handle<std::vector<reco::Track> > tracks;
 //     iEvent.getByToken(tracks_, tracks);
      //TrajectoryStateTransform transform;
/*      foreach (const reco::Track &track, *tracks)
	{
	  FreeTrajectoryState atVtx   =  trajectoryStateTransform::innerFreeState(track, &*magfield_);
	  trackingRecHit_iterator it_hit = track.recHitsBegin(), ed_hit = track.recHitsEnd();
	  for (; it_hit != ed_hit; ++it_hit)
	    {
	      const TrackingRecHit *hit = *it_hit;
	      if ( hit == nullptr || !hit->isValid() )
		continue;

	      int subdet = hit->geographicalId().subdetId();

	      if ( subdet == 0 )
		continue;

	      const GeomDet *det = geometry_->idToDet( hit->geographicalId() );

	      if ( det == nullptr )
		{
		  edm::LogError("MissingDetId") << "DetIDs " << (int)(hit->geographicalId()) << " is not in geometry.\n";
		  continue;
                }

	      TrajectoryStateOnSurface prop = propagator_->propagate(atVtx, det->surface());
	      if ( subdet >= 3 )
		{ // strip
		  markClusters<SiStripCluster>(siStripDetsWithClusters, hit, &track, prop);
                }
	      else if (subdet >= 1)
		{ // pixel
		  markClusters<SiPixelCluster>(siPixelDetsWithClusters, hit, &track, prop);
                }
	      else
		{
		  edm::LogWarning("HitNotFound") << "Hit of type " << typeid(*hit).name() << ",  detid "
						 << hit->geographicalId().rawId() << ", subdet " << subdet;
		}
            }
        }
    }*/

    // Handle<std::vector<reco::Vertex> > vertices;
    //   iEvent.getByToken(vertices_, vertices);
    //
    //   // Needed in case of simsplit
    //   if ( simSplitPixel_ )
    //     iEvent.getByToken(pixeldigisimlinkToken, pixeldigisimlink);
    //
    //   // gavril : to do: choose the best vertex here instead of just choosing the first one ?
    //   std::unique_ptr<edmNew::DetSetVector<SiPixelCluster> > newPixelClusters( splitClusters( siPixelDetsWithClusters, vertices->front() ) );
    //   iEvent.put(std::move(newPixelClusters));
    //   allSiPixelClusters.clear(); siPixelDetsWithClusters.clear();
    //
    // }






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
PxdMap::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void
PxdMap::endJob()
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
PxdMap::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(PxdMap);
