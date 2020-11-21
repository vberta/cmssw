import FWCore.ParameterSet.Config as cms

MessageLogger = cms.Service("MessageLogger",
    suppressInfo = cms.untracked.vstring(),
    suppressFwkInfo = cms.untracked.vstring(),
    suppressDebug = cms.untracked.vstring(),
    cout = cms.untracked.PSet(
        placeholder = cms.untracked.bool(True)
    ),
    default = cms.untracked.PSet(

    ),
    cerr = cms.untracked.PSet(
        optionalPSet = cms.untracked.bool(True),
        INFO = cms.untracked.PSet(
            limit = cms.untracked.int32(0)
        ),
        noTimeStamps = cms.untracked.bool(False),
        FwkReport = cms.untracked.PSet(
            optionalPSet = cms.untracked.bool(True),
            reportEvery = cms.untracked.int32(1),
            limit = cms.untracked.int32(10000000)
        ),
        default = cms.untracked.PSet(
            limit = cms.untracked.int32(10000000)
        ),
        Root_NoDictionary = cms.untracked.PSet(
            optionalPSet = cms.untracked.bool(True),
            limit = cms.untracked.int32(0)
        ),
        FwkSummary = cms.untracked.PSet(
            optionalPSet = cms.untracked.bool(True),
            reportEvery = cms.untracked.int32(1),
            limit = cms.untracked.int32(10000000)
        ),
        threshold = cms.untracked.string('INFO')
    ),
    suppressWarning = cms.untracked.vstring(),
    statistics = cms.untracked.vstring('cerr_stats'),
    cerr_stats = cms.untracked.PSet(
        optionalPSet = cms.untracked.bool(True),
        threshold = cms.untracked.string('WARNING'),
        output = cms.untracked.string('cerr')
    ),
    destinations = cms.untracked.vstring(
        'cout', 
        'cerr'),
    debugModules = cms.untracked.vstring(),
    categories = cms.untracked.vstring('FwkReport', 
        'FwkSummary', 
        'Root_NoDictionary')
)


