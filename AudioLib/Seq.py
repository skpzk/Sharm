from Gui import Gui
from State import State
from AudioLib.Utils import *


class Seq:
	def __init__(self, audio, vcf, div, ID):

		self.div = div
		self.audio = audio
		self.vcf = vcf

		self.steps = 4
		self.currentStep = 0
		self.lastStep = 0
		self.notes = [69, 69, 69, 69]

		self.called = False
		self.lastNote = 0
		self.lastDiv = 1
		self.ID = ID
		self.state = None

		self.voices = []
		self.divVoices = []

	def callback(self):
		if not self.called:
			self.called = True

			self.divOff()
			d = dict()
			d['type'] = 'seqnote'
			d['seqid'] = self.ID
			d['step'] = self.lastStep
			Gui.events.put(State.Event('note off', d))

			div = self.notes[self.currentStep]

			self.lastDiv = div
			self.lastStep = self.currentStep
			self.currentStep = np.mod(self.currentStep + 1, 4)

			self.divOn(div)

			d = dict()
			d['type'] = 'seqnote'
			d['seqid'] = self.ID
			d['step'] = self.lastStep
			Gui.events.put(State.Event('note on', d))

			self.called = False

	def noteOn(self, note):
		for voice in self.voices:
			voice.on(note)

	def noteOff(self, note):
		for voice in self.voices:
			voice.off(note)

	def divOn(self, div):
		self.vcf.on()
		for voice in self.voices:
			if voice.ID <= 2:
				if voice in self.divVoices:
					freq = mtof(voice.baseNote)
					freqDiv = freq / div
					note = ftom(freqDiv)
					voice.lastNote = note
					voice.on(note)
					self.voices[1].setMasterNote(note)
					self.voices[2].setMasterNote(note)
				else:
					pass
			else:
				if (voice not in self.divVoices) and (self.voices[0] in self.divVoices):
					voice.lastNote = note = voice.baseNote
					voice.on(note)

				elif voice in self.divVoices:
					voice.setDiv(div)
					voice.lastNote = note = voice.baseNote
					voice.on(note)

				else:
					pass

	def divOff(self):
		for voice in self.voices:
			if voice.ID <= 2:
				if voice in self.divVoices:
					voice.off(voice.lastNote)
				else:
					pass
			else:
				if (self.voices[0] not in self.divVoices) and (voice not in self.divVoices):
					pass
				else:
					voice.off(voice.lastNote)

	def addVoice(self, voice):
		if voice not in self.divVoices:
			if voice.ID > 2:
				voice.fallbackDiv = voice.div
			self.divVoices.append(voice)
		else:
			pass

	def removeVoice(self, voice):
		if voice in self.divVoices:
			self.divVoices.remove(voice)
			if voice.ID > 2:
				voice.div = voice.fallbackDiv
		else:
			pass

	def toggleVoice(self, voice, state):
		if state == 0:
			self.addVoice(voice)
		else:
			self.removeVoice(voice)