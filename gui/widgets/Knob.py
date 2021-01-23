from PySide6.QtWidgets import QDial
from PySide6.QtGui import QPainter, QColor, QPen, QBrush
from PySide6.QtCore import Qt, Slot
from PySide6 import QtCore, QtGui
from PySide6.QtCore import Signal

from state.State import State

from gui.utils import *


import numpy as np

""" 
	todo:
		- display other values
		- qproperty to change range
		- change value from external
		- send value change to state
		- get same linewidth for different sizes, but linewidth can grow when resizing
		- same for fontsize
"""
"""
size management:
	a knob gets a base size for which it has a linewidth of x and a fontsize of y
	if its size changes, the linewidth and fontsize change to keep good proportions
"""

"""
State management :
Bug :
- when setting value from state, if knob.setMax or knob.setMin is called before knob.checkState, 
the value of checkState will be ignored
	- workaround : call knob.setStateParam with a different key just before calling knob.checkState
	- a better workaround would be to ignore valueChanged when it is called because of a setMax 
"""

implementedKnobs = ['Vco1', 'Vco2', 'Sub1', 'Sub2', 'Sub1 level', 'Sub2 level', 'Vol', 'Tempo',
                    'Clk1', 'Clk2', 'Clk3', 'Clk4', 'Vco1 level', 'Vco2 level',
                    'Cutoff', 'Reso', 'A', 'D', 'EG Amount',
                    'Step1', 'Step2', 'Step3', 'Step4']

titleColor = "0xfd971f"



class Knob(QDial):
	repaintStepTitle = Signal()
	fontsize1 = 200
	def __init__(self, knobmargin, text: str):
		super(Knob, self).__init__()
		self.installEventFilter(self)

		QDial.setRange(self, 0, 127)
		self._knobMargin = knobmargin
		self._hasFixedSize = False
		self._hasFixedFontSize = False
		self._text = text
		self._fixedSize = 0
		self._fixedFontSize = 0
		self._ringColor = int("0x000000", 0)

		self.relativeSize = 0

		self._stateKey = text.lower()

		self.seq = ""

		self.inhibit_paint = False

		# self.isTitleColored = True
		self.coloredTitle = False

		# it works, despite the warning
		# admittedly, it is a bit convoluted
		self.repaintStepTitle.connect(self.sequencerCallbackSlot)

		self.radius = 0
		self.center = QtCore.QPointF(0, 0)
		self.doubleClick = False

		self.tmpValue = 0

		# most knobs are type 1, only Vco1 and 2 are type 2
		self.sizeType = 1

		# print("knob initialized")
		# self.connect(QDial, valueChange)
		self.setValue(0)
		self.valueChanged.connect(self.warnState)


	# connect(tableWidget,SIGNAL(itemChanged(QTableWidgetItem *)), this, SLOT(on_any_itemChanged(QTableWidgetItem *)));

	def warnState(self):
		# mprint("key =", self._stateKey, "Statevalue = ", State.params[self._stateKey], "value = ", self.value(), "Warning state")
		# print("value = ", self.value())
		State.params[self._stateKey] = self.value() / self.maximum()

	def checkState(self):
		try:
			self.setValue(State.params[self._stateKey] * self.maximum())
			# mprint("key =", self._stateKey, "Statevalue = ", State.params[self._stateKey], "value = ", self.value())
		except KeyError:
			# print("Key error : key =", self._stateKey)
			self.warnState()

	def setStateParam(self, param: str):
		self._stateKey = param.lower()

	def _getFixedSize(self):
		# print("getfixedSize called")
		return self._fixedSize

	def _setFixedSize(self, size):
		# print("setfixedSize called")
		self._fixedSize = float(size)
		self._hasFixedSize = True

	def _getFixedFontSize(self):
		# print("getfixedSize called")
		return self._fixedFontSize

	def _setFixedFontSize(self, size):
		# print("setfixedSize called")
		self._fixedFontSize = float(size)
		self._hasFixedFontSize = True

	def _getRingColor(self):
		# print("getfixedSize called")
		return "#" + "%06x" %(self._ringColor)

	def _setRingColor(self, color: str):
		# print("setfixedSize called")
		self._ringColor = int("0x" + color[1:], 0)

	fixedSize = QtCore.Property(str, _getFixedSize, _setFixedSize)
	fixedFontSize = QtCore.Property(str, _getFixedFontSize, _setFixedFontSize)
	ringColor = QtCore.Property(str, _getRingColor, _setRingColor)

	def isTitleColored(self):
		if self._text[:-1] == 'Step':
			try:
				activeStep = State.params[self.seq + "activestep"]
				if activeStep == int(self._text[-1]):
					return True
			except KeyError:
				pass
		elif self._text == "Tempo":
			# print("I'm here")
			try:
				tempoKnobActive = State.params["activetempo"]
				if tempoKnobActive == 1:
					# print("yep")
					return True
			except KeyError:
				pass
		elif self._text[:-1] == "Clk":
			# print("I'm here")
			try:
				knobActive = State.params["activerhythm" + str(self._text[-1])]
				if knobActive == 1:
					# print("yep")
					return True
			except KeyError:
				pass
		return False

	def sequencerCallback(self):
		self.repaintStepTitle.emit()

	def mousePressEvent(self, me: QtGui.QMouseEvent) -> None:
		if distance(me.pos(), self.center) < self.radius:
			super(Knob, self).mousePressEvent(me)
		else:
			pass

	def mouseReleaseEvent(self, me: QtGui.QMouseEvent) -> None:
		if distance(me.pos(), self.center) < self.radius:
			if not self.doubleClick:
				# print("mouse event type = ", me.flags == QtCore.Qt.MouseEventCreatedDoubleClick)
				super(Knob, self).mouseReleaseEvent(me)
			else:
				self.doubleClick = False
		else:
			pass

	def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:
		self.doubleClick = True
		if self.value() == 0:
			self.setValue(self.tmpValue)
		else:
			self.tmpValue = self.value()
			self.setValue(0)

	def eventFilter(self, watched: QtCore.QObject, event: QtCore.QEvent) -> bool:
		if event.type() == QtCore.QEvent.Type.KeyPress:
			if event.key() == Qt.Key_M:
				if self.value() == 0:
					self.setValue(self.tmpValue)
				else:
					self.tmpValue = self.value()
					self.setValue(0)
				return True
			elif event.key() == Qt.Key_Escape:
				self.clearFocus()
				return True
		return False

	@Slot()
	def sequencerCallbackSlot(self):
		if self.coloredTitle != self.isTitleColored():
			self.coloredTitle = not self.coloredTitle
			self.repaint()

	def paintEvent(self, pe) -> None:
		if not self.inhibit_paint:

			extent = 1.5 * np.pi
			offset = 1.25 * np.pi

			painter = QPainter(self)

			# So that we can use the background color
			painter.setBackgroundMode(Qt.OpaqueMode)

			# Smooth out the circle
			painter.setRenderHint(QPainter.Antialiasing)

			# Use background color
			bgColor = painter.background().color()
			painter.setBrush(painter.background())
			if self._text not in implementedKnobs:
				painter.setBrush(QtGui.QBrush(QtGui.QColor(int("0xcccccc", 0))))

			# Store color from stylesheet, pen will be overridden
			pointColor = QColor(painter.pen().color())

			# print(QDial.width(self), QDial.height(self))

			# draw widget borders
			pen = QPen(QColor(self._ringColor), 1)
			pen.setCapStyle(Qt.SquareCap)
			painter.setPen(pen)
			# uncomment the following line to draw outer rect
			# painter.drawRect(0, 0, np.floor(QDial.width(self)), QDial.height(self))

			# No border
			painter.setPen(QPen(Qt.NoPen))

			# the heignt of the widget is 2*radius + 2*fontsize1 + 2*fontsize2
			# where fontsize1 = .4radius and fontsize2 = .9*.4*radius
			# so QDial.height = radius * (2+.4*2+.4*.9*2)
			#

			fontsize1factor = .4
			fontsize2reduction = .9
			fontsize2factor = fontsize1factor*fontsize2reduction


			center_x = QDial.width(self) / 2.0
			center_y = QDial.height(self) / 2.0

			if not self._hasFixedSize:
				if not self._hasFixedFontSize:
					radius = np.min((QDial.width(self) / 2. - self._knobMargin,
					                 QDial.height(self) / (2.+ 2*fontsize1factor + 2*fontsize2factor) - self._knobMargin))
					radius = np.max((radius, 1))
					# print("Radius = ", radius, ", height = ", QDial.height(self), ", width = ", QDial.width(self))
					center_y = center_y - radius * (fontsize1factor + fontsize2factor)
				else:
					radius = np.min((QDial.width(self) / 2. - self._knobMargin,
					                 (QDial.height(self) - 4*self._fixedFontSize) / 2. - self._knobMargin))
					radius = np.max((radius, 1))
					center_y = center_y - (self._fixedFontSize * (1+fontsize2reduction))
			else:
				radius = self._fixedSize / 2.
				radius = np.max((radius, 1))
				center_y = center_y - radius * (fontsize1factor + fontsize2factor)

			self.radius = radius

			# Draw arc
			rectangle = QtCore.QRectF(center_x - radius,
			                          center_y - radius,
			                          2 * radius,
			                          2 * radius)

			"""The startAngle and spanAngle must be specified in 1/16th of a degree, 
			i.e. a full circle equals 5760 (16 * 360). 
			Positive values for the angles mean counter-clockwise 
			while negative values mean the clockwise direction. 
			Zero degrees is at the 3 o'clock position."""

			linewidth = radius / 30. * 2

			# linewidth = 1
			pen = QPen(QColor(self._ringColor), linewidth)
			pen.setCapStyle(Qt.RoundCap)
			# pen.setCapStyle(Qt.FlatCap)

			painter.setPen(pen)

			# adapt to linewidth to make it more pleasant to the eye
			capRadius = linewidth/4
			angleCap = np.arcsin(capRadius/radius)

			start_deg = (90 - np.rad2deg(extent/2)) + np.rad2deg(angleCap)
			start_16deg = start_deg * 16

			extent_deg =  np.rad2deg(extent) - 2 * np.rad2deg(angleCap)
			extent_16deg = extent_deg * 16

			painter.drawArc(rectangle, start_16deg, extent_16deg)

			#draw inner circle
			pen = QPen(QColor(pointColor), linewidth)
			pen.setCapStyle(Qt.RoundCap)

			painter.setPen(pen)
			painter.setBrush(QtGui.QColor(bgColor))

			radius_inner = 15./20. * radius
			painter.drawEllipse(QtCore.QPointF(center_x, center_y), radius_inner, radius_inner)

			self.center = QtCore.QPointF(center_x, center_y)


			"""
			# Get ratio between current value and maximum to calculate angle
			if (param != NULL):
				if (param->value != this->value()) 
					param->setValue(this->value())
			"""
			ratio = (QDial.value(self) - QDial.minimum(self)) / (QDial.maximum(self) - QDial.minimum(self))

			# The maximum amount of degrees is 270, offset by 225
			angle = ratio * extent - offset

			# Draw the indicator
			painter.setBrush(QBrush(pointColor))

			a_y = center_y + np.sin(angle) * (radius -.1)
			a_x = center_x + np.cos(angle) * (radius -.1)

			pen = QPen(pointColor, linewidth)
			pen.setCapStyle(Qt.RoundCap)
			painter.setPen(pen)

			painter.drawLine(a_x, a_y, np.round(center_x), center_y)

			if not self._hasFixedFontSize:
				fontsize1 = radius * fontsize1factor
				if self.sizeType == 1 and fontsize1 != Knob.fontsize1:
					Knob.fontsize1 = fontsize1
				else:
					fontsize1 = Knob.fontsize1
				fontsize2 = fontsize1 * fontsize2reduction
			else:
				fontsize1 = self._fixedFontSize
				fontsize2 = fontsize1 * fontsize2reduction



			self.fontsize1 = fontsize1

			textRect_ = QtCore.QRectF(0, center_y + radius, QDial.width(self), 2*fontsize1)

			if self.coloredTitle:
				painter.setPen(QColor(int(titleColor, 0)))


			f = painter.font()
			f.setPointSizeF(fontsize1)
			painter.setFont(f)
			# painter.drawRect(textRect_)
			painter.drawText(textRect_, Qt.AlignHCenter | Qt.AlignTop, self._text)
			# painter.drawText(textRect_, Qt.AlignHCenter | Qt.AlignTop, str(fontsize1))

			textRect_ = QtCore.QRectF(0, center_y + radius + fontsize1*2, QDial.width(self), 2*fontsize2)

			if self.hasFocus():
				painter.setPen(QtGui.QColor("red"))

			f.setPointSizeF(fontsize2)
			painter.setFont(f)
			# painter.drawRect(textRect_)
			painter.drawText(textRect_, Qt.AlignHCenter | Qt.AlignTop, str(QDial.value(self)))

			painter.end()