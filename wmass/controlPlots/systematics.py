systematics = {
    "Generator_weight" : [
        ["LHEPdfWeight" + str(i)  for i in range(0, 99)], 
        ["LHEScaleWeight" + str(i) for i in range(0,9)]
    ],
    "puWeight"  : [["puWeightUp", "puWeightDown"]],
    "Muon_Trigger_BCDEF_SF": [["Muon_Trigger_BCDEF_SFstatUp", "Muon_Trigger_BCDEF_SFstatDown", "Muon_Trigger_BCDEF_SFsystUp", "Muon_Trigger_BCDEF_SFsystDown"]],    
    "Muon_ID_BCDEF_SF"     : [["Muon_ID_BCDEF_SFstatUp", "Muon_ID_BCDEF_SFstatDown", "Muon_ID_BCDEF_SFsystUp", "Muon_ID_BCDEF_SFsystDown"]],    
                              
    "Muon_ISO_BCDEF_SF"    : [["Muon_ISO_BCDEF_SFstatUp", "Muon_ISO_BCDEF_SFstatDown", "Muon_ISO_BCDEF_SFsystUp", "Muon_ISO_BCDEF_SFsystDown"]], 
    "corrected" : [["correctedUp", "correctedDown"]],
    "nom"       : [["jerUp", "jerDown", "jesTotalUp", "jesTotalDown", "unclustEnUp","unclustEnDown"]],
}

    
