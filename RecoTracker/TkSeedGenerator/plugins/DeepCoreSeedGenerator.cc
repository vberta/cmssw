// -*- C++ -*-
//
// Package:    trackJet/DeepCoreSeedGenerator
// Class:      DeepCoreSeedGenerator
//
/**\class DeepCoreSeedGenerator DeepCoreSeedGenerator.cc trackJet/DeepCoreSeedGenerator/plugins/DeepCoreSeedGenerator.cc

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

#include "DeepCoreSeedGenerator.h"

#include <memory>

// user include files

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
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

#include "TrackingTools/GeomPropagators/interface/StraightLinePlaneCrossing.h"
#include "TrackingTools/GeomPropagators/interface/Propagator.h"
#include "TrackingTools/Records/interface/TrackingComponentsRecord.h"

#include "MagneticField/Engine/interface/MagneticField.h"
#include "MagneticField/Records/interface/IdealMagneticFieldRecord.h"

#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "SimDataFormats/Vertex/interface/SimVertex.h"

#include "Geometry/CommonDetUnit/interface/PixelGeomDetUnit.h"

#include "DataFormats/TrajectorySeed/interface/TrajectorySeedCollection.h"

#include "PhysicsTools/TensorFlow/interface/TensorFlow.h"

//
// class declaration
//


DeepCoreSeedGenerator::DeepCoreSeedGenerator(const edm::ParameterSet& iConfig, const DeepCoreCache* cache)
    :

      vertices_(consumes<reco::VertexCollection>(iConfig.getParameter<edm::InputTag>("vertices"))),
      pixelClusters_(
          consumes<edmNew::DetSetVector<SiPixelCluster>>(iConfig.getParameter<edm::InputTag>("pixelClusters"))),
      cores_(consumes<edm::View<reco::Candidate>>(iConfig.getParameter<edm::InputTag>("cores"))),
      topoToken_(esConsumes<TrackerTopology, TrackerTopologyRcd>()),
      ptMin_(iConfig.getParameter<double>("ptMin")),
      deltaR_(iConfig.getParameter<double>("deltaR")),
      chargeFracMin_(iConfig.getParameter<double>("chargeFractionMin")),
      centralMIPCharge_(iConfig.getParameter<double>("centralMIPCharge")),
      pixelCPE_(iConfig.getParameter<std::string>("pixelCPE")),
      weightfilename_(iConfig.getParameter<edm::FileInPath>("weightFile").fullPath()),
      inputTensorName_(iConfig.getParameter<std::vector<std::string>>("inputTensorName")),
      outputTensorName_(iConfig.getParameter<std::vector<std::string>>("outputTensorName")),
      // nThreads(iConfig.getParameter<unsigned int>("nThreads")),
      // singleThreadPool(iConfig.getParameter<std::string>("singleThreadPool")),
      probThr(iConfig.getParameter<double>("probThr")),
      session_(tensorflow::createSession(cache->graph_def))

{
  produces<TrajectorySeedCollection>();
  produces<reco::TrackCollection>();
}

DeepCoreSeedGenerator::~DeepCoreSeedGenerator() {}

void DeepCoreSeedGenerator::produce(edm::Event& iEvent, const edm::EventSetup& iSetup) {
  auto result = std::make_unique<TrajectorySeedCollection>();
  auto resultTracks = std::make_unique<reco::TrackCollection>();

  tensorflow::setLogging("3");
  // graph_ = tensorflow::loadGraphDef(weightfilename_);
  // tensorflow::SessionOptions sessionOptions;
  // tensorflow::setThreading(sessionOptions, nThreads, singleThreadPool);
  // session_ = tensorflow::createSession(graph_, sessionOptions);
  const tensorflow::TensorShape input_size_eta({1, 1});
  const tensorflow::TensorShape input_size_pt({1, 1});
  const tensorflow::TensorShape input_size_cluster({1, jetDimX, jetDimY, Nlayer});
  std::vector<std::string> output_names;
  output_names.push_back(outputTensorName_[0]);
  output_names.push_back(outputTensorName_[1]);

  using namespace edm;
  using namespace reco;

  iSetup.get<IdealMagneticFieldRecord>().get(magfield_);
  iSetup.get<GlobalTrackingGeometryRecord>().get(geometry_);
  iSetup.get<TrackingComponentsRecord>().get("AnalyticalPropagator", propagator_);

  // iEvent.getByToken(pixelClusters_, inputPixelClusters);
  const auto& inputPixelClusters = iEvent.get(pixelClusters_);
  allSiPixelClusters.clear();
  // siPixelDetsWithClusters.clear();
  allSiPixelClusters.reserve(
      // inputPixelClusters->dataSize());  // this is important, otherwise push_back invalidates the iterators
      inputPixelClusters.dataSize());  // this is important, otherwise push_back invalidates the iterators

  // Handle<std::vector<reco::Vertex>> vertices;
  // iEvent.getByToken(vertices_, vertices);
  const auto& vertices = iEvent.get(vertices_);


  // Handle<edm::View<reco::Candidate>> cores;
  // iEvent.getByToken(cores_, cores);
  const auto& cores = iEvent.get(cores_);

  edm::ESHandle<PixelClusterParameterEstimator> pixelCPEhandle;
  const PixelClusterParameterEstimator* pixelCPE;
  iSetup.get<TkPixelCPERecord>().get(pixelCPE_, pixelCPEhandle);
  pixelCPE = pixelCPEhandle.product();

  // edm::ESHandle<TrackerTopology> tTopoHandle;
  // iSetup.get<TrackerTopologyRcd>().get(tTopoHandle);
  // const TrackerTopology* const tTopo = tTopoHandle.product();
  // auto topoToken_ = esConsumes<TrackerTopology, TrackerTopologyRcd>();
  const TrackerTopology* const tTopo = &iSetup.getData(topoToken_);

  auto output = std::make_unique<edmNew::DetSetVector<SiPixelCluster>>();

  // for (unsigned int ji = 0; ji < cores.size(); ji++) {  //loop jet
  for (const auto& jet : cores) {

    if (jet.pt() > ptMin_) {
      std::set<long long int> ids;
      // const reco::Candidate& jet = (cores)[ji];
      const reco::Vertex& jetVertex = vertices[0];

      std::vector<GlobalVector> splitClustDirSet = splittedClusterDirections(jet, tTopo, pixelCPE, jetVertex, 1,inputPixelClusters);
      bool l2off = (splitClustDirSet.empty());
      if (splitClustDirSet.empty()) {  //if layer 1 is broken find direcitons on layer 2
        splitClustDirSet = splittedClusterDirections(jet, tTopo, pixelCPE, jetVertex, 2,inputPixelClusters);
      }
      splitClustDirSet.emplace_back(GlobalVector(jet.px(), jet.py(), jet.pz()));
      for (int cc = 0; cc < (int)splitClustDirSet.size(); cc++) {

        tensorflow::NamedTensorList input_tensors;//TensorFlow session setup (2/2)
        input_tensors.resize(3);
        input_tensors[0] =
            tensorflow::NamedTensor(inputTensorName_[0], tensorflow::Tensor(tensorflow::DT_FLOAT, input_size_eta));
        input_tensors[1] =
            tensorflow::NamedTensor(inputTensorName_[1], tensorflow::Tensor(tensorflow::DT_FLOAT, input_size_pt));
        input_tensors[2] = tensorflow::NamedTensor(inputTensorName_[2],
                                                   tensorflow::Tensor(tensorflow::DT_FLOAT, {input_size_cluster}));

        //put all the input tensor to 0
        input_tensors[0].second.matrix<float>()(0, 0) = 0.0;
        input_tensors[1].second.matrix<float>()(0, 0) = 0.0;
        for (int x = 0; x < jetDimX; x++) {
          for (int y = 0; y < jetDimY; y++) {
            for (int l = 0; l < 4; l++) {
              input_tensors[2].second.tensor<float, 4>()(0, x, y, l) = 0.0;
            }
          }
        } //end of TensorFlow session setup

        GlobalVector bigClustDir = splitClustDirSet[cc];

        // const LocalPoint jetInter(0, 0, 0);

        jet_eta = jet.eta();
        jet_pt = jet.pt();
        input_tensors[0].second.matrix<float>()(0, 0) = jet.eta();
        input_tensors[1].second.matrix<float>()(0, 0) = jet.pt();

        // edmNew::DetSetVector<SiPixelCluster>::const_iterator detIt = inputPixelClusters->begin();

        const GeomDet* globDet =
            DetectorSelector(2, jet, bigClustDir, jetVertex, tTopo, inputPixelClusters);  //select detector mostly hitten by the jet

        if (globDet == nullptr) //no intersection between bigClustDir and pixel detector modules found
          continue;

        const GeomDet* goodDet1 = DetectorSelector(1, jet, bigClustDir, jetVertex, tTopo, inputPixelClusters);
        const GeomDet* goodDet3 = DetectorSelector(3, jet, bigClustDir, jetVertex, tTopo, inputPixelClusters);
        const GeomDet* goodDet4 = DetectorSelector(4, jet, bigClustDir, jetVertex, tTopo, inputPixelClusters);

        // for (; detIt != inputPixelClusters->end(); detIt++) {  //loop deset
        // for (const auto& detset : inputPixelClusters){
        for (const auto& detset : inputPixelClusters){
          // const edmNew::DetSet<SiPixelCluster>& detset = *detIt;
          const GeomDet* det =
              geometry_->idToDet(detset.id());  //lui sa il layer con cast a  PXBDetId (vedi dentro il layer function)

          // for (auto cluster = detset.begin(); cluster != detset.end(); cluster++) {  //loop cluster
          for (const auto& aCluster : detset){

            // const SiPixelCluster& aCluster = *cluster;
            det_id_type aClusterID = detset.id();
            if (DetId(aClusterID).subdetId() != 1)
              continue;

            int lay = tTopo->layer(det->geographicalId());

            std::pair<bool, Basic3DVector<float>> interPair =
                findIntersection(bigClustDir, (reco::Candidate::Point)jetVertex.position(), det);
            if (interPair.first == false)
              continue;
            Basic3DVector<float> inter = interPair.second;
            auto localInter = det->specificSurface().toLocal((GlobalPoint)inter);

            GlobalPoint pointVertex(jetVertex.position().x(), jetVertex.position().y(), jetVertex.position().z());

            // LocalPoint clustPos_local = pixelCPE->localParametersV(aCluster, (*geometry_->idToDetUnit(detIt->id())))[0].first;
            LocalPoint clustPos_local = pixelCPE->localParametersV(aCluster, (*geometry_->idToDetUnit(detset.id())))[0].first;

            if (std::abs(clustPos_local.x() - localInter.x()) / pitchX <= jetDimX / 2 &&
                std::abs(clustPos_local.y() - localInter.y()) / pitchY <=
                    jetDimY / 2) {  //used the baricenter, better description maybe useful

              if (det == goodDet1 || det == goodDet3 || det == goodDet4 || det == globDet) {
                fillPixelMatrix(aCluster, lay, localInter, det, input_tensors);
              }
            }  //cluster in ROI
          }    //cluster
        }      //detset

        //here the NN produce the seed from the filled input
        std::pair<double[jetDimX][jetDimY][Nover][Npar], double[jetDimX][jetDimY][Nover]> seedParamNN =
            DeepCoreSeedGenerator::SeedEvaluation(input_tensors,output_names);

        for (int i = 0; i < jetDimX; i++) {
          for (int j = 0; j < jetDimY; j++) {
            for (int o = 0; o < Nover; o++) {
              // if (seedParamNN.second[i][j][o] > (0.85 - o * 0.1 - (l2off ? 0.35 : 0))) {
              if (seedParamNN.second[i][j][o] > (probThr - o * 0.1 - (l2off ? 0.35 : 0))) {
                std::pair<bool, Basic3DVector<float>> interPair =
                    findIntersection(bigClustDir, (reco::Candidate::Point)jetVertex.position(), globDet);
                auto localInter = globDet->specificSurface().toLocal((GlobalPoint)interPair.second);

                int flip = pixelFlipper(globDet);  // 1=not flip, -1=flip
                int nx = i - jetDimX / 2;
                int ny = j - jetDimY / 2;
                nx = flip * nx;
                std::pair<int, int> pixInter = local2Pixel(localInter.x(), localInter.y(), globDet);
                nx = nx + pixInter.first;
                ny = ny + pixInter.second;
                LocalPoint xyLocal = pixel2Local(nx, ny, globDet);

                double xx = xyLocal.x() + seedParamNN.first[i][j][o][0] * 0.01; //0.01=internal normalization of NN
                double yy = xyLocal.y() + seedParamNN.first[i][j][o][1] * 0.01; //0.01=internal normalization of NN
                LocalPoint localSeedPoint = LocalPoint(xx, yy, 0);

                double track_eta =
                    seedParamNN.first[i][j][o][2] * 0.01 + bigClustDir.eta();  //NOT SURE ABOUT THIS 0.01, only to debug
                double track_theta = 2 * std::atan(std::exp(-track_eta));
                double track_phi =
                    seedParamNN.first[i][j][o][3] * 0.01 + bigClustDir.phi();  //NOT SURE ABOUT THIS 0.01, only to debug

                double pt = 1. / seedParamNN.first[i][j][o][4];
                double normdirR = pt / sin(track_theta);

                const GlobalVector globSeedDir(
                    GlobalVector::Polar(Geom::Theta<double>(track_theta), Geom::Phi<double>(track_phi), normdirR));
                LocalVector localSeedDir = globDet->surface().toLocal(globSeedDir);
                int64_t seedid = (int64_t(xx * 200.) << 0) + (int64_t(yy * 200.) << 16) +
                                 (int64_t(track_eta * 400.) << 32) + (int64_t(track_phi * 400.) << 48);
                if (ids.count(seedid) != 0) {
                  continue;
                }
                if (true) {  //1 TO JET CORE; 0=NO JET CORE (seeding iteration skipped, useful to total eff and FakeRate comparison)
                  ids.insert(seedid);

                  //Covariance matrix, the hadrcoded variances = NN residuals width (see documentation of DeepCore)
                  float em[15] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};// (see LocalTrajectoryError for details), order as follow:
                  em[0] = 0.15 * 0.15;  // q/pt
                  em[2] = 0.5e-5;       // dxdz
                  em[5] = 0.5e-5;       // dydz
                  em[9] = 2e-5;         // x
                  em[14] = 2e-5;        // y
                  long int detId = globDet->geographicalId();
                  LocalTrajectoryParameters localParam(localSeedPoint, localSeedDir, TrackCharge(1));
                  result->emplace_back(TrajectorySeed(PTrajectoryStateOnDet(localParam, pt, em, detId, /*surfaceSide*/ 0),
                                                   edm::OwnVector<TrackingRecHit>(),
                                                   PropagationDirection::alongMomentum));

                  GlobalPoint globalSeedPoint = globDet->surface().toGlobal(localSeedPoint);
                  reco::Track::CovarianceMatrix mm;
                  resultTracks->emplace_back(
                      reco::Track(1,
                                  1,
                                  reco::Track::Point(globalSeedPoint.x(), globalSeedPoint.y(), globalSeedPoint.z()),
                                  reco::Track::Vector(globSeedDir.x(), globSeedDir.y(), globSeedDir.z()),
                                  1,
                                  mm));
                }
              }
            }
          }
        }
      }  //bigcluster
    }    //jet > pt
  }      //jet
  iEvent.put(std::move(result));
  iEvent.put(std::move(resultTracks));
}

std::pair<bool, Basic3DVector<float>> DeepCoreSeedGenerator::findIntersection(const GlobalVector& dir,
                                                                              const reco::Candidate::Point& vertex,
                                                                              const GeomDet* det) {
  StraightLinePlaneCrossing vertexPlane(Basic3DVector<float>(vertex.x(), vertex.y(), vertex.z()),
                                        Basic3DVector<float>(dir.x(), dir.y(), dir.z()));

  std::pair<bool, Basic3DVector<float>> pos = vertexPlane.position(det->specificSurface());

  return pos;
}

std::pair<int, int> DeepCoreSeedGenerator::local2Pixel(double locX, double locY, const GeomDet* det) {
  LocalPoint locXY(locX, locY);
  float pixX = (dynamic_cast<const PixelGeomDetUnit*>(det))->specificTopology().pixel(locXY).first;
  float pixY = (dynamic_cast<const PixelGeomDetUnit*>(det))->specificTopology().pixel(locXY).second;
  std::pair<int, int> out(pixX, pixY);
  return out;
}

LocalPoint DeepCoreSeedGenerator::pixel2Local(int pixX, int pixY, const GeomDet* det) {
  float locX = (dynamic_cast<const PixelGeomDetUnit*>(det))->specificTopology().localX(pixX);
  float locY = (dynamic_cast<const PixelGeomDetUnit*>(det))->specificTopology().localY(pixY);
  LocalPoint locXY(locX, locY);
  return locXY;
}

int DeepCoreSeedGenerator::pixelFlipper(const GeomDet* det) {
  int out = 1;
  LocalVector locZdir(0, 0, 1);
  GlobalVector globZdir = det->specificSurface().toGlobal(locZdir);
  const GlobalPoint& globDetCenter = det->position();
  float direction =
      globZdir.x() * globDetCenter.x() + globZdir.y() * globDetCenter.y() + globZdir.z() * globDetCenter.z();
  if (direction < 0)
    out = -1;
  return out;
}

void DeepCoreSeedGenerator::fillPixelMatrix(
    const SiPixelCluster& cluster,
    int layer,
    Point3DBase<float, LocalTag> inter,
    const GeomDet* det,
    tensorflow::NamedTensorList input_tensors) {

  int flip = pixelFlipper(det);  // 1=not flip, -1=flip

  for (int i = 0; i < cluster.size(); i++) {
    SiPixelCluster::Pixel pix = cluster.pixel(i);
    std::pair<int, int> pixInter = local2Pixel(inter.x(), inter.y(), det);
    int nx = pix.x - pixInter.first;
    int ny = pix.y - pixInter.second;
    nx = flip * nx;

    if (abs(nx) < jetDimX / 2 && abs(ny) < jetDimY / 2) {
      nx = nx + jetDimX / 2;
      ny = ny + jetDimY / 2;
      //14000 = normalization of ACD counts used in the NN
      input_tensors[2].second.tensor<float, 4>()(0, nx, ny, layer - 1) += (pix.adc) / (14000.f);
    }
  }
}

// std::pair<double[jetDimX][jetDimY][Nover][Npar], double[jetDimX][jetDimY][Nover]> DeepCoreSeedGenerator::SeedEvaluation(
std::pair<double[DeepCoreSeedGenerator::jetDimX][DeepCoreSeedGenerator::jetDimY][DeepCoreSeedGenerator::Nover]
                [DeepCoreSeedGenerator::Npar],
          double[DeepCoreSeedGenerator::jetDimX][DeepCoreSeedGenerator::jetDimY][DeepCoreSeedGenerator::Nover]>
DeepCoreSeedGenerator::SeedEvaluation(tensorflow::NamedTensorList input_tensors, std::vector<std::string> output_names) {
  std::vector<tensorflow::Tensor> outputs;
  // std::vector<std::string> output_names;
  // output_names.push_back(outputTensorName_[0]);
  // output_names.push_back(outputTensorName_[1]);
  tensorflow::run(session_, input_tensors, output_names, &outputs);
  auto matrix_output_par = outputs.at(0).tensor<float, 5>();
  auto matrix_output_prob = outputs.at(1).tensor<float, 5>();

  std::pair<double[jetDimX][jetDimY][Nover][Npar], double[jetDimX][jetDimY][Nover]> output_combined;

  for (int x = 0; x < jetDimX; x++) {
    for (int y = 0; y < jetDimY; y++) {
      for (int trk = 0; trk < Nover; trk++) {
        output_combined.second[x][y][trk] =
            matrix_output_prob(0, x, y, trk, 0);  //outputs.at(1).matrix<double>()(0,x,y,trk);

        for (int p = 0; p < Npar; p++) {
          output_combined.first[x][y][trk][p] =
              matrix_output_par(0, x, y, trk, p);  //outputs.at(0).matrix<double>()(0,x,y,trk,p);
        }
      }
    }
  }
  return output_combined;
}

const GeomDet* DeepCoreSeedGenerator::DetectorSelector(int llay,
                                                       const reco::Candidate& jet,
                                                       GlobalVector jetDir,
                                                       const reco::Vertex& jetVertex,
                                                       const TrackerTopology* const tTopo,
                                                       const edmNew::DetSetVector<SiPixelCluster>& clusters) {
  struct trkNumCompare {
    bool operator()(std::pair<int, const GeomDet*> x, std::pair<int, const GeomDet*> y) const {
      return x.first > y.first;
    }
  };

  std::set<std::pair<int, const GeomDet*>, trkNumCompare> track4detSet;

  // const LocalPoint jetInter(0, 0, 0);

  // edmNew::DetSetVector<SiPixelCluster>::const_iterator detIt = inputPixelClusters->begin();

  double minDist = 0.0;
  GeomDet* output = (GeomDet*)nullptr;

  // for (; detIt != inputPixelClusters->end(); detIt++) {  //loop deset
  for (const auto& detset : clusters){

    // const edmNew::DetSet<SiPixelCluster>& detset = *detIt;
    const GeomDet* det = geometry_->idToDet(detset.id());
    // for (auto cluster = detset.begin(); cluster != detset.end(); cluster++) {  //loop cluster
     for (const auto& cluster : detset){
      auto aClusterID = detset.id();
      if (DetId(aClusterID).subdetId() != 1)
        continue;
      int lay = tTopo->layer(det->geographicalId());
      if (lay != llay)
        continue;
      std::pair<bool, Basic3DVector<float>> interPair =
          findIntersection(jetDir, (reco::Candidate::Point)jetVertex.position(), det);
      if (interPair.first == false)
        continue;
      Basic3DVector<float> inter = interPair.second;
      auto localInter = det->specificSurface().toLocal((GlobalPoint)inter);
      if ((minDist == 0.0 || std::abs(localInter.x()) < minDist) && std::abs(localInter.y()) < 3.35) {
        minDist = std::abs(localInter.x());
        output = (GeomDet*)det;
      }
    }  //cluster
  }    //detset
  return output;
}
std::vector<GlobalVector> DeepCoreSeedGenerator::splittedClusterDirections(const reco::Candidate& jet,
                                                                           const TrackerTopology* const tTopo,
                                                                           const PixelClusterParameterEstimator* pixelCPE,
                                                                           const reco::Vertex& jetVertex,
                                                                           int layer,
                                                                           const edmNew::DetSetVector<SiPixelCluster>& clusters) {
  std::vector<GlobalVector> clustDirs;

  // edmNew::DetSetVector<SiPixelCluster>::const_iterator detIt_int = inputPixelClusters->begin();

  // for (; detIt_int != inputPixelClusters->end(); detIt_int++) {
  for (const auto& detset_int : clusters){
    // const edmNew::DetSet<SiPixelCluster>& detset_int = *detIt_int;
    const GeomDet* det_int = geometry_->idToDet(detset_int.id());
    int lay = tTopo->layer(det_int->geographicalId());
    if (lay != layer)
      continue;  //NB: saved bigClusters on all the layers!!

    // for (auto cluster = detset_int.begin(); cluster != detset_int.end(); cluster++) {
    for (const auto& aCluster : detset_int){
      // const SiPixelCluster& aCluster = *cluster;
      GlobalPoint clustPos = det_int->surface().toGlobal(
          // pixelCPE->localParametersV(aCluster, (*geometry_->idToDetUnit(detIt_int->id())))[0].first);
          pixelCPE->localParametersV(aCluster, (*geometry_->idToDetUnit(detset_int.id())))[0].first);
      GlobalPoint vertexPos(jetVertex.position().x(), jetVertex.position().y(), jetVertex.position().z());
      GlobalVector clusterDir = clustPos - vertexPos;
      GlobalVector jetDir(jet.px(), jet.py(), jet.pz());
      if (Geom::deltaR(jetDir, clusterDir) < deltaR_) {
        clustDirs.emplace_back(clusterDir);
      }
    }
  }
  return clustDirs;
}

std::unique_ptr<DeepCoreCache> DeepCoreSeedGenerator::initializeGlobalCache(const edm::ParameterSet& iConfig) {
  // this method is supposed to create, initialize and return a DeepCoreCache instance
  std::unique_ptr<DeepCoreCache> cache = std::make_unique<DeepCoreCache>();
  // std::string graphPath = iConfig.getParameter<std::string>("weightfilename_");
  std::string graphPath = iConfig.getParameter<edm::FileInPath>("weightFile").fullPath();
  cache->graph_def = tensorflow::loadGraphDef(graphPath);
  return cache;
}

void DeepCoreSeedGenerator::globalEndJob(DeepCoreCache* cache) { delete cache->graph_def; }

// ------------ method called once each job just before starting event loop  ------------
void DeepCoreSeedGenerator::beginJob() {}

// ------------ method called once each job just after ending the event loop  ------------
void DeepCoreSeedGenerator::endJob() {}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void DeepCoreSeedGenerator::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  edm::ParameterSetDescription desc;
  desc.add<edm::InputTag>("vertices", edm::InputTag("offlinePrimaryVertices"));
  desc.add<edm::InputTag>("pixelClusters", edm::InputTag("siPixelClustersPreSplitting"));
  desc.add<edm::InputTag>("cores", edm::InputTag("jetsForCoreTracking"));
  desc.add<double>("ptMin", 300);
  desc.add<double>("deltaR", 0.1);
  desc.add<double>("chargeFractionMin", 18000.0);
  desc.add<double>("centralMIPCharge", 2);
  desc.add<std::string>("pixelCPE", "PixelCPEGeneric");
  desc.add<edm::FileInPath>("weightFile",
                            edm::FileInPath("RecoTracker/TkSeedGenerator/data/DeepCoreSeedGenerator_TrainedModel.pb"));
  desc.add<std::vector<std::string>>("inputTensorName", {"input_1", "input_2", "input_3"});
  desc.add<std::vector<std::string>>("outputTensorName", {"output_node0", "output_node1"});
  // desc.add<unsigned>("nThreads", 1);
  // desc.add<std::string>("singleThreadPool", "no_threads");
  desc.add<double>("probThr", 0.85);
  descriptions.addDefault(desc);
}

//define this as a plug-in
// DEFINE_FWK_MODULE(DeepCoreSeedGenerator);
