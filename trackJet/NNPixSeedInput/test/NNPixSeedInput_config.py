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


#from Configuration.AlCa.autoCond import autoCond

# from Configuration.AlCa.autoCond import autoCond
# process.GlobalTag.globaltag = autoCond['run2_mc']

process.GlobalTag.globaltag="94X_mc2017_realistic_v10"

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(1000) ) #-1 = tutti

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(
        #'https://cmsweb.cern.ch/das/request?input=file%20dataset%3D/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/RunIIFall17DRPremix-94X_mc2017_realistic_v10-v1/GEN-SIM-RECODEBUG&instance=prod/global&idx=0&limit=10'
        #'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/50000/44048461-9FE4-E711-A2F8-0CC47A4D7606.root'
        'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/510000/909C1D76-3FE4-E711-84C0-EC0D9A0B30E0.root'#'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16DR80Premix/QCD_Pt_3200toInf_TuneCUETP8M1_13TeV_pythia8/GEN-SIM-RECODEBUG/PREMIX_RECODEBUG_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/130000/1876E67B-E6AE-E611-8A1A-0CC47A4D765A.root'

    )
)


process.demo = cms.EDProducer('NNPixSeedInput' ,#demo = nome libero
 pixelClusters=cms.InputTag("siPixelClusters"),
 vertices = cms.InputTag("offlinePrimaryVertices"),
 cores = cms.InputTag("ak4CaloJets"),
 #cores =cms.InputTag("ak4PFJetsCHS"),
 ptMin = cms.double(1000), #800
 simTracks= cms.InputTag("g4SimHits"),
 simVertex= cms.InputTag("g4SimHits"),
 pixelCPE = cms.string( "PixelCPEGeneric" )
)

process.TFileService = cms.Service("TFileService",
      fileName = cms.string("histo.root"),
      closeFileFast = cms.untracked.bool(True)
  )


process.p = cms.Path(process.demo

) #process-demo + process.altrodemo + .... (se ne ho diversi)
