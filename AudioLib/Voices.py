from AudioLib import Audio, Note
from AudioLib.Utils import *
import numpy as np


class Voices:
	MAXSIZE = 16

	def __init__(self, audioConst, ID=-1):

		self.fc = 200
		self.Q = 1
		self.notes = []
		self.baseNote = 69
		self.masterNote = self.baseNote
		self.div = 1
		self.fallbackDiv = 1
		self.lastNote = []
		self.audio = audioConst
		self.noteVoices = 1
		self.wave = 'tri'
		self.callsList = []

		self.adsr = [0, 0, 127, 0]
		self.vol = 1
		self.ID = ID

	def on(self, midiNote):

		if not self.isNotePlayed(midiNote):
			voice = self.findFreeVoice()
			self.notes[voice].on(midiNote)
			self.notes[voice].order = self.lastOrder()
		else:
			voice = self.findStopVoice(midiNote)
			self.notes[voice].on(midiNote)

			self.updateOrder(self.notes[voice].order)

			self.notes[voice].order = self.lastOrder()

	def off(self, midiNote):  # tbd

		voice = self.findStopVoice(midiNote)
		if voice != -1:
			self.notes[voice].off()

	def lastOrder(self):
		o = -1
		for note in self.notes:
			if note.order > o:
				o = note.order
		return o + 1

	def updateStatus(self):
		for note in self.notes:
			if (not note.env.isActive) and (note.note != -1):
				o = note.order
				i = note.noteId
				self.notes.remove(note)
				self.callsList.remove(note)
				self.updateOrder(o)
				self.updateId(i)

	def findFreeVoice(self):
		if len(self.notes) < self.MAXSIZE:
			self.notes.append(Note.Note(self.audio, self.adsr, self.wave, self.vol))
			self.callsList.append(self.notes[-1])
			self.notes[-1].noteId = len(self.notes) - 1
			return len(self.notes) - 1
		else:
			for note in self.notes:
				if note.order == 0:
					self.updateOrder(0)
					return note.noteId
		return 0  # safety first

	def findStopVoice(self, midinote):
		for note in self.notes:
			if note.note == midinote:
				return note.noteId
		return -1

	def isNotePlayed(self, midinote):
		for note in self.notes:
			if note.note == midinote:
				return True
		return False

	def updateOrder(self, n):
		for note in self.notes:
			if note.order >= n:
				note.order -= 1

	def updateId(self, n):
		for note in self.notes:
			if note.noteId > n:
				note.noteId -= 1

	def close(self):
		for note in self.notes:
			note.close()

	def __call__(self):
		data = np.zeros(self.audio.CHUNK)
		for call in self.callsList:
			# print(call)
			data += call()
		# print(data)
		return Audio.ssat(data)

	def called(self):
		print("Voice", self.ID, "Called")

	def prompt(self):
		print("Voice ", self.ID, " : ")
		for note in self.notes:
			print("notes[%d]\tnote:%d\torder:%d\tactive:%d" % (note.noteId, note.note, note.order, note.isActive))
		print("")

	def setBaseNote(self, note):
		self.baseNote = ftom(mtof(note) / self.div)

	def setMasterNote(self, note):
		self.masterNote = note
		self.setDiv(self.div)

	def setDiv(self, div):
		self.div = div
		self.setBaseNote(self.masterNote)

	def setVol(self, vol):
		self.vol = vol
		for note in self.notes:
			note.setVol(vol)

	def setWave(self, wave):
		self.wave = wave
		for note in self.notes:
			note.setWave(wave)

	def setNbOscs(self, nb):
		self.noteVoices = nb
		for note in self.notes:
			note.setNbOscs(nb)

	def setFc(self, fc):
		self.fc = fc
		for note in self.notes:
			note.setFc(fc)

	def setQ(self, Q):
		self.Q = Q
		for note in self.notes:
			note.setQ(Q)

	def setA(self, a):
		self.adsr[0] = a
		for note in self.notes:
			note.env.setA(a)

	def setD(self, d):
		self.adsr[1] = d
		for note in self.notes:
			note.env.setD(d)

	def setS(self, s):
		self.adsr[2] = s
		for note in self.notes:
			note.env.setS(s)

	def setR(self, r):
		self.adsr[3] = r
		for note in self.notes:
			note.env.setR(r)


class VoicesList:
	def __init__(self, audio, nbVoices):
		self.voices = []
		self.chunk = audio.CHUNK
		for i in range(nbVoices):
			self.voices.append(Voices(audio, i+1))

	def __call__(self):
		data = np.zeros(self.chunk)
		for voice in self.voices:
			# print(voice)
			data += voice()  # call voices

		return Audio.ssat(data)

	def setVol(self, vol):
		for voice in self.voices:
			voice.setVol(vol)

	def setWave(self, wave):
		for voice in self.voices:
			voice.setWave(wave)

	def setFc(self, fc):
		for voice in self.voices:
			voice.setFc(fc)

	def setQ(self, Q):
		for voice in self.voices:
			voice.setQ(Q)

	def setA(self, a):
		for voice in self.voices:
			voice.setA(a)

	def setD(self, d):
		for voice in self.voices:
			voice.setD(d)

	def setS(self, s):
		for voice in self.voices:
			voice.setS(s)

	def setR(self, r):
		for voice in self.voices:
			voice.setR(r)

	def updateStatus(self):
		for voice in self.voices:
			voice.updateStatus()
