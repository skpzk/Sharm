from Gui import Ui
from State import State
from AudioLib.Utils import *
from AudioLib.Audio import AudioConstTest as AudioConst
from Dev.DebugUtils import *


class Seq(AudioConst):
	def __init__(self, audioPatch, ID):

		# self.div = div

		self.vcf = audioPatch.vcf

		self.steps = 4
		self.currentStep = 0
		self.lastStep = 0
		# self.divs = [1] * 4
		self.notes = [0.] * 4
		# self.currentDiv = 1
		self.currentNote = 0

		self.called = False
		self.ID = ID
		# cprint(ID)
		self.state = None
		self.range = 1

		if ID == 1:
			self.vco = audioPatch.vco1
			self.sub1 = audioPatch.sub1vco1
			self.sub2 = audioPatch.sub2vco1
			self.env = audioPatch.envVco1
		else:
			self.vco = audioPatch.vco2
			self.sub1 = audioPatch.sub1vco2
			self.sub2 = audioPatch.sub2vco2
			self.env = audioPatch.envVco2

	def callback(self):
		if not self.called:
			self.called = True

			# send signal to Ui to change
			# the color of the last step to black
			d = dict()
			d['type'] = 'seqnote'
			d['seqid'] = self.ID
			d['step'] = self.lastStep
			Ui.events.put(State.Event('note off', d))

			# div = self.divs[self.currentStep]
			note = self.notes[self.currentStep]

			# cprint("note = ", note, "\nrange = ", self.range)
			note = note * self.range

			self.lastStep = self.currentStep
			self.currentStep = np.mod(self.currentStep + 1, 4)

			# self.setDiv(div)
			self.setNote(note)
			# self.currentDiv = div
			self.currentNote = note

			# send signal to Ui to change
			# the color of the last step to black
			d = dict()
			d['type'] = 'seqnote'
			d['seqid'] = self.ID
			d['step'] = self.lastStep
			Ui.events.put(State.Event('note on', d))

			self.called = False

	def setNoteFromState(self, noteInt: int, stepID: int):
		note = (float(noteInt) - 1200.) / 100.
		stepID = int(stepID - 1)
		self.notes[stepID] = note

	def setDiv(self, div):
		self.vcf.on()
		self.vco.setDiv(div, True)
		self.sub1.setDiv(div, True)
		self.sub2.setDiv(div, True)
		self.env.on()

	def setNote(self, note):

		self.vcf.on()
		self.vco.setNote(note, True)
		# self.sub1.setNote(note, True)
		# self.sub2.setNote(note, True)
		self.env.on()

	def call(self):
		return np.ones(self.CHUNK) * self.currentNote

	def setRange(self, seqrange):
		self.range = int(seqrange)
