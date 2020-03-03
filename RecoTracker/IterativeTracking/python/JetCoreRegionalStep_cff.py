import FWCore.ParameterSet.Config as cms

# This step runs over all clusters

# run only if there are high pT jets
jetsForCoreTracking = cms.EDFilter("CandPtrSelector", src = cms.InputTag("ak4CaloJetsForTrk"), cut = cms.string("pt > 100 && abs(eta) < 2.5"))

# care only at tracks from main PV
firstStepGoodPrimaryVertices = cms.EDFilter("PrimaryVertexObjectFilter",
     filterParams = cms.PSet(
     	     minNdof = cms.double(25.0),
             maxZ = cms.double(15.0),
             maxRho = cms.double(2.0)
     ),
     src=cms.InputTag('firstStepPrimaryVertices')
)

# SEEDING LAYERS
jetCoreRegionalStepSeedLayers = cms.EDProducer("SeedingLayersEDProducer",
    layerList = cms.vstring('BPix1+BPix2', 'BPix1+BPix3', 'BPix2+BPix3',
                            'BPix1+FPix1_pos', 'BPix1+FPix1_neg',
                            'BPix2+FPix1_pos', 'BPix2+FPix1_neg',
                            'FPix1_pos+FPix2_pos', 'FPix1_neg+FPix2_neg',
                            #'BPix2+TIB1','BPix2+TIB2',
                            'BPix3+TIB1','BPix3+TIB2'),
    TIB = cms.PSet(
        matchedRecHits = cms.InputTag("siStripMatchedRecHits","matchedRecHit"),
        TTRHBuilder = cms.string('WithTrackAngle'), clusterChargeCut = cms.PSet(refToPSet_ = cms.string('SiStripClusterChargeCutNone'))
    ),
    BPix = cms.PSet(
        useErrorsFromParam = cms.bool(True),
        hitErrorRPhi = cms.double(0.0027),
        hitErrorRZ = cms.double(0.006),
        TTRHBuilder = cms.string('WithTrackAngle'),
        HitProducer = cms.string('siPixelRecHits'),
        #skipClusters = cms.InputTag('jetCoreRegionalStepClusters')
    ),
    FPix = cms.PSet(
        useErrorsFromParam = cms.bool(True),
        hitErrorRPhi = cms.double(0.0051),
        hitErrorRZ = cms.double(0.0036),
        TTRHBuilder = cms.string('WithTrackAngle'),
        HitProducer = cms.string('siPixelRecHits'),
        #skipClusters = cms.InputTag('jetCoreRegionalStepClusters')
    )
)
from Configuration.Eras.Modifier_trackingPhase1_cff import trackingPhase1
_layerListForPhase1 = [
        'BPix1+BPix2', 'BPix1+BPix3', 'BPix1+BPix4',
        'BPix2+BPix3', 'BPix2+BPix4',
        'BPix3+BPix4',
        'BPix1+FPix1_pos', 'BPix1+FPix1_neg',
        'BPix2+FPix1_pos', 'BPix2+FPix1_neg',
        'FPix1_pos+FPix2_pos', 'FPix1_neg+FPix2_neg',
        'FPix1_pos+FPix3_pos', 'FPix1_neg+FPix3_neg',
        'FPix2_pos+FPix3_pos', 'FPix2_neg+FPix3_neg',
        #'BPix3+TIB1','BPix3+TIB2'
        'BPix4+TIB1','BPix4+TIB2'
    ]
trackingPhase1.toModify(jetCoreRegionalStepSeedLayers, layerList = _layerListForPhase1)

# TrackingRegion
from RecoTauTag.HLTProducers.tauRegionalPixelSeedTrackingRegions_cfi import tauRegionalPixelSeedTrackingRegions as _tauRegionalPixelSeedTrackingRegions
jetCoreRegionalStepTrackingRegions = _tauRegionalPixelSeedTrackingRegions.clone(RegionPSet=dict(
    ptMin = 10,
    deltaPhiRegion = 0.20,
    deltaEtaRegion = 0.20,
    JetSrc = "jetsForCoreTracking",
    vertexSrc = "firstStepGoodPrimaryVertices",
    howToUseMeasurementTracker = "Never"
))

# Seeding
from RecoTracker.TkHitPairs.hitPairEDProducer_cfi import hitPairEDProducer as _hitPairEDProducer
jetCoreRegionalStepHitDoublets = _hitPairEDProducer.clone(
    seedingLayers = "jetCoreRegionalStepSeedLayers",
    trackingRegions = "jetCoreRegionalStepTrackingRegions",
    produceSeedingHitSets = True,
    maxElementTotal = 12000000,
)
from RecoTracker.TkSeedGenerator.seedCreatorFromRegionConsecutiveHitsEDProducer_cff import seedCreatorFromRegionConsecutiveHitsEDProducer as _seedCreatorFromRegionConsecutiveHitsEDProducer
jetCoreRegionalStepSeeds = _seedCreatorFromRegionConsecutiveHitsEDProducer.clone(
    seedingHitSets = "jetCoreRegionalStepHitDoublets",
    forceKinematicWithRegionDirection = True
)

# QUALITY CUTS DURING TRACK BUILDING
import TrackingTools.TrajectoryFiltering.TrajectoryFilter_cff
jetCoreRegionalStepTrajectoryFilter = TrackingTools.TrajectoryFiltering.TrajectoryFilter_cff.CkfBaseTrajectoryFilter_block.clone(
    minPt = 0.1,
    maxCCCLostHits = cms.int32(9999),
    maxConsecLostHits = cms.int32(2),
    maxLostHits = cms.int32(999),
    maxLostHitsFraction = cms.double(1.1),
    maxNumberOfHits = cms.int32(100),
    minimumNumberOfHits = cms.int32(2),
    pixelSeedExtension = cms.bool(False),
    seedExtension = cms.int32(0),
    seedPairPenalty = cms.int32(0),
    strictSeedExtension = cms.bool(False)

)

from Configuration.Eras.Modifier_pp_on_XeXe_2017_cff import pp_on_XeXe_2017
from Configuration.Eras.Modifier_pp_on_AA_2018_cff import pp_on_AA_2018
for e in [pp_on_XeXe_2017, pp_on_AA_2018]:
    e.toModify(jetCoreRegionalStepTrajectoryFilter, minPt=5.0)

import TrackingTools.KalmanUpdators.Chi2MeasurementEstimator_cfi
jetCoreRegionalStepChi2Est = TrackingTools.KalmanUpdators.Chi2MeasurementEstimator_cfi.Chi2MeasurementEstimator.clone(
    ComponentName = cms.string('jetCoreRegionalStepChi2Est'),
    nSigma = cms.double(3.0),
    MaxChi2 = cms.double(30.0)
)

# TRACK BUILDING
import RecoTracker.CkfPattern.GroupedCkfTrajectoryBuilder_cfi
#need to also load the refToPSet_ used by GroupedCkfTrajectoryBuilder
CkfBaseTrajectoryFilter_block = RecoTracker.CkfPattern.GroupedCkfTrajectoryBuilder_cfi.CkfBaseTrajectoryFilter_block
jetCoreRegionalStepTrajectoryBuilder = RecoTracker.CkfPattern.GroupedCkfTrajectoryBuilder_cfi.GroupedCkfTrajectoryBuilder.clone(
    MeasurementTrackerName = '',
    trajectoryFilter = cms.PSet(refToPSet_ = cms.string('jetCoreRegionalStepTrajectoryFilter')),
    maxCand = 50,
    estimator = cms.string('jetCoreRegionalStepChi2Est'),
    maxDPhiForLooperReconstruction = cms.double(2.0),
    maxPtForLooperReconstruction = cms.double(0),
    keepOriginalIfRebuildFails = True,
    lockHits = False,
    requireSeedHitsInRebuild = False,

    )


#customized cleaner
trajectoryCleanerBySharedHits_JetCore = cms.ESProducer("TrajectoryCleanerESProducer",
    ComponentName = cms.string('jetCoreTrajectoryCleanerBySharedHits'),
    ComponentType = cms.string('TrajectoryCleanerBySharedHits'),
    MissingHitPenalty = cms.double(20.0),
    ValidHitBonus = cms.double(5.0),
    allowSharedFirstHit = cms.bool(True),
    fractionShared = cms.double(0.45)
)

CkfBaseTrajectoryFilter_blockLoose = cms.PSet(
    ComponentType = cms.string('CkfBaseTrajectoryFilter'),
    chargeSignificance = cms.double(-1.0),
    constantValueForLostHitsFractionFilter = cms.double(2.0),
    extraNumberOfHitsBeforeTheFirstLoop = cms.int32(4),
    maxCCCLostHits = cms.int32(9999),
    maxConsecLostHits = cms.int32(2),
    maxLostHits = cms.int32(999),
    maxLostHitsFraction = cms.double(1.1),
    maxNumberOfHits = cms.int32(100),
    minGoodStripCharge = cms.PSet(
        refToPSet_ = cms.string('SiStripClusterChargeCutNone')
    ),
    minHitsMinPt = cms.int32(3),
    minNumberOfHitsForLoopers = cms.int32(13),
    minNumberOfHitsPerLoop = cms.int32(4),
    minPt = cms.double(0.9),
    minimumNumberOfHits = cms.int32(2),
    nSigmaMinPt = cms.double(5.0),
    pixelSeedExtension = cms.bool(False),
    seedExtension = cms.int32(0),
    seedPairPenalty = cms.int32(0),
    strictSeedExtension = cms.bool(False)
)



import RecoTracker.TkSeedGenerator.jetCoreDirectSeedGenerator_cfi
import RecoTracker.TkSeedGenerator.jetCorePerfectSeedGenerator_cfi
jetCoreSeeds  = RecoTracker.TkSeedGenerator.jetCoreDirectSeedGenerator_cfi.jetCoreDirectSeedGenerator.clone(
# jetCoreSeeds  = RecoTracker.TkSeedGenerator.jetCorePerfectSeedGenerator_cfi.JetCorePerfectSeedGenerator.clone(
vertices="firstStepPrimaryVertices"
)

# MAKING OF TRACK CANDIDATES
import RecoTracker.CkfPattern.CkfTrackCandidates_cfi
jetCoreRegionalStepTrackCandidates = RecoTracker.CkfPattern.CkfTrackCandidates_cfi.ckfTrackCandidates.clone(
    # src = cms.InputTag('jetCoreRegionalStepSeeds'),
    src = cms.InputTag('jetCoreSeeds'),
    maxSeedsBeforeCleaning = cms.uint32(10000),
    TrajectoryBuilderPSet = cms.PSet( refToPSet_ = cms.string('jetCoreRegionalStepTrajectoryBuilder')),
    TrajectoryCleaner = 'jetCoreTrajectoryCleanerBySharedHits',
    NavigationSchool = cms.string('SimpleNavigationSchool'),
    ### these two parameters are relevant only for the CachingSeedCleanerBySharedInput
    #numHitsForSeedCleaner = cms.int32(50),
    #onlyPixelHitsForSeedCleaner = cms.bool(True),
)


# TRACK FITTING
import RecoTracker.TrackProducer.TrackProducer_cfi
jetCoreRegionalStepTracks = RecoTracker.TrackProducer.TrackProducer_cfi.TrackProducer.clone(
    AlgorithmName = cms.string('jetCoreRegionalStep'),
    src = 'jetCoreRegionalStepTrackCandidates',
    Fitter = cms.string('FlexibleKFFittingSmoother')
    )

from Configuration.Eras.Modifier_fastSim_cff import fastSim
import RecoTracker.FinalTrackSelectors.trackListMerger_cfi
_fastSim_jetCoreRegionalStepTracks = RecoTracker.FinalTrackSelectors.trackListMerger_cfi.trackListMerger.clone(
    TrackProducers = (),
    hasSelector=cms.vint32(),
    selectedTrackQuals = cms.VInputTag(),
    copyExtras = True
    )
fastSim.toReplaceWith(jetCoreRegionalStepTracks,_fastSim_jetCoreRegionalStepTracks)


# Final selection
from RecoTracker.IterativeTracking.InitialStep_cff import initialStepClassifier1
#from RecoTracker.IterativeTracking.DetachedTripletStep_cff import detachedTripletStepClassifier1

#jetCoreRegionalStep = initialStepClassifier1.clone()
#jetCoreRegionalStep.src='jetCoreRegionalStepTracks'
#jetCoreRegionalStep.qualityCuts = [-0.3,0.0,0.2]
#jetCoreRegionalStep.vertices = 'firstStepGoodPrimaryVertices'

#jetCoreRegionalStepClassifier1 = initialStepClassifier1.clone()
#jetCoreRegionalStepClassifier1.src = 'jetCoreRegionalStepTracks'
#jetCoreRegionalStepClassifier1.qualityCuts = [-0.2,0.0,0.4]
#jetCoreRegionalStepClassifier2 = detachedTripletStepClassifier1.clone()
#jetCoreRegionalStepClassifier2.src = 'jetCoreRegionalStepTracks'



#from RecoTracker.FinalTrackSelectors.ClassifierMerger_cfi import *
#jetCoreRegionalStep = ClassifierMerger.clone()
#jetCoreRegionalStep.inputClassifiers=['jetCoreRegionalStepClassifier1','jetCoreRegionalStepClassifier2']


from RecoTracker.FinalTrackSelectors.TrackCutClassifier_cff import *
jetCoreRegionalStep = TrackCutClassifier.clone()
jetCoreRegionalStep.src='jetCoreRegionalStepTracks'
jetCoreRegionalStep.mva.minPixelHits = [1,1,1]
jetCoreRegionalStep.mva.maxChi2 = [9999.,9999.,9999.]
jetCoreRegionalStep.mva.maxChi2n = [1.6,1.0,0.7]
jetCoreRegionalStep.mva.minLayers = [3,5,5]
jetCoreRegionalStep.mva.min3DLayers = [1,2,3]
jetCoreRegionalStep.mva.maxLostLayers = [4,3,2]
jetCoreRegionalStep.mva.maxDz = [0.5,0.35,0.2];
jetCoreRegionalStep.mva.maxDr = [0.3,0.2,0.1];
jetCoreRegionalStep.vertices = 'firstStepGoodPrimaryVertices'

from RecoTracker.FinalTrackSelectors.TrackMVAClassifierPrompt_cfi import *

fastSim.toModify(jetCoreRegionalStep,vertices = "firstStepPrimaryVerticesBeforeMixing")

#LWTNN selector
from RecoTracker.FinalTrackSelectors.TrackLwtnnClassifier_cfi import *
from RecoTracker.FinalTrackSelectors.trackSelectionLwtnn_cfi import *
trackingPhase1.toReplaceWith(jetCoreRegionalStep, TrackLwtnnClassifier.clone(
     src = 'jetCoreRegionalStepTracks',
     qualityCuts = [0.6, 0.7, 0.8],
))
(trackingPhase1 & fastSim).toModify(jetCoreRegionalStep,vertices = "firstStepPrimaryVerticesBeforeMixing")



# Final sequence
JetCoreRegionalStepTask = cms.Task(jetsForCoreTracking,
                                   firstStepGoodPrimaryVertices,
                                   #jetCoreRegionalStepClusters,
                                   jetCoreRegionalStepSeedLayers,
                                   jetCoreRegionalStepTrackingRegions,
                                   jetCoreRegionalStepHitDoublets,
                                   jetCoreRegionalStepSeeds,
                                   jetCoreSeeds,
                                   jetCoreRegionalStepTrackCandidates,
                                   jetCoreRegionalStepTracks,
#                                   jetCoreRegionalStepClassifier1,jetCoreRegionalStepClassifier2,
                                   jetCoreRegionalStep)
JetCoreRegionalStep = cms.Sequence(JetCoreRegionalStepTask)
fastSim.toReplaceWith(JetCoreRegionalStepTask,
                      cms.Task(jetCoreRegionalStepTracks,
                                   jetCoreRegionalStep))
