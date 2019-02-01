# dummy class to use as root of analysis tree

class input:
   
    def __init__(self):
        
        pass
        
        self.myTH1 = []
        self.myTH2 = []
        self.myTH3 = []

    def doSomething(self,d):

        self.d = d

        entries = d.Count()

        print entries.GetValue(), 'input'
        
        return self.d

    def getTH1(self):

        return self.myTH1

    def getTH2(self):

        return self.myTH2  

    def getTH3(self):

        return self.myTH3    


