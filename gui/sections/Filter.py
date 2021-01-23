import PySide6.QtWidgets as Qtw

from gui.sections.Section import section
from gui.widgets import Knob

from gui.defs import *
import numpy as np


def createFilterSection():
	box = Qtw.QGroupBox("Filter")
	box, vbox = section("Filter")

	titles = ["Reso", "EG Amount", "A", "D"]
	hbox = Qtw.QHBoxLayout()

	knob = Knob.Knob(3, "Cutoff")

	knob.setStyleSheet(knobDefaultStyleSheet('filter'))
	knob.checkState()

	hbox.addWidget(knob)

	grid = Qtw.QGridLayout()
	widget = Qtw.QWidget()

	params = ["reso", "egamount", "filtera", "filterd"]

	for i in range(4):
		knob = Knob.Knob(3, titles[i])

		knob.setStyleSheet(knobDefaultStyleSheet('filter'))

		if i == 1:
			knob.setMinimum(-127)
		knob.setStateParam(params[i])
		knob.checkState()

		# grid.addWidget(knob, i // 2, np.mod(i, 2))
		hbox.addWidget(knob)

	grid.setContentsMargins(0, 0, 0, 0)
	grid.setVerticalSpacing(0)
	grid.setHorizontalSpacing(0)
	# widget.setLayout(grid)
	# hbox.addWidget(widget)
	hbox.setContentsMargins(0, 0, 0, 0)
	hbox.setSpacing(0)

	# hbox.setStretch(0, 1)
	# hbox.setStretch(1, 3)

	vbox.addLayout(hbox)

	box.setLayout(vbox)
	return box