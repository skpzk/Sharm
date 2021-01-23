import numpy as np

cdef extern from "math.h":
	double log(double x)

cdef extern from "math.h":
	double pow(double x, double n)

cdef extern from "math.h":
	double floor(double x)

cdef extern from "math.h":
	double ceil(double x)

cdef extern from "math.h":
	double fabs(double x)

def mtof(note):
	cdef int i
	cdef double[:] freq
	freq = note
	for i in range(len(note)):
		freq[i] = 440 * ((2 ** (1/12)) ** (freq[i] - 69))
	return np.array(freq)

def ftom(freq):
	cdef int i
	cdef double[:] note
	note = freq[:]
	for i in range(len(note)):
		note[i] = 69 + np.log(note[i]/440) / np.log(np.power(2, 1/12))
	return np.array(note)

def mtof2D(note):
	cdef int i
	cdef double[:] freq
	freq = note[:, 0]
	for i in range(len(note)):
		freq[i] = 440 * ((2 ** (1/12)) ** (freq[i] - 69))
	return np.expand_dims(np.array(freq), axis=1)

def ftom2D(freq):
	cdef int i
	cdef double[:] note
	note = freq[:, 0]
	for i in range(len(note)):
		note[i] = 69 + np.log(note[i]/440) / np.log(np.power(2, 1/12))
	return np.expand_dims(np.array(note), axis=1)

cdef double ETConst = pow(2., 1./12.)
#print("EtConst = ", ETConst)
cdef double midiA440 = 69.

def add_freq_and_note2D(freq, note):
	cdef double logETConst = np.log(ETConst)
	cdef double logETConstInv = 1./np.log(ETConst)
	cdef double freqInv = 1./440.
	cdef double A440 = 440.
	cdef int i
	cdef double[:] cnote, cout, cfreq
#	cdef double[:] cfreq
	cnote = note[:, 0]
	cfreq = freq[:, 0]
	cout = freq[:, 0]
	for i in range(len(cfreq)):
		cout[i] = A440 * pow(ETConst, ( log(cfreq[i] * freqInv) * logETConstInv + cnote[i]) )
#		print(cout[i])
	return np.expand_dims(np.array(cout), axis=1)



def add_freq_note_and_range2D(freq, note, rangeValue):
#	cdef double[:] cfreq
	cdef double logETConst = np.log(ETConst)
	cdef double logETConstInv = 1./np.log(ETConst)
	cdef double freqInv = 1./440.
	cdef double A440 = 440.
	cdef int i
	cdef double[:] cnote, cfreq
	cnote = note[:, 0]
	cfreq = freq[:, 0]

	for i in range(len(cfreq)):
		cnote[i] = 1 * (cnote[i] >= 1) - 1 * (cnote[i] <= -1) + cnote[i] * (cnote[i] > -1) * (cnote[i] < 1)
		cfreq[i] = A440 * pow(ETConst, ( log(cfreq[i] * freqInv) * logETConstInv + cnote[i] * rangeValue) )
#		print(cout[i])
#		pass
#	return np.expand_dims(np.array(cout), axis=1)


def quantize2D(freq, value):
	cdef double logETConst = np.log(ETConst)
	cdef double logETConstInv = 1./np.log(ETConst)
	cdef double freqInv = 1./440.
	cdef double A440 = 440.
	# value : 0 = 12ET, 1 = 8ET, 2 = 12JI, 2 = 8JI
	cdef float[8] ratios8JI = [1, 9./8, 5./4, 4./3, 3./2, 5./3, 15./8, 2]
	cdef float[13] ratios12JI = [1., 16./15, 9./8, 6./5, 5./4, 4./3, 45./32, 3./2, 8./5, 5./3, 9./5, 15./8, 2]
	cdef int[8] notes8ET = [0, 2, 4, 5, 7, 9, 11, 12]
	cdef int i, j, quant, position, note, scaled
	cdef double[:] cfreq
	cdef double baseA, scaledFreq
	# ratios are already sorted
	cfreq = freq[:, 0]
	quant = value
	if quant == 0:
		for i in range(len(cfreq)):
			cfreq[i] = A440 * pow(ETConst, int(log(cfreq[i] * freqInv) * logETConstInv))
	if quant == 1:
		for i in range(len(cfreq)):
			note = (int(log(cfreq[i] * freqInv) * logETConstInv + 69) - 69)
			position = note % 12
			scaled = 0
			for j in range(len(notes8ET) - 1):
				if (position >= notes8ET[j]) and (position < notes8ET[j+1]):
					scaled = notes8ET[j]
					break
			scaled = note - position + scaled # ref A
			cfreq[i] = A440 * pow(ETConst, scaled)
	if quant == 2:
		for i in range(len(cfreq)):
			# find closest A
#			if cfeq[i] == 0:
#				print("cfreq[i] == 0 for some reason")
#			print("ceil(440. / cfreq[i]) = ", ceil(440. / cfreq[i]))
#			baseA = (((cfreq[i] >= 440.) * floor(cfreq[i]  / 440.) + (cfreq[i] < 440.) * 1. / ceil(440. / cfreq[i])))*440
#			print(baseA)
#			print("negative power : ", pow(2, -1))
			baseA = 440 * pow(2, floor(log(cfreq[i] / 440) / log(2)))
#			print(baseA)
			# find closest ratio
			scaledFreq = baseA * 2
#			j = 0
#			print("len ratios   = ", len(ratios12JI))
#			print("range ratios = ", range(len(ratios12JI) - 1))
			for j in range(len(ratios12JI) - 1):
#				print("j = ", j)
#				print("freq = ", cfreq[i])#, end="")
#				print(", j = ", j)#, end="")
#				print(", ratios = %.2f, %.2f" %(ratios12JI[j], ratios12JI[j+1]))#, end="")
#				print(", distance down = % 3.2f" % fabs(cfreq[i] - ratios12JI[j] * baseA))#, end="")
#				print(", distance up = % 3.2f" % fabs(cfreq[i] - ratios12JI[j+1] * baseA))
				if fabs(cfreq[i] - ratios12JI[j] * baseA) <= fabs(cfreq[i] - ratios12JI[j+1] * baseA):
#					print("closest match : ", ratios12JI[j])
					scaledFreq = ratios12JI[j] * baseA
#					print("scaled freq = ", scaledFreq)
					break
			cfreq[i] = scaledFreq
	if quant == 3:
		for i in range(len(cfreq)):
			# find closest A
#			baseA = (((cfreq[i] >= 440.) * floor(cfreq[i]  / 440.) + (cfreq[i] < 440.) * 1. / ceil(440. / cfreq[i])))*440
			baseA = 440 * pow(2, floor(log(cfreq[i] / 440) / log(2)))
#			print(baseA)
			# find closest ratio
#			scaledFreq = 440
			scaledFreq = baseA * 2
			for j in range(len(ratios12JI) - 1):
				if fabs(cfreq[i] - ratios8JI[j] * baseA) <= fabs(cfreq[i] - ratios8JI[j+1] * baseA):
					scaledFreq = ratios8JI[j] * baseA
					break
			cfreq[i] = scaledFreq

	return np.expand_dims(np.array(cfreq), axis=1)
