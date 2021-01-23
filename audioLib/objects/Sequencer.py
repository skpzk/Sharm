from audioLib.objects.Patchbay import PatchPoint
from audioLib.objects.Vco import stateKeys
from audioLib.utils.Utils import *
from state.State import State


class CVInputs:
	seq = PatchPoint()


class Sequencer:
	def __init__(self):
		self.rhythms = []
		self.lastStepCalled = 0
		self.r0 = 0
		self.stateKeys = stateKeys()
		self.steps = [0.] * 4
		self.cvSteps = [0.] * 4
		self.clks = [False] * 4
		self.r = np.expand_dims(np.zeros(AudioConst.CHUNK), axis=1)
		self.sequence = np.expand_dims(np.zeros(AudioConst.CHUNK), axis=1)
		self.clock = np.expand_dims(np.zeros(AudioConst.CHUNK), axis=1)
		self.cvClock = np.expand_dims(np.zeros(AudioConst.CHUNK), axis=1)
		self.cvClockLastValue = 0

		self.reset = False
		self.next = False

		self._stateCallbackName = ""

		self.inputs = CVInputs()
		self.cvBuffer = emptyChunk()

		State.params.setCallback('next', self.nextCallback)
		State.params.setCallback('reset', self.resetCallback)

	def setStateCallbackName(self, name):
		self._stateCallbackName = name

	def nextCallback(self):
		self.next = True

	def resetCallback(self):
		if State.params['reset'] == 1:
			self.reset = True

	def checkValues(self):
		keys = [self.stateKeys.step1, self.stateKeys.step2, self.stateKeys.step3, self.stateKeys.step4]
		for i in range(4):
			try:
				self.steps[i] = float(np.clip(State.params[keys[i]], -1, 1))
			except KeyError:
				pass
		keys = [self.stateKeys.clk1, self.stateKeys.clk2, self.stateKeys.clk3, self.stateKeys.clk4]
		for i in range(len(keys)):
			try:
				self.clks[i] = bool(np.clip(State.params[keys[i]], 0, 1))
			except KeyError:
				pass
		try:
			if not self.reset:
				self.reset = bool(np.clip(State.params["reset"], 0, 1))
		except KeyError:
			pass

	def output(self, out):
		out[:] = self.sequence

	def CVClockOutput(self, out):
		out[:] += self.cvClock

	def clockOrOutput(self, out):
		self.clock *= 1
		out[:] |= self.clock

	def tick(self):
		"""
			method called by Clock class (ie the main clock)
		"""

		# check ctrl panel values
		self.checkValues()

		r = self.r
		r = r == 1
		# get rhythms signals and | them
		# print("len rhythms", len(self.rhythms))
		for i in range(len(self.rhythms)):
			if self.clks[i]:
				self.rhythms[i].orOutput(r)

		if self.next:
			r[0] = 1
			self.next = False

		self.clock = np.copy(r*1)

		self.cvClock = np.mod(np.cumsum(self.clock, axis=0) + self.cvClockLastValue, 2)
		self.cvClockLastValue = self.cvClock[-1, 0]

		# sum and mod
		r = np.mod(np.cumsum(np.append(np.ones((1, 1)) * self.r0, r, axis=0), axis=0), 4)
		self.r0 = r[-1]
		if self.reset:
			# when reset is held, the seq is on step 0
			r.fill(0)
			# self.r0 = -1
			self.reset = False

		# warn state
		_, idx = np.unique(r, return_index=True)
		idx = list(np.sort(idx))
		# stepsnumber = list(r[np.sort(idx)]+1)
		stepsnumber = list(r[idx]+1)
		try:
			idx.pop(stepsnumber.index(self.lastStepCalled))
			stepsnumber.remove(self.lastStepCalled)
		except ValueError:
			pass

		for step in stepsnumber:
			State.params[self._stateCallbackName] = step
			self.lastStepCalled = step


		# check CV inputs :
		# if cv input is connected, check value at step change and add value to step
		if self.inputs.seq.isConnected():
			self.cvBuffer.fill(0)
			self.inputs.seq(self.cvBuffer)
			for i in range(len(idx)):
				index = idx[i]
				if index != 256:
					stepsn = int(stepsnumber[i] - 1)
					self.cvSteps[stepsn] = self.cvBuffer[index, 0]
		else:
			self.cvSteps = [0] * 4


		# compute value
		self.sequence.fill(0)
		for i in range(4):
			self.sequence += np.clip(self.steps[i] + self.cvSteps[i], -1, 1) * (r[:-1] == i)
