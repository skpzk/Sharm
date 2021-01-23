from audioLib.objects.Patchbay import PatchPoint
from audioLib.objects.Vco import stateKeys
from audioLib.utils.Utils import *
from state.State import State

class inputs:
	div = PatchPoint()


class Rhythm:
	def __init__(self, clock):
		self.clock = clock
		self.div = 2
		self.divKnobValue = 1
		self.r0 = 0
		self.r = np.expand_dims(np.zeros(AudioConst.CHUNK), axis=1)
		self.CVDiv = np.expand_dims(np.zeros(AudioConst.CHUNK), axis=1)
		self.inputs = inputs()

		self.stateKeys = stateKeys()

		State.params.setCallback('reset', self.reset)
		self.colorKnobName = ""

	def reset(self):
		# print("reset callback called")
		if State.params['reset'] == 1:
			self.r.fill(0)
			self.r0 = 1

	def checkValues(self):
		try:
			divKnobValue = State.params[self.stateKeys.div] * 16
			self.divKnobValue = int(np.clip(divKnobValue, 1, 16))
			self.div = self.divKnobValue
		except KeyError:
			pass

	def orOutput(self, out):
		out[:] |= self.r


	def tick(self):

		# check ctrl panel
		self.checkValues()
		# check CV inputs
		self.CVDiv.fill(0)
		self.inputs.div(self.CVDiv)
		# print("CVDiv = ", self.CVDiv[0])
		self.div += self.CVDiv[0] * 8
		self.div = int(np.clip(self.div, 1, 16))
		# print("self.div = ", self.div)
		# print("R1 tick method")
		signal = self.clock.risingEdgeSignal
		if self.div != 1:
			r = np.cumsum(signal, axis=0) + self.r0

			self.r0 = np.mod(r[-1][0], self.div)

			r = r * signal

			r = np.mod(r, self.div)

			self.r = (r == 1)
		else:
			self.r = signal

		try:
			State.params[self.colorKnobName] = np.mod(State.params[self.colorKnobName] + np.count_nonzero(self.r), 2)
		except KeyError:
			State.params[self.colorKnobName] = 0
			pass
