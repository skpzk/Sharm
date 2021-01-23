from PySide6 import QtCore, QtGui
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import QEvent
from PySide6.QtCore import Qt

import PySide6.QtWidgets as Qtw

from gui.sections import Patchbay, Vcos, Rhythm, Sequencer, Env, Filter, General, Transport

from gui.defs import *
from gui.widgets.Buttons import Button

"""
to do :
+ rewrite paint event for groupBox title
+ move section creation in gui.sections
- check todo for knob & patchpoint
"""

class Window(QMainWindow):
	def __init__(self):
		super(Window, self).__init__()
		self.installEventFilter(self)

		layout = QHBoxLayout()

		layout.setSpacing(0)
		layout.setContentsMargins(10, 10, 10, 10)

		layout.addWidget(self.createMainSection())
		layout.setStretch(0, 580)
		self.patchbay = self.createPatchbay()
		layout.addWidget(self.patchbay)
		layout.setStretch(1, 280)

		layout.setSpacing(8)

		self.setStyleSheet(mainWindowStyleSheet())

		centralWidget = QWidget(self)
		self.setCentralWidget(centralWidget)
		centralWidget.setLayout(layout)

		self.setWindowTitle("Sharm v2")
		self.setWindowIcon(QtGui.QIcon("gui/images/icon.svg"))
		# self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint)
		self.setFocus()

	def eventFilter(self, watched, event):
		if event.type() == QEvent.Type.KeyPress:
			if event.key() == Qt.Key_Q:
				QApplication.quit()
			elif event.key() == Qt.Key_Space:
				playButton = self.findChildren(Button, QtCore.QRegularExpression(''))
				for button in playButton:
					if button.text() == "Play":
						button.setChecked(not button.isChecked())
						button.warnState()
						break
			return True
		return False

	def createMainSection(self):
		widget = QWidget()
		layout = QVBoxLayout()

		layout.addWidget(self.createTopControls())
		layout.addWidget(self.createBottomControls())

		layout.setStretch(0, 5)
		layout.setStretch(1, 1)

		widget.setLayout(layout)
		layout.setContentsMargins(0, 0, 0, 0)
		widget.setContentsMargins(0, 0, 0, 0)
		return widget

	def createTopControls(self):
		widget = QWidget()
		layout = QHBoxLayout()

		layout.addWidget(self.createSequencerControls())
		layout.addStretch(1)
		layout.addWidget(self.createVcoSection())

		layout.setContentsMargins(0, 0, 0, 0)
		layout.setStretch(0, 8)

		layout.setStretch(2, 8)

		widget.setContentsMargins(0, 0, 0, 0)

		widget.setLayout(layout)
		return widget

	def createSequencerControls(self):
		widget = QWidget()
		layout = QVBoxLayout()

		layout.addWidget(self.createSequencerSections(1))
		layout.addWidget(self.createSequencerSections(2))
		layout.addWidget(self.createRhythmSection())

		hbox = Qtw.QHBoxLayout()
		hbox.setContentsMargins(0, 0, 0, 0)
		hbox.addWidget(self.createTransportSection())
		hbox.addWidget(self.createEnvSection())
		hbox.setStretch(0, 1)
		hbox.setStretch(1, 1)

		layout.addLayout(hbox)

		layout.setContentsMargins(0, 0, 0, 0)
		widget.setContentsMargins(0, 0, 0, 0)
		layout.setStretch(0, 2)
		layout.setStretch(1, 2)
		layout.setStretch(2, 4)
		layout.setStretch(3, 2)

		widget.setLayout(layout)
		return widget

	def createBottomControls(self):
		widget = QWidget()
		layout = QHBoxLayout()

		layout.addWidget(self.createGeneralSection())
		layout.addWidget(self.createFilterSection())

		layout.setContentsMargins(0, 0, 0, 0)
		widget.setContentsMargins(0, 0, 0, 0)

		widget.setLayout(layout)
		return widget

	def createPatchbay(self):
		return Patchbay.Patchbay(self)

	def createSequencerSections(self, seqID):
		return Sequencer.createSequencerSections(seqID, self)

	def createRhythmSection(self):
		return Rhythm.createRhythmSection()

	def createVcoSection(self):
		return Vcos.createVcoSection()

	def createTransportSection(self):
		return Transport.createTransportSection()

	def createGeneralSection(self):
		return General.createGeneralSection()

	def createFilterSection(self):
		return Filter.createFilterSection()

	def createEnvSection(self):
		return Env.createEnvSection()
