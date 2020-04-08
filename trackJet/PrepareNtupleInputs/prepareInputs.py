# Auto generated configuration file
# using:
# Revision: 1.19
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v
# with command line options: step2 --conditions auto:phase1_2017_realistic -s DIGI:pdigi_valid,L1,DIGI2RAW,HLT:@relval2017 --datatier GEN-SIM-DIGI-RAW -n 10 --geometry DB:Extended --era Run2_2017 --eventcontent FEVTDEBUGHLT --filein file:step1.root --fileout file:step2.root
import FWCore.ParameterSet.Config as cms

from Configuration.StandardSequences.Eras import eras

# process = cms.Process('TRAINING',eras.Run2_2017)
process = cms.Process('TRAINING',eras.Run2_2018)


# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.Digi_cff')
process.load('Configuration.StandardSequences.SimL1Emulator_cff')
process.load('Configuration.StandardSequences.DigiToRaw_cff')
# process.load('HLTrigger.Configuration.HLT_2e34v40_cff')
process.load('HLTrigger.Configuration.HLT_2018v32_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.load('Configuration.StandardSequences.RawToDigi_cff')
process.load('Configuration.StandardSequences.L1Reco_cff')
process.load('Configuration.StandardSequences.Reconstruction_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1)
)

# Input source
process.source = cms.Source("PoolSource",
    dropDescendantsOfDroppedBranches = cms.untracked.bool(False),
    fileNames = cms.untracked.vstring([
	# '/store/mc/RunIISummer17DRPremix/QCD_Pt_1800to2400_TuneCUETP8M1_13TeV_pythia8/AODSIM/92X_upgrade2017_realistic_v10-v5/90000/AA3AFFA9-149C-E711-BBBD-0CC47AF9B32A.root'
	#'/store/mc/RunIISummer17DRPremix/QCD_Pt_1800to2400_TuneCUETP8M1_13TeV_pythia8/AODSIM/92X_upgrade2017_realistic_v10-v5/90000/4633A554-2A9C-E711-8E16-0025905C543A.root'
    'file:/afs/cern.ch/user/v/vbertacc/workdir/CMSSW_10_2_5/src/test_generator/step3_RAW2DIGI_L1Reco_RECO_RECOSIM_EI.root'
    # '/store/mc/RunIISpring18DRPremix/QCD_Pt_1000to1400_TuneCP5_13TeV_pythia8/AODSIM/100X_upgrade2018_realistic_v10-v1/90000/FCEE5CD3-5B2B-E811-AC21-20CF305B05AE.root' #THISONE
  ]),
    secondaryFileNames = cms.untracked.vstring([
        'file:/afs/cern.ch/user/v/vbertacc/workdir/CMSSW_10_2_5/src/test_generator/HighPtJets_GEN_SIM_bug_1000-7000_100ev.root'])

    # '/store/mc/RunIISpring18GS/QCD_Pt_1000to1400_TuneCP5_13TeV_pythia8/GEN-SIM/100X_upgrade2018_realistic_v10-v1/90002/9E33B836-3624-E811-B047-0CC47A1DF806.root',  #AND THISONE
    # '/store/mc/RunIISpring18GS/QCD_Pt_1000to1400_TuneCP5_13TeV_pythia8/GEN-SIM/100X_upgrade2018_realistic_v10-v1/90000/DCEE8A53-1B24-E811-B016-002590E7E010.root']) #AND THISONE

# '/store/mc/RunIISummer17GS/QCD_Pt_1800to2400_TuneCUETP8M1_13TeV_pythia8/GEN-SIM/92X_upgrade2017_realistic_v10-v1/70000/06D75549-2D86-E711-96BC-0025904A9430.root',
# '/store/mc/RunIISummer17GS/QCD_Pt_1800to2400_TuneCUETP8M1_13TeV_pythia8/GEN-SIM/92X_upgrade2017_realistic_v10-v1/70000/382F5125-2686-E711-B88B-001E67DDCC81.root',
# '/store/mc/RunIISummer17GS/QCD_Pt_1800to2400_TuneCUETP8M1_13TeV_pythia8/GEN-SIM/92X_upgrade2017_realistic_v10-v1/70000/A6D39341-2D86-E711-BB73-90B11C2AAEEC.root',
# '/store/mc/RunIISummer17GS/QCD_Pt_1800to2400_TuneCUETP8M1_13TeV_pythia8/GEN-SIM/92X_upgrade2017_realistic_v10-v1/70000/F038BA39-2D86-E711-AE1D-0CC47AD98D10.root',
# '/store/mc/RunIISummer17GS/QCD_Pt_1800to2400_TuneCUETP8M1_13TeV_pythia8/GEN-SIM/92X_upgrade2017_realistic_v10-v1/70001/648053BF-4886-E711-9A86-001E67A3EBD8.root',
# '/store/mc/RunIISummer17GS/QCD_Pt_1800to2400_TuneCUETP8M1_13TeV_pythia8/GEN-SIM/92X_upgrade2017_realistic_v10-v1/70001/B843A86A-B886-E711-A108-001E67D80528.root'])

#'/store/mc/RunIISummer17GS/QCD_Pt_1800to2400_TuneCUETP8M1_13TeV_pythia8/GEN-SIM/92X_upgrade2017_realistic_v10-v1/70000/06D75549-2D86-E711-96BC-0025904A9430.root'])
)

process.options = cms.untracked.PSet(
   allowUnscheduled = cms.untracked.bool(True),
#   numberOfThreads = cms.untracked.uint32(40),
#   numberOfStreams = cms.untracked.uint32(40),
   wantSummary = cms.untracked.bool(True)
)


process.RECOSIMoutput = cms.OutputModule("PoolOutputModule",
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('GEN-SIM-RECO'),
        filterName = cms.untracked.string('')
    ),
    fileName = cms.untracked.string('file:step3.root'),
    outputCommands = cms.untracked.vstring(["drop *"]),
    splitLevel = cms.untracked.int32(0)
)

process.RECOSIMoutput.outputCommands.append("keep SimTracks_g4SimHits_*_*")
process.RECOSIMoutput.outputCommands.append("keep SimVertexs_g4SimHits_*_*")
process.RECOSIMoutput.outputCommands.append("keep PSimHits_g4SimHits_*_*")
process.RECOSIMoutput.outputCommands.append("keep *_ak4CaloJets_*_*")
process.RECOSIMoutput.outputCommands.append("keep *_offlinePrimaryVertices_*_*")
process.RECOSIMoutput.outputCommands.append("keep *_*iPixelCluster*_*_*")
process.RECOSIMoutput.outputCommands.append("keep *_simSiPixelDigis_*_*")


# Other statements
process.mix.digitizers = cms.PSet(process.theDigitizersValid)
from Configuration.AlCa.GlobalTag import GlobalTag
# process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:phase1_2017_realistic', '')
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:phase1_2018_realistic', '')


# Path and EndPath definitions

# Path and EndPath definitions
process.digitisation_step = cms.Path(process.pdigi_valid)
process.L1simulation_step = cms.Path(process.SimL1Emulator)
process.digi2raw_step = cms.Path(process.DigiToRaw)
process.raw2digi_step = cms.Path(process.RawToDigi)
process.reconstruction_step = cms.Path(process.localreco)
process.RECOSIMoutput_step = cms.EndPath(process.RECOSIMoutput)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.FEVTDEBUGHLToutput_step = cms.EndPath(process.RECOSIMoutput)

# Schedule definition
process.schedule = cms.Schedule(process.digitisation_step,process.L1simulation_step,process.digi2raw_step)
process.schedule.extend([process.raw2digi_step,process.reconstruction_step])

#process.schedule = cms.Schedule(process.raw2digi_step,process.L1Reco_step,process.reconstruction_step,process.recosim_step,process.eventinterpretaion_step,process.Flag_HBHENoiseFilter,process.Flag_HBHENoiseIsoFilter,process.Flag_CSCTightHaloFilter,process.Flag_CSCTightHaloTrkMuUnvetoFilter,process.Flag_CSCTightHalo2015Filter,process.Flag_globalTightHalo2016Filter,process.Flag_globalSuperTightHalo2016Filter,process.Flag_HcalStripHaloFilter,process.Flag_hcalLaserEventFilter,process.Flag_EcalDeadCellTriggerPrimitiveFilter,process.Flag_EcalDeadCellBoundaryEnergyFilter,process.Flag_ecalBadCalibFilter,process.Flag_goodVertices,process.Flag_eeBadScFilter,process.Flag_ecalLaserCorrFilter,process.Flag_trkPOGFilters,process.Flag_chargedHadronTrackResolutionFilter,process.Flag_muonBadTrackFilter,process.Flag_BadChargedCandidateFilter,process.Flag_BadPFMuonFilter,process.Flag_BadChargedCandidateSummer16Filter,process.Flag_BadPFMuonSummer16Filter,process.Flag_trkPOG_manystripclus53X,process.Flag_trkPOG_toomanystripclus53X,process.Flag_trkPOG_logErrorTooManyClusters,process.Flag_METFilters,process.prevalidation_step,process.prevalidation_step1,process.validation_step,process.validation_step1,process.dqmoffline_step,process.dqmoffline_1_step,process.dqmoffline_2_step,process.dqmofflineOnPAT_step,process.dqmofflineOnPAT_1_step,process.dqmofflineOnPAT_2_step,process.RECOSIMoutput_step,process.MINIAODSIMoutput_step,process.DQMoutput_step)
#process.schedule.extend(process.HLTSchedule)
process.schedule.extend([process.endjob_step,process.FEVTDEBUGHLToutput_step])
#from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
#associatePatAlgosToolsTask(process)

# customisation of the process.

# Automatic addition of the customisation function from HLTrigger.Configuration.customizeHLTforMC
#from HLTrigger.Configuration.customizeHLTforMC import customizeHLTforMC

#call to customisation function customizeHLTforMC imported from HLTrigger.Configuration.customizeHLTforMC
#process = customizeHLTforMC(process)
#
# End of customisation functions

# Customisation from command line

# Add early deletion of temporary data products to reduce peak memory need
#from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
#process = customiseEarlyDelete(process)




# Schedule definition
#process.schedule = cms.Schedule(process.raw2digi_step,process.L1Reco_step,process.reconstruction_step,process.recosim_step,process.eventinterpretaion_step,process.Flag_HBHENoiseFilter,process.Flag_HBHENoiseIsoFilter,process.Flag_CSCTightHaloFilter,process.Flag_CSCTightHaloTrkMuUnvetoFilter,process.Flag_CSCTightHalo2015Filter,process.Flag_globalTightHalo2016Filter,process.Flag_globalSuperTightHalo2016Filter,process.Flag_HcalStripHaloFilter,process.Flag_hcalLaserEventFilter,process.Flag_EcalDeadCellTriggerPrimitiveFilter,process.Flag_EcalDeadCellBoundaryEnergyFilter,process.Flag_ecalBadCalibFilter,process.Flag_goodVertices,process.Flag_eeBadScFilter,process.Flag_ecalLaserCorrFilter,process.Flag_trkPOGFilters,process.Flag_chargedHadronTrackResolutionFilter,process.Flag_muonBadTrackFilter,process.Flag_BadChargedCandidateFilter,process.Flag_BadPFMuonFilter,process.Flag_BadChargedCandidateSummer16Filter,process.Flag_BadPFMuonSummer16Filter,process.Flag_trkPOG_manystripclus53X,process.Flag_trkPOG_toomanystripclus53X,process.Flag_trkPOG_logErrorTooManyClusters,process.Flag_METFilters,process.prevalidation_step,process.prevalidation_step1,process.validation_step,process.validation_step1,process.dqmoffline_step,process.dqmoffline_1_step,process.dqmoffline_2_step,process.dqmofflineOnPAT_step,process.dqmofflineOnPAT_1_step,process.dqmofflineOnPAT_2_step,process.RECOSIMoutput_step,process.MINIAODSIMoutput_step,process.DQMoutput_step)
#process.schedule.associate(process.patTask)
#from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
#associatePatAlgosToolsTask(process)

# customisation of the process.

# Automatic addition of the customisation function from SimGeneral.MixingModule.fullMixCustomize_cff
#from SimGeneral.MixingModule.fullMixCustomize_cff import setCrossingFrameOn

#call to customisation function setCrossingFrameOn imported from SimGeneral.MixingModule.fullMixCustomize_cff
#process = setCrossingFrameOn(process)

# End of customisation functions
#do not add changes to your config after this point (unless you know what you are doing)
#from FWCore.ParameterSet.Utilities import convertToUnscheduled
#process=convertToUnscheduled(process)

# customisation of the process.

# Automatic addition of the customisation function from PhysicsTools.PatAlgos.slimming.miniAOD_tools
#from PhysicsTools.PatAlgos.slimming.miniAOD_tools import miniAOD_customizeAllMC

#call to customisation function miniAOD_customizeAllMC imported from PhysicsTools.PatAlgos.slimming.miniAOD_tools
#process = miniAOD_customizeAllMC(process)

# End of customisation functions

# Customisation from command line

#Have logErrorHarvester wait for the same EDProducers to finish as those providing data for the OutputModule
#from FWCore.Modules.logErrorHarvester_cff import customiseLogErrorHarvesterUsingOutputCommands
#process = customiseLogErrorHarvesterUsingOutputCommands(process)

# Add early deletion of temporary data products to reduce peak memory need
#from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
#process = customiseEarlyDelete(process)
# End adding early deletion
