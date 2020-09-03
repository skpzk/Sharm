"""
	useful resources :
		https://www.w3.org/2011/audio/audio-eq-cookbook.html
		https://arachnoid.com/BiQuadDesigner/

		https://en.wikipedia.org/wiki/Digital_biquad_filter
		https://en.wikibooks.org/wiki/Digital_Signal_Processing/IIR_Filter_Design#Chain_of_Second_Order_Sections

"""

from AudioLib import Audio, Env
from AudioLib.Utils import *


class Coefs:
	def __init__(self, chunk):
		self.a1 = np.zeros(chunk)
		self.a2 = np.zeros(chunk)
		self.b0 = np.zeros(chunk)
		self.b1 = np.zeros(chunk)
		self.b2 = np.zeros(chunk)


class State:
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


class Lpf:
	def __init__(self, audioConst, fc=220, Q=1):
		self.fc = fc
		self.Q = 0
		self.Qinv = 0
		self.coefs = Coefs(audioConst.CHUNK)
		self.state = State()
		self.T = 1 / audioConst.RATE
		self.audio = audioConst
		self.egAmount = 1
		self.limitFc = audioConst.RATE/2
		self.env = Env.EnvAD(audioConst)

		self.updateQ(Q)

	def __call__(self, inbuffer):
		outbuffer = self.applyFilter(inbuffer)

		return outbuffer

	def on(self):
		self.env.on()

	def setEG(self, eg):
		self.egAmount = eg

	def setA(self, a):
		self.env.setA(a)

	def setD(self, d):
		self.env.setD(d)

	def computeCoefsFaster(self):
		w0 = 2 * np.pi * self.fc * self.T

		# protection against self.Q done when updating Q

		a0 = 1 + np.sin(w0) * .5 * self.Qinv
		a0inv = 1. / a0
		# a0 never equals 0 as long as fc <= samplerate/2

		cosw0 = np.cos(w0)

		b1 = (1 - cosw0) * .5 * a0inv

		self.coefs.b0 = b1
		self.coefs.b1 = b1 * 2
		self.coefs.b2 = b1

		self.coefs.a1 = -2 * cosw0 * a0inv
		self.coefs.a2 = (2 - a0) * a0inv

	def computeCoefsFasterArray(self, fc):
		w0 = 2 * np.pi * fc * self.T

		# protection against self.Q done when updating Q

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

	def applyFilter(self, inbuffer):
		outbuffer = []

		env = self.env() * self.egAmount

		fc = self.fc + env * 200
		fc = (fc < self.limitFc) * fc + self.limitFc * (fc >= self.limitFc)
		self.computeCoefsFasterArray(fc)
		for i in range(len(inbuffer)):
			out = inbuffer[i] * self.coefs.b0[i] + self.coefs.b1[i] * self.state.xn1 + self.coefs.b2[i] * self.state.xn2 \
			    - self.coefs.a1[i] * self.state.yn1 - self.coefs.a2[i] * self.state.yn2

			self.state.update(inbuffer[i], out)
			outbuffer.append(out)

		return np.array(outbuffer)

	def updateFc(self, fc):
		self.updateFcFaster(fc)

	def updateFcFaster(self, fc):
		self.fc = (fc < self.limitFc) * fc + self.limitFc * (fc >= self.limitFc)
		self.computeCoefsFaster()

	def updateMidiFc(self, note):
		note = int(note)
		fc = mtof(note)
		if fc != self.fc:
			self.fc = fc
			self.computeCoefsFaster()

	def updateQ(self, Q):
		self.Q = Q
		if self.Q == 0:
			self.Q = 1e-9

		self.Qinv = 1./self.Q


class Vcf:
	def __init__(self, audioConst):
		self.chunk = audioConst.CHUNK
		self.rate = audioConst.RATE
		self.callsList = []

		self.filter = Lpf(audioConst)

	def __call__(self):
		data = np.zeros(self.chunk)
		for call in self.callsList:
			# print(call)
			data += call()  # call voices
		data = self.filter(data)

		return Audio.ssat(data)

	def on(self):
		self.filter.on()

	def setEG(self, eg):
		self.filter.setEG(eg)

	def setA(self, a):
		self.filter.setA(a)

	def setD(self, d):
		self.filter.setD(d)

	def updateFc(self, fc):
		self.filter.updateMidiFc(fc)

	def updateQ(self, q):
		self.filter.updateQ(q)
