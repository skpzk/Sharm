import PySide6.QtWidgets as Qtw

from gui.sections.Section import section
from gui.widgets import Knob

from gui.defs import *
from state.State import State


def createGeneralSection():
	box, vbox = section("General")
	titles = ["Vol", "Tempo"]
	hbox = Qtw.QHBoxLayout()
	for i in range(2):
		knob = Knob.Knob(3, titles[i])

		knob.setStyleSheet(knobDefaultStyleSheet('general'))
		knob.checkState()
		if titles[i] == "Tempo":
			State.params.setCallback("activetempo", knob.sequencerCallback)

		hbox.addWidget(knob)
	hbox.setContentsMargins(0, 0, 0, 0)
	hbox.setSpacing(0)

	vbox.addLayout(hbox)
	box.setLayout(vbox)
	return box
