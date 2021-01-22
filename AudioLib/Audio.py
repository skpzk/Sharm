import sounddevice as sd
import threading
import multiprocessing

import time
import numpy as np
from AudioLib.Utils import *
from Dev.DebugUtils import *


class AudioConstTest:
	CHUNK = int(0.25 * 1024)
	RATE = 44100


class AudioConst:
	"""
	this class contains information about the audio rate and the size of the audio buffer
	all audio objects could inherit from it
	"""
	def __init__(self, audio):
		self.CHUNK = audio.CHUNK
		self.RATE = audio.RATE


"""Callback pattern:
	Rythm:
		MasterClk is synced by the main audio loop
		MasterClk calls the four clk
		clks call seqs
		seqs start and stop voices

	Audio:
		audio mainloop calls vcf
		vcf calls voices
		voices call notes
		notes call osc
	"""


class Audio(threading.Thread):
	playback_frames = multiprocessing.Queue(maxsize=50)
	p = []
	stream = []
	CHUNK = []
	FORMAT = []
	CHANNELS = []
	RATE = []
	On = True
	callsList = []
	synclist = []

	def callback(self, outdata, frames, _, status):
		if status:
			print(status)
		if not self.playback_frames.empty():
			data = self.playback_frames.get(block=False)
		else:
			data = np.expand_dims(np.zeros(frames), axis=1)
		# cprint(data)
		outdata[:] = data

	def __init__(self, chunk=None):
		self.init_playback(chunk)
		threading.Thread.__init__(self)

	def init_playback(self, chunk):
		self.init_audio(chunk)
		self.stream = sd.OutputStream(channels=self.CHANNELS,
		                              callback=self.callback,
		                              samplerate=self.RATE,
		                              blocksize=self.CHUNK,
		                              dtype='float32')

		self.stream.start()

	def init_audio(self, chunk):
		# this feature is intended for debugging purposes only
		# and sould not appear in the final program
		if chunk is not None:
			self.CHUNK = chunk
		else:
			self.CHUNK = int(0.25 * 1024)
			# self.CHUNK = 4 * 1024
		self.CHANNELS = 1
		self.RATE = 44100
		self.callsList = []
		self.synclist = []

	def stop(self):
		self.On = False

	def write(self, data):
		self.playback_frames.put(data, block=True)

	def compute(self):

		data = np.zeros(self.CHUNK)

		for call in self.callsList:
			data += call()

		data = ssat(data, 1)

		data = np.expand_dims(data, axis=1)
		# cprint(data)
		self.write(data)

	def run(self):

		while self.On:
			# cprint("Running")
			# this should be called by the more accurate callback function
			for sync in self.synclist:
				sync()

			self.compute()


if __name__ == "__main__":
	from AudioLib import Vco, Vca, Env
	from AudioLib import AudioPatch
	audio = Audio()
	audio.start()

	# audioPatch = AudioPatch.AudioPatch()

	env = Env.Env()
	vca = Vca.Vca()
	vco = Vco.Vco()
	sub = Vco.Sub(vco)
	vca.soundSources.append(vco)
	vca.soundSources.append(sub)
	vca.envSource.env = env
	env.on()
	vco.setWave('sqr')
	sub.setWave('sine')

	sub.setDiv(20)
	vco.setVolume(0.2)
	sub.setVolume(0.6)
	vco.modSources.pwm = sub.call
	# vco.setNote(60)
	audio.callsList.append(vca)
	time.sleep(1)
	vco.setBaseNote(60)
	# vco.modSources.freq = ""
	time.sleep(1)
	env.r = 120
	env.off()
	vco.setBaseNote(69)
	time.sleep(1)

	audio.stop()
