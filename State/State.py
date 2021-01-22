import configparser
import multiprocessing
from Gui import Ui
from os.path import join
from Dev.DebugUtils import *

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
		try:
			_ = self.value['type']
		except KeyError:
			self.value['type'] = 'undef'


class State:
	def __init__(self, sharm):

		self.seq1 = sharm.seq1
		self.seq2 = sharm.seq2
		self.audioPatch = sharm.audioPatch
		self.voices = []
		self.setVoices()
		self.masterClk = sharm.masterClk
		self.clk = sharm.clk
		self.audio = sharm.audio
		self.sharm = sharm

		self.seq1.state = self
		self.seq2.state = self

		self.genericRotDict = self.createGenericRotDict()
		self.dictOfCallbackLists = dict()
		self.dictOfCallbackFunctions = dict()
		self.initPatchbayDicts()

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
				Ui.events.put(Event(key, d))

	def update(self, key, value):
		if isinstance(value, dict):
			self.state[key] = value
		else:
			self.state[key] = dict([('value', value)])

	def change(self, message):
		updating = True  # if the message can't be read, the state isn't updated
		# cprint(message.value)
		if message.value['type'] == 'rot':
			if message.value['rottype'] in ['general', 'filter']:
				try:
					# self.audioPatch.mainVa['test'] = 1
					self.genericRotDict[message.param](message.value['value'])
				except KeyError:
					updating = False

			elif message.value['rottype'] == 'env':
				if message.param.lower() == 'a':
					self.audioPatch.envVco1.setA(message.value['value'])
					self.audioPatch.envVco2.setA(message.value['value'])
				elif message.param.lower() == 'd':
					self.audioPatch.envVco1.setD(message.value['value'])
					self.audioPatch.envVco2.setD(message.value['value'])

			elif message.value['rottype'] == 'vco':
				if message.param[:5] == 'level':
					voiceID = message.value['voiceid']
					self.voices[voiceID].setVolume(message.value['value'])

				elif message.param[:3] == 'Vco':
					voiceID = message.value['voiceid']
					# cprint("State : setVcoNote for voice", voiceID)
					self.voices[voiceID].setNote(message.value['value'])

				elif message.param[:3] == 'Sub':
					voiceID = message.value['voiceid']
					self.voices[voiceID].setDiv(message.value['value'])

			elif message.value['rottype'] == 'rhythm':
				if message.param[:4] == 'Step':
					seqID = message.value['seqid']
					stepID = message.value['stepid']
					note = message.value['value']
					if seqID == 1:
						self.seq1.setNoteFromState(int(note), int(stepID))
					else:
						self.seq2.setNoteFromState(int(note), int(stepID))
				elif message.param[:3] == 'Clk':
					clkID = message.value['clkid']
					self.clk[clkID - 1].setDiv(message.value['value'])

			else:
				updating = False
		elif message.value['type'] == 'patchbay':
			# cprint("Patchbay")
			callbackList = []
			function = []
			patchOut = message.value['out']
			patchIn = message.value['in']
			connect = message.value['connect']
			try:
				# callbackList = self.dictOfCallbackLists[patchIn]
				function = self.dictOfCallbackFunctions[patchOut]
				if function:
					if connect == 1:
						cprint("Connecting...")
						self.connect(patchIn, function)
					else:
						cprint("Disconnecting...")
						try:
							self.connect(patchIn, '')
						except TypeError:
							pass
				else:
					print("not implemented yet")
					updating = False
			except KeyError:
				cprint("Error selecting patchpoint, name does not exist")
				updating = False

		else:

			if message.param[:11] == 'callbackClk':
				state = message.value['state']
				clkID = message.value['clkid']
				seqID = message.value['seqid']
				if seqID == 1:
					# print("toogle seq1")
					self.clk[clkID - 1].toggleCallback(1, self.seq1.callback, state)
				else:
					# print("toogle seq2")
					self.clk[clkID - 1].toggleCallback(2, self.seq2.callback, state)

			elif message.param[:6] == 'assign':
				# seqID = message.value['seqid']
				voiceID = message.value['voiceid']
				# cprint("Voice ID = ", voiceID)
				state = message.value['state']
				if state == 0:
					self.voices[voiceID].sequencerActive = True
				else:
					self.voices[voiceID].sequencerActive = False

			elif message.param[:4] == 'wave':
				v0 = message.value['v0']
				v1 = message.value['v1']
				v2 = message.value['v2']
				self.voices[v0].setWave(message.value['wave'])
				self.voices[v1].setWave(message.value['wave'])
				self.voices[v2].setWave(message.value['wave'])

			elif message.param == "range":
				self.seq1.setRange(message.value['range'])
				self.seq2.setRange(message.value['range'])

			else:
				updating = False

		if updating:
			self.update(message.param, message.value)
		else:
			cprint("Can't read the message")
			cprint("message : ", message.param, " : ", message.value)
			pass

	def createGenericRotDict(self):
		d = dict()
		d['Vol'] = self.audioPatch.mainVca.setVol
		d['Tempo'] = self.masterClk.setRate

		d['fc'] = self.audioPatch.vcf.setFc
		d['Q'] = self.audioPatch.vcf.setQ
		d['D filter'] = self.audioPatch.vcf.setD
		d['A filter'] = self.audioPatch.vcf.setA
		d['EG Amount'] = self.audioPatch.vcf.setEg

		return d

	def initPatchbayDicts(self):
		d = self.dictOfCallbackLists
		d["VCA"] = []
		d["CUTOFF"] = []
		d["PLAY"] = []
		d["RESET"] = []
		d["TRIGGER"] = []
		d["RHYTHM 1"] = []
		d["RHYTHM 2"] = []
		d["RHYTHM 3"] = []
		d["RHYTHM 4"] = []
		d["UNDEF"] = []
		d["CLOCK"] = []

		d = self.dictOfCallbackFunctions
		d["VCA"] = []
		d["VCO 1"] = self.audioPatch.vco1.call
		d["VCO 1 SUB 1"] = self.audioPatch.sub1vco1.call
		d["VCO 1 SUB 2"] = self.audioPatch.sub2vco1.call
		d["VCA EG"] = []
		d["VCO 2"] = self.audioPatch.vco2.call
		d["VCO 2 SUB 1"] = self.audioPatch.sub1vco2.call
		d["VCO 2 SUB 2"] = self.audioPatch.sub2vco2.call
		d["VCF EG"] = []
		d["SEQ 1"] = self.seq1.call
		d["SEQ 1 CLK"] = []
		d["SEQ 2"] = self.seq1.call
		d["SEQ 2 CLK"] = []
		d["CLOCK"] = []
		d["TRIGGER"] = []

	def connect(self, patchIn: str, function):
		if patchIn == 'VCO 1':
			cprint("Connecting VCO1, function = ", function)
			self.audioPatch.vco1.modSources.freq = function
		elif patchIn == "VCO 1 SUB":
			cprint("Connecting subVCO1, function = ", function)
			self.audioPatch.sub1vco1.modSources.div = function
			self.audioPatch.sub2vco1.modSources.div = function
		elif patchIn == "VCO 1 PWM":
			cprint("Connecting VCO1 pwm, function = ", function)
			self.audioPatch.vco1.modSources.pwm = function
		elif patchIn == 'VCO 2':
			cprint("Connecting VCO2, function = ", function)
			self.audioPatch.vco2.modSources.freq = function
		elif patchIn == "VCO 2 SUB":
			cprint("Connecting subVCO2, function = ", function)
			self.audioPatch.sub1vco2.modSources.div = function
			self.audioPatch.sub2vco2.modSources.div = function
		elif patchIn == "VCO 2 PWM":
			cprint("Connecting VCO2 pwm, function = ", function)
			self.audioPatch.vco2.modSources.pwm = function
		elif patchIn == "CUTOFF":
			cprint("Connecting CUTOFF, function = ", function)
			self.audioPatch.vcf.filter.modSources.cutoff = function

	def setVoices(self):
		self.voices.append(self.audioPatch.vco1)
		self.voices.append(self.audioPatch.vco2)
		self.voices.append(self.audioPatch.sub1vco1)
		self.voices.append(self.audioPatch.sub2vco1)
		self.voices.append(self.audioPatch.sub1vco2)
		self.voices.append(self.audioPatch.sub2vco2)
