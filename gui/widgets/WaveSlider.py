import PySide6.QtWidgets as Qtw
from PySide6 import QtGui

from gui.utils import *
from state.State import State


def compute_sqr_path(x0, y0, width, height):
	amplitude = height / 2
	y_middle = y0 + amplitude

	distance_x = width / 2

	points = []

	p1 = QtCore.QPointF(x0, y_middle + amplitude)
	points.append(QtCore.QPointF(x0, y0))
	points.append(QtCore.QPointF(x0 + 2 * distance_x, y0))
	points.append(QtCore.QPointF(x0 + 2 * distance_x, y_middle + amplitude))

	path = QtGui.QPainterPath(p1)

	for point in points:
		path.lineTo(point)

	return path


def compute_tri_path(x0, y0, width, height):
	amplitude = height / 2

	distance_x = width / 2

	points = []

	p1 = QtCore.QPointF(x0, y0 + height)
	points.append(QtCore.QPointF(x0 + distance_x, y0))
	points.append(QtCore.QPointF(x0 + 2 * distance_x, y0 + height))

	path = QtGui.QPainterPath(p1)

	for point in points:
		path.lineTo(point)

	return path


def compute_saw_path(x0, y0, width, height):
	amplitude = height / 2

	points = []

	p1 = QtCore.QPointF(x0, y0 + height)
	points.append(QtCore.QPointF(x0 + width, y0))
	points.append(QtCore.QPointF(x0 + width, y0 + height))

	path = QtGui.QPainterPath(p1)

	for point in points:
		path.lineTo(point)

	return path


def compute_arrow(x0, y0, width, height):
	# width = c * cos(30°)
	# c = w/cos(30°)

	c = np.min([width, height / np.cos(np.deg2rad(30))])
	y_middle = y0 + height / 2

	x_middle = x0 + width / 2

	distance_y = c * np.cos(np.deg2rad(30))

	points = []

	p1 = QtCore.QPointF(x_middle - c / 2, y_middle - distance_y / 2)
	points.append(QtCore.QPointF(x_middle + c / 2, y_middle - distance_y / 2))
	points.append(QtCore.QPointF(x_middle, y_middle + distance_y / 2))
	points.append(p1)

	poly = QtGui.QPolygonF(points)

	return poly


class WaveSlider(Qtw.QSlider):
	def __init__(self, nb_items, direction: str = "right"):
		super(WaveSlider, self).__init__()
		self.steps = nb_items
		self.setMaximum(nb_items - 1)
		self.setSizePolicy(Qtw.QSizePolicy.Expanding, Qtw.QSizePolicy.Expanding)

		self.handlePos = QtCore.QPointF(0, 0)
		self.barRect = QtCore.QRectF(0, 0, 0, 0)

		self.direction = direction

		self._stateKey = ""
		self.valueChanged.connect(self.warnState)

		self.setValue(0)

	# connect(tableWidget,SIGNAL(itemChanged(QTableWidgetItem *)), this, SLOT(on_any_itemChanged(QTableWidgetItem *)));

	def warnState(self):
		State.params[self._stateKey] = self.value() / self.maximum()

	def checkState(self):
		try:
			self.setValue(State.params[self._stateKey] * self.maximum())
		except KeyError:
			self.warnState()

	def setStateParam(self, param: str):
		self._stateKey = param.lower()

	def mouseMoveEvent(self, ev: QtGui.QMouseEvent) -> None:
		# move handle to the correct pos
		# print("cursor on bar :", self.barRect.contains(ev.pos()))
		if self.barRect.contains(ev.pos()):
			pos = self.getMousePositionInSteps(ev.pos())
			self.setValue(pos)

	def getMousePositionInSteps(self, mousePos):
		dist = np.abs(self.barRect.y() - mousePos.y() + self.barRect.height())
		posfloat = dist / self.barRect.height() * self.steps
		pos = np.floor(posfloat)
		# pos = (self.steps) - pos
		# print("pos = ", pos, "distance =", dist, "step = ", posfloat)
		return pos

	def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
		# if mouse on handle : grab and move it
		# else : move handle to the correct pos
		# print("cursor on bar :", self.barRect.contains(ev.pos()))
		if self.barRect.contains(ev.pos()):
			pos = self.getMousePositionInSteps(ev.pos())
			self.setValue(pos)

	def mouseReleaseEvent(self, ev: QtGui.QMouseEvent) -> None:
		pass

	def paintEvent(self, arg__1: QtGui.QPaintEvent) -> None:

		p = QtGui.QPainter(self)

		bgColor = QtGui.QColor(p.background().color())
		bgColor.setNamedColor("transparent")
		pointColor = QtGui.QColor(p.pen().color())

		p.setBrush(QtGui.QBrush(bgColor))
		# if self.direction == 'right':
		# 	p.drawRect(QtCore.QRectF(0, 0, self.width(), self.height()))
		# else:
		# 	p.drawRect(QtCore.QRectF(0, 0, self.width(), self.height()))

		#### compute size, depending on available space and nb of items

		# width represents the width of the rectangle containing the handle
		# height = steps * width
		# width = min(self.width / 2, self.height/steps)

		width = np.min([self.width()/2, self.height() / self.steps])

		# dbg
		# width = 9

		height = width * self.steps

		"""draw outer rect"""
		if self.direction == 'right':
			outer_rect_x = 0
			outer_rect_y = 0
		else:
			outer_rect_x = self.width() - width
			outer_rect_y = 0

		rect = QtCore.QRectF(outer_rect_x, outer_rect_y, width-1, height)

		p.drawRect(rect)
		# p.drawText(QtCore.QPointF(0, 70), str(self.value()))

		p.setRenderHint(QtGui.QPainter.Antialiasing)
		"""draw handle"""
		p.setBrush(QtGui.QBrush(pointColor))

		margin = width * 1 / 9

		x0_handle = 2 * margin + outer_rect_x
		y0_handle = 2 * margin + outer_rect_y
		y_handle = int((self.maximum() - self.value()) / (self.maximum() + 1) * height)
		w_handle = width - 4 * margin
		h_handle = width - 4 * margin

		handleRect = QtCore.QRectF(x0_handle, y0_handle + y_handle, w_handle,
		                           h_handle)
		p.drawRect(handleRect)

		self.handlePos = QtCore.QPointF(x0_handle, y0_handle)

		if self.direction == 'right':
			self.barRect = QtCore.QRectF(outer_rect_x, outer_rect_y, 2 * width, height)
		else:
			self.barRect = QtCore.QRectF(outer_rect_x - width, outer_rect_y, 2 * width, height)


		p.setRenderHint(QtGui.QPainter.Antialiasing)

		# draw waves indicators :
		# sqr, saw, between sqr and saw, tri, sin

		p.setBrush(QtGui.QBrush(bgColor))
		margin = width * 2 / 9
		# print("margin = ", margin)
		width_w_indic = width - 2 * margin
		height_w_indic = width - 2 * margin

		if self.direction == 'right':
			x0_w = width + margin
		else:
			x0_w = outer_rect_x - width + margin
		y0_w = 0 + margin

		# sin wave :
		radius_sine_wave_indic = width_w_indic / 2
		p.drawEllipse(QtCore.QPointF(x0_w + radius_sine_wave_indic, y0_w + radius_sine_wave_indic), radius_sine_wave_indic,
		              radius_sine_wave_indic)

		# tri wave :
		path = compute_tri_path(x0_w, y0_w + width, width_w_indic, height_w_indic)
		p.drawPath(path)

		# saw wave :
		path = compute_saw_path(x0_w, y0_w + 2 * width, width_w_indic, height_w_indic)
		p.drawPath(path)

		# btw sqr and saw wave :
		poly = compute_arrow(x0_w, y0_w + 3 * width, (width_w_indic), height_w_indic)
		p.drawPolygon(poly)

		# square wave :
		p.setBrush(QtGui.QBrush(bgColor))
		path = compute_sqr_path(x0_w, y0_w + 4 * width, width_w_indic, height_w_indic)
		p.drawPath(path)

	# p.drawLine(QtCore.QPointF(self.width() / 2, 0), QtCore.QPointF(self.width() / 2, self.height()))
