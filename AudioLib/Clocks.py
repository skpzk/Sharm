import numpy as np
import time
from AudioLib import Audio


class MasterClk:  # frequency range is 1/3Hz - 50Hz

	def __init__(self, audio, rate=1):
		self.minFreq = 1/3
		self.maxFreq = 50
		self.f = rate
		self.audio = audio
		self.t0 = self.t1 = 0

		self.interval = 1. / self.f
		self.running = False
		self.callbackList = []
		self.audio.synclist.append(self.sync)
		self.tic = True

		self.elapsed = 0

	def setRateMidi(self, rate):
		f = self.calcRateMidi(rate)
		f = f * self.minFreq / self.calcRateMidi(0)
		self.f = f
		self.interval = 1 / self.f

	@staticmethod
	def calcRateMidi(rate):
		return np.exp((rate - 64) / 25)

	def correctRate(self, rate):
		rate = (rate - self.calcRateMidi(0)) * (self.maxFreq - self.minFreq)\
		       / (self.calcRateMidi(127) - self.calcRateMidi(0)) + self.minFreq
		return rate

	def start(self):
		self.running = True
		self.t0 = time.time()
		self.t1 = self.t0

	def stop(self):
		self.running = False
		self.t0 = self.t1 = 0

	def sync(self):
		if self.running:
			t = np.multiply(np.arange(self.audio.CHUNK), 1. / float(self.audio.RATE))
			if self.elapsed > self.interval:
				self.elapsed = 0
				self.call()
			self.elapsed += t[-1] + t[1]

	def call(self):
		seq1Called = False
		seq2Called = False
		for c in self.callbackList:
			seq1Called, seq2Called = c(seq1Called, seq2Called)

	def tictoc(self):
		if self.tic:
			print("Tic")
			self.tic = False
		else:
			print("Toc")
			self.tic = True


class Clk:
	def __init__(self, master, ID, div=1):
		self.master = master
		self.master.callbackList.append(self.callback)
		self.div = div
		self.callbackList = []
		self.callsDict = dict()
		self.count = 0
		self.ID = ID

	def setCallback(self, seqID, func):
		self.callsDict[str(seqID)] = func

	def removeCallback(self, seqID):
		self.callsDict.pop(str(seqID))

	def toggleCallback(self, seqID, function=None, state=""):
		"""function called by State when the gui asks for it
		It adds or removes a callback to the sequencers"""
		if function is None:
			function = []
		if state == "":
			if str(seqID) in self.callsDict.keys():
				self.removeCallback(seqID)
			else:
				self.setCallback(seqID, function)
		else:
			if state == 1 and (str(seqID) in self.callsDict.keys()):
				self.removeCallback(seqID)
			elif str(seqID) not in self.callsDict.keys():
				self.setCallback(seqID, function)

	def callback(self, seq1called, seq2called):
		"""Checks how many times it has been called by the master clock and call the seqs if necessary"""
		self.count += 1
		if self.count >= self.div:
			self.count = 0
			return self.call(seq1called, seq2called)
		else:
			return seq1called, seq2called

	def call(self, seq1called, seq2called):
		"""calls the seqs only if they have not been already called"""
		for seq, c in self.callsDict.items():
			if seq == '1' and not seq1called:
				c()
				seq1called = True
			elif seq == '2' and not seq2called:
				c()
				seq2called = True
		return seq1called, seq2called

	def setDiv(self, div):
		self.div = div


if __name__ == "__main__":
	# testing the frequency range of MasterClk
	import matplotlib.pyplot as plt

	clk = MasterClk(Audio.Audio())

	midiRate = np.array([i for i in range(128)])
	clockrate = clk.correctRate(clk.calcRateMidi(midiRate))
	print(clockrate)
	plt.figure()
	plt.plot(midiRate, clockrate)
	plt.show()
