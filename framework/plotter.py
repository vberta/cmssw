import os
import ROOT
import copy

ROOT.gInterpreter.Declare('TH1D *Obj2TH1D(TObject *p) { return (TH1D*)p; }')

class plotter:
    
    def __init__(self, outdir, folder = '', fileList = []):

        self.folder = folder # folder containig the various outputs
        self.fileList = fileList # list of files in each folders
        self.canvas = []
        self.outdir = outdir
        
        ROOT.gROOT.SetBatch()

        if not os.path.exists(self.outdir):
            os.system("mkdir -p " + self.outdir)

    def getHistos(self):

        self.histos = []

        os.chdir(self.folder)

        for f in self.fileList:

            hlist = []
            
            fIn = ROOT.TFile.Open(f)

            for key in fIn.GetListOfKeys():

                h = fIn.Get(key.GetName())
                h.Sumw2()
                    
                hlist.append(copy.deepcopy(h))

            self.histos.append(hlist)

        os.chdir('..')

        self.histos = zip(*self.histos) # now in the right order

    def createStack(self):

        self.stacks = []

        for group in self.histos:
            
            hs = ROOT.THStack(group[0].GetName(),"")
            for h in group:
                hs.Add(h)

            self.stacks.append(hs)

    def plotDataMC(self):

        
        self.getHistos()

        for group in self.histos: # group of histos with same name

            legend = ROOT.TLegend(0.62, 0.70, 0.82, 0.88)
            legend.SetFillColor(0)
            legend.SetBorderSize(0)
            legend.SetTextSize(0.03)

            legend.AddEntry(group[0], "Data", "PE1")
            legend.AddEntry(group[1], "MC", "f")

            group[0].Scale(1./group[0].Integral())
            group[1].Scale(1./group[1].Integral())
            
            c = ROOT.TCanvas(group[0].GetName(), '')
            rp = ROOT.TRatioPlot(group[0], group[1])
            
            #group[1].SetLineWidth(2)
            #group[1].SetFillStyle(1001)
            #group[1].SetLineColor(ROOT.kBlack)
            #group[1].SetFillColor(ROOT.kAzure - 9)

            c.SetTicks(0, 1)
            rp.GetLowYaxis().SetNdivisions(505)
            c.cd()
            rp.Draw()

            h = ROOT.Obj2TH1D(rp.GetUpperRefObject())
            h.SetMarkerStyle(ROOT.kFullCircle)
            h.SetLineWidth(1)
            h.SetMarkerSize(1.0)
            h.SetMarkerColor(ROOT.kBlack)
            h.SetLineColor(ROOT.kBlack)

            legend.Draw()
            
            c.Update()
            c.SaveAs("{dir}/{c}.pdf".format(dir=self.outdir,c=c.GetName()))
            
            #self.canvas.append(copy.deepcopy(c))

    def draw(self):

        if not os.path.exists(self.outdir):
            os.system("mkdir -p " + self.outdir)

        for c in self.canvas:
            c.SetDirectory(self.outdir)    
        
        os.chdir(self.outdir)

        for c in self.canvas:
            c.SaveAs("{c}.pdf".format(c=c.GetName()))

        os.chdir('..')


            
                
                



                                  

    