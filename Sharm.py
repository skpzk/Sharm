import queue
import multiprocessing
import threading
import tkinter as tk
import time

from Gui import Gui
from State import State
from AudioLib import Voices, Seq, Audio, Clocks, Filter


class Sharm:
	def __init__(self):
		self.called = False

		self.audio = Audio.Audio()
		audioConst = Audio.AudioConst(self.audio)

		self.voices = Voices.VoicesList(audioConst, 6)
		# voices[0 -> 1] : vco 1 & 2
		# voices[2 -> 3] : sub1/2 of vco 1
		# voices[4 -> 5] : sub1/2 of vco 2
		self.vcf = Filter.Vcf(audioConst)
		self.vcf.callsList.append(self.voices)
		self.audio.callsList.append(self.vcf)

		self.masterClk, self.clk = self.init_clk()

		# GUI = threading.Thread(target=init_gui, args=[sharm])
		self.gui = multiprocessing.Process(target=self.init_gui)
		self.gui.start()

		self.seq1, self.seq2 = self.init_seq()

		self.state = State.State(self)

		self.audio.start()

	def init_seq(self):
		seq1 = Seq.Seq(self.audio, self.vcf, 1, 1)
		seq2 = Seq.Seq(self.audio, self.vcf, 1, 2)

		seqVoices = [[1, 3, 4], [2, 5, 6]]

		for voiceID in seqVoices[0]:
			seq1.voices.append(self.voices.voices[voiceID - 1])
		for voiceID in seqVoices[1]:
			seq2.voices.append(self.voices.voices[voiceID - 1])

		return seq1, seq2

	def init_clk(self):
		masterClk = Clocks.MasterClk(self.audio)
		clk = []
		div = 1
		for i in range(4):
			clk.append(Clocks.Clk(masterClk, i, div))
		masterClk.start()
		return masterClk, clk

	@staticmethod
	def init_gui():
		root = tk.Tk()
		sharmGui = Gui.Gui(root)

		checkQueue = threading.Thread(target=sharmGui.checkQueueLoop)
		checkQueue.start()
		root.mainloop()
		checkQueue.join()
		time.sleep(0.5)

	def mainLoop(self):
		# main_loop(self.voices, self.state)
		try:
			message = State.events.get(block=True)
			if isinstance(message, State.Event):
				if message.param == -1:
					print("Interrupt caught!")
					self.close()
					raise KeyboardInterrupt
				else:
					self.state.change(message)

		except queue.Empty:
			pass

	def close(self):
		if not self.called:
			self.called = True
			self.state.save()

			self.audio.stop()

			self.gui.join()
			self.gui.close()
