import ROOT
import math

files = ["histosWPlus.root", "histosWMinus.root"]
fOut = ["coeffWPlus.root", "coeffWMinus.root"]


for idx,f in enumerate(files):

	fIn = ROOT.TFile.Open(f)

	hNum =[]
	hNum2 =[]
	hDen =[]

	out = ROOT.TFile(fOut[idx], "recreate")

	for key in fIn.GetListOfKeys():

		name = key.GetName()
		h = fIn.Get(name)

		if "denom" in name:
			hDen.append(h)
		elif "A" in name:
			hNum.append(h)
		else: 
			hNum2.append(h)

	for k,h in enumerate(hNum):
		
		for j in range(1,h.GetNbinsY()+1):
			for in in range(1, GetNbinsX()+1):

				h.SetBinContent(i,j,h.GetBinContent(i,j)/hDen[0].GetBinContent(i,j))

				# error propagation

				stdErr2 = hNum2[k].GetBinContent(i,j)/hDen[0].GetBinContent(i,j) - h.GetBinContent(i,j)*h.GetBinContent(i,j)
				sqrtneff = hDen[0].GetBinContent(i,j)/hDen[0].GetBinError(i,j)

				coefferr = math.sqrt(stdErr2)/sqrtneff

				h.SetBinError(i,j,coefferr)

                cont = h.GetBinContent(i,j)
                err = h.GetBinError(i,j)
                    
                if k == 0  
                    h.SetBinContent(i,j, 20./3.*cont + 2./3.)
                    h.SetBinError(i,j, 20./3.*err)
                
                elif k == 1 || k == 5 || k == 6        
                    h.SetBinContent(i,j, 5*cont)
                    h.SetBinError(i,j, 5*err)
                
                elif(k == 2)         
                    h.SetBinContent(i,j, 10*cont)
                    h.SetBinError(i,j, 10*err)
                
                else       
                    h.SetBinContent(i,j, 4*cont)
                    h.SetBinError(i,j, 4*err)

    	out.cd()

    	h.Write()
