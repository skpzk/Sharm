import PySide6.QtWidgets as Qtw

from gui.sections.Section import section
from gui.widgets import Knob

from gui.defs import *
from gui.widgets.Buttons import Button
from state.State import State


def createRhythmSection():
	box, vbox = section("Rhythm")

	hbox = Qtw.QHBoxLayout()
	for i in range(4):
		knob = Knob.Knob(3, "Clk" + str(i + 1))

		knob.setStyleSheet(knobDefaultStyleSheet('rhythm'))
		knob.setMaximum(16)
		knob.setMinimum(1)
		knob.relativeSize = 1

		knob.setStateParam("rhythm"+str(i + 1))
		State.params.setCallback("activerhythm" + str(i+1), knob.sequencerCallback)

		knob.checkState()

		hbox.addWidget(knob)
	hbox.setContentsMargins(0, 0, 0, 0)
	hbox.setSpacing(0)

	vbox.setContentsMargins(0, 0, 0, 0)
	vbox.setSpacing(0)
	# widget = QtW.QWidget()
	# widget.setLayout(hbox)
	vbox.addLayout(hbox)
	# widget.setContentsMargins(0, 0, 0, 0)

	# widget2 = QtW.QWidget()
	grid = Qtw.QGridLayout()

	for i in range(8):
		title = "Seq" + str(i // 4 + 1)

		# button = QtW.QPushButton(title)
		button = Button(title)
		button.setCheckable(True)
		# button.setFlat(True)
		# button = Q
		button.setStyleSheet(buttonDefaultStyleSheet())

		stateParam = "clk" + str((i%4) + 1) + title

		button.setStateParam(stateParam)
		button.checkState()

		grid.addWidget(button, i // 4, i % 4)

	grid.setContentsMargins(5, 10, 5, 0)
	grid.setSpacing(10)
	# widget2.setLayout(grid)
	vbox.addLayout(grid)
	# widget2.setContentsMargins(0, 0, 0, 0)
	vbox.addWidget(Qtw.QLabel())

	vbox.setStretch(1, 1)
	vbox.setStretch(2, 1)
	# vbox.setStretch(2, 1)

	box.setLayout(vbox)

	return box