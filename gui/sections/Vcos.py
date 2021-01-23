import PySide6.QtWidgets as Qtw
import numpy as np

from PySide6 import QtCore

from gui.widgets import Knob, Radio, SectionLabel, WaveSlider

from gui.defs import *
from gui.widgets.Buttons import Button





def secondLine():
	"""first knob line"""
	hbox = Qtw.QHBoxLayout()

	layoutConf(hbox)

	slider = WaveSlider.WaveSlider(5)
	slider.setValue(4)
	slider.setStateParam("vco1wave")
	slider.checkState()

	hbox.addWidget(slider)

	knob = Knob.Knob(3, "Vco1")
	knob.sizeType = 2
	knob.setStyleSheet(knobDefaultStyleSheet('vco1'))
	knob.setStateParam("vco1knobfreq")
	knob.checkState()



	hbox.addWidget(knob)

	vboxrange = Qtw.QVBoxLayout()
	layoutConf(vboxrange)

	ranges = [5, 2, 1]
	rangeRadio = ""
	vboxrange.addStretch(1)

	rangeGroup = Qtw.QWidget()
	rangeGroup.setContentsMargins(0, 0, 0, 0)

	for i in range(3):
		rangeRadio = Radio.Radio("±%d" % ranges[i], i)
		# rangeRadio = Qtw.QRadioButton("±%d" % ranges[i])
		rangeRadio.setStateParam('rangeradio')
		rangeRadio.stateValue = "r" + str(ranges[i])
		rangeRadio.checkState()

		vboxrange.addWidget(rangeRadio)
		# rangeGroup.addButton(rangeRadio)
		vboxrange.setStretch(i +1, 1)
	# rangeRadio.setChecked(True)

	label = Qtw.QLabel("Range")
	label.setAlignment(QtCore.Qt.AlignCenter)
	vboxrange.addWidget(label)

	vboxrange.addStretch(1)

	rangeGroup.setLayout(vboxrange)
	# hbox.addLayout(vboxrange)
	hbox.addWidget(rangeGroup)

	knob = Knob.Knob(3, "Vco2")
	knob.sizeType = 2
	knob.setStyleSheet(knobDefaultStyleSheet('vco2'))
	knob.setStateParam("vco2knobfreq")
	knob.checkState()

	hbox.addWidget(knob)

	slider = WaveSlider.WaveSlider(5, 'left')
	slider.setValue(4)
	slider.setStateParam("vco2wave")
	slider.checkState()

	hbox.addWidget(slider)

	a = 15
	b = 20
	unit = 100

	stretch_slider = a
	stretch_radio = 2 * b
	stretch_knob = unit - stretch_slider - stretch_radio / 2

	stretches = [stretch_slider, stretch_knob, stretch_radio, stretch_knob, stretch_slider]
	# print(stretches)

	for i in range(5):
		hbox.setStretch(i, stretches[i])
	return hbox, stretches


def thirdLine():
	hbox = Qtw.QHBoxLayout()

	layoutConf(hbox)
	titles = ['Sub1', 'Sub2']
	stateParams = ["vco1sub1div", "vco1sub2div", "vco2sub1div", "vco2sub2div"]


	for i in range(4):

		knob = Knob.Knob(3, titles[np.mod(i, 2)])
		knob.setStyleSheet(knobDefaultStyleSheet('vco' + str(i//2 + 1)))
		knob.setMaximum(16)
		knob.setMinimum(1)

		knob.setStateParam(stateParams[i])
		knob.checkState()

		hbox.addWidget(knob)

	return hbox


def fourthLine():
	hbox = Qtw.QHBoxLayout()

	# layoutConf(hbox)
	# print(hbox.spacing())
	# print(hbox.contentsMargins())

	hbox.setContentsMargins(10, 0, 10, 0)
	hbox.setSpacing(20)

	hbox.addWidget(SectionLabel.SectionLabel("Seq1Assign"))
	hbox.addWidget(SectionLabel.SectionLabel("Seq2Assign"))

	return hbox


def fifthLine():
	hbox = Qtw.QHBoxLayout()

	# layoutConf(hbox)

	for i in range(2):
		widget = Qtw.QWidget()
		hbox_i = Qtw.QHBoxLayout()
		# layoutConf(hbox_i)

		titles = ["Vco" + str(i + 1), "Sub1", "Sub2"]
		for ii in range(3):
			button = Button(titles[ii])
			button.setCheckable(True)
			button.setStyleSheet(buttonDefaultStyleSheet())

			stateParam = "seq" + str(i + 1) + "assign" + titles[ii]

			button.setStateParam(stateParam)
			button.checkState()

			hbox_i.addWidget(button)

		widget.setLayout(hbox_i)
		# hbox.addLayout(hbox_i)
		hbox.addWidget(widget)
		hbox.setStretch(i, 1)

	return hbox


def sixthLine(stretches):
	hbox = Qtw.QHBoxLayout()

	layoutConf(hbox)

	hbox.addStretch(1)

	knob = Knob.Knob(3, "Vco1 level")
	knob.sizeType = 2
	knob.setStyleSheet(knobDefaultStyleSheet('vco1'))
	knob.setStateParam("vco1knoblevel")
	knob.checkState()

	hbox.addWidget(knob)

	vboxquant = Qtw.QVBoxLayout()
	layoutConf(vboxquant)

	quantizes = ["12-ET", "8-ET", "12-JI", "8-JI"]
	quantRadio = ""
	vboxquant.addStretch(1)

	radioWidget = Qtw.QWidget()
	radioWidget.setContentsMargins(0, 0, 0, 0)

	for i in range(4):
		quantRadio = Radio.Radio(quantizes[i], i)
		quantRadio.setStateParam('quantRadio')
		quantRadio.checkState()

		# quantRadio = Qtw.QRadioButton(quantizes[i])
		vboxquant.addWidget(quantRadio)
		# radioGroup.addButton(quantRadio)
		vboxquant.setStretch(i + 1, 1)
	# quantRadio.setChecked(True)

	label = Qtw.QLabel("Quantize")
	label.setAlignment(QtCore.Qt.AlignCenter)

	vboxquant.addWidget(label)

	vboxquant.addStretch(1)

	radioWidget.setLayout(vboxquant)
	# hbox.addLayout(vboxquant)
	hbox.addWidget(radioWidget)

	knob = Knob.Knob(3, "Vco2 level")
	knob.sizeType = 2
	knob.setStyleSheet(knobDefaultStyleSheet('vco2'))
	knob.setStateParam("vco2knoblevel")
	knob.checkState()

	hbox.addWidget(knob)

	hbox.addStretch(1)

	for i in range(5):
		hbox.setStretch(i, stretches[i])

	return hbox


def seventhLine():
	hbox = Qtw.QHBoxLayout()


	layoutConf(hbox)
	titles = ['Sub1 level', 'Sub2 level']
	stateParams = ["vco1sub1knoblevel", "vco1sub2knoblevel", "vco2sub1knoblevel", "vco2sub2knoblevel"]

	for i in range(4):
		knob = Knob.Knob(3, titles[np.mod(i, 2)])
		knob.setStyleSheet(knobDefaultStyleSheet('vco' + str(i // 2 + 1)))

		knob.setStateParam(stateParams[i])
		knob.checkState()

		hbox.addWidget(knob)

	return hbox


def createVcoSection():
	widget = Qtw.QWidget()
	vbox = Qtw.QVBoxLayout(widget)

	layoutConf(vbox)

	"""Add main labels :"""
	labels_hbox = Qtw.QHBoxLayout()

	layoutConf(labels_hbox)

	labels_hbox.addWidget(SectionLabel.SectionLabel("Vco1"))
	labels_hbox.addWidget(SectionLabel.SectionLabel("Vco2"))

	vbox.addLayout(labels_hbox)



	"""Add first knob line"""
	hbox, stretches = secondLine()
	vbox.addLayout(hbox)

	"""Add subs knob line"""
	vbox.addLayout(thirdLine())

	vbox.addWidget(Qtw.QLabel())
	"""Add labels for seq assign"""
	vbox.addLayout(fourthLine())

	"""Add buttons for seq assign"""
	vbox.addLayout(fifthLine())

	"""Add knobs for vol ctrl"""
	vbox.addLayout(sixthLine(stretches))

	"""Add knobs for subs vol ctrl"""
	vbox.addLayout(seventhLine())

	vbox.addWidget(Qtw.QLabel())
	# vbox.addWidget(Qtw.QLabel())

	stretch = [1, 6, 4, 1, 1, 2, 6, 4]
	for i in range(8):
		vbox.setStretch(i, stretch[i])



	return widget


if __name__ == "__main__":

	from gui.minimal_window_for_test import Window
	from PySide6 import QtCore, QtGui

	app = Qtw.QApplication()

	window = Window()
	window.show()

	window.setStyleSheet("QMainWindow{"
	                   "background-color: white;"
	                   # "background-color: #51ceaa;"
	                   "}"
	                   "QGroupBox{"
	                   "border: 0px solid #414141;"
	                   "border-top: 1px solid black;"
	                   "margin: 0px;"
	                   "margin-top: 10px;"
	                   "background-color: white;"
	                   # "background-color: red;"
	                   "padding: 0px; padding-top: 0px}"
	                   "QGroupBox::title{"
	                   "subcontrol-origin: margin;"
	                   "subcontrol-position: top;  "
	                   "padding: 0 10px 0 10px;"
	                   "padding: 0 0px 0 0px;"
	                   "background-color: black;"
	                   "font-size: 500pt;"
	                   "color: white"
	                   "}"
	                   )

	window.setCentralWidget(createVcoSection())

	window.resize(QtCore.QSize(500, 500))

	app.exec_()