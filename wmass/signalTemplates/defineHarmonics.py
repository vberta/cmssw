import sys
sys.path.append('../../framework')
from module import *

class defineHarmonics(module):
   
    def __init__(self):
        
        self.myTH1 = []
        self.myTH2 = []
        self.myTH3 = []

    def run(self,d):

        # angular coefficients as defined in https://arxiv.org/pdf/1609.02536.pdf

        self.d = d.Define("P0", "float(1./2.*(1.-3.*CStheta_preFSR*CStheta_preFSR))")\
        .Define("P1", "float(2.*CStheta_preFSR*sqrt(1.-CStheta_preFSR*CStheta_preFSR)*cos(CSphi_preFSR))")\
        .Define("P2", "float(1./2. *(1.-CStheta_preFSR*CStheta_preFSR)*cos(2.*CSphi_preFSR))")\
        .Define("P3", "float(sqrt(1.-CStheta_preFSR*CStheta_preFSR)*cos(CSphi_preFSR))")\
        .Define("P4", "float(CStheta_preFSR)")\
        .Define("P5", "float((1.-CStheta_preFSR*CStheta_preFSR)*sin(2.*CSphi_preFSR))")\
        .Define("P6", "float(2.*CStheta_preFSR*sqrt(1.-CStheta_preFSR*CStheta_preFSR)*sin(CSphi_preFSR))")\
        .Define("P7", "float(sqrt(1.-CStheta_preFSR*CStheta_preFSR)*sin(CSphi_preFSR))")\
        .Define("PUL", "float(1+CStheta_preFSR*CStheta_preFSR)")
        
        return self.d

    def getTH1(self):

        return self.myTH1

    def getTH2(self):

        return self.myTH2  

    def getTH3(self):

        return self.myTH3

