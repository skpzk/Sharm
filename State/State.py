import configparser
import multiprocessing
from Gui import Gui
from os.path import join

events = multiprocessing.Queue(maxsize=100)


class Event:
	def __init__(self, param, value):
		self.param = param
		if not isinstance(value, dict):
			d = dict()
			d['type'] = 'undef'
			d['value'] = value
			self.value = d
		else:
			self.value = value


class State:
	def __init__(self, sharm):

		self.seq1 = sharm.seq1
		self.seq2 = sharm.seq2
		self.voices = sharm.voices
		# self.gui = gui
		self.masterClk = sharm.masterClk
		self.clk = sharm.clk
		self.audio = sharm.audio
		self.vcf = sharm.vcf
		self.sharm = sharm

		self.seq1.state = self
		self.seq2.state = self

		self.genericRotDict = self.createGenericRotDict()

		self.state = configparser.ConfigParser()
		self.read()
		self.apply()

		print("State Finished")

		sharm.audio.stateFinished = True

	def read(self):
		path = join("State", "state.sharm")
		self.state.read(path)

	def save(self):
		path = join("State", "state.sharm")
		with open(path, 'w') as f:
			self.state.write(f)

	def apply(self):
		for key in self.state.sections():
			if key != 'Random':
				d = dict()
				for k in self.state[key].keys():
					try:
						value = int(self.state[key][k])
					except ValueError:
						try:
							value = float(self.state[key][k])
						except ValueError:
							value = self.state[key][k]
					d[k] = value

				events.put(Event(key, d))

				Gui.events.put(Event(key, d))

	def update(self, key, value):
		if isinstance(value, dict):
			self.state[key] = value
		else:
			self.state[key] = dict([('value', value)])

	def change(self, message):
		updating = True  # if the message can't be read, the state isn't updated
		if message.value['type'] == 'rot':
			if message.value['rottype'] in ['generic', 'filterrot', 'envrot']:
				try:
					self.genericRotDict[message.param](message.value['value'])
				except KeyError:
					updating = False

			elif message.value['rottype'] == 'vcorot':
				if message.param[:5] == 'level':
					voiceID = message.value['id']
					self.voices.voices[voiceID].setVol(message.value['value'])

				elif message.param[:3] == 'Vco':
					voiceID = message.value['voiceid'] - 1
					# print("State : setBaseNote")
					self.voices.voices[voiceID].setBaseNote(message.value['value'])
					self.voices.voices[voiceID * 2 + 2].setMasterNote(message.value['value'])
					self.voices.voices[voiceID * 2 + 3].setMasterNote(message.value['value'])

				elif message.param[:3] == 'Sub':
					voiceID = message.value['voiceid']
					self.voices.voices[voiceID].setDiv(message.value['value'])

			elif message.value['rottype'] == 'rythmrot':
				if message.param[:4] == 'Step':
					seqID = message.value['seqid']
					stepID = message.value['stepid']
					note = message.value['value']
					if seqID == 1:
						self.seq1.notes[stepID - 1] = int(note)
					else:
						self.seq2.notes[stepID - 1] = int(note)
				elif message.param[:3] == 'Clk':
					clkID = message.value['clkid']
					self.clk[clkID - 1].setDiv(message.value['value'])

			else:
				updating = False
		else:
			if message.param == 'Random':
				self.seq1.random()
				self.seq2.random()

			elif message.param[:11] == 'callbackClk':
				state = message.value['state']
				clkID = message.value['clkid']
				seqID = message.value['seqid']
				if seqID == 1:
					self.clk[clkID - 1].toggleCallback(1, self.seq1.callback, state)
				else:
					self.clk[clkID - 1].toggleCallback(2, self.seq2.callback, state)

			elif message.param[:6] == 'assign':
				seqID = message.value['seqid']
				voiceID = message.value['voiceid']
				state = message.value['state']
				if seqID == 1:
					self.seq1.toggleVoice(self.voices.voices[voiceID], state)
				else:
					self.seq2.toggleVoice(self.voices.voices[voiceID], state)

			elif message.param[:4] == 'wave':
				v0 = message.value['v0']
				v1 = message.value['v1']
				v2 = message.value['v2']
				self.voices.voices[v0].setWave(message.value['wave'])
				self.voices.voices[v1].setWave(message.value['wave'])
				self.voices.voices[v2].setWave(message.value['wave'])

			else:
				updating = False

		if updating:
			self.update(message.param, message.value)
		else:
			print("Can't read the message")
			print("message : ", message.param, " : ", message.value)
			pass

	def createGenericRotDict(self):
		d = dict()
		d['A'] = self.voices.setA
		d['D'] = self.voices.setD
		d['S'] = self.voices.setS
		d['R'] = self.voices.setR
		d['Vol'] = self.voices.setVol
		d['Tempo'] = self.masterClk.setRateMidi

		d['fc'] = self.vcf.updateFc
		d['Q'] = self.vcf.updateQ
		d['D filter'] = self.vcf.setD
		d['A filter'] = self.vcf.setA
		d['EG Amount'] = self.vcf.setEG

		return d
