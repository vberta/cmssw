from CRABClient.UserUtilities import config, getUsernameFromSiteDB
config = config()

config.General.requestName = 'fetchSimHitsAll'
config.General.workArea = 'crab_projects'
config.General.transferOutputs = True
config.General.transferLogs = True

config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'prepareInputs.py'

config.Data.inputDataset = '/QCD_Pt_1000to1400_TuneCP5_13TeV_pythia8/RunIISpring18DRPremix-100X_upgrade2018_realistic_v10-v1/AODSIM'
config.Data.secondaryInputDataset = '/QCD_Pt_1000to1400_TuneCP5_13TeV_pythia8/RunIISpring18GS-100X_upgrade2018_realistic_v10-v1/GEN-SIM'
#config.Data.useParent = True

config.Data.inputDBS = 'global'
config.Data.splitting = 'EventAwareLumiBased'
config.Data.unitsPerJob = 1000
#config.Data.unitsPerJob = 10
#config.Data.totalUnits = 30
config.Data.outLFNDirBase = '/store/user/%s/TrainJetCore' % (getUsernameFromSiteDB())
config.Data.publication = True
config.Data.outputDatasetTag = 'TrainJetCoreAll'

config.Site.storageSite = 'T2_IT_Bari'
