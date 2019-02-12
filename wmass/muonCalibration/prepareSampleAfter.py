class prepareSampleAfter:

    ROOT.gInterpreter.ProcessLine('''
    std::vector<TRandom3> myRndGens(8);
    int seed = 1; // not 0 because seed 0 has a special meaning
    for (auto &&gen : myRndGens) gen.SetSeed(seed++);
    ''')


    def __init__(self, cut,isMC = True, gen = False, res = 'J'):
        
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
                    .Define('v1', 'ROOT::Math::PtEtaPhiMVector(corrpt1,eta1,phi1,0.105)')\
                    .Define('v2', 'ROOT::Math::PtEtaPhiMVector(corrpt2,eta2,phi2,0.105)')\
                    .Define('corrMass', 'float((v1+v2).M())')

        else:

            self.d = d.Filter(self.cut)\
                    .Define('smearedgenMass', 'genMass+myRndGens[rdfslot_].Gaus(0, massError)')


        heta1 = d.Histo1D(("eta1", " ; #eta muon pos; ", 100, -2.5, 2.5), "eta1")

        return self.d

    def getTH1(self):

        return self.myTH1

    def getTH2(self):

        return self.myTH2  

    def getTH3(self):

        return self.myTH3
