import ROOT

class module2:
	def __init__(self):
	 	pass

	def beginJob(self, d): 	
	 	
	 	self.d = d

	def dosomething(self):

		entries1 = self.d.Filter("Wrap_preFSR>0").Count()
		
		print("%s entries passed all filters" %entries1.GetValue())

		return self.d