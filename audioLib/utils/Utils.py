import numpy as np

from audioLib.AudioConst import AudioConst
from audioLib.utils.Scales import Scale

etConst = 2**(1/12)
logEtConst = np.log(etConst)
logEtConstInv = 1 / np.log(etConst)

def logtof(note):
	"""Convert log note to frequency"""
	# return const ^ (note)
	return np.power(etConst, note)

def ftolog(freq):
	# remove references to midi numbers, most of the time it is not needed
	"""Convert frequency to log note"""
	# return log(freq)/logconst
	return np.multiply(np.log(freq), logEtConstInv)

def ftom(freq):
	"""Convert frequency to midi note"""
	note = 69 + np.log(freq/440) / np.log(np.power(2, 1/12))
	return note


def mtof(note):
	"""Convert midi note to frequency"""
	f = 440 * np.power(np.power(2, (1 / 12)), (note - 69))
	return f

def ftom8(freq):
	"""Convert frequency to midi note (8 equal steps)"""
	note = 69 + np.log(freq/440) / np.log(np.power(2, 1/8))
	return note

def mtof8(note):
	"""Convert midi note to frequency (8 equal steps)"""
	f = 440 * np.power(np.power(2, (1 / 12)), (note - 69))
	return f

def ftomDiat(freq):
	"""Convert frequency to midi note (diatonic scale)"""
	# print("freq shape before :", freq.shape)
	note = (69 + np.log(freq/440) / np.log(np.power(2, 1/12))).astype('int')
	if note.ndim > 1:
		note = note[:, 0]
	# print("note shape before :", note.shape)
	note = Scale("major").applyScale(note)
	# note = np.expand_dims(note, axis=1)
	# print("note shape after  :", np.transpose(note).shape)
	return note

def mtofDiat(note):
	"""Convert midi note to frequency (diatonic scale)"""
	return np.transpose(mtof(note))

def find_nearest(array, value):
	array = np.asarray(array)
	# print("array.shape:", array.shape)
	# print("array = ", array)

	idx = (np.abs(array - value)).argmin(1)

	# print("idx = ", idx)

	# print("idx shape before", idx.shape)

	idx = np.expand_dims(idx, axis=1)
	# print("idx shape after", idx.shape)

	retValue = np.take_along_axis(array, idx, 1)

	# print("retvalue", retValue.shape)

	return retValue

def quantJI(freq, scale="chromatic"):
	"""
		using asymetric scale from : https://en.wikipedia.org/wiki/Just_intonation
		A 		E 		B 		F♯
		5:3 	5:4 	15:8 	45:32
		F 		C 		G 		D
		4:3 	1:1 	3:2 	9:8
		D♭ 		A♭ 		E♭ 		B♭
		16:15 	8:5 	6:5 	9:5
		"""

	if scale not in ["chromatic", "diatonic"]:
		print("wrong scale")
		scale = "chromatic"

	if scale=="chromatic":
		ratios = np.array([5 / 3, 5 / 4, 15 / 8, 45 / 32, 4 / 3, 1, 3 / 2, 9 / 8, 16 / 15, 8 / 5, 6 / 5, 9 / 5])
	else:
		ratios = np.array([1, 9/8, 5/4, 4/3, 3/2, 5/3, 15/8])
	ratios.sort()

	# find the closest A frequence under freq
	baseratio = (freq >= 440) * np.floor(freq / 440) + (freq < 440) * 1 / np.ceil(440 / freq)
	# print("baseratio.shape()", baseratio.shape)
	# baseratio = np.expand_dims(baseratio, axis=1)
	# print("baseratio.shape()", baseratio.shape)

	ratios = np.expand_dims(ratios, axis=0)
	# print("ratios shape :", ratios.shape)

	quantfreq = find_nearest(440 * baseratio * ratios, freq)
	return quantfreq

def quant12JI(freq):
	return quantJI(freq, "chromatic")

def quant8JI(freq):
	return quantJI(freq, "diatonic")


def simpleNotesList():
	return ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']


def simpleNoteDict():
	d = dict()
	notes = simpleNotesList()
	for i in range(len(notes)):
		d[notes[i]] = i + 69
	return d


def notesList():
	names = simpleNotesList()
	namesList = []
	for i in range(128):
		name = names[np.mod(i-69, 12)] + str(i//12 - 1)
		namesList.append(name)
	return namesList


def ssat(data, lim=1. / 16.):
	return (abs(data) <= lim) * data + np.sign(data) * (abs(data) > lim) * lim

def cum_reset_np(v):
	"""
	thanks piRSquared at : https://stackoverflow.com/questions/43524997/cumsum-entire-table-and-reset-at-zero
	"""
	z = np.zeros_like(v)
	i = np.where(v)
	r = np.arange(1, len(i[0]) + 1)
	p = np.where(np.append(False, (np.diff(i) != 1)))[0]
	b = np.append(0, np.append(p, r.size))
	z[i] = r - b[:-1].repeat(np.diff(b))
	return z

def emptyChunk():
	return np.expand_dims(np.zeros(AudioConst.CHUNK), axis=1)

def empty1DChunk():
	return np.zeros(AudioConst.CHUNK)

def emptyIntChunk():
	return np.expand_dims(np.zeros(AudioConst.CHUNK, dtype='int'), axis=1)

if __name__ == "__main__":
	# freqs = np.linspace(440, 880, 10)
	# Equal temperament :
	freqs = 440 * np.logspace(0, 12, num=5, base=np.power(2, 1/12))

	print(freqs)
	freqs = np.expand_dims(freqs, axis=1)
	# quant12JI(np.array([110, 220, 440, 880, 1760]))
	print("final result : ", quant12JI(freqs).shape)
	# print(quant8JI(freqs))
	# quant12JI(np.array([440, 459]))
