from CRABClient.UserUtilities import config, getUsernameFromSiteDB
config = config()

config.General.requestName = 'NNPixSeedInput_debugged'
config.General.workArea = 'crab_projects'
config.General.transferOutputs = True
config.General.transferLogs = True


config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'NNPixSeedInput_config.py'

config.Data.inputDataset = '/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/RunIIFall17DRPremix-94X_mc2017_realistic_v10-v1/GEN-SIM-RECODEBUG'
config.Data.inputDBS = 'global'
config.Data.splitting = 'EventAwareLumiBased'
config.Data.unitsPerJob = 100
config.Data.outLFNDirBase = '/store/user/%s/NNPixSeedInput' % (getUsernameFromSiteDB())
config.Data.publication = True
config.Data.outputDatasetTag = 'NNPixSeedInput_debugged'
config.Data.totalUnits = config.Data.unitsPerJob*100

config.Site.storageSite = "T2_IT_Pisa"
