from LineshapeFitter import *
import os

def runFits(hmap,inputFile,genFile,outputFile,J=0):
    f=ROOT.TFile(outputFile,"RECREATE")
    direc = inputFile.split('.root')[0]
    os.mkdir('results'+direc)
    scale=ROOT.TH3D(hmap)
    scale.SetName("scale")
    sigma=ROOT.TH3D(hmap)
    sigma.SetName("sigma")
    for i in range(1,hmap.GetNbinsX()+1):
        for j in range(1,hmap.GetNbinsY()+1):
            for k in range(1,hmap.GetNbinsZ()+1):
                bin=hmap.GetBin(i,j,k)
                fitter=LineshapeFitter(inputFile,genFile,bin)
                if J==0:
                    if 'MC' in inputFile:
                        fitter.build1DModel()
                    else: 
                        fitter.build1DModelBkg()
                else:
                    if 'MC' in inputFile:
                        fitter.build1DModelJPsi()
                    else:
                        fitter.build1DModelJPsiBkg()
                fitter.fit(0)
                fitter.fit(0)
                fitter.fit(1)
                fitter.plot()

                scale.SetBinContent(bin,fitter.w.var("scale").getVal())
                scale.SetBinError(bin,fitter.w.var("scale").getError())
                sigma.SetBinContent(bin,fitter.w.var("error1").getVal())
                sigma.SetBinError(bin,fitter.w.var("error1").getError())
                fitter.write()
    f.cd()            
    scale.Write()
    sigma.Write()
    f.Close()

def runFits1D(inputFilestr,genFilestr,outputFile,J=0):
    
    closureType = ['eta1', 'eta2', 'pt1', 'pt2']
    inputFile=ROOT.TFile.Open(inputFilestr)
    genFile=ROOT.TFile.Open(genFilestr)

    isData = ''
    if 'Data' in inputFilestr:
        isData = '_DATA'

    print isData    

    for clos in closureType:

        if not os.path.exists("FITS_{}{}".format(clos,isData)):
            os.mkdir("FITS_{}{}".format(clos, isData))

        f=ROOT.TFile(outputFile.split('.')[0]+'_'+clos+'.root',"RECREATE")
        
        histoData2D = inputFile.Get("closure_"+clos)
        genData2D = genFile.Get("closure_"+clos)

        scale=ROOT.TH1D(histoData2D.ProjectionX())
        scale.SetName("scale")
        sigma=ROOT.TH1D(histoData2D.ProjectionX())
        sigma.SetName("sigma")

        for i in range(1,histoData2D.GetNbinsX()+1):

            data = histoData2D.ProjectionY("proj{}".format(i),i,i)
            gen = genData2D.ProjectionY("projGen{}".format(i),i,i)

            fitter=LineshapeFitter(data,gen,i, "FITS_{}".format(clos))
            if J==0:
                if 'MC' in inputFile:
                    fitter.build1DModel()
                else: 
                    fitter.build1DModelBkg()
            else:
                if 'MC' in inputFile:
                    fitter.build1DModelJPsi()
                else:
                    fitter.build1DModelJPsiBkg()
            fitter.fit(0)
            fitter.fit(0)
            fitter.fit(1)
            fitter.plot()

            scale.SetBinContent(i,fitter.w.var("scale").getVal())
            scale.SetBinError(i,fitter.w.var("scale").getError())
            sigma.SetBinContent(i,fitter.w.var("error1").getVal())
            sigma.SetBinError(i,fitter.w.var("error1").getError())
            #fitter.write()

        f.cd()            
        scale.Write()
        sigma.Write()
        f.Close()


