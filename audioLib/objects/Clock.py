from audioLib.objects.Patchbay import PatchPoint
from audioLib.objects.Vco import Osc, sqrTable, sawTable, sineTable, stateKeys
from state.State import State

from audioLib.utils.Utils import *

"""
Clock is a simple square wave generator, 
a rising edge is the tic.
the clock ranges from 1/3 Hz to 50 Hz (with a log scale ?)
"""


class CVInputs:
	clk = PatchPoint()

class Clock(Osc):
	def __init__(self):
		super(Clock, self).__init__(0, 0)
		self.signal = np.expand_dims(np.zeros(AudioConst.CHUNK), 1)
		self.risingEdgeSignal = np.expand_dims(np.zeros(AudioConst.CHUNK), 1)
		self.freq = np.expand_dims(np.ones(AudioConst.CHUNK), 1)
		self.wave = 'sqr'
		self._sig_last_value = 0

		self.knobfreq = 0

		self.inputs = CVInputs()

		self.stateKeys = stateKeys()
		self.play = True
		# self.trigger = False

		self.rhythms = []
		self.seqs = []

		# State.params.setCallback('trigger', self.setTrigger)

	def detectRisingEdge(self):
		trigger_val = 0
		signal = np.append(np.ones((1,1)) * self._sig_last_value, self.signal, axis=0)
		t1 = signal[:-1] > trigger_val
		t2 = signal[1:] > trigger_val
		trig = t1 ^ t2
		trig = trig & (signal[1:] > trigger_val)
		self.risingEdgeSignal = trig
		# print(self.signal)
		# self._sig_last_value = self.signal[-1]
		self._sig_last_value = self.signal[-1, 0]


	def checkValues(self):
		try:
			knobFreqValue = np.clip(State.params[self.stateKeys.freq], 0, 1)
			self.knobfreq = mtof(ftom(1/3) + (ftom(50) - ftom(1/3)) * knobFreqValue)
		except KeyError:
			pass
		try:
			self.play = (np.clip(State.params['play'], 0, 1) == 1)
		except KeyError:
			pass

	def updateFreq(self):
		self.freq.fill(self.knobfreq)

	def CVOutput(self, out: np.ndarray) -> None:
		if self.play:
			if self.inputs.clk.isConnected():
				self.inputs.clk(out)
			else:
				self.outputWave(out, True)
		else:
			out.fill(0)

	def tick(self):
		"""
		this method is called once per cycle by the main audio class
		it gives the base tempo
		"""
		# check ctrl panel inputs
		self.checkValues()

		self.updateFreq()

		# check cv inputs

		self.updatePhaseIncrement()
		self.updatePhase()
		self.signal.fill(0)
		self.CVOutput(self.signal)



		# if self.trigger:
		# 	self.trigger = False
		# 	self.signal[0] = 1
		self.detectRisingEdge()
		# for _ in range(np.count_nonzero(self.risingEdgeSignal)):
		# 	print("tick")
		try:
			State.params["activetempo"] = np.mod(State.params["activetempo"] + np.count_nonzero(self.risingEdgeSignal), 2)
			# print("activetempo = ", State.params["activetempo"])
			# print("non zero = ", np.count_nonzero(self.risingEdgeSignal))
		except KeyError:
			State.params["activetempo"] = 0

		for r in self.rhythms:
			r.tick()

		for seq in self.seqs:
			seq.tick()
