class filter:
   
    def __init__(self, string):
        
        pass
        
        self.myTH1 = []
        self.myTH2 = []
        self.myTH3 = []
        self.trigLoop = False
        self.string = string

    def run(self,d):

        self.d = d.Filter(self.string) # selects W-
        
        return self.d

    def getTH1(self):

        return self.myTH1

    def getTH2(self):

        return self.myTH2  

    def getTH3(self):

        return self.myTH3

    def triggerLoop(self):

        return self.trigLoop         


