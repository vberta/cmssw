from CRABClient.UserUtilities import config,getUsernameFromCRIC
config = config()

config.General.requestName = 'centralEGunSample_all_8core'
config.General.workArea = 'crab_projects'
config.General.transferOutputs = True
config.General.transferLogs = True

config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'prepareInputs.py'

# config.Data.inputDataset = '/QCD_Pt_1000to1400_TuneCP5_13TeV_pythia8/RunIISpring18DRPremix-100X_upgrade2018_realistic_v10-v1/AODSIM'
config.Data.inputDataset = '/UBGGun_E-1000to7000_Eta-1p2to2p1_13TeV_pythia8/RunIIFall17DRStdmix-NoPU_94X_mc2017_realistic_v11-v2/AODSIM'
# config.Data.secondaryInputDataset = '/QCD_Pt_1000to1400_TuneCP5_13TeV_pythia8/RunIISpring18GS-100X_upgrade2018_realistic_v10-v1/GEN-SIM'
config.Data.secondaryInputDataset = '/UBGGun_E-1000to7000_Eta-1p2to2p1_13TeV_pythia8/RunIIFall17DRStdmix-NoPU_94X_mc2017_realistic_v11-v2/GEN-SIM-DIGI-RAW'

#config.Data.useParent = True

config.Data.inputDBS = 'global'
config.Data.splitting = 'EventAwareLumiBased'

config.JobType.numCores=8
config.JobType.maxMemoryMB=20000

config.Data.unitsPerJob = 2000
# config.Data.unitsPerJob = 10
config.Data.totalUnits = 10000000

config.Data.outLFNDirBase = '/store/user/%s/DeepCoreTrainingSampleEC_signelCore_4M' % (getUsernameFromCRIC())
# config.Data.outLFNDirBase = '/store/user/vbertacc/DeepCoreTrainingSampleEC'
config.Data.publication = True
# config.Data.outputDatasetTag = 'TrainJetCoreAll'
config.Data.outputDatasetTag = 'DeepCoreTrainingSampleEC_all'

config.Site.storageSite = 'T2_IT_Pisa'
