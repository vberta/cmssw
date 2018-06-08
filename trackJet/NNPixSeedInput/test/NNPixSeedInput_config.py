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

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(10) ) #-1 = tutti

process.source = cms.Source("PoolSource",
    # replace 'myfile.root',' with the source file you want to use
    fileNames = cms.untracked.vstring(
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/510000/909C1D76-3FE4-E711-84C0-EC0D9A0B30E0.root'
        'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/50000/44048461-9FE4-E711-A2F8-0CC47A4D7606.root',
        'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/50000/987BD26A-9FE4-E711-B33F-0025905A48F2.root',
        'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/50000/C299B94A-9FE4-E711-9380-0CC47A7C3420.root',
        'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/510000/82A7A781-7FE4-E711-A50C-FA163E209BDB.root',
        'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/510000/909C1D76-3FE4-E711-84C0-EC0D9A0B30E0.root',
        'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/510000/96670A7C-3FE4-E711-9B02-001E675A681F.root',
        'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/02F54734-89DD-E711-A599-FA163E401012.root',
        'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/04121868-D3DE-E711-B68B-0CC47A4C8E5E.root',
        'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/04C60493-D4DA-E711-8C3E-001E67E6965D.root',
        'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/06D25F8E-16DA-E711-BAA5-FA163ECFFD5D.root',
        'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/08043237-80DA-E711-9396-FA163ECFFD5D.root',
        'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/0A0C10A1-0DDD-E711-8DE9-90B11C08AD7D.root'
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/0C2055B2-DDDC-E711-A558-0242AC130002.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/0C61E7FE-47DA-E711-B32F-0CC47AD9914A.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/0E043B41-4DDB-E711-B074-FA163E3F211F.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/14CDFE10-17DC-E711-8028-02163E01762C.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/16FF8DFD-40DA-E711-AFB0-FA163ECFFD5D.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/18926E72-24DA-E711-B497-008CFAEBDEEC.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/1A3E7492-2DDA-E711-8F9E-001E67A3E8F9.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/1C8F07C3-61DA-E711-BE41-FA163E581A36.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/1E666AE7-F7D9-E711-BCCA-24BE05BDBE21.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/1EDB65C7-1ADA-E711-9E9B-E0071B6CAD20.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/20267D0E-3DDA-E711-AF5D-24BE05CEFB41.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/224854D5-20DA-E711-8D71-E0071B7A6890.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/229B34EE-5DDD-E711-9781-5065F381A2F1.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/2433345D-0DDA-E711-BDC2-008CFAC94024.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/2657A53E-82DD-E711-A249-FA163E773EC0.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/282C1078-37DA-E711-B305-FA163EC83E8B.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/30A20E41-5ADB-E711-AA8D-008CFAC91A30.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/30DD96CE-0FDA-E711-B6A0-008CFAC940B8.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/3471507A-44DA-E711-8529-008CFAC93C9C.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/3A0DE83F-19DE-E711-96FA-0025905B860E.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/3A8B2F40-9DDA-E711-A337-A4BF010114DB.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/3ABB7DED-18DE-E711-A424-0CC47A78A42E.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/3EB7C311-30DA-E711-9FF1-02163E00C79E.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/441FBA04-3DDA-E711-A80A-24BE05CEEB31.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/4C1C0381-36DA-E711-95A9-001E67A3EAB1.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/5018AE38-0BDA-E711-8687-24BE05C68681.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/5026FBD1-1BDA-E711-948B-008CFAEBDEEC.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/543D21F9-35DA-E711-A864-008CFAE45400.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/5E683EE7-36DA-E711-AECC-00259029E91C.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/609E2448-D8DC-E711-9BEF-001E67A404B0.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/623C670B-5FDD-E711-A4C1-5065F3816291.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/625230ED-23DA-E711-842C-E0071B7A4550.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/66358E50-49DA-E711-ACEF-0025901FB100.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/663B5BF9-3BDA-E711-9599-5065F381F1C1.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/682308F0-D2DD-E711-A54E-FA163E401012.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/68637802-30DC-E711-9D74-008CFAC93B28.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/6ACCC0E5-13DA-E711-A29A-008CFAEBDEEC.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/6AE44832-1DDA-E711-A05F-FA163E21FB72.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/6C423BF8-3BDA-E711-8D10-5065F381F1C1.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/6CB933EB-60DA-E711-B45A-008CFAC940CC.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/6CD5D81D-D6DA-E711-AB77-A4BF0101F533.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/74FB2BDF-BCDE-E711-B3DB-FA163EC75482.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/74FC2E65-D3DE-E711-AFE6-0025905B8574.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/82D1EC08-02DA-E711-83B1-24BE05C618F1.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/8C65697F-95DD-E711-BDC1-24BE05C63651.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/9C99EF3D-56DA-E711-9501-008CFAC93D54.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/9E00E0B4-4EDF-E711-BBA8-0CC47A4C8ECA.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/9E2A3E25-10DA-E711-B8D4-E0071B7A6850.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/9E5B85D1-2CDA-E711-9D6A-24BE05C68681.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/9E7D5084-3CDA-E711-A8EA-02163E012FA0.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/A2A4E64B-22DA-E711-90A6-A4BF0102A4F5.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/A4FAC448-FED9-E711-BE51-24BE05C618F1.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/A849DA87-F4E1-E711-8537-0025905B859A.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/AA418E95-17DB-E711-9F8C-FA163E3F211F.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/AC26D6C2-16DA-E711-BCF4-008CFAEBDEEC.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/B2CC85D4-24DC-E711-BE1D-0242AC130002.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/B4F706FF-5EDD-E711-9BB9-E0071B74AC00.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/B6270F05-19DE-E711-9855-0025905B85A2.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/B6D73D86-7BDA-E711-B29E-008CFAC9428C.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/BA5AE061-8EDB-E711-9FF7-002590FD5A78.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/BE5349A5-19DE-E711-A448-0025905B85C6.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/C69B9ED3-2FDB-E711-A6D5-FA163E8674D5.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/C6CE9803-3DDA-E711-9D11-24BE05CEEB31.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/CA09185B-31DA-E711-A33E-008CFAC94284.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/CABEEAA9-41DA-E711-96F8-008CFAC940A0.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/D4EE7032-26DA-E711-95C0-001E67A3E8F9.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/DA9D19D6-FCD9-E711-9944-4C79BA181101.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/DC00B4D1-4CDA-E711-9C4E-0CC47AA98F98.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/DE2102CA-47DA-E711-B113-00259019A43E.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/E42F51EE-38DA-E711-8646-FA163EBDD8C3.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/EC280575-43DA-E711-85C8-02163E012FA0.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/EC70007C-0DDA-E711-89E2-E0071B73B6B0.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/EE08109E-30DC-E711-9C4D-008CFAC913F8.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/F41EEA59-71DA-E711-8F32-FA163E7B13F7.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/F624C980-BBDC-E711-AE51-FA163E4825B4.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/F6379B43-48DA-E711-BD39-002590FD5A78.root',
        # 'root://cms-xrd-global.cern.ch//store/mc/RunIIFall17DRPremix/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/GEN-SIM-RECODEBUG/94X_mc2017_realistic_v10-v1/60000/F647219F-FCD9-E711-BAD0-24BE05C4D801.root'
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
