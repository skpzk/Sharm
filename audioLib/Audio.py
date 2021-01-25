import queue

import numpy as np
import sounddevice as sd
import threading
import multiprocessing

from audioLib.AudioConst import AudioConst
from audioLib.objects.AudioObject import AudioObject
from audioLib.objects.Clock import Clock


class Audio:
	playback_frames = multiprocessing.Queue(maxsize=20)
	def __init__(self):

		self.audioConst = AudioConst()
		self.audioObject = None
		self.clock = None
		self.T = []

		self._isOn = True
		self.runQueue = threading.Thread(target=self._run)
		self.runQueue.start()

		self.stream = None

	def setAudioObject(self, audioObj: AudioObject):
		self.audioObject = audioObj

	def setClock(self, clock: Clock):
		self.clock = clock


	def init_playback(self):
		self.stream = sd.OutputStream(channels=self.audioConst.CHANNELS,
		                              callback=self.callbackQueue,
		                              samplerate=self.audioConst.RATE,
		                              blocksize=self.audioConst.CHUNK,
		                              dtype=self.audioConst.DTYPE)

		self.stream.start()

	def callbackQueue(self, out: np.ndarray, _0, _1, status) -> None:
		if status:
			out.fill(0)
			# status = None
		else:
			if not self.playback_frames.empty():
				out[:] = self.playback_frames.get(block=False)
			else:
				# print("Underrun")
				out.fill(0)
				pass

	def startAudio(self):
		self.init_playback()

	def stop(self):
		self.stream.stop()
		self._isOn = False
		self.runQueue.join()

		# empty queue to stop all threads correctly
		while not self.playback_frames.empty():
			self.playback_frames.get()

	def _run(self):
		out = np.expand_dims(np.zeros(AudioConst.CHUNK), axis=1)
		while self._isOn:
			out.fill(0)
			if self.clock is not None:
				self.clock.tick()

			if self.audioObject is not None:
				self.audioObject.output(out)

			try:
				self.playback_frames.put(out.copy(), block=True, timeout=1)
			except queue.Full:
				pass
