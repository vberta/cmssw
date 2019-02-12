import math 

class basicPlots:
   
    def __init__(self, gen = False, weight = False, res = 'J', calib = False):
        
        
        self.myTH1 = []
        self.myTH2 = []
        self.myTH3 = []
        
        self.gen = gen
        self.weight = weight
        self.res = res
        self.calib = calib

    def run(self,d):

        self.d = d

        heta1 = d.Histo1D(("eta1", " ; #eta muon pos; ", 100, -2.5, 2.5), "eta1")
        heta2 = d.Histo1D(("eta2", " ; #eta muon neg; ", 100, -2.5, 2.5), "eta2")

        hphi1 = d.Histo1D(("phi1", " ; #phi muon pos; ", 100, -math.pi, math.pi), "phi1")
        hphi2 = d.Histo1D(("phi2", " ; #phi muon neg; ", 100, -math.pi, math.pi), "phi2")


        self.myTH1.append(heta1)
        self.myTH1.append(heta2)

        self.myTH1.append(hphi1)
        self.myTH1.append(hphi2)

        mypt1 = 'pt1'
        mypt2 = 'pt2'

        if self.calib: 
            mypt1 = 'corrpt1'
            mypt2 = 'corrpt2'

        if self.res == 'Z':

            hptRes = d.Histo1D(("ptRes", " ; p_{T} Z ; ", 200, 0, 100), "ptRes")
            hmass = d.Histo1D(("mass", " ; Z dimuon mass ; ", 100, 75, 115), "mass")

            self.myTH1.append(hptRes)
            self.myTH1.append(hmass)

            if not self.gen:

                hpt1 = d.Histo1D(("pt1", " ; p_{T} muon pos; ", 100, 22, 100), "{}".format(mypt1))
                hpt2 = d.Histo1D(("pt2", " ; p_{T} muon neg; ", 100, 20, 100), "{}".format(mypt2))
                
                self.myTH1.append(hpt1)
                self.myTH1.append(hpt2)
                
        
            else:

                if self.weight:

                    hpt1 = d.Histo1D(("pt1", " ; p_{T} muon pos; ", 100, 22, 100), "mcpt1", "ptWeight")
                    hpt2 = d.Histo1D(("pt2", " ; p_{T} muon neg; ", 100, 20, 100), "mcpt2", "ptWeight")
                    

                    self.myTH1.append(hpt1)
                    self.myTH1.append(hpt2)
            

                else:
            
                    hpt1 = d.Histo1D(("pt1", " ; p_{T} muon pos; ", 100, 22, 100), "mcpt1")
                    hpt2 = d.Histo1D(("pt2", " ; p_{T} muon neg; ", 100, 20, 100), "mcpt2")
                    
                    self.myTH1.append(hpt1)
                    self.myTH1.append(hpt2)

        else:

            hptRes = d.Histo1D(("ptRes", " ; p_{T} J/#Psi ; ", 200, 0, 100), "ptRes")
            hmass = d.Histo1D(("mass", " ; J/#Psi dimuon mass ; ", 100, 2.895, 3.295), "mass")

            self.myTH1.append(hptRes)
            self.myTH1.append(hmass)

            if not self.gen:

                hpt1 = d.Histo1D(("pt1", " ; p_{T} muon pos; ", 100, 5, 30), "{}".format(mypt1))
                hpt2 = d.Histo1D(("pt2", " ; p_{T} muon neg; ", 100, 5, 30), "{}".format(mypt2))
                
                self.myTH1.append(hpt1)
                self.myTH1.append(hpt2)
                
        
            else:

                if self.weight:

                    hpt1 = d.Histo1D(("pt1", " ; p_{T} muon pos; ", 100, 5, 30), "mcpt1", "ptWeight")
                    hpt2 = d.Histo1D(("pt2", " ; p_{T} muon neg; ", 100, 5, 30), "mcpt2", "ptWeight")
                    

                    self.myTH1.append(hpt1)
                    self.myTH1.append(hpt2)
                    

                else:
            
                    hpt1 = d.Histo1D(("pt1", " ; p_{T} muon pos; ", 100, 5, 30), "mcpt1")
                    hpt2 = d.Histo1D(("pt2", " ; p_{T} muon neg; ", 100, 5, 30), "mcpt2")
                    
                    self.myTH1.append(hpt1)
                    self.myTH1.append(hpt2)


        

        return self.d

    def getTH1(self):

        return self.myTH1

    def getTH2(self):

        return self.myTH2  

    def getTH3(self):

        return self.myTH3

    def triggerLoop(self):

        return self.trigLoop         


