import numpy as np
from AudioLib.AudioConst import AudioConstTest as AudioConst
from Dev.DebugUtils import *


class Env(AudioConst):
	def __init__(self, adsr=None):
		super().__init__()
		if adsr is None:
			adsr = [0, 0, 127, 0]
		self._a_s = 0
		self.a = adsr[0]
		self._d_s = 0
		self.d = adsr[1]
		self._s = 0
		self.s = adsr[2]
		self._r_s = 0
		self.r = adsr[3]
		self.elapsed = 0
		self.isOn = False
		self.isActive = False
		self.max = 0
		self.maxvol = 1.
		self.updateEnv = True

	def on(self):
		self.isOn = True
		self.isActive = True
		self.elapsed = 0

	def off(self):
		self.elapsed = 0
		self.isOn = False

	def compute_attack(self, t):
		env = (t + self.elapsed) / (self._a_s * (self._a_s != 0) + (self._a_s == 0))
		env = env * (env <= 1) + (env > 1)  # saturate to 1
		return env

	def compute_decay(self, t):
		env = 1 - (t + self.elapsed - self._a_s) * (1. - self.s) / (self._d_s * (self._d_s != 0) + (self._d_s == 0))
		env = env * (env >= self.s) + (env < self.s) * self.s
		return env

	@property
	def a(self):
		return self._a_s

	@a.setter
	def a(self, a):
		self._a_s = 3 * np.exp((a - 127) * 1. / 20)

	@property
	def d(self):
		return self._d_s

	@d.setter
	def d(self, d):
		self._d_s = 3 * np.exp((d - 127) * 1. / 20)

	@property
	def s(self):
		return self._s

	@s.setter
	def s(self, s):
		self._s = float(s) / 127.

	@property
	def r(self):
		return self._r_s

	@r.setter
	def r(self, r):
		self._r_s = 5 * np.exp((r - 127) * 1. / 8)

	def setA(self, a):
		# cprint("setting a")
		self.a = a

	def setD(self, d):
		# cprint("setting d")
		self.d = d

	def setR(self, r):
		self.r = r

	def setS(self, s):
		self.s = s

	def setADSR(self, adsr):
		self.a = adsr[0]
		self.d = adsr[1]
		self.s = adsr[2]
		self.r = adsr[3]

	def __call__(self):
		t = np.multiply(np.arange(self.CHUNK), 1. / float(self.RATE))
		if self.isOn:
			if self.elapsed < self._a_s + self._d_s:
				env = self.compute_attack(t) * ((t + self.elapsed) <= self._a_s) + \
					self.compute_decay(t) * (
					((t + self.elapsed) <= (self._a_s + self._d_s)) * (t + self.elapsed) > self._a_s) + \
					((t + self.elapsed) > (self._a_s + self._d_s)) * self.s
				self.elapsed += t[-1] + t[1]
				self.max = env[-1]
				return np.array(env * self.maxvol)
			else:
				self.elapsed += t[-1] + t[1]
				self.max = self.s
				return np.ones(self.CHUNK) * self.maxvol * self.s
		else:
			if self.elapsed < self._r_s:
				env = self.max * (1 - (t + self.elapsed) / (self._r_s * (self._r_s != 0) + (self._r_s == 0)))
				self.elapsed += t[-1] + t[1]
				env = env * (env > 0)
				return np.array(env * self.maxvol)
			else:
				self.isActive = False
				return np.zeros(self.CHUNK)


class EnvAD(Env):
	def __init__(self):
		super().__init__()
		self.s = 0
		self.r = 0

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
		t = np.multiply(np.arange(self.CHUNK), 1. / float(self.RATE))
		if self.isOn:
			if self.elapsed < self._a_s + self._d_s:
				env = self.compute_attack(t) * ((t + self.elapsed) <= self._a_s) + \
					self.compute_decay(t) * (
					((t + self.elapsed) <= (self._a_s + self._d_s)) * (t + self.elapsed) > self._a_s) + \
					((t + self.elapsed) > (self._a_s + self._d_s)) * self.s
				self.elapsed += t[-1] + t[1]
				self.max = env[-1]
				return np.array(env * self.maxvol)
			else:
				self.isOn = False
				self.isActive = False
				return np.zeros(self.CHUNK)
		else:
			return np.zeros(self.CHUNK)
