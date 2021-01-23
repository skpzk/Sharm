from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPolygonF, QFontMetrics
from PySide6 import QtGui

from PySide6.QtCore import Qt, QSize

import PySide6.QtWidgets as Qtw

from gui.utils import *
from gui.widgets.PatchCordList import PatchCordList

implementedPatchPoints = ['VCO 1', 'VCO 2', 'VCO 1 SUB 1', 'VCO 1 SUB 2', 'VCO 2 SUB 1', 'VCO 2 SUB 2',
                          "VCO 1 SUB", "VCO 2 SUB", "VCO 1 PWM", "VCO 2 PWM", 'VCA', 'VCA EG', "RHYTHM 1",
                          "RHYTHM 2", "RHYTHM 3", "RHYTHM 4", "SEQ 1", "SEQ 2", "VCF EG", "CUTOFF", "NOISE",
                          "CLOCK", "SEQ 1 CLK", "SEQ 2 CLK", "SH", "TRIGGER"]

"""
todo : 
- set sizehint
+ manage pcs in a struct
"""


class Patchpoint(QWidget):
	def __init__(self, parent: Qtw.QWidget, text: str, ioType: str = 'in'):
		super(Patchpoint, self).__init__(parent)
		self._ppMargin = 3
		self._hasFixedSize = False
		self._hasFixedFontSize = False
		self._text = text
		self.title = text
		self._fixedSize = 0
		self._fixedFontSize = 0
		self.setMinimumSize(QSize(36, 36))
		self.center = QtCore.QPointF(0, 0)
		self.mainRadius = 0
		if (ioType == 'in') or (ioType == 'out'):
			self.io = ioType
		else:
			self.io = 'in'

		self.lastPc = None
		self.pcs = PatchCordList()

		self.hasPcGrabbed = False
		self._ppColor = QColor("black")

		self.bgColor = QColor("blue")
		self.pointColor = QColor("red")

		self.setMouseTracking(True)
		self.fontsize = -1

	# def connectToPC(self, PC):
	# 	print("Connected")

	def getCenter(self):
		self.computeCenter()
		return self.mapToParent(self.center)


	def setPcToHoveredIfCursorOnPp(self, event):
		if distance(event.pos(), self.center) < self.mainRadius:
			for pc in self.pcs:
				# print("isHovered")
				pc.isHovered = True
				pc.repaint()
		else:
			for pc in self.pcs:
				# print("is not")
				pc.isHovered = False
				pc.repaint()


	def enterEvent(self, event: QtGui.QEnterEvent) -> None:
		self.setPcToHoveredIfCursorOnPp(event)

	def leaveEvent(self, event: QtGui.QEnterEvent) -> None:
		for pc in self.pcs:
			pc.isHovered = False
			pc.repaint()

	# print("knob initialized")

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

	fixedSize = QtCore.Property(str, _getFixedSize, _setFixedSize)
	fixedFontSize = QtCore.Property(str, _getFixedFontSize, _setFixedFontSize)

	def _getPpColor(self):
		# print("getfixedSize called")
		return self._ppColor

	def _setPpColor(self, color: str):
		# print("setfixedSize called")
		self._ppColor = QtGui.QColor(color)

	ppColor = QtCore.Property(str, _getPpColor, _setPpColor)

	def createPoly(self, n_points, radius, center_x, center_y):
		polygon = QPolygonF()
		w = 360 / n_points  # angle per step
		for i in range(n_points):  # add the points of polygon
			t = w * i
			x = radius * np.cos(np.deg2rad(t))
			y = radius * np.sin(np.deg2rad(t))
			polygon.append(QtCore.QPointF(center_x + x, center_y + y))

		return polygon

	def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
		# cprint("mouse press   detected", self._text)

		# if self has no PC or ctrl is pressed :
		if self.pcs.is_empty() or event.modifiers() == Qt.ControlModifier:
			# pb create PC ( anchored end = self, loose end = pouse pos)
			self.parent().createPC(self)
			self.hasPcGrabbed = True
		elif not self.pcs.is_empty():
			# elif self has a pc, disconnect it from self
			pc = self.pcs.last()
			self.pcs.remove(pc)
			self.parent().movePC(pc, self)
			self.hasPcGrabbed = True
	# else : ignore

	def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
		# print("mouse move    detected", self._text)
		if event.buttons() == Qt.LeftButton and self.hasPcGrabbed:
			# send mouse position to pb
			# set pc loos end to mouse pos
			self.parent().moveLastPC(self.mapToParent(event.pos()))
		else:
			# set pc to hevered if the mouse in on the pp
			self.setPcToHoveredIfCursorOnPp(event)


	def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
		if self.hasPcGrabbed:
			# cprint("mouse release detected", self._text)
			# send mouse release to pb
			self.hasPcGrabbed = False
			self.parent().findReleasePp(self.mapToParent(event.pos()))
	# detect pp of release
	# if it exist and is of the good io type, connect pc to pp
	# if not, delete pc

	def isMouseReleaseOnPP(self, pos):

		if distance(self.getCenter(), pos) < self.mainRadius:
			# print("mouse release is on PP", self._text)
			return True, self
		return False, self

	def computeCenter(self):
		height = QWidget.height(self)
		width = QWidget.width(self)
		center_x = width / 2
		center_y = height / 2


		fontsizefactor = .38

		if not self._hasFixedSize:
			if not self._hasFixedFontSize:
				mainradius = np.min((width / 2 - self._ppMargin,
				                     height / (2 + 2 * fontsizefactor) - self._ppMargin))
				mainradius = np.max((mainradius, 1))
				center_y_pp = center_y + mainradius * fontsizefactor
			else:
				mainradius = np.min((width / 2. - self._ppMargin,
				                     (height - 2 * self._fixedFontSize) / 2. - self._ppMargin))
				mainradius = np.max((mainradius, 1))
				center_y_pp = center_y + self._fixedFontSize
		else:
			mainradius = self._fixedSize / 2
			mainradius = np.max((mainradius, 1))
			center_y_pp = center_y + mainradius * fontsizefactor

		self.center = QtCore.QPointF(center_x, center_y_pp)
		self.mainRadius = mainradius

		return mainradius, fontsizefactor, center_x, center_y_pp, width


	def paintEvent(self, pe) -> None:

		mainradius, fontsizefactor, center_x, center_y_pp, width = self.computeCenter()

		painter = QPainter(self)
		# So that we can use the background color
		painter.setBackgroundMode(Qt.OpaqueMode)
		# Smooth out the circle
		painter.setRenderHint(QPainter.Antialiasing)
		# Use background color
		textBgColor = QColor(painter.background().color())
		# print("bgcolor = ", bgColor)
		bgColor = QColor("transparent")
		pointColor = QColor(painter.pen().color())

		self.pointColor = pointColor
		self.bgColor = textBgColor

		alpha = 150

		if self.parent().displayPp == 'all' or self.parent().displayPp == self.io:
			pointColor.setAlpha(255)
		else:
			pointColor.setAlpha(alpha)

		# draw text
		if not self._hasFixedFontSize:
			fontsize = mainradius * fontsizefactor
		else:
			fontsize = self._fixedFontSize
		self.fontsize = fontsize
		textRect_ = QtCore.QRectF(0, center_y_pp - mainradius - 2 * fontsize, width, 2 * fontsize)
		f = painter.font()
		f.setPointSizeF(fontsize)

		# self._io = 'in'
		if self.io == 'out':
			fm = QFontMetrics(f).boundingRect(self._text)
			# print("fm = ", fm)
			painter.setBrush(pointColor)
			painter.setPen(QPen(pointColor))
			painter.drawRect(QtCore.QRectF(center_x - fm.width() / 2, center_y_pp - mainradius - 2 * fontsize,
			                               fm.width(), fm.height()))
			painter.setPen(QPen(textBgColor))

		painter.setFont(f)
		painter.setBackgroundMode(Qt.TransparentMode)
		painter.drawText(textRect_, Qt.AlignHCenter | Qt.AlignTop, self._text)

		# draw hexagon
		painter.setBrush(bgColor)
		painter.setPen(pointColor)
		painter.drawPolygon(self.createPoly(6, mainradius, center_x, center_y_pp))

		# draw outer circle
		radius_outer = mainradius * .8
		if self.title not in implementedPatchPoints:
			painter.setBrush(QtGui.QBrush(QtGui.QColor(int("0x999999", 0))))
		painter.drawEllipse(QtCore.QPointF(center_x, center_y_pp), radius_outer, radius_outer)

		# draw inner circle
		radius_inner = mainradius * .5
		# painter.setBrush(QBrush(pointColor))
		painter.setBrush(QColor(self._ppColor))
		painter.drawEllipse(QtCore.QPointF(center_x, center_y_pp), radius_inner, radius_inner)

	# print("self.center from paintEvent :", self.center)
