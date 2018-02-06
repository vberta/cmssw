import FWCore.ParameterSet.Config as cms

process = cms.Process("Demo")

process.load("FWCore.MessageService.MessageLogger_cfi")
process.load("Configuration.StandardSequences.GeometryDB_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
# process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryDB_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.StandardSequences.RawToDigi_cff')
process.load('Configuration.StandardSequences.Reconstruction_cff')
# process.load('Configuration.StandardSequences.EndOfProcess_cff')
# process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
# process.load("SimGeneral.MixingModule.mixNoPU_cfi")
# process.load('Configuration/StandardSequences/Simulation_cff')
# process.load('Configuration/StandardSequences/SimL1Emulator_cff')
# process.load('Configuration/StandardSequences/DigiToRaw_cff')
# process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')


from Configuration.AlCa.autoCond import autoCond
process.GlobalTag.globaltag = autoCond['run2_mc']

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(1) ) #-1 = tutti

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(
        'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16DR80Premix/QCD_Pt_3200toInf_TuneCUETP8M1_13TeV_pythia8/GEN-SIM-RECODEBUG/PREMIX_RECODEBUG_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/130000/1876E67B-E6AE-E611-8A1A-0CC47A4D765A.root'
    )
)


process.demo = cms.EDProducer('PxdMap' ,#demo = nome libero
 pixelClusters=cms.InputTag("siPixelClusters"),
 vertices = cms.InputTag("offlinePrimaryVertices"),
 cores = cms.InputTag("ak4PFJetsCHS"),
 ptMin = cms.double(800), #800
)

process.TFileService = cms.Service("TFileService",
      fileName = cms.string("histo.root"),
      closeFileFast = cms.untracked.bool(True)
  )


process.p = cms.Path(process.demo

) #process-demo + process.altrodemo + .... (se ne ho diversi)
