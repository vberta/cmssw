class prepareSample:

    def __init__(self, cut, target, isMC = True, gen = False):
        
        self.myTH1 = []
        self.myTH2 = []
        self.myTH3 = []

        self.isMC = isMC
        self.gen = gen
        self.cut = cut
        self.target = target
 
    def run(self,d):

        if not self.gen:

            self.d = d.Filter(self.cut)\
                     .Define('scale', 'mass/{t}'.format(t=self.target))\
                     .Define('resolution', 'massErr/{t}'.format(t=self.target))\
                     .Define('v1', 'ROOT::Math::PtEtaPhiMVector(pt1,eta1,phi1,0.105)')\
                     .Define('v2', 'ROOT::Math::PtEtaPhiMVector(pt2,eta2,phi2,0.105)')\
                     .Define('rapidity', '(v1+v2).Rapidity()')\
                     .Filter('fabs(rapidity)<2.4')\
                     .Define('ptRes', 'float((v1+v2).Pt())')

            

        else:

            self.d = d.Filter(self.cut)\
                     .Define('scale', 'mass/{t}'.format(t=self.target))\
                     .Define('resolution', 'massErr/{t}'.format(t=self.target))\
                     .Define('v1', 'ROOT::Math::PtEtaPhiMVector(mcpt1,eta1,phi1,0.105)')\
                     .Define('v2', 'ROOT::Math::PtEtaPhiMVector(mcpt2,eta2,phi2,0.105)')\
                     .Define('rapidity', '(v1+v2).Rapidity()')\
                     .Filter('fabs(rapidity)<2.4')\
                     .Define('ptRes', 'float((v1+v2).Pt())')


        return self.d

    def getTH1(self):

        return self.myTH1

    def getTH2(self):

        return self.myTH2  

    def getTH3(self):

        return self.myTH3
