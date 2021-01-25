from audioLib.Audio import Audio

from audioLib.AudioPatch import AudioPatch
from state.State import State


class Sharm:
	def __init__(self):

		State().read()

		self.audio = Audio()

		audioPatch = AudioPatch()
		self.audioPatch = audioPatch
		self.audio.setAudioObject(audioPatch.output())
		self.audio.setClock(audioPatch.clock)

		State().params['patchbay'].setCallback(audioPatch.patchbay)

	def close(self):
		State().save()
		self.audio.stop()

		# return self.audio.T
