import numpy as np
from AudioLib.Audio import AudioConstTest as AudioConst
from Dev.DebugUtils import *
from AudioLib.ModSources import ModSources

"""Add anti-pop filter"""


class Vca(AudioConst):
	"""
	this audio module gets audio data from self.soundSources
	and applies to them an enveloppe if it has one
	"""
	def __init__(self):
		super().__init__()
		self.soundSources = []
		self.envSource = ModSources([('env', 1)])
		self.env = np.ones(self.CHUNK)
		self.vol = 1

	def __call__(self):
		data = np.zeros(self.CHUNK)
		for s in self.soundSources:
			data += s()  # call oscs
		env = np.ones(self.CHUNK)
		env = self.envSource.env()
		self.env = env
		data = np.multiply(data, env)
		data = np.multiply(data, self.vol)
		# cprint(env)
		# cprint("Max(data) = ", np.max(data))
		# cprint("len(data) = ", len(data))
		return data

	def setVol(self, vol):
		self.vol = vol / 127.
