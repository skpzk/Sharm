import numpy as np
from AudioLib.Utils import *


class Osc:
	def __init__(self, audioConst, freq=440, wave='tri'):
		self.f = freq
		self.phi = 0
		self.audio = audioConst
		self.maxvol = 0.5
		self.wave = wave
		self.osc = self.oscTri

		self.t = np.multiply(np.arange(self.audio.CHUNK), 1. / float(self.audio.RATE))

		self.volume = 1

	def output(self, phase=0):  # trying a new branchless way  #seems to take the same time
		w = 2. * np.pi * self.f
		data = self.osc(phase, w)
		self.phi = np.mod((self.t[-1] + self.t[1]) * w + self.phi, 2. * np.pi)
		return data / 16.

	def oscSine(self, _, w, __=0):
		s = np.multiply(np.sin(np.multiply(self.t, w) + self.phi), self.maxvol * self.volume)
		return s

	def oscSaw(self, _, w, shape=1.):
		s = np.multiply(saw(np.multiply(self.t, w) + self.phi, shape), self.maxvol * self.volume)
		return s

	def oscSqr(self, _, w, shape=.5):
		s = np.multiply(sqr(np.multiply(self.t, w) + self.phi, shape), self.maxvol * self.volume)
		return s

	def oscTri(self, phase, w, shape=.5):
		s = self.oscSaw(phase, w, shape)
		return s

	def setNote(self, note):
		self.f = mtof(note)

	def setVolume(self, vol):
		self.volume = vol

	def setWave(self, wave):
		self.wave = wave
		if wave == 'sine':
			self.osc = self.oscSine
		elif wave == 'saw':
			self.osc = self.oscSaw
		elif wave == 'tri':
			self.osc = self.oscTri
		elif wave == 'sqr':
			self.osc = self.oscSqr

	def __call__(self):
		# print("Osc called")
		return self.output()
