import PySide6.QtWidgets as Qtw

from gui.sections.Section import section
from gui.widgets import Knob

from gui.defs import *
import numpy as np


def createEnvSection():
	box, vbox = section("Env")

	titles = ['A', 'D']
	param = ["enva", "envd"]
	grid = Qtw.QGridLayout()
	for i in range(2):
		knob = Knob.Knob(3, titles[i])

		knob.setStyleSheet(knobDefaultStyleSheet('env'))
		knob.setStateParam(param[i])
		knob.checkState()

		grid.addWidget(knob, i // 2, np.mod(i, 2))
	grid.setContentsMargins(0, 0, 0, 0)
	grid.setSpacing(0)

	vbox.addLayout(grid)

	box.setLayout(vbox)

	return box