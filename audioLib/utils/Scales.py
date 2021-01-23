import numpy as np


def find_nearest(array, value):
	array = np.asarray(array)

	idx = np.expand_dims((np.abs(array - value)).argmin(0), axis=0)

	return np.take_along_axis(array, idx, 0)


class Scale:
	def __init__(self, scale="chromatic"):
		# pass
		self.scalesDict = dict()
		self.setScalesDict()

		self.tonic = 69

		self.currentScale = list(self.scalesDict.values())[0]
		self.currentScaleName = list(self.scalesDict.keys())[0]
		self.setScale(scale)

	def setScale(self, scale: str):
		try:
			self.currentScale = self.scalesDict[scale]
			self.currentScaleName = scale
		except KeyError:
			print("Invalid scale name")
			self.setScale("chromatic")

	def setScalesDict(self):
		self.scalesDict["chromatic"] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
		self.scalesDict["major"] = [0, 2, 4, 5, 7, 9, 11]
		self.scalesDict["minorHarm"] = [0, 2, 3, 5, 7, 8, 11]
		self.scalesDict["minorMelUp"] = [0, 2, 3, 5, 7, 9, 11]
		self.scalesDict["minorMelDown"] = [0, 2, 3, 5, 7, 8, 10]
		self.scalesDict["minorPenta"] = [0, 3, 5, 7, 10]
		self.scalesDict["majorPenta"] = [0, 2, 4, 7, 9]
		self.scalesDict["Ambassel"] = [0, 1, 5, 7, 8]
		# cf https://www.benicinia.com/2018/12/ethiopian-traditional-musical-scales.html
		self.scalesDict["exotic1"] = [0, 1, 3, 6, 7, 8, 11]
		self.scalesDict["exotic2"] = [0, 2, 4, 6, 8, 10]
		self.scalesDict["japanese"] = [0, 1, 5, 7, 8]
		self.scalesDict["octatonic"] = [0, 2, 3, 5, 6, 8, 9, 11]
		self.scalesDict["wholeTone"] = [0, 2, 4, 6, 8, 10]
		# scales from volca modular
		self.scalesDict["thirdMode"] = [0, 2, 3, 4, 6, 7, 8, 10, 11]
		self.scalesDict["fourthMode"] = [0, 1, 2, 5, 6, 7, 8, 11]
		self.scalesDict["fifthMode"] = [0, 1, 5, 6, 7, 11]
		self.scalesDict["sixthMode"] = [0, 2, 4, 5, 6, 8, 10, 11]
		self.scalesDict["seventhMode"] = [0, 1, 2, 3, 5, 6, 7, 8, 9, 11]
		# Messiaen modes

	def setTonic(self, midinote):
		self.tonic = midinote

	def applyScale(self, note):
		position = np.mod(note - self.tonic, 12)
		position = note - position

		scale = np.expand_dims(self.currentScale, 1)

		array = np.repeat(scale, note.shape[0], axis=1)
		array = array + position

		scaledNote = find_nearest(array, note)

		return scaledNote

if __name__ == "__main__":
	scale = Scale("major")
	notes = np.array(np.arange(10) +  60)
	print(notes)
	print(scale.applyScale(notes))
