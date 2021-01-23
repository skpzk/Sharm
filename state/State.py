import configparser

from os.path import join


class StateDict(dict):
	def __init__(self, names=""):
		super().__init__(names)
		self._callbacks = dict()

	def setCallback(self, key, value):
		try:
			self._callbacks[key].append(value)
		except KeyError:
			self._callbacks[key] = [value]

	def __setitem__(self, key, value):
		if key == "":
			key = "dump"
		dict.__setitem__(self, key, value)
		try:
			for callback in self._callbacks[key]:
				callback()
		except KeyError:
			self._callbacks[key] = []


class PatchBayDict(dict):
	def __init__(self, names=""):
		super().__init__(names)
		# print("pbd created")
		self.patchbay = None

	def setCallback(self, patchbay):
		self.patchbay = patchbay

	def callback(self, inpp, value):
		if self.patchbay is not None:
			if value.connect:
				self.patchbay.connect(ppin=inpp, ppout=value.out)
			else:
				self.patchbay.disconnect(ppin=inpp, ppout=value.out)

	def __setitem__(self, key, value):
		# todo : write doc for this function
		key = key.replace(" ", "").lower()
		value.out = value.out.replace(" ", "").lower()
		if value.connect:
			if key in dict.keys(self):
				if isinstance(dict.__getitem__(self, key), list):
					if value.out not in self[key]:
						self[key].append(value.out)
				else:
					dict.__setitem__(self, key, [value.out])
			else:
				dict.__setitem__(self, key, [value.out])
		else:
			# print("disconnect")
			if key in dict.keys(self):
				self[key].remove(value.out)
			if len(self[key]) == 0:
				self.pop(key)

		self.callback(key, value)


class State:
	params = StateDict()

	@staticmethod
	def read():
		path = join("state", "state.sharm")
		state = configparser.ConfigParser()
		state.read(path)
		State.params = StateDict((state['DEFAULT'].items()))
		# print(type(state['DEFAULT'].items()))
		State.guessType()

	@staticmethod
	def guessType():
		for key, value in State.params.items():
			try:
				value = eval(value)
				if key == 'patchbay':
					value = PatchBayDict(value)
			except NameError:
				pass
			except SyntaxError:
				pass
			State.params[key] = value
		try:
			_ = State().params['patchbay']
		except KeyError:
			State().params['patchbay'] = PatchBayDict()
		# print('params inside State : ', State.params)

	@staticmethod
	def save():
		path = join("state", "state.sharm")
		state = configparser.ConfigParser(State.params)
		with open(path, 'w') as f:
			state.write(f)
