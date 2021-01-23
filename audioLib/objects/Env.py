from audioLib.objects.Patchbay import PatchPoint
from audioLib.objects.Vco import stateKeys
from audioLib.utils.Utils import *
from state.State import State


class attack_state:
	offset = 0
	cont = 0
	lastValue = 0

class CVInputs:
	trig = PatchPoint()


"""
everything seems to be working, there is some cleaning and testing left:

- correct_trigger -> test if a convolution is faster
+ get rid of class decay_state
+ we only need to store the last value of maks, not the whole previous mask
+ don't return values, use internal params
- add comments detailing the equation used for attack computing (and a thanks to Luke)
- can this run faster ?

"""


class Env:
	def __init__(self):
		self.stateKeys = stateKeys()
		self.CHUNK = AudioConst.CHUNK
		self.RATE = AudioConst.RATE

		self.attack_time = 0
		self.decay_time = 0

		self.seqs = []

		self.previousmaskLastValue = 0
		self.mask = np.zeros(AudioConst.CHUNK)

		self.trig = emptyIntChunk()
		self.trigger = False

		self.attackState = attack_state()

		self.lastValue = 0

		self.env = np.zeros(AudioConst.CHUNK)

		self.hold = False
		self.dont_trigger = False

		self.inputs = CVInputs()
		# self.t gets input from trigger patchpoint
		self.t = emptyChunk()


		State.params.setCallback('trigger', self.setTrigger)

	def computeTimeFromKnob(self, k, a_or_d: str):
		if a_or_d == 'a':
			# a ranges from 1ms to 10s
			t0 = .001
		else:
			# d ranges from 5ms to 10s
			t0 = .005
		t1 = 10
		# inversion of indices is intentional, it ensures that X0 < X1 (where X = t or f)
		f1 = 1 / t0
		f0 = 1 / t1
		# 1/t has logarithmic variation with linear variation of knob value
		if a_or_d == 'a':
			self.attack_time = 1 / mtof(ftom(f0) + (1 - k) * (ftom(f1) - ftom(f0)))
		else:
			self.decay_time = 1 / mtof(ftom(f0) + (1 - k) * (ftom(f1) - ftom(f0)))

	def correct_trigger(self, trig):

		# this whole function could maybe be sinmpler with the use of the magic cum_reset_np function
		# but I'm too tired right now to change it

		attack_samples = (self.attack_time * self.RATE)

		# get indexes of triggers
		idx = np.nonzero(trig)
		idx = list(idx[0])
		try:
			ref = idx[0] - self.attackState.offset
		except IndexError:
			ref = -1 * self.attackState.offset

		# rem = []
		# if the previous chunk has an unfinished attack, don't ignore the first trigger of this chunk
		# ie start at idx[0]
		# else, start at idx[1]
		start_index = (self.attackState.offset == 0) * 1

		for i in idx[start_index:]:
			# if the trigger happens during an attack phase, remove it
			if (i - ref) < attack_samples:
				idx.remove(i)
			else:
				ref = i

		# idx = [i for i in idx if i not in rem]

		# trig corrected = 1 when in attack phase
		trig_corrected = np.zeros(self.CHUNK)

		# if the previous chunk has an unfinished attack, continue it here
		trig_corrected[0:int(np.clip(self.attackState.cont, 0, self.CHUNK))] = 1
		for i in idx:
			trig_corrected[i:int(np.clip((i + attack_samples), 0, self.CHUNK))] = 1

		# the previous operation could be done with a convolution, not sure which is faster

		try:
			# if there is one trigger left, use it to compute attack time for next chunk
			base = idx[-1]
		except IndexError:
			# else, use values from previous chunk
			base = - self.attackState.offset

		tmp = base + attack_samples
		# do it only if this chunk ends during an attack phase:
		if trig_corrected[-1] == 1:
			self.attackState.offset = (self.CHUNK - base) * (tmp > self.CHUNK)
			self.attackState.cont = (tmp - self.CHUNK) * (tmp > self.CHUNK)
		else:
			self.attackState.offset = 0
			self.attackState.cont = 0
		# print("attack offset = ", self.attack_offset)

		self.mask = trig_corrected

	def computeANumpy(self, mask, a0):
		attack_samples = self.attack_time * self.RATE
		target = .01
		max_amplitude = 1
		rate = (1.0 / attack_samples) * np.log(target / (max_amplitude + target))

		# a[n] = A^n*(n[0] - r) + r

		# change this line to account for the fact that the starting value of A is the last value of D
		M0 = np.zeros(self.CHUNK) - max_amplitude - target
		M0 = a0 - max_amplitude - target

		M1 = np.ones(self.CHUNK) * np.exp(rate)
		M2 = cum_reset_np(np.ones(self.CHUNK) * mask)
		M0 = M0 * np.power(M1, M2) + (max_amplitude + target)
		self.attackState.lastValue = M0[-1]
		return M0

	def computeDNumpy(self, mask, d0):
		decay_samples = self.decay_time * self.RATE
		target = -.01
		max_amplitude = -1
		rate = (1.0 / decay_samples) * np.log(target / (max_amplitude + target))

		# a[n] = A^n*(n[0] - r) + r

		M0 = d0
		M1 = np.ones(self.CHUNK) * np.exp(rate)
		M2 = cum_reset_np(np.ones(self.CHUNK) * mask)
		M0 = M0 * np.power(M1, M2)
		return M0

	def computea0(self, dec):
		self.a0 = np.zeros(self.CHUNK)

		# if this chunk begins with an attack phase:
		if self.mask[0] == 1:
			# if the last chunk ended during an attack, use its value as a0
			# for the first attack phase of this chunk

			# if the last chunk ended during a decay, use the last value of decay
			# for the first attack phase of this chunk

			val = self.lastValue

			# get index of the end of the first attack phase
			idx = np.flatnonzero(1 - self.mask)
			try:
				end = idx[0]
			except IndexError:
				# if the decay phase lasts for the entire chunk
				end = self.CHUNK
			self.a0[:end] = val

		# if this chunk has decays, use their last value for each attack

		# get decays last value:
		dec_last_values = dec * np.append(self.mask[1:], 0)

		dec_last_values = np.append(0, dec_last_values[:-1])

		# maks a0 with convolution:
		# without the following line, the convolution takes too much time
		conv_length = np.clip(int(self.attack_time * self.RATE), 0, self.CHUNK)
		self.a0 += np.resize(np.convolve(dec_last_values, np.ones(conv_length)), self.CHUNK)

		pass

	def computed0(self):

		# d0 is essentially the same as 1 - mask

		self.d0 = 1 - self.mask

		# if the decay comes after an attack, use 1 as first value
		# so there is nothing more to do

		# if the decay is the continuation of a previous decay, use its value as base
		if self.previousmaskLastValue == 0 and self.mask[0] == 0:
			# last chunk ended in a decay phase
			# get last value :
			val = self.lastValue
			# get the index of the end of the first decay phase of this chunk:
			idx = np.flatnonzero(self.mask)
			try:
				end = idx[0]
			except IndexError:
				# if the decay phase lasts for the entire chunk
				end = self.CHUNK
			self.d0[:end] = val

	def setTrigger(self):
		# print("setTrigger called")
		if State.params['eg'] == 1:
			self.trigger = True
		elif State.params['eg'] == 1:
			self.hold = True

	def checkValues(self):
		try:
			knobAValue = np.clip(State.params[self.stateKeys.a], 0, 1)
			self.computeTimeFromKnob(knobAValue, 'a')
		except KeyError:
			pass
		try:
			knobDValue = np.clip(State.params[self.stateKeys.d], 0, 1)
			self.computeTimeFromKnob(knobDValue, 'd')
		except KeyError:
			pass
		try:
			egValue = State.params["eg"]
			if egValue == .5:
				self.hold = True
			else:
				self.hold = False
			if egValue == 0:
				self.dont_trigger = True
			else:
				self.dont_trigger = False
		except KeyError:
			pass

	def detectRisingEdge(self, signal):
		trigger_val = 0
		signal = np.append(np.zeros((1,1)), signal, axis=0)

		t1 = signal[:-1] > trigger_val
		t2 = signal[1:] > trigger_val
		trig = t1 ^ t2
		trig = trig & (signal[1:] > trigger_val)
		return trig

	def output(self, out):

		self.checkValues()

		self.trig.fill(0)
		for seq in self.seqs:
			seq.clockOrOutput(self.trig)

		if self.dont_trigger:  # ie if EG button is unlit
			self.trig.fill(0)

		if self.trigger:
			# print("trigger")
			self.trigger = False
			self.trig[0] = 1
		# t2 = time() - t2

		### ADD HERE CV INPUT FOR TRIGGER
		self.t.fill(0)
		self.inputs.trig(self.t)

		self.trig = np.add(self.trig, self.detectRisingEdge(self.t).astype(int))

		self.correct_trigger(self.trig)

		# attack maximum values is always reached, so the starting value of D is always 1,
		# but the starting value of A is the last value of D
		# so it is best to compute D first
		# and then use the last value of D as a starting point for A

		self.computed0()
		self.env = self.computeDNumpy(1 - self.mask, self.d0) * (1 - self.mask)

		# this takes too much time when a_knob > .6
		# solved by adding this line : conv_length = np.clip(int(self.attack_time * self.RATE), 0, self.CHUNK)
		self.computea0(self.env)

		self.env += self.computeANumpy(self.mask, self.a0)

		if self.hold :
			self.env.fill(1)

		self.previousmaskLastValue = self.mask[-1]
		self.lastValue = self.env[-1]

		out[:] = np.expand_dims(np.clip(self.env, 0, 1), axis=1)
