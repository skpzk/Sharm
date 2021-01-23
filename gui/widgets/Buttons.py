from PySide6 import QtGui, QtCore
from PySide6.QtWidgets import QApplication, QHBoxLayout, QPushButton, QGroupBox, QGridLayout
from PySide6.QtCore import Qt, QSize


from gui.minimal_window_for_test import Window

import PySide6.QtWidgets as Qtw

from state.State import State

implementedButtons = ['Play', 'Seq1', 'Seq2', 'Vco1', 'Vco2', 'Sub1', 'Sub2', 'Next', 'Reset', 'EG']


# class Button(Qtw.QPushButton):
class Button(Qtw.QAbstractButton):
	def __init__(self, title: str):
		# super(Button, self).__init__(title)
		super(Button, self).__init__()
		# self._text = title
		self.setText(title)



		self._stateKey = title.lower()

		# QPushButton(self).clicked.connect(self.warnState())
		self.clicked.connect(self.warnState)

		self.pressedColor = QtGui.QColor("#444444")

		self.setSizePolicy(Qtw.QSizePolicy.Expanding, Qtw.QSizePolicy.Expanding)
		# self.setSizePolicy(Qtw.QSizePolicy.Ignored, Qtw.QSizePolicy.Ignored)
		self.setMinimumHeight(10)

		if title not in implementedButtons:
			self.bgColor = QtGui.QColor(int("0xcccccc", 0))
		else:
			self.bgColor = QtGui.QColor("white")
			# self.bgColor = QtGui.QPainter(self).background().color()
			# self.bgColor = None

	def getColorFromStyleSheet(self):
		s = self.styleSheet()
		# print(s)
		s = s.split("}")
		style = None
		color = QtGui.QColor("black")
		bgColor = QtGui.QColor("white")
		if self.isDown():
			for subs in s:
				if "Pressed" in subs:
					style = subs
					break
		elif self.isChecked():
			for subs in s:
				if "Checked" in subs:
					style = subs
					break
		else:
			for subs in s:
				if "Button{" in subs:
					style = subs
					break
		if style is not None:
			style = style.split(";")
			for subs in style:
				if "background" in subs:
					bgColor = QtGui.QColor(subs.split(" ")[-1])
					# print("bgColor = ", subs.split(" ")[-1])
				if "color" in subs and "background" not in subs:
					color = QtGui.QColor(subs.split(" ")[-1])

		return color, bgColor

	def sizeHint(self) -> QtCore.QSize:
		return QtCore.QSize(100, 50)

	def warnState(self):
		State.params[self._stateKey] = self.isChecked() * 1
		# print("key =", self._stateKey, "clicked")
		# print("key =", self._stateKey, "Statevalue = ", State.params[self._stateKey], "value = ", self.isChecked(), "Warning state")

	def warnStatePressed(self):
		State.params[self._stateKey] = self.isDown() * 1
		# print("Pressed")
		# print("key =", self._stateKey, "Statevalue = ", State.params[self._stateKey], "value = ", self.isChecked(), "Warning state")

	def checkState(self):
		try:
			# self.setValue(State.params[self._stateKey] * self.maximum())
			checked = State.params[self._stateKey] * 1
			self.setChecked(checked == 1)
		# mprint("key =", self._stateKey, "Statevalue = ", State.params[self._stateKey], "value = ", self.value())
		except KeyError:
			# print("Key error : key =", self._stateKey)
			self.warnState()

	def setStateParam(self, param: str):
		self._stateKey = param.lower()

	def paintEvent(self, arg__1: QtGui.QPaintEvent) -> None:

		p = QtGui.QPainter(self)

		p.setBackgroundMode(Qt.OpaqueMode)
		# bgColor = QtGui.QColor(p.background().color())
		bgColor = self.bgColor
		pointColor = QtGui.QColor(p.pen().color())

		p.setRenderHint(QtGui.QPainter.Antialiasing)

		# select colors depending on the state

		# print("checked")
		# bgColor = QtGui.QColor("black")
		# pointColor = QtGui.QColor("white")
		pointColor, bgColor = self.getColorFromStyleSheet()
		if hasattr(self, "held"):
			if self.held and not self.isDown():
				bgColor = QtGui.QColor(self._heldColor)

			# pointColor = QtGui.QColor("black")
		# print("check state :", self.checkState())
		# print("pressed     :", self.isDown())

		p.setBrush(QtGui.QBrush(bgColor))

		# draw outer rect
		# w = QPushButton.width(self)
		# h = QPushButton(self).height()
		w = self.width()
		h = self.height()
		p.drawRect(QtCore.QRectF(0, 0, w, h))

		# draw text
		p.setPen(pointColor)
		p.setBackgroundMode(Qt.TransparentMode)
		p.drawText(QtCore.QRectF(0, 0, w, h), Qt.AlignHCenter| Qt.AlignVCenter,  self.text())
