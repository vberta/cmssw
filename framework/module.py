import ROOT

class module:
	def __init__(self):
	 	pass

	def beginJob(self, d): 	
	 	
	 	self.d = d
		print "in beginJob"

	def dosomething(self):

		entries1 = self.d.Filter("GenPart_pt[GenPart_bareMuonIdx]>20").Count()
		
		print("%s entries passed all filters" %entries1.GetValue())

		return self.d