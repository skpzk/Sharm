# distutils: language = c++

import numpy as np

from cpython cimport array
import array

from audioLib.utils.Utils import *
from audioLib.AudioConst import AudioConst
from audioLib.objects.AudioObject import AudioObject

from state.State import State

from time import time


cdef class Input:
	cdef double[:] data
	def __init__(self, defaultValue):
		self.data = np.ones(AudioConst.CHUNK) * defaultValue
#		self.callback = None

	cdef public output(self, out):
		out[:] = self.data

cdef class Inputs:
#	cdef double[:] sound, env
	cdef public Input sound, env
	def __init__(self):
		self.sound = Input(0)
		self.env = Input(1)

#	def setSoundInput(self, sound):
#		self.sound = sound

cdef class Coefs:
	cdef double[:] a1, a2, b0, b1, b2
	def __init__(self):
		self.a1 = empty1DChunk()
		self.a2 = empty1DChunk()
		self.b0 = empty1DChunk()
		self.b1 = empty1DChunk()
		self.b2 = empty1DChunk()

cdef class FilterState:
	cdef double xn1, xn2, yn1, yn2

	def __init__(self):
		self.xn1 = 0
		self.xn2 = 0
		self.yn1 = 0
		self.yn2 = 0

	def update(self, x, y):
		self.xn2 = self.xn1
		self.yn2 = self.yn1
		self.xn1 = x
		self.yn1 = y


cdef class CVcf:
	cdef double[:] inBuffer, env
	cdef double knobCutoff, Qinv, knobEgAmount, T
	cdef public Inputs inputs
	cdef FilterState state
	cdef Coefs coefs

	def __init__(self):
#		print("CVcf __init__() method")
		self.knobCutoff = 0
		self.Qinv = .707
		self.knobEgAmount = 0
		self.T = 1 / AudioConst.RATE

		self.inputs = Inputs()

		self.env = empty1DChunk()
		self.inBuffer = empty1DChunk()

		self.state = FilterState()
		self.coefs = Coefs()

	def setKnobCutoff(self, cutoff):
		self.knobCutoff = cutoff

#		self.ca = array.array('d', np.zeros(AudioConst.CHUNK))
	def setSoundInput(self, sound):
		self.inputs.setSoundInput(sound)

	def checkValues(self):
		try:
			knobCutoff = np.clip(State.params['cutoff'], 0, 1)
			# 20Hz - > 20kHz
			# todo : replace this with faster cython function
			self.knobCutoff = mtof(ftom(20) + (ftom(20000) - ftom(20)) * knobCutoff)
		except KeyError:
			pass
		try:
			knobReso = np.clip(State.params['reso'], 0, 1)
			knobReso = knobReso * 5 + .1
			self.Qinv = 1/knobReso
		except KeyError:
			pass
		try:
			self.knobEgAmount = np.clip(State.params['egamount'], -1, 1)
		except KeyError:
			pass

	def computeValues(self, cvCutoff):
		fc = np.ones(AudioConst.CHUNK) * self.knobCutoff
		# todo : replace this with faster cython function
		fc = mtof( ftom(fc) + np.multiply(self.env,self.knobEgAmount * 4 * 12))
#		print("fc = ", fc)
		fc = mtof( ftom(fc) + np.multiply(cvCutoff, 5 * 12))
		fc = np.clip(fc, 0, AudioConst.RATE/2)
		self.computeCoefsFasterArray(fc)

	def computeCoefsFasterArray(self, fc):
		# print("type fc = ", type(fc))
		w0 = 2 * np.pi * fc * self.T

		# protection against self.Q = 0 done when updating Q

		a0 = 1 + np.sin(w0) * .5 * self.Qinv
		a0inv = 1. / a0
		# a0 never equals 0 as long as fc <= samplerate/2

		cosw0 = np.cos(w0)

		b1 = np.multiply((1 - cosw0), .5 * a0inv)

		self.coefs.b0 = b1
		self.coefs.b1 = b1 * 2
		self.coefs.b2 = b1

		self.coefs.a1 = np.multiply(-2 * cosw0, a0inv)
		self.coefs.a2 = np.multiply((2 - a0), a0inv)

	def filter(self, out):
		# warning: Index should be typed for more efficient access
		# the following line prevents from the warning
		cdef int i

		for i in range(AudioConst.CHUNK):

#			sample = inbuf[i] * b0[i] + b1[i] * xn1 + b2[i] * xn2 - a1[i] * yn1 - a2[i] * yn2
			sample = self.inBuffer[i] * self.coefs.b0[i] + self.coefs.b1[i] * self.state.xn1 + self.coefs.b2[i] * self.state.xn2 \
				- self.coefs.a1[i] * self.state.yn1	- self.coefs.a2[i] * self.state.yn2
			sample = 1 * (sample >= 1) - 1 * (sample <= -1) + sample * (sample > -1) * (sample < 1)
			self.state.update(self.inBuffer[i], sample)

			out[i, 0] = sample

		# print("c = ", self.c)

#		self.state.update(xn1, yn1)
#		self.state.update(self.inBuffer[-1], sample)



	def output(self, out: np.ndarray, inbuf: np.ndarray, env: np.ndarray, cvCutoff: np.ndarray) -> None:
		# check ctrl panel inputs
		self.inBuffer = inbuf
		self.checkValues()

		self.env = env

		# filter the sound
		self.computeValues(cvCutoff)
		self.filter(out)
