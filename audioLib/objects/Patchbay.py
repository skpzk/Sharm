from copy import deepcopy

import numpy as np

from audioLib.objects.AudioObject import AudioObject
from audioLib.objects.NoiseGenerator import NoiseGenerator, SH


class PpDict(dict):
	__getattr__ = dict.__getitem__
	__delattr__ = dict.__delitem__
	def __init__(self, names=""):
		super().__init__(names)

	def __setattr__(self, key, value):
		dict.__setitem__(self, key, value)


class PatchPoint():
	def __init__(self, **kwargs):
		self.defaultValue = 0

		self.outs = PpDict()
		# self.isConnected = False
		self.blockPop = False

		for key, value in kwargs.items():
			if key == 'defaultValue':
				self.defaultValue = value

	def __call__(self, out):
		out.fill(0)
		# outs = deepcopy(dict(self.outs))
		# for cvout in self.outs.values():
		# 	cvout(out)
		self.blockPop = True
		for cvout in self.outs.values():
			cvout(out)
		self.blockPop = False

	def isConnected(self):
		# print("Is connected ?")
		if len(self.outs) > 0:
			# print("yes")
			return True
		# print("Nope")
		return False


class Patchbay():
	def __init__(self):
		self.ins = PpDict()
		self.outs = PpDict()
		self.ins.vco1 = PatchPoint()
		self.ins.vco2 = PatchPoint()
		self.ins.vco1sub = PatchPoint()
		self.ins.vco2sub = PatchPoint()
		self.ins.vco1pwm = PatchPoint()
		self.ins.vco2pwm = PatchPoint()
		self.ins.vca = PatchPoint()

		self.ins.rhythm1 = PatchPoint()
		self.ins.rhythm2 = PatchPoint()
		self.ins.rhythm3 = PatchPoint()
		self.ins.rhythm4 = PatchPoint()

		self.ins.cutoff = PatchPoint()
		self.ins.clock = PatchPoint()

		self.ins.trigger = PatchPoint()

		self.ins.seq1 = PatchPoint()
		self.ins.seq2 = PatchPoint()


		self.outs.vco1 = AudioObject(defaultValue=0).CVOutput
		self.outs.vco2 = AudioObject(defaultValue=0).CVOutput
		self.outs.vco1sub1 = AudioObject(defaultValue=0).CVOutput
		self.outs.vco2sub1 = AudioObject(defaultValue=0).CVOutput

		self.outs.vca = AudioObject(defaultValue=0).CVOutput
		self.outs.vcaeg = AudioObject(defaultValue=1).CVOutput


		self.outs.seq1 = AudioObject(defaultValue=0).CVOutput
		self.outs.seq2 = AudioObject(defaultValue=0).CVOutput
		self.outs.vcfeg = AudioObject(defaultValue=1).CVOutput

		self.outs.noise = NoiseGenerator().CVOutput
		self.outs.sh = SH().CVOutput
		self.outs.clock = AudioObject(defaultValue=0).CVOutput

		self.outs.seq1clk = AudioObject(defaultValue=0).CVOutput
		self.outs.seq2clk = AudioObject(defaultValue=0).CVOutput



	def connect(self, **kwargs):
		try:
			# print("connecting output %s to input %s" %(kwargs['ppout'], kwargs['ppin']))
			in_name = kwargs['ppin']
			out_name = kwargs['ppout']
			self.ins[in_name].outs[out_name] = self.outs[out_name]
			# self.ins[in_name].isConnected = True
		except KeyError:
			print("wrong keyword args")

	def disconnect(self, **kwargs):
		try:
			in_name = kwargs['ppin']
			out_name = kwargs['ppout']
			while self.ins[in_name].blockPop:
				# print("Can't disconnect right now")
				pass
			self.ins[in_name].outs.pop(out_name)
		except KeyError:
			print("wrong keyword args")
