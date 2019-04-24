# Base class from which the other modules will inherit

class module:
   
    def __init__(self):
        
        self.myTH1 = []
        self.myTH2 = []
        self.myTH3 = []
        

    def run(self,d):

        pass 


    def defineSubcollectionFromIndex(self, collection, subcollection, idx, d, syst={}):

        columns = list(d.GetColumnNames())
        columns.extend(d.GetDefinedColumnNames())

        subSetWithSyst = []
        mainWithSyst = []

        if syst:

            for nom, variations in syst.iteritems(): 

                if len(variations)>0: # case variations

                    main = [c for c in columns if c.startswith(collection) and nom in c] # columns of the main collection
                
                    subSet = [c.replace(collection,subcollection) for c in main] # columns of the sub collection if affected by the syst

                    for var in variations:
                        subSetWithSyst.extend([c.replace(nom,var) for c in subSet]) # now with systematics
                        mainWithSyst.extend([c.replace(nom,var) for c in main])

                    for i,s in enumerate(subSetWithSyst):
                        d = d.Define(s, '{vec}[{idx}]'.format(vec=mainWithSyst[i], idx=idx))

                else: #case nominal

                    main = [c for c in columns if c.startswith(collection)] # columns of the main collection
                    mainNom = [c for c in main if not 'Up' in c]
                    mainNom2 = [c for c in mainNom if not 'Down' in c]


                    subSet = [c.replace(collection,subcollection) for c in mainNom2 ]
                    subSetNom = [c for c in subSet if not 'Up' in c]
                    subSetNom2 = [c for c in subSetNom if not 'Down' in c]

                    for i,s in enumerate(subSetNom2):
                        d = d.Define(s, '{vec}[{idx}]'.format(vec=mainNom2[i], idx=idx))

                    # define new vector length 

                    d = d.Define("n{}".format(subcollection), "{}".format(1))
        else:

            main = [c for c in columns if c.startswith(collection)] # columns of the main collection
            mainNom = [c for c in main if not 'Up' in c]
            mainNom2 = [c for c in mainNom if not 'Down' in c]


            subSet = [c.replace(collection,subcollection) for c in mainNom2 ]
            subSetNom = [c for c in subSet if not 'Up' in c]
            subSetNom2 = [c for c in subSetNom if not 'Down' in c]

            for i,s in enumerate(subSetNom2):
                d = d.Define(s, '{vec}[{idx}]'.format(vec=mainNom2[i], idx=idx))

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