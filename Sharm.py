import queue
import multiprocessing
import threading
import tkinter as tk
import time

from Gui import Ui
from State import State
from AudioLib import Seq, Audio, Clocks, AudioPatch

"""
New audio design
audio -> Mainclk -> clks -> seqs -> change Vco note and Sub div, trigger env and vcf env
audio -> Vcf -> Va -----> Va -> Vco + subs
.       > env         |       > env
.                     --> Va -> Vco + subs
.                             > env
"""

"""
TDL:
- sequencer is continuous, not dividers
- add function to set the sequencer range
- add quantize function
- still issues at the beginning of Reso and end of cutoff
- values of rots (eg. in env section) ar not aligned proprely
- bug with cutoff when patched, maybe too low values ?
"""

"""
modifications en cours:
+ permettre aux rots d'envoyer des valeurs négatives
+ modifier les rots des séquenceurs pour aller de -120 à +120
+ modifier en conséquence State, vco 
- et sub
- modifier state pour lier les boutons de range
- activer par défaut un bouton de range
- tester
- régler le problème avec les mod sources, maybe add a bool has_input or something
- intégrer la partie dev dans le projet principal tfaçon personne ne regarde le git
"""


class Sharm:
	def __init__(self):
		self.called = False

		self.audio = Audio.Audio()
		self.audioPatch = AudioPatch.AudioPatch()

		self.audio.callsList.append(self.audioPatch)

		self.masterClk, self.clk = self.init_clk()

		# GUI = threading.Thread(target=init_gui, args=[sharm])
		self.gui = multiprocessing.Process(target=self.init_gui)
		self.gui.start()

		self.seq1, self.seq2 = self.init_seq()

		self.state = State.State(self)

		self.audio.start()

	def init_seq(self):
		seq1 = Seq.Seq(self.audioPatch, 1)
		seq2 = Seq.Seq(self.audioPatch, 2)

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
		sharmGui = Ui.Gui(root)

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
