# dummy class to use as root of analysis tree

class input:
   
    def __init__(self):
        
        pass
        
        self.myTH1 = []
        self.myTH2 = []
        self.myTH3 = []
        self.trigLoop = False

    def run(self,d):

        self.d = d
        
        return self.d

    def getTH1(self):

        return self.myTH1

    def getTH2(self):

        return self.myTH2  

    def getTH3(self):

        return self.myTH3  

    def triggerLoop(self):

        return self.trigLoop        


