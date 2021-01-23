from audioLib.objects.AudioObject import AudioObject
from audioLib.objects.Patchbay import PatchPoint
from state.State import State
from audioLib.utils.Utils import *


class inputs:
	sound = AudioObject()
	env = AudioObject(defaultValue=1)
	filter = AudioObject()
	filterenv = AudioObject(defaultValue=1)
	filterCutoff = PatchPoint()
	vca = PatchPoint()


class Vca(AudioObject):
	def __init__(self):
		super(Vca, self).__init__(1, 1)
		self.vol = 0
		self.inputs = inputs()
		self.env = np.ones((AudioConst.CHUNK, 1))
		self.filterenv = np.ones((AudioConst.CHUNK, 1))
		self.mixer = np.zeros((AudioConst.CHUNK, 1))
		self.wave = np.zeros((AudioConst.CHUNK, 1))
		self.cutoff = emptyChunk()

	def checkValues(self):
		try:
			self.vol = np.clip(State.params['vol'], 0, 1)
		except KeyError:
			pass
	# State.params['vol'] = .5

	def CVOutput(self, out: np.ndarray) -> None:
		out[:] = self.wave

	def EGOutput(self, out: np.ndarray) -> None:
		out[:] = self.env

	def filterEGOutput(self, out: np.ndarray) -> None:
		out[:] = self.filterenv

	def output(self, out: np.ndarray) -> None:
		self.checkValues()
		env = self.env
		self.inputs.env.output(env)
		mixer = self.mixer.copy()
		self.inputs.vca(mixer)

		env += np.clip(mixer, 0, 1)

		mixer = self.mixer.copy()
		self.inputs.sound.output(mixer)

		self.filterenv.fill(0)

		self.inputs.filterenv.output(self.filterenv)
		self.cutoff.fill(0)
		self.inputs.filterCutoff(self.cutoff)

		self.inputs.filter.output(out, mixer[:, 0], self.filterenv[:, 0], self.cutoff[:, 0])

		out[:] *= env * self.vol
		self.wave[:] = out
