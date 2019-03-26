# Base class from which the other modules will inherit

class module:
   
    def __init__(self):
        
        self.myTH1 = []
        self.myTH2 = []
        self.myTH3 = []
        

    def run(self,d):

        pass 

    def defineSubcollectionFromIndex(self, collection, subcollection, idx, d):

        columns = list(d.GetColumnNames())
        columns.extend(d.GetDefinedColumnNames())

        main = [c for c in columns if c.startswith(collection)] # columns of the main collection

        subSet = [c.replace(collection,subcollection) for c in main if c.startswith(collection)] # columns of the sub collection

        for i,s in enumerate(subSet):
            
            d = d.Define(s, '{vec}[{idx}]'.format(vec=main[i], idx=idx))

        # define new vector length 

        d = d.Define("n{}".format(subcollection), "{}".format(1))


        return d


    def defineSubcollectionFromIndexWithSyst(self, collection, subcollection, idx, d, nom, syst):

        columns = list(d.GetColumnNames())
        columns.extend(d.GetDefinedColumnNames())

        main = [c for c in columns if c.startswith(collection)] # columns of the main collection

        subSetWithSyst = []

        for sys in syst: # syst is a list of strings containing the systematics ex. Up and Down

            subSet = [c.replace(collection,subcollection) for c in main if c.startswith(collection) and nom in c] # columns of the sub collection if affected by the syst
            subSetWithSyst.extend([c.replace(nom,sys) for c in subSet]) # now with systematics


        for i,s in enumerate(subSetWithSyst):
            
            d = d.Define(s, '{vec}[{idx}]'.format(vec=main[i], idx=idx))

        return d

    def getTH1(self):

        return self.myTH1

    def getTH2(self):

        return self.myTH2  

    def getTH3(self):

        return self.myTH3  


