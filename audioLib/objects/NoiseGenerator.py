import numpy as np

from audioLib.AudioConst import AudioConst
from audioLib.objects.AudioObject import AudioObject


class NoiseGenerator(AudioObject):
	def __init__(self):
		super(NoiseGenerator, self).__init__()

	def CVOutput(self, out: np.ndarray) -> None:
		out[:] = np.clip(np.random.default_rng().normal(size=(AudioConst.CHUNK, 1)), -1, 1)


class SH(AudioObject):
	def __init__(self):
		super(SH, self).__init__()

	def CVOutput(self, out: np.ndarray) -> None:
		out[:] = np.clip(np.ones((AudioConst.CHUNK, 1)) * np.random.default_rng().normal(), -1, 1)
