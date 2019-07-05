import ROOT
from array import array
import copy
import numpy as np

import sys
sys.path.append('../../framework')
from module import *

class TemplateFitter(module):
    def __init__(self, string):

        pass
        
        self.myTH1 = []
        self.myTH2 = []
        self.myTH3 = []
        self.string = string
    
    def TH2_to_array(self, h):

        nx = h.GetNbinsX()
        ny = h.GetNbinsY()

        out = []

        for iy in range(1,ny+1):
            for ix in range(1,nx+1):
                aux = h.GetBinContent(ix, iy)
                out.append(aux)

        return np.array(out)

    def run(self,d):

        self.d = d

        ROOT.gROOT.SetBatch()

        fIn = ROOT.TFile.Open(self.string)
      
        
        myf = fIn.Get("Templates2D/nom")


        T = []
        integrals = []

        for key in myf.GetListOfKeys():
            
            name = key.GetName()
            if "pseudodata" in name: continue

            th2=ROOT.TH2D

            th2 = myf.Get(key.GetName())

            T.append(self.TH2_to_array(th2))
            integrals.append(th2.Integral())

        data = myf.Get("pseudodata")
        N_data = self.TH2_to_array(data)
        Sigma = np.sqrt(N_data)

        yw = N_data/Sigma

        A = np.transpose(np.stack(T))

        R = []
        for i,rows in enumerate(A):
            R.append(rows/Sigma[i])

        Aw = np.stack(R)

        out = np.linalg.lstsq(Aw, yw)

        print( "fit res", out[0])

        N_bins = 16*11
        N_bins_tot = 100*80

        print( "number of W pT - Y bins", N_bins)
        chisq = out[1]/(N_bins_tot-N_bins)
        print( "reduced chi square of the fit: ", chisq)
        print( out[1], N_bins_tot-N_bins)

        Cova = np.linalg.inv(np.dot(Aw.T,Aw))   

        # take eigenvalues
        var=np.linalg.eig(Cova)[0]
        # take eigenvectors
        eig=np.linalg.eig(Cova)[1]

        corr = np.corrcoef(Cova)

        # compute the error band corresponding to 1 sigma variations
        err = np.zeros(N_bins)

        yArr = [-6.0, -3.0, -2.5, -2.0, -1.6, -1.2, -0.8, -0.4, 0, 0.4, 0.8, 1.2 ,1.6, 2.0, 2.5, 3.0, 6.0]
        ptArr = [0., 4., 8., 12., 16., 20., 24., 32., 40., 60., 100., 200.]

        h = ROOT.TH2D("h", "h", len(yArr)-1, array('f',yArr), len(ptArr)-1, array('f',ptArr))

        for i in range (0, np.size(var)): # loop over variations
            err[i] = 0
            for j in range(0, np.size(eig[i])): # loop over eigenvectors components
                err[i] = err[i] + (np.sqrt(var[j])*eig[j][i])**2 # sum in quadrature of the variations

        for i in range (0, h.GetNbinsX()): #y
            for j in range (0, h.GetNbinsY()): #pt

                #print i + j*h.GetNbinsX(), out[0][i + j*h.GetNbinsX()]
                h.SetBinContent(i+1,j+1, out[0][i + j*h.GetNbinsX()]*integrals[i + j*h.GetNbinsX()])
                h.SetBinError(i+1,j+1, np.sqrt(err[i + j*h.GetNbinsX()])*integrals[i + j*h.GetNbinsX()])
                
        self.myTH2.append(copy.deepcopy(h))

        return self.d


