# import numpy as np
import time
# import queue
import pyaudio
import threading
import multiprocessing

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

	def __init__(self, chunk=None):
		self.init_playback(chunk)
		threading.Thread.__init__(self)

	def callback(self, in_data, frame_count, _0, status):
		in_data = bytes(np.zeros(frame_count, dtype=np.int16))

		if not self.playback_frames.empty():
			in_data = self.playback_frames.get(block=False)
		else:
			# cprint("Underrun")
			pass

		# print("len(playback_frames) = ", self.playback_frames.qsize())

		return in_data, pyaudio.paContinue

	def init_audio(self, chunk):
		if chunk is not None:
			self.CHUNK = chunk
		else:
			self.CHUNK = int(0.25 * 1024)
			# self.CHUNK = 4 * 1024
		self.FORMAT = pyaudio.paInt16
		self.CHANNELS = 1
		self.RATE = 44100
		self.callsList = []
		self.synclist = []

	def init_playback(self, chunk):
		self.init_audio(chunk)
		self.p = pyaudio.PyAudio()
		self.stream = self.p.open(format=self.FORMAT,
															channels=self.CHANNELS,
															rate=self.RATE,
															input=False,
															output=True,
															frames_per_buffer=self.CHUNK,
															stream_callback=self.callback)

		self.stream.start_stream()

	def close(self):
		self.stream.stop_stream()
		self.stream.close()
		self.p.terminate()

	def write(self, data):
		self.playback_frames.put(data, block=True)

	def stop(self):
		self.On = False

	def compute(self):

		data = np.zeros(self.CHUNK)

		for call in self.callsList:
			data += call()

		data = ssat(data) * 8.
		data = data * np.power(2, 14)

		data = np.array(data, dtype=np.int16)

		self.write(bytes(data))

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

	time.sleep(5)

	audio.stop()
	audio.join()
	audio.close()
