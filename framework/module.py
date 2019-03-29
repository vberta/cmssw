# Base class from which the other modules will inherit

class module:
   
    def __init__(self):
        
        self.myTH1 = []
        self.myTH2 = []
        self.myTH3 = []
        

    def run(self,d):

        pass 


    def defineSubcollectionFromIndex(self, collection, subcollection, idx, d, syst):

        columns = list(d.GetColumnNames())
        columns.extend(d.GetDefinedColumnNames())

        main = [c for c in columns if c.startswith(collection)] # columns of the main collection

        subSetWithSyst = []

        for nom, variations in syst.iteritems(): 

            if len(variations)>0: # case variations
                
                subSet = [c.replace(collection,subcollection) for c in main if c.startswith(collection) and nom in c] # columns of the sub collection if affected by the syst
                print subSet, "subSet"

                for var in variations:
                    subSetWithSyst.extend([c.replace(nom,var) for c in subSet]) # now with systematics
                print subSetWithSyst, "subSetWithSyst"

                for i,s in enumerate(subSetWithSyst):
                    d = d.Define(s, '{vec}[{idx}]'.format(vec=main[i], idx=idx))

            else: #case nominal
                subSet = [c.replace(collection,subcollection) for c in main if c.startswith(collection)]
                subSetNom = [c for c in subSet if not 'Up' in c]
                subSetNom2 = [c for c in subSetNom if not 'Down' in c]
                print subSetNom2, "subSet nominal"

                for i,s in enumerate(subSetNom2):
            
                    d = d.Define(s, '{vec}[{idx}]'.format(vec=main[i], idx=idx))

                # define new vector length 

                d = d.Define("n{}".format(subcollection), "{}".format(1))

        return d

    def getTH1(self):

        return self.myTH1

    def getTH2(self):

        return self.myTH2  

    def getTH3(self):

        return self.myTH3  

    def reset(self):

        self.myTH1 = []
        self.myTH2 = []
        self.myTH3 = [] 