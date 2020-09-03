import numpy as np


class Env:
	def __init__(self, audio, adsr=None):
		if adsr is None:
			adsr = [0, 0, 1, 0]
		self.a_s = 0
		self.setA(adsr[0])
		self.d_s = 0
		self.setD(adsr[1])
		self.s = 0
		self.setS(adsr[2])
		self.r_s = 0
		self.setR(adsr[3])
		self.elapsed = 0
		self.audio = audio
		self.isOn = False
		self.isActive = False
		self.max = 0
		self.maxvol = 1. / 16.

	def on(self):
		self.isOn = True
		self.isActive = True
		self.elapsed = 0

	def off(self):
		self.elapsed = 0
		self.isOn = False

	def compute_attack(self, t):
		env = (t + self.elapsed) / (self.a_s * (self.a_s != 0) + (self.a_s == 0))
		env = env * (env <= 1) + (env > 1)  # saturate to 1
		return env

	def compute_decay(self, t):
		env = 1 - (t + self.elapsed - self.a_s) * (1. - self.s) / (self.d_s * (self.d_s != 0) + (self.d_s == 0))
		env = env * (env >= self.s) + (env < self.s) * self.s
		return env

	def setA(self, a):
		self.a_s = 3 * np.exp((a - 127) * 1. / 20)

	def setD(self, d):
		self.d_s = 3 * np.exp((d - 127) * 1. / 20)

	def setS(self, s):
		self.s = float(s) / 127.

	def setR(self, r):
		self.r_s = 5 * np.exp((r - 127) * 1. / 8)

	def setADSR(self, adsr):
		self.setA(adsr[0])
		self.setD(adsr[1])
		self.setS(adsr[2])
		self.setR(adsr[3])

	def __call__(self):
		t = np.multiply(np.arange(self.audio.CHUNK), 1. / float(self.audio.RATE))
		if self.isOn:
			if self.elapsed < self.a_s + self.d_s:
				env = self.compute_attack(t) * ((t + self.elapsed) <= self.a_s) + \
					self.compute_decay(t) * (
					((t + self.elapsed) <= (self.a_s + self.d_s)) * (t + self.elapsed) > self.a_s) + \
					((t + self.elapsed) > (self.a_s + self.d_s)) * self.s
				self.elapsed += t[-1] + t[1]
				self.max = env[-1]
				return np.array(env * self.maxvol)
			else:
				self.elapsed += t[-1] + t[1]
				self.max = self.s
				return np.ones(self.audio.CHUNK) * self.maxvol * self.s
		else:
			if self.elapsed < self.r_s:
				env = self.max * (1 - (t + self.elapsed) / (self.r_s * (self.r_s != 0) + (self.r_s == 0)))
				self.elapsed += t[-1] + t[1]
				env = env * (env > 0)
				return np.array(env * self.maxvol)
			else:
				self.isActive = False
				return np.zeros(self.audio.CHUNK)


class EnvAD(Env):
	def __init__(self, audio, ad=None):
		Env.__init__(self, audio, ad)
		self.s = 0
		self.r_s = 0

	def on(self):
		if not self.isActive:
			self.isOn = True
			self.isActive = True
			self.elapsed = 0

	def off(self):
		pass

	def setR(self, r):
		pass

	def setS(self, s):
		pass

	def __call__(self):
		t = np.multiply(np.arange(self.audio.CHUNK), 1. / float(self.audio.RATE))
		if self.isOn:
			if self.elapsed < self.a_s + self.d_s:
				env = self.compute_attack(t) * ((t + self.elapsed) <= self.a_s) + \
					self.compute_decay(t) * (
					((t + self.elapsed) <= (self.a_s + self.d_s)) * (t + self.elapsed) > self.a_s) + \
					((t + self.elapsed) > (self.a_s + self.d_s)) * self.s
				self.elapsed += t[-1] + t[1]
				self.max = env[-1]
				return np.array(env * self.maxvol)
			else:
				self.isOn = False
				self.isActive = False
				return np.zeros(self.audio.CHUNK)
		else:
			return np.zeros(self.audio.CHUNK)
