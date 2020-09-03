import numpy as np
from AudioLib import Audio, Env, Osc
from AudioLib.Utils import *


class Note:
	def __init__(self, audioConst, adsr=None, wave='tri', vol=127):
		if adsr is None:
			adsr = [0, 0, 1, 0]
		nb_osc = 1
		self.oscs = []
		self.order = -1
		self.note = -1
		self.noteId = -1
		self.isActive = False
		self.audio = audioConst
		self.CHUNK = self.audio.CHUNK
		self.callsList = []
		self.env = Env.Env(audioConst, adsr)
		self.vol = 0
		self.setVol(vol)
		self.wave = wave

		for i in range(nb_osc):
			self.oscs.append(Osc.Osc(audioConst))

		for osc in self.oscs:
			osc.setVolume(1)
			osc.setNote(69)
			osc.setWave(self.wave)
			self.callsList.append(osc)

	def on(self, note):
		for osc in self.oscs:
			osc.setNote(note)
			osc.setVolume(1)
		self.isActive = True
		self.env.on()
		self.note = note

	def off(self):
		self.isActive = False
		self.env.off()

	def setVol(self, vol):
		self.vol = float(vol)/127

	def setWave(self, wave):
		self.wave = wave
		for osc in self.oscs:
			osc.setWave(self.wave)

	def __call__(self):
		data = np.zeros(self.CHUNK)
		for call in self.callsList:
			data += call()  # call oscs
		data = np.multiply(data, self.vol)
		# cprint('Vol = ', self.vol)
		data = np.multiply(data, self.env())
		# cprint('Env = ', self.env())
		return Audio.ssat(data)
