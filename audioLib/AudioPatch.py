from audioLib.objects.Env import Env
from audioLib.objects.Clock import Clock

from audioLib.objects.Mixer import Mixer
from audioLib.objects.Patchbay import Patchbay
from audioLib.objects.Rhythm import Rhythm
from audioLib.objects.Sequencer import Sequencer
from audioLib.objects.Vca import Vca
from audioLib.objects.Vco import Vco, Sub1


from audioLib.objects.cython import CFilter

class AudioPatch:
	def __init__(self):

		patchbay = Patchbay()

		vco1 = Vco()
		vco1.stateKeys.freq = "vco1knobfreq"
		vco1.stateKeys.wave = "vco1wave"
		vco1.stateKeys.vcoVolume = "vco1knoblevel"
		vco1.stateKeys.assignvco = "seq1assignvco1"
		vco1.inputs.vco = patchbay.ins.vco1
		vco1.inputs.sub = patchbay.ins.vco1sub
		vco1.inputs.pwm = patchbay.ins.vco1pwm

		vco1sub1 = Sub1()
		vco1sub1.vco = vco1
		vco1sub1.stateKeys.div = "vco1sub1div"
		vco1sub1.stateKeys.sub1level = "vco1sub1knoblevel"
		vco1sub1.stateKeys.assignsub = "seq1assignsub1"

		vco1.inputs.btwpwm = vco1sub1

		vco1sub2 = Sub1()
		vco1sub2.vco = vco1
		vco1sub2.stateKeys.div = "vco1sub2div"
		vco1sub2.stateKeys.sub1level = "vco1sub2knoblevel"
		vco1sub2.stateKeys.assignsub = "seq1assignsub2"


		vco2 = Vco()
		vco2.stateKeys.freq = "vco2knobfreq"
		vco2.stateKeys.wave = "vco2wave"
		vco2.stateKeys.vcoVolume = "vco2knoblevel"
		vco2.stateKeys.assignvco = "seq2assignvco2"
		vco2.inputs.vco = patchbay.ins.vco2
		vco2.inputs.sub = patchbay.ins.vco2sub
		vco2.inputs.pwm = patchbay.ins.vco2pwm

		vco2sub1 = Sub1()
		vco2sub1.vco = vco2
		vco2sub1.stateKeys.div = "vco2sub1div"
		vco2sub1.stateKeys.sub1level = "vco2sub1knoblevel"
		vco2sub1.stateKeys.assignsub = "seq2assignsub1"

		vco2.inputs.btwpwm = vco2sub1

		vco2sub2 = Sub1()
		vco2sub2.vco = vco2
		vco2sub2.stateKeys.div = "vco2sub2div"
		vco2sub2.stateKeys.sub1level = "vco2sub2knoblevel"
		vco2sub2.stateKeys.assignsub = "seq2assignsub2"

		# print(vco1.stateKeys)

		mixer = Mixer()
		mixer.inputs.append(vco1.output)
		mixer.inputs.append(vco2.output)
		mixer.inputs.append(vco1sub1.output)
		mixer.inputs.append(vco1sub2.output)
		mixer.inputs.append(vco2sub1.output)
		mixer.inputs.append(vco2sub2.output)

		patchbay.outs.vco1 = vco1.CVOutput
		patchbay.outs.vco1sub1 = vco1sub1.CVOutput
		patchbay.outs.vco1sub2 = vco1sub2.CVOutput
		patchbay.outs.vco2 = vco2.CVOutput
		patchbay.outs.vco2sub1 = vco2sub1.CVOutput
		patchbay.outs.vco2sub2 = vco2sub2.CVOutput

		filter = CFilter.CVcf()

		vca = Vca()
		vca.inputs.filter = filter
		vca.inputs.sound = mixer

		clock = Clock()
		clock.stateKeys.freq = "tempo"
		patchbay.outs.clock = clock.CVOutput
		clock.inputs.clk = patchbay.ins.clock

		rhythm1 = Rhythm(clock)
		rhythm1.stateKeys.div = "rhythm1"
		rhythm1.inputs.div = patchbay.ins.rhythm1
		rhythm1.colorKnobName = "activerhythm1"


		rhythm2 = Rhythm(clock)
		rhythm2.stateKeys.div = "rhythm2"
		rhythm2.inputs.div = patchbay.ins.rhythm2
		rhythm2.colorKnobName = "activerhythm2"

		rhythm3 = Rhythm(clock)
		rhythm3.stateKeys.div = "rhythm3"
		rhythm3.inputs.div = patchbay.ins.rhythm3
		rhythm3.colorKnobName = "activerhythm3"

		rhythm4 = Rhythm(clock)
		rhythm4.stateKeys.div = "rhythm4"
		rhythm4.inputs.div = patchbay.ins.rhythm4
		rhythm4.colorKnobName = "activerhythm4"

		clock.rhythms.append(rhythm1)
		clock.rhythms.append(rhythm2)
		clock.rhythms.append(rhythm3)
		clock.rhythms.append(rhythm4)

		seq1 = Sequencer()
		seq1.setStateCallbackName("seq1activestep")
		seq1.rhythms.append(rhythm1)
		seq1.rhythms.append(rhythm2)
		seq1.rhythms.append(rhythm3)
		seq1.rhythms.append(rhythm4)
		seq1.stateKeys.step1 = "seq1step1"
		seq1.stateKeys.step2 = "seq1step2"
		seq1.stateKeys.step3 = "seq1step3"
		seq1.stateKeys.step4 = "seq1step4"
		seq1.stateKeys.clk1 = "clk1seq1"
		seq1.stateKeys.clk2 = "clk2seq1"
		seq1.stateKeys.clk3 = "clk3seq1"
		seq1.stateKeys.clk4 = "clk4seq1"

		seq1.inputs.seq = patchbay.ins.seq1

		seq2 = Sequencer()
		seq2.setStateCallbackName("seq2activestep")
		seq2.rhythms.append(rhythm1)
		seq2.rhythms.append(rhythm2)
		seq2.rhythms.append(rhythm3)
		seq2.rhythms.append(rhythm4)
		seq2.stateKeys.step1 = "seq2step1"
		seq2.stateKeys.step2 = "seq2step2"
		seq2.stateKeys.step3 = "seq2step3"
		seq2.stateKeys.step4 = "seq2step4"
		seq2.stateKeys.clk1 = "clk1seq2"
		seq2.stateKeys.clk2 = "clk2seq2"
		seq2.stateKeys.clk3 = "clk3seq2"
		seq2.stateKeys.clk4 = "clk4seq2"

		seq2.inputs.seq = patchbay.ins.seq2

		patchbay.outs.seq1 = seq1.output
		patchbay.outs.seq2 = seq2.output
		patchbay.outs.seq1clk = seq1.CVClockOutput
		patchbay.outs.seq2clk = seq2.CVClockOutput

		vco1.seq = seq1
		vco2.seq = seq2

		clock.seqs.append(seq1)
		clock.seqs.append(seq2)

		vcaEnv = Env()
		vcaEnv.seqs.append(seq1)
		vcaEnv.seqs.append(seq2)
		vcaEnv.stateKeys.a = "enva"
		vcaEnv.stateKeys.d = "envd"
		vcaEnv.inputs.trig = patchbay.ins.trigger

		filterenv = Env()
		filterenv.seqs.append(seq1)
		filterenv.seqs.append(seq2)
		filterenv.stateKeys.a = "filtera"
		filterenv.stateKeys.d = "filterd"

		vca.inputs.env = vcaEnv
		vca.inputs.filterenv = filterenv
		vca.inputs.filterCutoff = patchbay.ins.cutoff

		patchbay.outs.vca = vca.CVOutput
		patchbay.outs.vcaeg = vca.EGOutput
		patchbay.outs.vcfeg = vca.filterEGOutput
		vca.inputs.vca = patchbay.ins.vca

		self.vco = vco1
		self.clock = clock
		self.outputAudioObj = vca
		self.patchbay = patchbay


	def output(self):
		return self.outputAudioObj
