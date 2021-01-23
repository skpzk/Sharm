import PySide6.QtWidgets as Qtw
from PySide6 import QtCore

from gui.sections.Section import section
from gui.widgets import Knob, SectionLabel

from gui.defs import *
from state.State import State


def createSequencerSections(seqID, parent):
	# there is a bug : the number seqID is not printed if there are no trailing spaces (at least 2)
	box, vbox = section("Sequencer " + str(seqID) + "  ")


	hbox = Qtw.QHBoxLayout()

	for i in range(4):
		knob = Knob.Knob(3, "Step" + str(i + 1))

		knob.setStyleSheet(knobDefaultStyleSheet('seq'))
		knob.setMinimum(-127)

		knob.setStateParam("seq" + str(seqID) + "step" + str(i + 1))
		knob.checkState()

		knob.seq = "seq" + str(seqID)
		State.params.setCallback("seq" + str(seqID) + "activestep", knob.sequencerCallback)

		hbox.addWidget(knob)
	layoutConf(hbox)

	vbox.addLayout(hbox)
	layoutConf(vbox)
	box.setLayout(vbox)
	return box


