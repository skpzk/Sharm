import numpy as np


class AudioObject:
	def __init__(self, nbCVInputs: int = 0, nbCVOutputs: int = 0, **kwargs):
		self.nbCVInputs = nbCVInputs
		self.nbCVOutputs = nbCVOutputs
		self.CVinputs = []
		self.CVoutputs = []

		self.defaultValue = 0

		for key, value in kwargs.items():
			if key == 'defaultValue':
				self.defaultValue = value

	def CVOutput(self, out: np.ndarray) -> None:
		out[:] += self.defaultValue

	def output(self, out: np.ndarray) -> None:
		# get inputs
		# treat inputs
		# compute output
		out.fill(self.defaultValue)