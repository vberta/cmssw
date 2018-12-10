from CRABClient.UserUtilities import config, getUsernameFromSiteDB
config = config()

config.General.requestName = 'NNClustSeedInputSimHit_4M'
config.General.workArea = 'crab_projects'
config.General.transferOutputs = True
config.General.transferLogs = True


config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'NNClustSeedInputSimHit_config.py'

config.Data.inputDataset = '/QCD_Pt_1800to2400_TuneCUETP8M1_13TeV_pythia8/arizzi-TrainJetCoreAll-ddeeece6d9d1848c03a48f0aa2e12852/USER'
config.Data.inputDBS = 'phys03'
config.Data.splitting = 'EventAwareLumiBased'
config.Data.unitsPerJob = 1000
config.Data.outLFNDirBase = '/store/user/%s/NNClustSeedInputSimHit' % (getUsernameFromSiteDB())
config.Data.publication = True
config.Data.outputDatasetTag = 'NNClustSeedInputSimHit_4M'
config.Data.totalUnits = config.Data.unitsPerJob*1000

config.Site.storageSite = "T2_IT_Pisa"
