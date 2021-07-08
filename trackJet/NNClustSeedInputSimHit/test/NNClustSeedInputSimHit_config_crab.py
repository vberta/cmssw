# from CRABClient.UserUtilities import config, getUsernameFromSiteDB
from CRABClient.UserUtilities import config,getUsernameFromCRIC
config = config()

# config.General.requestName = 'NNClustSeedInputSimHit_1LayClustPt_cutPt'
config.General.requestName = 'NNClustSeedInputSimHit_EC_centralEgun_pt500cut'
config.General.workArea = 'crab_projects'
config.General.transferOutputs = True
config.General.transferLogs = True


config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'NNClustSeedInputSimHit_config.py'
config.JobType.numCores=8
config.JobType.maxMemoryMB=20000

# config.Data.inputDataset = '/QCD_Pt_1800to2400_TuneCUETP8M1_13TeV_pythia8/arizzi-TrainJetCoreAll-ddeeece6d9d1848c03a48f0aa2e12852/USER'
config.Data.inputDataset = '/UBGGun_E-1000to7000_Eta-1p2to2p1_13TeV_pythia8/vbertacc-DeepCoreTrainingSampleEC_all-3b4718db5896f716d6af32b678bbc9f2/USER'
config.Data.inputDBS = 'phys03'
config.Data.splitting = 'EventAwareLumiBased'
config.Data.unitsPerJob = 2000#1000
# config.Data.outLFNDirBase = '/store/user/%s/NNClustSeedInputSimHit' % (getUsernameFromSiteDB())
config.Data.outLFNDirBase = '/store/user/%s/NNClustSeedInputSimHit' % (getUsernameFromCRIC())

config.Data.publication = True
# config.Data.outputDatasetTag = 'NNClustSeedInputSimHit_1LayClustPt_cutPt'
config.Data.outputDatasetTag = 'NNClustSeedInputSimHit_EC_centralEgun_pt500cut'
config.Data.totalUnits = config.Data.unitsPerJob*10000 #1000

config.Site.storageSite = "T2_IT_Pisa"


#input file location (endcap):
#/gpfs/ddn/srm/cms/store/user/vbertacc/DeepCoreTrainingSampleEC_signelCore_4M/UBGGun_E-1000to7000_Eta-1p2to2p1_13TeV_pythia8/DeepCoreTrainingSampleEC_all
#on das(endcap):
#https://cmsweb.cern.ch/das/request?input=%2FUBGGun_E-1000to7000_Eta-1p2to2p1_13TeV_pythia8%2Fvbertacc-DeepCoreTrainingSampleEC_all-3b4718db5896f716d6af32b678bbc9f2%2FUSER&instance=prod%2Fphys03