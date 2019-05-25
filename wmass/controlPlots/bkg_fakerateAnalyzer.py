from ROOT import *
import array as array
import math 
import sys
import copy as copy
sys.path.append('../../framework')
from module import *
from header import *
from bkg_variables import *
from bkg_selections import *



# class bkg_fakerateAnalyzer(module):
class bkg_fakerateAnalyzer:  
    # def __init__(self, outdir='./bkg', folder='./', norm = 1, skipHisto = 1, fileList,)  :
    def __init__(self, outdir='./bkg', folder='./', norm = 1,)  :
    
        self.outdir = outdir
        self.folder = folder
        self.norm = norm
        # self.skipHisto = skipHisto
        # self.fileList = fileList 
        
        self.rootFiles = []
        self.relisoCUT = 0.15
        self.isoCUT = 5
        self.QCDmult = 1. #multiplication factor to QCD bkg
        
        self.sampleList = ['WToMuNu','QCD','Data','DataLike']
        self.signList = ['Plus','Minus']
        self.regionList = ['Signal','Sideband', 'Tot']
        # self.varList = []
        # for var in bkg_variables['Muon1']['D2variables'] : self.varList.append(var)
        self.varList = ["pfRelIso04_all_VS_corrected_MET_nom_mt","pfRelIso04_all_TIMES_corrected_pt_VS_corrected_MET_nom_mt","pfRelIso04_all_VS_MET_pt","pfRelIso04_all_TIMES_corrected_pt_VS_MET_pt"]
        self.varName = ["relIso_vs_Mt", "absIso_vs_Mt","relIso_vs_MET", "absIso_vs_MET"]
        
        #open all the useful rootfile
        # for f in fileList
        #     rootFiles.append(TFile.Open(self.folder+'/'+f))
        for f in range(len(self.sampleList)-1) :
            if (self.sampleList[f]!='DataLike') : self.rootFiles.append(TFile.Open(self.folder+'/'+self.sampleList[f]+'.root'))
    
    
    def ratio_2Dto1D(self,histo,isocut =0.15,name = "histoRate") : #histo = 2D isto iso:Mt, isocut=tight def., name=output histo name
        #this func. produce an histogram of fake or prompt rate in fuction of Mt (to verify ABCD assumption)
        isoMin= histo.GetYaxis().GetBinCenter(1)-histo.GetYaxis().GetBinWidth(1)/2
        binsize = histo.GetYaxis().GetBinWidth(1)
        Ncut=(isocut-isoMin)/binsize
        Ncut = int(Ncut)
        print name,isocut, Ncut, isoMin
        histo.Scale(self.norm)
        # histoDen = histo.ProjectionX("histoDen",Ncut,-1)
        histoDen = histo.ProjectionX("histoDen")
        histoNum = histo.ProjectionX("histoNum",0,Ncut-1)
        histoRate = histoNum.Clone(name)
        histoRate.Divide(histoNum,histoDen,1,1)
        return histoRate
    
    
    def integrated_preliminary(self) :
    
        print "getting histos"
        histoDict = {}                          
        for s in self.signList :
            for v,name in map(None,self.varList,self.varName) :
                for f,rootFile in map(None,self.sampleList,self.rootFiles) :
                    if(f!='DataLike') :
                        for r in self.regionList :
                            if(r!='Tot') :
                                print "Get histo:" 'controlPlotsbkg_'+r+s+'/nom/Muon1_'+v
                                print "key=",s+v+f+r
                                histoDict[s+v+f+r] =  rootFile.Get('controlPlotsbkg_'+r+s+'/nom/Muon1_'+v)
                            else:
                                print "clone histo:", f+'_'+s+'_'+name+'_Tot'
                                histoDict[s+v+f+r] = histoDict[s+v+f+'Sideband'].Clone(f+'_'+s+'_'+name+'_Tot')
                                for rr in self.regionList :
                                    if (rr =="Sideband" or rr=="Tot") : continue
                                    print "Added histo:", histoDict[s+v+f+rr].GetName()
                                    print "key=",s+v+f+r
                                    print "key added=",s+v+f+rr
                                    histoDict[s+v+f+r].Add(histoDict[s+v+f+rr])

                    else :
                        print "cloned (datalike) histo:", 'DataLike_'+s+'_'+name+'_Tot'
                        print "key=",s+v+f+'Tot'
                        histoDict[s+v+f+'Tot']= histoDict[s+v+'WToMuNuTot'].Clone('DataLike_'+s+'_'+name+'_Tot')
                        for ff in self.sampleList :
                            if (ff =="WToMuNu" or ff=="Data" or ff=="DataLike"):  continue
                            print "Added (data like) histo:", histoDict[s+v+ff+'Tot'].GetName()
                            print "key summed=",s+v+ff+'Tot'
                            histoDict[s+v+f+'Tot'].Add(histoDict[s+v+ff+'Tot'])
                print "=======================================================================" 
  
        # print histos            
        print "ratios (integrated, preliminary)"
        ratios = []
        for s in self.signList :
            for v,name in map(None,self.varList,self.varName) :
                for f in self.sampleList :
                    print 'ratio_'+histoDict[s+v+f+'Tot'].GetName()
                    if 'relIso' in name : cutvalue =  self.relisoCUT
                    else : cutvalue = self.isoCUT
                    ratios.append(self.ratio_2Dto1D(histoDict[s+v+f+'Tot'],cutvalue,'ratio_'+histoDict[s+v+f+'Tot'].GetName()))
        
        output = TFile(self.outdir+"/bkg_integrated_preliminary.root","recreate")
        for h in range(len(ratios)):
            ratios[h].Write()



    # def differential_preliminary :
    
    # def differential_fakerate :



    def integrated_preliminary_OLD_NOT_USE(self) :
        # lvar = [0 for v in range(len(self.varList))]
        # lreg = [lvar for r in range(len(self.regionList))]
        # lsig = [lreg for s in range(len(self.signList))]
        # histos = [lsig for f in range(len(self.sampleList))]
        
        lreg = [0 for r in range(len(self.regionList))]
        lsam = [copy.deepcopy(lreg) for f in range(len(self.sampleList))]
        lvar = [copy.deepcopy(lsam) for v in range(len(self.varList))]
        histos = [copy.deepcopy(lvar) for s in range(len(self.signList))]
        # for f in range(len(self.sampleList)) :
        #     if (self.sampleList[f]!='DataLike') : rootfile = TFile.Open(self.folder+'/'+self.sampleList[f]+'.root')
        #     for s in range(len(self.signList)) :
        #         for r in range(len(self.regionList)) :
        #             for v in range(len(self.varList)) :
        #                 if(self.sampleList[f]!='DataLike' and self.regionList[f]!='Tot') :
        #                     histos[f][s][r][v] =  rootfile.Get('controlPlotsbkg_'+self.regionList[r]+self.signList[s]+'/nom/+Muon1_'+self.varList[v])
        print histos      
        print "getting histos"                          
        for s in range(len(self.signList)) :
            # if (self.sampleList[f]!='DataLike') : rootfile = TFile.Open(self.folder+'/'+self.sampleList[f]+'.root')
            for v in range(len(self.varList)) :
                for f in range(len(self.sampleList)) :
                    if(self.sampleList[f]!='DataLike') :
                        for r in range(len(self.regionList)) :
                            if(self.regionList[r]!='Tot') :
                                print "Get histo:" 'controlPlotsbkg_'+self.regionList[r]+self.signList[s]+'/nom/+Muon1_'+self.varList[v]#, "from file:",self.rootFiles[f] 
                                histos[s][v][f][r] =  self.rootFiles[f].Get('controlPlotsbkg_'+self.regionList[r]+self.signList[s]+'/nom/Muon1_'+self.varList[v])
                                
                                #line below the dictionary approach, not used.
                                # hdict[self.sampleList[f]+'_'+self.regionList[r]+'_'+self.signList[s]+'_'+self.varList[v]] = self.rootFiles[f].Get('controlPlotsbkg_'+self.regionList[r]+self.signList[s]+'/nom/Muon1_'+self.varList[v])
                                # print "HISTO", s,v,f,r, "name", histos[s][v][f][r]
                            else:
                                print "clone histo:", self.sampleList[f]+'_'+self.signList[s]+'_'+histos[s][v][f][r-1].GetName()+'_Tot'
                                histos[s][v][f][r] = histos[s][v][f][r-1].Clone(self.sampleList[f]+'_'+self.signList[s]+'_'+self.varName[v]+'_Tot')
                                for rr in range(len(self.regionList)-2) :
                                    print "Added histo:", histos[s][v][f][rr].GetName()
                                    histos[s][v][f][r].Add(histos[s][v][f][rr])
                                # print "HISTO",  s,v,f,r, histos[s][v][f][r]

                    else :
                        print "cloned (datalike) histo:", 'DataLike_'+self.signList[s]+'_'+histos[s][v][f-2][len(self.regionList)-1].GetName()+'_Tot'
                        histos[s][v][f][len(self.regionList)-1] = histos[s][v][f-2][len(self.regionList)-1].Clone('DataLike_'+self.signList[s]+'_'+self.varName[v]+'_Tot')
                        for ff in range(len(self.sampleList)-3) :
                            print "Added (data like) histo:", histos[s][v][ff][len(self.regionList)-1].GetName()
                            histos[s][v][f][len(self.regionList)-1].Add(histos[s][v][ff][len(self.regionList)-1])
                        # print "HISTO",  s,v,f,r, histos[s][v][f][len(self.regionList)-1]
                print "======================================================================="

        # print histos            
        print "ratios (integrated, preliminary)"
        ratios = []
        for s in range(len(self.signList)) :
            for v in range(len(self.varList)) :
                for f in range(len(self.sampleList)) :
                    print 'ratio_'+histos[s][v][f][len(self.regionList)-1].GetName()
                    if v == 0 or v==2 : cutvalue =  self.relisoCUT
                    else : cutvalue = self.isoCUT
                    ratios.append(self.ratio_2Dto1D(histos[s][v][f][len(self.regionList)-1],cutvalue,'ratio_'+histos[s][v][f][len(self.regionList)-1].GetName()))
        
        output = TFile(self.outdir+"/bkg_integrated_preliminary.root","recreate")
        for h in range(len(ratios)):
            ratios[h].Write()