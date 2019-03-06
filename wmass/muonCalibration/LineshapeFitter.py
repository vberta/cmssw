import ROOT
import os
import math


class LineshapeFitter(object):
    def __init__(self,histoData, genData, bin, mydir,twoD = 0,customGEN = ""):

        self.direc = mydir
        self.conditionals=[]
        self.bin=bin 
        
        self.w = ROOT.RooWorkspace("w","w")
        self.w.factory("x[0,1000]")
        self.w.factory("y[0,1000]")
        self.w.factory("z[0,1000]")
        self.w.factory("genx[0,1000]")
        if twoD==1:
            hist = ROOT.RooDataHist("data","data",ROOT.RooArgList(self.w.var("x"),self.w.var("y")),histoData)
        elif twoD==0:
            hist = ROOT.RooDataHist("data","data",ROOT.RooArgList(self.w.var("x")),histoData)
        else:    
            hist = ROOT.RooDataHist("data","data",ROOT.RooArgList(self.w.var("x"),self.w.var("y"),self.w.var("z")),histoData)

        getattr(self.w,'import')(hist)
        genhist = ROOT.RooDataHist("gen","gen",ROOT.RooArgList(self.w.var("genx")),genData)
        getattr(self.w,'import')(genhist)
        self.dataSize=histoData.Integral()
        self.genSize=genData.Integral()

    def build1DModel(self):
        self.w.factory('scale[1.0,0.99,1.01]')
        self.w.factory('error1[0.5,0.4,1]')
        self.w.factory('error2[0.0]')
        getattr(self.w,'importClassCode')(ROOT.RooGaussianSumPdf.Class(),1)
        pdf = ROOT.RooGaussianSumPdf("model","model",self.w.var("x"),self.w.var('scale'),self.w.var('error1'),self.w.var('error2'),self.w.data("gen"),'genx')
        getattr(self.w,'import')(pdf)

    def build1DModelBkg(self):
        self.w.factory('scale[1.0,0.99,1.01]')
        self.w.factory('error1[0.5,0.4,1]')
        self.w.factory('error2[0.0]')
        getattr(self.w,'importClassCode')(ROOT.RooGaussianSumPdf.Class(),1)
        pdf = ROOT.RooGaussianSumPdf("modelSig","model",self.w.var("x"),self.w.var('scale'),self.w.var('error1'),self.w.var('error2'),self.w.data("gen"),'genx')
        getattr(self.w,'import')(pdf)
        self.w.factory("RooExponential::expo(x,slope[-1,-10,10])")
        self.w.factory("SUM::model(NSIG[100000,0,500000000]*modelSig,NBKG[1000,0,500000000]*expo)")

    def build1DModelJPsiBkg(self):
        self.w.factory('scale[1.0,0.99,1.01]')
        self.w.factory('error1[0.01,0.004,0.5]')
        self.w.factory('error2[0.0]')
        getattr(self.w,'importClassCode')(ROOT.RooGaussianSumPdf.Class(),1)
        pdf = ROOT.RooGaussianSumPdf("modelSig","model",self.w.var("x"),self.w.var('scale'),self.w.var('error1'),self.w.var('error2'),self.w.data("gen"),'genx')
        getattr(self.w,'import')(pdf)
        self.w.factory("RooExponential::expo(x,slope[-1,-10,10])")
        self.w.factory("SUM::model(NSIG[100000,0,500000000]*modelSig,NBKG[1000,0,500000000]*expo)")

    def build1DModelJPsi(self):
        self.w.factory('scale[1.0,0.99,1.01]')
        self.w.factory('error1[0.01,0.004,0.5]')
        self.w.factory('error2[0.0]')
        getattr(self.w,'importClassCode')(ROOT.RooGaussianSumPdf.Class(),1)
        pdf = ROOT.RooGaussianSumPdf("model","model",self.w.var("x"),self.w.var('scale'),self.w.var('error1'),self.w.var('error2'),self.w.data("gen"),'genx')
        getattr(self.w,'import')(pdf)


    def build1DModelRel(self):
        self.w.factory('scale[1.0,0.99,1.01]')
        self.w.factory('error1[1,0.3,3]')
        self.w.var("error1").setError(1000.0)
        self.w.factory('error2[0.0]')
        getattr(self.w,'importClassCode')(ROOT.RooGaussianSumPdfRelative.Class(),1)
        pdf = ROOT.RooGaussianSumPdfRelative("modelSig","model",self.w.var("x"),self.w.var('scale'),self.w.var('error1'),self.w.var('error2'),self.w.data("gen"),'genx')
        getattr(self.w,'import')(pdf)
        self.w.factory("RooExponential::expo(x,slope[-1,-10,10])")
        self.w.factory("SUM::model(NSIG[100000,0,500000000]*modelSig,NBKG[1000,0,500000000]*expo)")




    def build2DModel(self):
        self.w.factory('scale[1.0,0.99,1.01]')
        self.w.factory('a2[0,-0.0008,0.001]')
        self.w.factory("expr::error1('sqrt(y*y/(x*x)+0.5*a2)*x',x,y,a2)")
        self.w.factory('error2[0.0]')
        getattr(self.w,'importClassCode')(ROOT.RooGaussianSumPdf.Class(),1)
        pdf = ROOT.RooGaussianSumPdf("modelSig","model",self.w.var("x"),self.w.var('scale'),self.w.function('error1'),self.w.var('error2'),self.w.data("gen"),'genx')
        getattr(self.w,'import')(pdf)
        self.w.factory("RooExponential::expo(x,slope[-1,-10,10])")
        self.w.factory("SUM::model(NSIG[100000,100,500000000]*modelSig,NBKG[1000,0,500000000]*expo)")
        self.conditionals.append('y')



    def build3DModel(self):
        self.w.factory('scale[1.0,0.995,1.005]')
        self.w.factory('a2[100e-6,5e-6,0.001]')
        self.w.factory('c2[100e-6,1e-6,0.001]')
        self.w.factory('b2[1e-8,1e-9,1e-4]')
        self.w.factory('d2[1,0,1000]')
        self.w.factory("expr::error1('sqrt(0.5*a2+0.25*b2*y*y+0.25*b2*z*z+0.25/(1+d2/(y*y)) +0.25/(1+d2/(z*z)))*x',x,y,z,a2,b2,c2,d2)")
        self.w.factory('error2[0.0]')
        getattr(self.w,'importClassCode')(ROOT.RooGaussianSumPdf.Class(),1)
        pdf = ROOT.RooGaussianSumPdf("modelSig","model",self.w.var("x"),self.w.var('scale'),self.w.function('error1'),self.w.var('error2'),self.w.data("gen"),'genx')
        getattr(self.w,'import')(pdf)
        self.w.factory("RooExponential::expo(x,slope[-1,-10,10])")
        self.w.factory("SUM::model(NSIG[100000,100,500000000]*modelSig,NBKG[1000,0,500000000]*expo)")
        self.conditionals.append('y')
        self.conditionals.append('z')



    def build1DCBModel(self):
        self.w.factory("RooCBShape::modelSig(x,scale[3,2.5,3.5],sigma[0.03,0.0001,5],alpha[3,0.1,10],n[5])")
        self.w.factory("RooExponential::expo(x,slope[-1,-10,10])")
        self.w.factory("SUM::model(NSIG[100000,0,500000000]*modelSig,NBKG[1000,0,500000000]*expo)")


    def plot(self):
        c=ROOT.TCanvas("c","c")
        frame=self.w.var("x").frame()
        self.w.data("data").plotOn(frame)
        self.w.pdf("model").plotOn(frame)
        chi=frame.chiSquare()
        self.w.pdf('model').paramOn(frame, self.w.data('data'), "chi2=%s" %chi)
        frame.Draw()
        c.SaveAs(self.direc+"/plot_"+str(self.bin)+".root")
        c.SaveAs(self.direc+"/plot_"+str(self.bin)+".pdf")
        c.SaveAs(self.direc+"/plot_"+str(self.bin)+".png")

    def fit(self,verbose=1):
        if verbose==0 :
            ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.WARNING)
        
        if len(self.conditionals)==0:    
            self.fitResult=self.w.pdf("model").fitTo(self.w.data("data"),ROOT.RooFit.Verbose(verbose),ROOT.RooFit.PrintLevel(verbose),ROOT.RooFit.Timer(0),ROOT.RooFit.NumCPU(1,0),ROOT.RooFit.Save(1))
            self.fitResult=self.w.pdf("model").fitTo(self.w.data("data"),ROOT.RooFit.Verbose(verbose),ROOT.RooFit.PrintLevel(verbose),ROOT.RooFit.Timer(0),ROOT.RooFit.NumCPU(1,0),ROOT.RooFit.Save(1))
        else:
            self.w.defineSet("conditionals",",".join(self.conditionals))
            self.fitResult=self.w.pdf("model").fitTo(self.w.data("data"),ROOT.RooFit.Verbose(verbose),ROOT.RooFit.PrintLevel(verbose),ROOT.RooFit.NumCPU(1,0),ROOT.RooFit.Save(1),ROOT.RooFit.ConditionalObservables(self.w.set('conditionals')))          
        print '-------FINAL RESULT------'
        if self.fitResult is not None:
            self.fitResult.Print()
            print '-COVARIANCE-'
            self.fitResult.correlationMatrix().Print()
            
    def write(self):
        self.outFile.cd()
        self.w.Write()
        
