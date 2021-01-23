import PySide6.QtWidgets as Qtw

from gui.defs import *
from gui.sections.Section import section

from gui.widgets.Buttons import Button
from gui.widgets.HoldButton import HoldButton


def createTransportSection():
	box, vbox = section("Transport")

	hbox1 = Qtw.QHBoxLayout()
	hbox2 = Qtw.QHBoxLayout()
	titles = [["Reset", "EG", "Next"], ["Play", "Trigger"]]
	hboxes = [hbox1, hbox2]

	for j in range(2):
		for title in titles[j]:

			if title != "EG":
				button = Button(title)
			else:
				button = HoldButton(title)
			if title not in ["Trigger", "Reset", "Next"]:
				button.setCheckable(True)
			if title == "Trigger":
				button.clicked.disconnect(button.warnState)
				button.pressed.connect(button.warnStatePressed)
			if title == "Reset":
				# button.clicked.disconnect(button.warnState)
				button.pressed.connect(button.warnStatePressed)
			# button.setFlat(True)
			# button = Q
			button.setStyleSheet(buttonDefaultStyleSheet())
			stateParam = title

			button.setStateParam(stateParam)
			button.checkState()

			hboxes[j].addWidget(button)

	vbox.addLayout(hbox1)
	vbox.addLayout(hbox2)

	hbox1.setSpacing(10)
	hbox2.setSpacing(10)
	hbox1.setContentsMargins(5, 10, 5, 10)
	hbox2.setContentsMargins(5, 0, 5, 5)

	box.setLayout(vbox)
	return box
