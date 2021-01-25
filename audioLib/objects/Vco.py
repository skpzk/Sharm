from time import time

from audioLib.AudioConst import AudioConst
from audioLib.objects.AudioObject import AudioObject
from audioLib.objects.Patchbay import PatchPoint
from audioLib.utils.Utils import *
from state.State import State


TABLELENGTH = 500000
firstHalfTable = int(np.floor(TABLELENGTH / 2))
secondHalfTable = TABLELENGTH - firstHalfTable

sineTable = np.expand_dims(np.array(np.sin(np.linspace(0, 1, TABLELENGTH) * 2 * np.pi)), 1)
sqrTable = np.expand_dims(np.array(((np.linspace(0, 1, TABLELENGTH) <= .5) - .5) * 2), 1)
sawTable = np.expand_dims(np.array(np.linspace(-1, 1, TABLELENGTH)), 1)
# sawTable = np.expand_dims(np.array(np.append(np.linspace(-1, 1, int(TABLELENGTH*9/10)), np.linspace(1, -1, int(TABLELENGTH*1/10)))), 1)
triTable = np.expand_dims(np.append(np.linspace(-1, 1, firstHalfTable), np.linspace(1, -1, secondHalfTable)), 1)

"""
The polyblep implementation comes from :
http://www.martin-finke.de/blog/articles/audio-plugins-018-polyblep-oscillator/
"""


class stateKeys:
	freq = ""
	quant = "quantradio"
	wave = ""
	vcoVolume = ""
	range = "rangeradio"
	assignvco = ""
	assignsub = ""
	step1 = ""
	step2 = ""
	step3 = ""
	step4 = ""
	clk1 = ""
	clk2 = ""
	clk3 = ""
	clk4 = ""
	a = 0
	d = 0
	div = 0
	sub1level = 0

class CVInputs:
	vco = PatchPoint()
	pwm = PatchPoint()
	sub = PatchPoint()
	btwpwm = AudioObject(defaultValue=.75)

class Osc(AudioObject):
	def __init__(self, cvinputs, cvoutputs):
		super(Osc, self).__init__(cvinputs, cvoutputs)
		self.volume = 1
		self.wave = 'sine'
		self.phase: np.array = np.zeros(257)
		self.freq: np.array = emptyChunk()
		self.phaseIncrement : np.array = np.zeros((256, 1))
		self.vco_or_sub = ""

		self.lastValue_for_polyBlep_Tri = 0

	def updatePhaseIncrement(self):
		# self.phaseIncrement = self.freq * float(TABLELENGTH) / float(AudioConst.RATE)
		self.phaseIncrement = np.clip(self.freq, 0, AudioConst.RATE/2) * TABLELENGTH / AudioConst.RATE
		# self.phaseIncrement = np.array(self.phaseIncrement).astype('int')

	def updatePhase(self):
		# self.phase has a length of Chunk+1 to compute the first phase value of the next chunk
		# when outputWave is executed, the last value of self.phase is ignored
		self.phase = np.mod(self.phase[-1] + np.cumsum(np.append(0, self.phaseIncrement)), TABLELENGTH)

	def CVOutput(self, out: np.ndarray) -> None:
		self.outputWave(out, True)

	def outputWave(self, out, cv=False):
		if cv:
			vol = 1
		else:
			vol = self.volume * 1/6

		try:
			if self.wave == "sine":
				out[:] += sineTable[self.phase[:-1].astype('int')] * vol
			elif self.wave == "sqr":
				if self.vco_or_sub != "":
					# ie if the signal is generated for audio output
					# not for a clock
					# apply poly blep
					out[:] += self.applyPolyBlepSqr(sqrTable[self.phase[:-1].astype('int')]) * vol
				else:
					out[:] += sqrTable[self.phase[:-1].astype('int')] * vol
			elif self.wave == "tri":
					out[:] += triTable[self.phase[:-1].astype('int')] * vol
			elif self.wave == "saw":
				if self.vco_or_sub != "":
					# ie if the signal is generated for audio output
					# not for a clock
					# apply poly blep
					out[:] += self.applyPolyBlepSaw(sawTable[self.phase[:-1].astype('int')]) * vol
				else:
					out[:] += sawTable[self.phase[:-1].astype('int')] * vol
			elif self.wave == "btw":
				if self.vco_or_sub == "sub":
					# print("pwm sub btw")
					out[:] += self.applyPolyBlepSaw(sawTable[self.phase[:-1].astype('int')]) * vol
				elif self.vco_or_sub == "vco":
					out[:] += self.applyPolyBlepSqr(sqrTable[self.phase[:-1].astype('int')]) * vol
				# out.fill(0)
				# pass
			else:
				out[:] += sineTable[self.phase[:-1].astype('int')] * vol
		except ValueError as ve:
			print(ve)
			print("shape out : ", out.shape)
			if self.vco_or_sub != "":
				print("shape of the rest : ", (self.applyPolyBlepSqr(sqrTable[self.phase[:-1].astype('int')]) * vol).shape)
			else:
				print("shape of the rest : ", (sineTable[self.phase[:-1].astype('int')] * vol).shape)

	def applyPolyBlepSqr(self, wave):
		return wave \
		       + self.polyBlepNumpy(np.mod(self.phase[:-1].copy()/TABLELENGTH, 1)) \
		       - self.polyBlepNumpy(np.mod(self.phase[:-1].copy()/TABLELENGTH + .5, 1))

	def applyPolyBlepSaw(self, wave):
		return wave \
		       - self.polyBlepNumpy(np.mod(self.phase[:-1].copy() / TABLELENGTH, 1))

	def polyBlepNumpy(self, t):
		# phaseIncrement = freq * 2 * np.pi / AudioConst.RATE
		dt = self.phaseIncrement[:, 0] / TABLELENGTH

		maskt1 = (t < dt)
		t1 = t / dt
		t1 = maskt1 * (t1 + t1 - t1 * t1 - 1.0)
		maskt2 = (t > (1. - dt))
		t2 = (t - 1.0) / dt
		return np.expand_dims(t1 + maskt2 * (t2 * t2 + t2 + t2 + 1.0), axis=1)

class Vco(Osc):
	"""
	Patchbay IO:
		Inputs : freq, pwm, sub division
		output : sound output from Vco + subs
	Ctrl IO:
		Inputs :
			- wave Slider : set wave
			- knob vco: freq (262Hz -> 4186Hz)
			- knob sub: div (1->16)
			- seq
			- range
			- quantize

	seq value -> range -> add to knob freq and freq CV -> quantize

	"""
	def __init__(self):
		super(Vco, self).__init__(3, 3)
		self.vco_or_sub = "vco"
		self.quantizeValue = 0

		self.freq = 440 * np.ones(AudioConst.CHUNK)
		self.pwm = np.expand_dims(np.ones(AudioConst.CHUNK) * 1, axis=1)
		self.knobfreq = 440
		self.phaseIncrement = self.freq * TABLELENGTH / AudioConst.RATE

		self.range = 1

		self.inputs = CVInputs()

		self.stateKeys = stateKeys()

		self.seq = None
		self.sequence = emptyChunk()
		self.seqassign = False

		self.T = []


		# print("phase Increment", self.phaseIncrement.shape)



	def computeFreq(self):
		# get value from knob
		# add value from seq + range
		# add value from CV
		# quantize
		self.freq = 0

	def quantize(self):
		# freq = np.expand_dims(self.freq, axis=1)
		# freq = self.freq
		if self.quantizeValue == "12-ET":
			self.freq = mtof(ftom(self.freq).astype('int'))
		elif self.quantizeValue == "8-ET":
			self.freq = mtofDiat(ftomDiat(self.freq))
		elif self.quantizeValue == "12-JI":
			self.freq = quant12JI(self.freq)
		elif self.quantizeValue == "8-JI":
			self.freq = quant8JI(self.freq)
		else:
			self.freq = mtof(int(ftom(self.freq)))



	def updateFreq(self):
		self.freq = np.expand_dims(np.ones(AudioConst.CHUNK), axis=1) * self.knobfreq

		buf = np.expand_dims(np.zeros(AudioConst.CHUNK), 1)

		if self.seq is not None:
			# print("getting sequence")
			self.seq.output(buf)
		self.sequence = buf.copy()

		if self.seqassign:
			self.freq = mtof(ftom(self.freq) + buf * self.range * 12)

		buf.fill(0)

		self.inputs.vco(buf)

		self.freq = mtof(ftom(self.freq) + buf * self.range * 12)

		self.freq = quantize2D(self.freq, self.quantizeValue)


	def checkValues(self):
		try:
			knobFreqValue = np.clip(State.params[self.stateKeys.freq], 0, 1)
			self.knobfreq = mtof(60 + (108 - 60) * knobFreqValue)
		except KeyError:
			pass
		try:
			quantValue = State.params[self.stateKeys.quant]
			if quantValue in ['12-ET', '8-ET', '12-JI', '8-JI']:
				self.quantizeValue = ['12-ET', '8-ET', '12-JI', '8-JI'].index(quantValue)
		except KeyError:
			pass
		try:
			rangeValue = State.params[self.stateKeys.range]
			if int(rangeValue[1]) in [1, 2, 5]:
				self.range = int(rangeValue[1])
		except KeyError:
			pass
		except TypeError:
			pass
		try:
			waveType = int((1 - State.params[self.stateKeys.wave]) * 4)
			waves = ["sine", "tri", "saw", "btw", "sqr"]
			self.wave = waves[waveType]
		except KeyError:
			pass
		try:
			self.volume = np.clip(State.params[self.stateKeys.vcoVolume], 0, 1)
		except KeyError:
			pass
		try:
			assign = State.params[self.stateKeys.assignvco] == 1
			self.seqassign = assign
		except KeyError:
			pass



	def output(self, out: np.ndarray) -> None:
		self.checkValues()

		self.updateFreq()

		self.updatePhaseIncrement()

		self.updatePhase()

		self.pwm.fill(0)
		if self.wave in ["sqr", "btw"]:
			if self.inputs.pwm.isConnected():

				self.inputs.pwm(self.pwm)
				self.pwm = np.clip(self.pwm, -1, 1) / 4 + .75
				self.phase[:-1] = self.phase[:-1] * self.pwm[:, 0]
			elif self.wave == "btw":

				self.inputs.btwpwm.CVOutput(self.pwm)
				self.pwm = np.clip(self.pwm, -1, 1) / 4 + .75
				self.phase[:-1] = self.phase[:-1] * self.pwm[:, 0]

		self.outputWave(out)

		
class Sub1(Osc):
	def __init__(self):
		super(Sub1, self).__init__(0, 0)
		self.vco_or_sub = "sub"
		self.stateKeys = stateKeys()
		self.div = np.expand_dims(np.ones(AudioConst.CHUNK), axis=1)
		self.divKnobValue = 1
		self.vco = None
		self.seqassign = False

	def checkValues(self):
		try:
			divKnobValue = State.params[self.stateKeys.div] * 16
			self.divKnobValue = np.clip(divKnobValue, 1, 16)
		except KeyError:
			pass
		try:
			level = State.params[self.stateKeys.sub1level]
			self.volume = np.clip(level, 0, 1)
		except KeyError:
			pass
		try:
			assign = State.params[self.stateKeys.assignsub] == 1
			self.seqassign = assign
		except KeyError:
			pass

	def computeDiv(self):
		self.div = np.expand_dims(np.ones(AudioConst.CHUNK), axis=1) * self.divKnobValue
		buf = np.expand_dims(np.zeros(AudioConst.CHUNK), 1)

		self.vco.inputs.sub(buf)
		self.div = np.clip(self.div + np.clip(buf, -1, 1) * 8, 1, 16).astype('int')
		if self.seqassign:
			self.div = np.clip(self.div + np.clip(self.vco.sequence, -1, 1) * -8, 1, 16).astype('int')

	def output(self, out: np.ndarray) -> None:
		# check Vco values :
		self.wave = self.vco.wave
		# check control panel values
		self.checkValues()

		# get CV input:
		self.computeDiv()
		# compute freq)
		self.freq = self.vco.freq * 1. / self.div

		#compute phase
		self.updatePhaseIncrement()
		self.updatePhase()

		self.outputWave(out)
		# out[:] *= 1 / 6
