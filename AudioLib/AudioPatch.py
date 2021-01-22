from Dev.DebugUtils import *
from AudioLib.Audio import AudioConstTest as AudioConst
from AudioLib import Vco, Vca, Env, Filter


class AudioPatch(AudioConst):
	def __init__(self):
		super().__init__()
		self.vco1 = Vco.Vco()
		self.sub1vco1 = Vco.Sub(self.vco1)
		self.sub2vco1 = Vco.Sub(self.vco1)

		self.vco2 = Vco.Vco()
		self.sub1vco2 = Vco.Sub(self.vco2)
		self.sub2vco2 = Vco.Sub(self.vco2)

		self.envVco1 = Env.Env([0, 0, 0, 0])
		self.envVco2 = Env.Env([0, 0, 0, 0])

		self.vcaVco1 = Vca.Vca()
		self.vcaVco1.soundSources.append(self.vco1)
		self.vcaVco1.soundSources.append(self.sub1vco1)
		self.vcaVco1.soundSources.append(self.sub2vco1)
		self.vcaVco1.envSource.env = self.envVco1

		self.vcaVco2 = Vca.Vca()
		self.vcaVco2.soundSources.append(self.vco2)
		self.vcaVco2.soundSources.append(self.sub1vco2)
		self.vcaVco2.soundSources.append(self.sub2vco2)
		self.vcaVco2.envSource.env = self.envVco2

		self.mainVca = Vca.Vca()
		self.mainVca.soundSources.append(self.vcaVco1)
		self.mainVca.soundSources.append(self.vcaVco2)

		self.vcf = Filter.Vcf()
		# filter takes care of its own env for now
		self.vcf.callsList.append(self.mainVca)

	def __call__(self):
		return self.vcf()
		# return self.mainVca()
