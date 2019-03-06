import ROOT
from array import array

class prepareSampleAfter:

    def __init__(self, cut, gen = False, weight = False, res = 'J'):
        
        self.myTH1 = []
        self.myTH2 = []
        self.myTH3 = []

        self.cut = cut
        self.gen = gen
        self.weight = weight
        self.res = res

        
    def run(self,d):
        

        if not self.gen:

            self.d = d.Filter(self.cut)\
                    .Define('v1corr', 'ROOT::Math::PtEtaPhiMVector(corrpt1,eta1,phi1,0.105)')\
                    .Define('v2corr', 'ROOT::Math::PtEtaPhiMVector(corrpt2,eta2,phi2,0.105)')\
                    .Define('corrMass', 'float((v1corr+v2corr).M())')

        else:

            

            self.d = d.Filter(self.cut)\
                     .Define('smearedgenMass', 'genMass+myRndGens[rdfslot_].Gaus(0, massErr)')
                    

        mass = 'corrMass'

        if self.gen:

            mass = 'smearedgenMass'

        pts=[20,30,40,50,60,70,100]
        etas=[-1.0,-0.7,-0.5,-0.25, 0.25, 0.5,0.7,1.0]
        masses=[]

        for i in range(0,101):
            masses.append(75+0.4*i)    

        if self.res == 'Z':

            if not self.weight: 

                heta1 = self.d.Histo2D(("closure_eta1", " ; #eta muon pos; Z dimuon mass", len(etas)-1, array('f',etas),len(masses)-1, array('f',masses)), "eta1", "{}".format(mass))
                heta2 = self.d.Histo2D(("closure_eta2", " ; #eta muon neg; Z dimuon mass", len(etas)-1, array('f',etas),len(masses)-1, array('f',masses)),"eta2", "{}".format(mass))

                hpt1 = self.d.Histo2D(("closure_pt1", " ; p_{T} muon pos; Z dimuon mass", len(pts)-1, array('f',pts),len(masses)-1, array('f',masses)), "pt1","{}".format(mass))
                hpt2 = self.d.Histo2D(("closure_pt2", " ; p_{T} muon neg; Z dimuon mass", len(pts)-1, array('f',pts),len(masses)-1, array('f',masses)), "pt2","{}".format(mass))

                self.myTH2.append(heta1)
                self.myTH2.append(heta2)

                self.myTH2.append(hpt1)
                self.myTH2.append(hpt2)


            else: #reweight gen to match Z data


                heta1 = self.d.Histo2D(("closure_eta1", " ; #eta muon pos; Z dimuon mass", len(etas)-1, array('f',etas),len(masses)-1, array('f',masses)), "eta1", "{}".format(mass), "ptWeight")
                heta2 = self.d.Histo2D(("closure_eta2", " ; #eta muon neg; Z dimuon mass", len(etas)-1, array('f',etas),len(masses)-1, array('f',masses)), "eta2", "{}".format(mass), "ptWeight")

                hpt1 = self.d.Histo2D(("closure_pt1", " ; p_{T} muon pos; Z dimuon mass", len(pts)-1, array('f',pts),len(masses)-1, array('f',masses)), "pt1", "{}".format(mass), "ptWeight")
                hpt2 = self.d.Histo2D(("closure_pt2", " ; p_{T} muon neg; Z dimuon mass", len(pts)-1, array('f',pts),len(masses)-1, array('f',masses)), "pt2", "{}".format(mass), "ptWeight")

                self.myTH2.append(heta1)
                self.myTH2.append(heta2)

                self.myTH2.append(hpt1)
                self.myTH2.append(hpt2)

        
        else:

            print 'ciao'

        return self.d

    def getTH1(self):

        return self.myTH1

    def getTH2(self):

        return self.myTH2  

    def getTH3(self):

        return self.myTH3
