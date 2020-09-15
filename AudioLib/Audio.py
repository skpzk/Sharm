import sounddevice as sd
import threading
import multiprocessing

import time
import numpy as np
from AudioLib.Utils import *
from AudioLib import Note


class AudioConst:
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
			# print(data.shape)
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

		data = ssat(data) * 8.
		data = data * np.power(2, 2)

		data = np.expand_dims(data, axis=1)
		self.write(data)

	def run(self):

		while self.On:
			# cprint("Running")
			# this should be called by the more accurate callback function
			for sync in self.synclist:
				sync()

			self.compute()


if __name__ == "__main__":
	audio = Audio()
	audio.start()

	note = Note.Note(audio)
	audio.callsList.append(note)
	note.env.setADSR([0, 0, 127, 0])
	note.on(69)

	time.sleep(1)

	audio.stop()
