import numpy as np

from Dev.DebugUtils import *
from AudioLib.Audio import AudioConstTest as AudioConst


class Mod(AudioConst, object):
	def __init__(self, const):
		super().__init__()
		self._mod = None
		self.const = const

	@property
	def mod(self):
		if self._mod is None:
			return np.ones(self.CHUNK) * self.const
		else:
			# cprint("called")
			return self._mod()

	@mod.setter
	def mod(self, func):
		mprint("setter called")
		if hasattr(func, '__call__'):
			self._mod = func
		else:
			self._mod = None
			raise TypeError

	def __call__(self):
		return self.mod


class ModSources(dict):
	__getattr__ = dict.__getitem__
	# __setattr__ = dict.__setitem__
	__delattr__ = dict.__delitem__

	def __init__(self, names):
		super().__init__()
		for name, const in names:
			self[name] = Mod(const)

	def __setattr__(self, key, value):
		if isinstance(value, int):
			dict.__setitem__(self, key, Mod(value))
		else:
			mprint("Key = ", key, "value = ", value)
			self[key].mod = value
