import PySide6.QtWidgets as Qtw

from PySide6 import QtGui
from PySide6.QtGui import QPaintEvent, QColor
from PySide6.QtCore import Qt, QPoint

from gui.utils import *
from gui.widgets.Patchpoint import Patchpoint
from state.State import State


pcColors = ["0x009acd",
            "0xcd0000",
            "0xee2c2c",
            "0xeeb422",
            "0xffd700",
            "0x00b2ee",
            "0x68228b",
            "0xff8c00",
            "0x228b22",
            "0x00ee76",
            "0xff69b4"]


class StateConnectEvent:
	def __init__(self, connect: bool, out: str):
		self.connect = connect
		self.out = out



def compute_point_on_segment(A: QtCore.QPoint, B: QtCore.QPoint, ratio: float) -> QtCore.QPoint:
	"""
	returns point at distance ratio * dtstance(AB) from point A in the direction of point B
	"""
	cos1 = B.x() - A.x()
	sin1 = B.y() - A.y()

	theta1 = np.arctan2(sin1, cos1)
	d = distance(A, B)
	return QtCore.QPoint(A.x() + ratio * d * np.cos(theta1), A.y() + ratio * d * np.sin(theta1))


def compute_control_points(A, B) -> (QtCore.QPoint, QtCore.QPoint, QtCore.QPoint):
	"""
	computes the coordinates of the control points to create a bezier curve
	the curve mimics a quadratic curve
	"""
	middlePoint = QtCore.QPoint(int(np.mean([A.x(), B.x()])), np.max([A.y(), B.y()]) + 50)
	# print("M :", middlePoint)

	# the distance of 2/3 creates a quadratic curve

	c1 = compute_point_on_segment(A, middlePoint, 2/3)
	c2 = compute_point_on_segment(B, middlePoint, 2/3)
	# print("c1 :", c1)
	# print("c2 :", c2)

	return c1, c2, middlePoint


class Patchcord(Qtw.QWidget):
	colors = pcColors.copy()

	def __init__(self, parent: Qtw.QWidget):
		super(Patchcord, self).__init__(parent)
		self.setAttribute(Qt.WA_TransparentForMouseEvents)
		self.startPoint = QPoint(0, 0) # the names startPoint and endPoint are arbitrarily attributed
		self.endPoint = QPoint(0, 0)  # they do not correspond to in or out
		self.endPointIo = ""

		self.startPp = None
		self.endPp = None

		self.inpp = None
		self.outpp = None

		self.isHovered = True

		# self.raise_()
		self.show()

		if len(self.colors) < 1:
			self.colors = pcColors.copy()
		self.color = QColor(int(self.colors.pop(np.random.randint(len(self.colors))),0))

	def connectPC(self):
		# cprint("Connect PC called")
		self.inpp.pcs.add(self)
		self.outpp.pcs.add(self)
		try:
			State.params['patchbay'][self.inpp.title] = StateConnectEvent(True, self.outpp.title)
		except KeyError:
			pass

	def deleteFromPpLists(self):
		if self.inpp is not None:
			if self in self.inpp.pcs:
				self.inpp.pcs.remove(self)
		if self.outpp is not None:
			if self in self.outpp.pcs:
				self.outpp.pcs.remove(self)

	def disconnectPC(self, pp):
		# cprint("diconnect PC called, pp.io = ", pp.io)
		try:
			State.params['patchbay'][self.inpp.title] = StateConnectEvent(False, self.outpp.title)
		except KeyError:
			pass

		if pp.io == 'out':

			self.endPp = self.outpp
			self.endPoint = self.outpp.getCenter()

			self.startPp = self.inpp
			self.startPoint = self.inpp.getCenter()

			self.outpp = None

		else:

			self.endPp = self.inpp
			self.endPoint = self.inpp.getCenter()

			self.startPp = self.outpp
			self.startPoint = self.outpp.getCenter()

			self.inpp = None
		self.endPointIo = pp.io
		self.repaint()

	def setPoints(self, **kwargs):
		for key, value in kwargs.items():

			if key == 'startpp' and isinstance(value, Patchpoint):
				# cprint("set start pp")
				self.startPoint = value.getCenter()
				self.startPp = value
				if value.io == 'in':
					self.inpp = value
					self.endPointIo = 'out'
				else:
					self.outpp = value
					self.endPointIo = 'in'

			if key == 'pos' and isinstance(value, Patchpoint):
				# print("set loose end pos")
				self.endPoint = value.getCenter()

			if key == 'pos' and (isinstance(value, QtCore.QPointF) or isinstance(value, QtCore.QPoint)):
				# print("set loose end pos")
				self.endPoint = value

			if key == 'endpp' and isinstance(value, Patchpoint):
				# cprint("set end pp")
				self.endPoint = value.getCenter()
				self.endPp = value
				if value.io == 'in':
					self.inpp = value
				else:
					self.outpp = value

	def resizeEvent(self, event:QtGui.QResizeEvent) -> None:
		self._get_start_and_end_points()

	def _get_start_and_end_points(self):
		if self.startPp is not None:
			self.startPoint = self.startPp.getCenter()
		if self.endPp is not None:
			self.endPoint = self.endPp.getCenter()

	def paintEvent(self, event: QPaintEvent) -> None:
		p = QtGui.QPainter(self)
		p.setRenderHint(QtGui.QPainter.Antialiasing)

		pen = QtGui.QPen(QtGui.QColor("black"), 1)

		pen.setCapStyle(Qt.RoundCap)
		p.setPen(pen)

		path = QtGui.QPainterPath(self.startPoint)
		c1, c2, m = compute_control_points(self.startPoint, self.endPoint)
		if self.startPoint != self.endPoint:
			path.cubicTo(c1, c2, self.endPoint)
		else:
			path.lineTo(m)
		# path.lineTo(self.end)
		if self.isHovered:
			alpha = 255
		else:
			alpha = 100
		bgColor = QtGui.QColor(0, 0, 0, alpha)
		pen = QtGui.QPen(bgColor, 11)
		pen.setCapStyle(Qt.RoundCap)
		p.setPen(pen)
		p.drawPath(path)

		color = self.color
		color.setAlpha(alpha)

		pen.setColor(color)
		pen.setWidth(10)
		p.setPen(pen)
		p.drawPath(path)