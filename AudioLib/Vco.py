import numpy as np
import inspect

from AudioLib.Utils import *
from Dev.DebugUtils import *
from AudioLib.Audio import AudioConstTest as AudioConst
from AudioLib.ModSources import ModSources


"""
Vco and sub inherit from Osc
VCO :
	when sequencer is inactive, it gets its frequency from the main knob + modsources
										active,   it gets its frequency from the main knob + modsources + sequencer note modification
	notes are computed by the getNotesMod method, which is redefined in vco subclass
"""


class Osc(AudioConst):
	def __init__(self):
		self._f = 440
		self.phi = 0
		self.wave = 'sine'
		self.osc = self.oscSine
		self._divFromRotary = 1
		self._divFromSeq = 1

		self._noteFromSeq = 69
		self._noteFromRotary = 0

		self.modSources = ModSources([('pwm', 0)])

		self.volume = 1
		self.out = []
		self.notes = ftom(np.ones(self.CHUNK) * self._f)

		self.sequencerActive = False

		self.t = np.multiply(np.arange(self.CHUNK), 1. / float(self.RATE))

	def oscSine(self, _, w, __=0):
		# cprint("osc sine called")
		# cprint(w)
		# cprint(self.phi)
		s = np.sin(np.multiply(self.t, w) + self.phi)
		return s

	def oscSaw(self, _, w, shape=1.):
		s = saw(np.multiply(self.t, w) + self.phi, shape)
		return s

	def oscSqr(self, _, w, shape=.5):
		pwm = self.modSources.pwm() / 2
		# trim values outside [0, 1]
		shape = trim(pwm + shape, [0, 1])
		s = sqr(np.multiply(self.t, w) + self.phi, shape)
		return s

	def oscTri(self, phase, w, shape=.5):
		s = self.oscSaw(phase, w, shape)
		return s

	def setVolume(self, vol):
		self.volume = vol / 127.

	@property
	def div(self):
		if self.sequencerActive:
			return self._divFromSeq
		else:
			return self._divFromRotary

	@property
	def _notes(self):
		if self.sequencerActive:
			return self._noteFromRotary + self._noteFromSeq
		else:
			return self._noteFromRotary

	def setDiv(self, div, fromSequencer=False):
		if fromSequencer:
			self._divFromSeq = div
		else:
			self._divFromRotary = div

	def setNote(self, note, fromSequencer=False):
		if fromSequencer:
			self._noteFromSeq = note
		else:
			self._noteFromRotary = note

	def setWave(self, wave):
		self.wave = wave
		if wave == 'sine':
			# cprint("Applied sine wave")
			self.osc = self.oscSine
		elif wave == 'saw':
			self.osc = self.oscSaw
		elif wave == 'tri':
			self.osc = self.oscTri
		elif wave == 'sqr':
			self.osc = self.oscSqr

	def __call__(self):
		self.out = self.output()
		# cprint(self.out)
		return self.out

	# used when the osc is a modification source
	def call(self):
		if len(self.out) == 0:
			# if the osc has not produced data yet, the output is computed
			# but without calling the modification sources to prevent infinite iterations
			# and without updating the phase of the osc
			# This precaution is an inheritance from the old audio design
			# and should hopefully not be necessary anymore,
			# hence the print output, to monitor it
			cprint("len(self.out) = 0 !")
			self.out = self.output(False, True)
			cprint("called as a mod source")
		return self.out

	def output(self, updatePhi=True, bypassCall=False):

		self.notes = self.getNotesMod(bypassCall)

		freqs = mtof(self.notes)

		w = 2. * np.pi * freqs

		data = self.osc(0, w)
		if updatePhi:
			self.phi = np.mod(np.multiply((self.t[-1] + self.t[1]), w[-1]) + self.phi, 2. * np.pi)
		return data * self.volume

	def getNotesMod(self, bypassCall):
		return [0]


class Vco(Osc):
	def __init__(self):
		super().__init__()
		self.modSources.freq = 0

	@property
	def f(self):
		return self._f / self.div

	# def setNote(self, note):
	# 	# cprint("note set :", note)
	# 	self._f = mtof(note)

	def getNotesMod(self, bypassCall):
		notes = np.zeros(self.CHUNK)
		if not bypassCall:
			# the output of f should be btw 1 and -1
			# it changes the frequency by +/- 5 oct
			# cprint("Modsources freq from osc = ", self.modSources)
			notes = self.modSources.freq()
			# cprint("notes : ", notes)
			notes = notes * 12 * 5
		notes = notes + self._notes
		# cprint("Vco notes = ", notes)
		return notes


class Sub(Osc):
	"""
	Sub oscillator, always linked to a parent Vco
	the sub osc should always be called after its Vco, as it uses
	the parent Vco's notes to compute its output
	"""
	def __init__(self, vco: Vco):
		super().__init__()
		self.parentVco = vco
		self.modSources.div = 0

	def getNotesMod(self, bypassCall):
		div = 0
		if not bypassCall:
			# the output of n should be btw 1 and -1
			# it changes the divider of the sub osc by +/- 8
			div = self.modSources.div()
			div = np.array(div * 8, dtype=np.int)
		div = trim(self.div + div, [1, 16])
		# cprint(div)
		# not sure if the sub shoud get the actual frequencies of the parent vco
		# or just its base frequency
		actual = False
		if actual:
			notesVco = self.parentVco.notes
			cprint("notes Vco = ", notesVco)
			freqsVco = mtof(notesVco)
		else:
			# this seems better
			freqsVco = self.parentVco.f
		freqs = np.divide(freqsVco, div)
		notes = ftom(freqs)
		return notes
