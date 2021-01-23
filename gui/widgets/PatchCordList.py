
class PatchCordList(list):
	def __init__(self):
		super(PatchCordList, self).__init__()

	def add(self, pc):
		if pc in self:
			self.remove(pc)
		self.append(pc)

	def last(self):
		if len(self) > 0:
			return self[-1]
		else:
			return None

	def is_empty(self):
		if len(self) == 0:
			return True
		else:
			return False