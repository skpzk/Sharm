import numpy as np
from audioLib.objects.AudioObject import AudioObject


class Mixer(AudioObject):
	def __init__(self):
		super(Mixer, self).__init__(0, 0)
		self.inputs = []

	def output(self, out: np.ndarray) -> None:
		out.fill(0)
		# t = []
		for inputObj in self.inputs:
			inputObj(out)
