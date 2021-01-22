import numpy as np


def ftom(freq):
	"""Convert frequency to midi note"""
	note = 69 + np.log(freq/440) / np.log(np.power(2, 1/12))
	return note


def mtof(note):
	"""Convert midi note to frequency"""
	f = 440 * np.power(np.power(2, (1 / 12)), (note - 69))
	return f


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


def trim(data, lims):
	data = (data > lims[0]) * data + lims[0] * (data <= lims[0])
	data = (data < lims[1]) * data + lims[1] * (data >= lims[1])
	return data


def ssat(data, lim=1. / 16.):
	return (abs(data) <= lim) * data + np.sign(data) * (abs(data) > lim) * lim


def saw(t, shape=1.):  # custom function that behaves essentially like a sine
	""" si t appartient à [0, shape*2pi] et shape != 0
					s = t * 2/(shape*2pi) - 1
			si t appartient à [shape*2pi, 2*pi] et (1-shape) != 0
					s = - (t-shape*2pi) * 2/((1-shape)*2pi) + 1 """
	t = np.mod(t, 2 * np.pi)
	# garder des deux lignes pour la clarte
	# sup = (t*2./((shape*(shape!=0) + (shape==0))*2*np.pi)-1)*(t<=(shape*2*np.pi))
	# sdown = ((t-shape*2*np.pi)*(-2.)/(((1-shape)*((1-shape)!=0) + ((1-shape)==0))*2*np.pi)+1)*
	# ((t-shape*2*np.pi)>0)
	return np.add((t * 2. / ((shape * (shape != 0) + (shape == 0)) * 2 * np.pi) - 1) * (t <= (shape * 2 * np.pi)), (
			(t - shape * 2 * np.pi) * (-2.) / (
				((1 - shape) * ((1 - shape) != 0) + ((1 - shape) == 0)) * 2 * np.pi) + 1) * (
					(t - shape * 2 * np.pi) > 0))


def sqr(t, shape=0.5):
	t = np.mod(t, 2 * np.pi)
	s = 2 * (t <= (shape * 2 * np.pi)) - 1
	return s


