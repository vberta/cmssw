#ifndef RecoTracker_TkSeedGenerator_JetCoreMCtruthSeedGenerator_H
#define RecoTracker_TkSeedGenerator_JetCoreMCtruthSeedGenerator_H

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
#include "DataFormats/Math/interface/Point3D.h"
#include "DataFormats/Math/interface/Vector3D.h"
#include "DataFormats/Candidate/interface/Candidate.h"

#include "RecoLocalTracker/ClusterParameterEstimator/interface/PixelClusterParameterEstimator.h"
#include "RecoLocalTracker/Records/interface/TkPixelCPERecord.h"

#include "TrackingTools/GeomPropagators/interface/StraightLinePlaneCrossing.h"
#include "TrackingTools/GeomPropagators/interface/Propagator.h"
#include "TrackingTools/Records/interface/TrackingComponentsRecord.h"

#include "MagneticField/Engine/interface/MagneticField.h"
#include "MagneticField/Records/interface/IdealMagneticFieldRecord.h"

#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "SimDataFormats/Track/interface/SimTrack.h"

#include "SimDataFormats/Vertex/interface/SimVertex.h"

#include "Geometry/CommonDetUnit/interface/PixelGeomDetUnit.h"

#include "DataFormats/TrajectorySeed/interface/TrajectorySeedCollection.h"

#include "SimDataFormats/TrackingHit/interface/PSimHit.h"


class JetCoreMCtruthSeedGenerator : public edm::one::EDProducer<edm::one::SharedResources> {
public:
  explicit JetCoreMCtruthSeedGenerator(const edm::ParameterSet&);
  ~JetCoreMCtruthSeedGenerator() override;

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);
  // A pointer to a cluster and a list of tracks on it
  struct TrackAndState {
    TrackAndState(const reco::Track* aTrack, TrajectoryStateOnSurface aState) : track(aTrack), state(aState) {}
    const reco::Track* track;
    TrajectoryStateOnSurface state;
  };

  template <typename Cluster>
  struct ClusterWithTracks {
    ClusterWithTracks(const Cluster& c) : cluster(&c) {}
    const Cluster* cluster;
    std::vector<TrackAndState> tracks;
  };

  typedef ClusterWithTracks<SiPixelCluster> SiPixelClusterWithTracks;

  double jet_pt;
  double jet_eta;
  double pitchX = 0.01;               //100 um (pixel pitch in X)
  double pitchY = 0.015;              //150 um (pixel pitch in Y)
  static constexpr int jetDimX = 30;  //pixel dimension of NN window on layer2
  static constexpr int jetDimY = 30;  //pixel dimension of NN window on layer2
  bool inclusiveConeSeed =
      true;  //true= fill tracks in a cone of deltaR_, false=fill tracks which have SimHit on globDet

private:
  void beginJob() override;
  void produce(edm::Event&, const edm::EventSetup&) override;
  void endJob() override;

  // ----------member data ---------------------------
  std::string propagatorName_;
  edm::ESHandle<MagneticField> magfield_;
  edm::ESHandle<GlobalTrackingGeometry> geometry_;
  edm::ESHandle<Propagator> propagator_;

  edm::EDGetTokenT<std::vector<reco::Vertex>> vertices_;
  edm::EDGetTokenT<edmNew::DetSetVector<SiPixelCluster>> pixelClusters_;
  std::vector<SiPixelClusterWithTracks> allSiPixelClusters;
  edm::Handle<edmNew::DetSetVector<SiPixelCluster>> inputPixelClusters;
  edm::EDGetTokenT<edm::View<reco::Candidate>> cores_;
  edm::EDGetTokenT<std::vector<SimTrack>> simtracksToken;
  edm::EDGetTokenT<std::vector<SimVertex>> simvertexToken;
  edm::EDGetTokenT<std::vector<PSimHit>> PSimHitToken;
  edm::Handle<std::vector<PSimHit>> simhits;

  double ptMin_;
  double deltaR_;
  double chargeFracMin_;
  double centralMIPCharge_;
  std::string pixelCPE_;

  std::pair<bool, Basic3DVector<float>> findIntersection(const GlobalVector&,
                                                         const reco::Candidate::Point&,
                                                         const GeomDet*);

  std::pair<int, int> local2Pixel(double, double, const GeomDet*);

  LocalPoint pixel2Local(int, int, const GeomDet*);

  int pixelFlipper(const GeomDet*);

  const GeomDet* DetectorSelector(
      int, const reco::Candidate&, GlobalVector, const reco::Vertex&, const TrackerTopology* const, const edmNew::DetSetVector<SiPixelCluster>&);

  std::vector<GlobalVector> splittedClusterDirections(const reco::Candidate&,
                                                      const TrackerTopology* const,
                                                      const PixelClusterParameterEstimator*,
                                                      const reco::Vertex&,
                                                      int,
                                                      const edmNew::DetSetVector<SiPixelCluster>&);  //if not working,: args=2 auto

  std::vector<PSimHit> coreHitsFilling(std::vector<PSimHit>,
                                       const GeomDet*,
                                       GlobalVector,
                                       const reco::Vertex&);  //if not working,: args=0 auto
  std::pair<std::vector<SimTrack>, std::vector<SimVertex>> coreTracksFilling(
      std::vector<PSimHit>,
      const std::vector<SimTrack>,
      const std::vector<SimVertex>);  //if not working,: args=1,2 auto

  std::vector<std::array<double, 5>> seedParFilling(std::pair<std::vector<SimTrack>, std::vector<SimVertex>>,
                                                    const GeomDet*,
                                                    const reco::Candidate&);

  std::pair<std::vector<SimTrack>, std::vector<SimVertex>> coreTracksFillingDeltaR(
      const std::vector<SimTrack>,
      const std::vector<SimVertex>,
      const GeomDet*,
      const reco::Candidate&,
      const reco::Vertex&);  //if not working,: args=0,1 auto
};
#endif
