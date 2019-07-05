import ROOT
import os

def unrollTH2(th2, catDic, templNumb):

    for i in range(1, th2.GetNbinsY()+1):

        th1 = th2.ProjectionX("",i,i)
        
        if templNumb>0:
                th1.SetName('templ{j}'.format(j=templNumb))
        else:
                th1.SetName('dataobs')

        if th1.GetEntries()>0:
            catDic['cat{i}'.format(i=i)].append(th1)
        else:
            for k in range(1, th1.GetNbinsX()+1):
                th1.SetBinContent(k, 1e-5)
            catDic['cat{i}'.format(i=i)].append(th1)

fIn = ROOT.TFile.Open('TEST/templates2DIncl.root')
myf = fIn.Get("Templates2D/nom")


catDic = {}

for i in range(1, 81):
    catDic['cat{i}'.format(i=i)] = []

j = 0

for key in myf.GetListOfKeys():

    th2 = myf.Get(key.GetName())
	
    unrollTH2(th2,catDic,j)

    j = j+1

if not os.path.exists('TEMPLATES'):
        
    os.system("mkdir -p " + 'TEMPLATES')
   
    os.chdir('TEMPLATES') 

for key, hList in catDic.iteritems():       

    fout = ROOT.TFile(key+'.root', "recreate")
    fout.cd()

    for h in hList:
        h.Write()

