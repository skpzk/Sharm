"""
	useful resources :
		https://www.w3.org/2011/audio/audio-eq-cookbook.html
		https://arachnoid.com/BiQuadDesigner/

		https://en.wikipedia.org/wiki/Digital_biquad_filter
		https://en.wikibooks.org/wiki/Digital_Signal_Processing/IIR_Filter_Design#Chain_of_Second_Order_Sections

"""

from AudioLib import Env
from AudioLib.ModSources import ModSources
from AudioLib.Utils import *
from AudioLib.Audio import AudioConstTest as AudioConst
from Dev.DebugUtils import *


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


class Lpf(AudioConst):
	def __init__(self):
		super().__init__()
		self.fc = 220
		self.Q = 0
		self.Qinv = 0
		self.coefs = Coefs(self.CHUNK)
		self.state = State()
		self.T = 1 / self.RATE
		self._egAmount = 1
		self.limitFc = self.RATE/2
		self.env = Env.EnvAD()
		self.modSources = ModSources([('cutoff', 0)])

		self.updateQ(1)

	def __call__(self, inbuffer):
		outbuffer = self.applyFilter(inbuffer)

		return outbuffer

	def on(self):
		self.env.on()

	@property
	def eg(self):
		return self._egAmount

	@eg.setter
	def eg(self, eg):
		self._egAmount = eg

	@property
	def a(self):
		return self.env.a

	@a.setter
	def a(self, a):
		self.env.a = a

	@property
	def d(self):
		return self.env.d

	@d.setter
	def d(self, d):
		self.env.d = d

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

	def getNotesMod(self, bypassCall):
		notes = np.zeros(self.CHUNK)
		if not bypassCall:
			# the output of f should be btw 1 and -1
			# it changes the frequency by +/- 5 oct
			notes = self.modSources.cutoff()
			# cprint("notes : ", notes)
			notes = notes * 12 * 5
			# cprint("Max notes = ", np.max(notes))
		notes = notes
		return notes

	def applyFilter(self, inbuffer):
		outbuffer = []

		env = self.env() * self._egAmount

		notes = self.getNotesMod(False)
		fc = self.fc + env * 200
		fc = mtof(ftom(fc) + notes)
		# cprint("Max fc before limits", np.max(fc))
		fc = (fc < self.limitFc) * fc + self.limitFc * (fc >= self.limitFc)
		# cprint("Max fc after  limits", np.max(fc))
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


class Vcf(AudioConst):
	def __init__(self):
		self.callsList = []

		self.filter = Lpf()

	def __call__(self):
		data = np.zeros(self.CHUNK)
		for call in self.callsList:
			# print(call)
			data += call()  # call voices
		data = self.filter(data)

		return ssat(data)

	def on(self):
		self.filter.on()

	@property
	def eg(self):
		return self.filter.eg

	@eg.setter
	def eg(self, eg):
		self.filter.eg = eg

	@property
	def a(self):
		return self.filter.a

	@a.setter
	def a(self, a):
		self.filter.a = a

	@property
	def d(self):
		return self.filter.d

	@d.setter
	def d(self, d):
		self.filter.d = d

	@property
	def fc(self):
		return self.filter.fc

	@fc.setter
	def fc(self, fc):
		self.filter.updateMidiFc(fc)

	@property
	def Q(self):
		return self.filter.Q

	@Q.setter
	def Q(self, q):
		self.filter.updateQ(q)

	def setFc(self, fc):
		self.fc = fc

	def setQ(self, q):
		self.Q = q

	def setA(self, a):
		self.a = a

	def setD(self, d):
		self.d = d

	def setEg(self, eg):
		self.eg = eg
