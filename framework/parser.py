class parser:
    
    def __init__(self, file):

        self.file = file
    
        self.f = open(self.file)                      

    def parse(self):

        print [x.strip() for x in self.f.readlines()] 
        return [x.strip() for x in self.f.readlines()] 

