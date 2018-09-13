from CRABClient.UserUtilities import config, getUsernameFromSiteDB
config = config()

config.General.requestName = 'NNClustSeedInput_1M_multiplied_4hit_30'
config.General.workArea = 'crab_projects'
config.General.transferOutputs = True
config.General.transferLogs = True


config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'NNClustSeedInput_config.py'

config.Data.inputDataset = '/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/RunIIFall17DRPremix-94X_mc2017_realistic_v10-v1/GEN-SIM-RECODEBUG'
config.Data.inputDBS = 'global'
config.Data.splitting = 'EventAwareLumiBased'
config.Data.unitsPerJob = 1000
config.Data.outLFNDirBase = '/store/user/%s/NNClustSeedInput' % (getUsernameFromSiteDB())
config.Data.publication = True
config.Data.outputDatasetTag = 'NNClustSeedInput_1M_multiplied_4hit_30'
config.Data.totalUnits = config.Data.unitsPerJob*1000

config.Site.storageSite = "T2_IT_Pisa"
