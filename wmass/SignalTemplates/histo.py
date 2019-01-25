class defineHarmonics:
   
    def __init__(self):
        
        pass
        
        self.myTH1 = []
        self.myTH2 = []
        self.myTH3 = []

    def run(self,d):

        # angular coefficients as defined in https://arxiv.org/pdf/1609.02536.pdf

        self.d = d.Define("P0", "1./2.*(1.-3.*CStheta_preFSR*CStheta_preFSR)").Define("P1", "2.*CStheta_preFSR*sqrt(1.-CStheta_preFSR*CStheta_preFSR)*TMath::Cos(CSphi_preFSR)").Define("P2", "1./2. *(1.-CStheta_preFSR*CStheta_preFSR)*TMath::Cos(2.*CSphi_preFSR)")
        .Define("P3", "TMath::Sqrt(1.-CStheta_preFSR*CStheta_preFSR)*TMath::Cos(CSphi_preFSR)").Define("P4", "CStheta_preFSR").Define("P5", "(1.-CStheta_preFSR*CStheta_preFSR)*TMath::Sin(2.*CSphi_preFSR)").Define("P6", "(2.*CStheta_preFSR*TMath::Sqrt(1.-CStheta_preFSR*CStheta_preFSR)*TMath::Sin(CSphi_preFSR)")
        .Define("P7", "TMath::Sqrt(1.-CStheta_preFSR*CStheta_preFSR)*TMath::Sin(CSphi_preFSR))").Define("PUL", "1+CStheta_preFSR*CStheta_preFSR")
        
        return self.d

    def getTH1(self):

        return self.myTH1

    def getTH2(self):

        return self.myTH2  

    def getTH3(self):

        return self.myTH3    


