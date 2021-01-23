from PySide6 import QtGui
from PySide6.QtCore import QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush
from PySide6.QtWidgets import QRadioButton, QStyleOption

import PySide6.QtWidgets as Qtw

from PySide6.QtCore import Qt
from gui.utils import *
from state.State import State

colors = ["0x38e643",
					"0x1e62ff",
					"0xf91c1c",
					"0xff7d00",
					"0x1e62ff",
					"0xf91c1c"
					]


class Radio(QRadioButton):
	def __init__(self, text: str, ID: int):
		super(Radio, self).__init__(text)
		# self.setSizePolicy(Qtw.QSizePolicy.Expanding, Qtw.QSizePolicy.Expanding)
		self.setSizePolicy(Qtw.QSizePolicy.Ignored, Qtw.QSizePolicy.Ignored)
		self._ID = ID

		self.setMinimumWidth(10)
		self.setMinimumHeight(15)
		# self.setMinimumSize(QtCore.QSize(0, 0))
		self.minimumSizeHint()

		self.center = QtCore.QPoint(0, 0)
		self.radius = 1
		self.textRect = QtCore.QRect(0, 0, 0, 0)

		self._stateKey = ""
		self.stateValue = self.text()

		self.toggled.connect(self.warnState)

		# self.hasFixedSize = False
		# self.fixedSize = 0
		self.paintSize = 0
		self.fontsize = 0
		self.fontsizefactor = 1.5

	def warnState(self):
		if self.isChecked():
			# print("radio text = ", self.text())
			State.params[self._stateKey] = self.stateValue

	def checkState(self):
		try:
			# print("State.params[self._stateKey] = ", State.params[self._stateKey], "self.text() = ",  self.stateValue, "==? :", State.params[self._stateKey] ==  self.stateValue)
			if State.params[self._stateKey] == self.stateValue:
				self.setChecked(True)
			else:
				self.setChecked(False)
		except KeyError:
			print("key error")
			self.setChecked(True)

	def setStateParam(self, param: str):
		self._stateKey = param.lower()

	def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
		if (distance(self.center, e.pos()) < self.radius ) or self.textRect.contains(e.pos()):
			self.setChecked(True)

	def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
		parent = self.topLevelWidget()
		# print(parent)
		radios = parent.findChildren(Radio, QtCore.QRegularExpression(''))
		# print("type of radios :", type(radios))
		self.computeSize()
		minsize = self.paintSize
		for radio in radios:
			if radio != self:
				radio.computeSize()
				minsize = min(minsize, radio.paintSize)

		# print("minsize = ", minsize)

		if minsize > 0:
			self.paintSize = minsize
			for radio in radios:
				# radio.resize(self.size())
				if radio.paintSize != minsize:
					radio.paintSize = minsize
					radio.repaint()
			labels = parent.findChildren(Qtw.QLabel, QtCore.QRegularExpression(''))
			# print("labels =", labels)
			for label in labels:
				if label.text() in ["Range", "Quantize"]:
					if self.fontsize != 0:
						# print("found fontsize")
						font = label.font()
						font.setPointSizeF(self.fontsize)
						label.setFont(font)



	def computeSize(self):
		self.paintSize = np.min([1/8 * self.width(), self.height()/4])
		self.fontsize = self.paintSize * self.fontsizefactor

	def paintEvent(self, ev):
		# print("Radio paintEventCalled")
		# print("size =", self.paintSize)

		opt = QStyleOption()
		opt.initFrom(self)
		painter = QPainter(self)


		# print("minimum size : ", self.minimumSize())
		# print("radio: hasHforW : ", self.hasHeightForWidth())
		# print("radio: size : ", self.size())
		# print("radio : minimumSizeHint() :", self.minimumSizeHint())



		# s = self.style()

		# s.drawPrimitive(QStyle.PE_Widget, opt, painter, self)

		# self.computeSize()
		size = self.paintSize
		# size = np.min([1/8 * self.width(), self.height()/4])

		fontsizefactor = self.fontsizefactor

		linewidth = 1

		painter.setRenderHint(QPainter.Antialiasing)

		pointColor = QColor(painter.pen().color())
		bgColor = QColor(painter.background().color())
		# bgColor = QColor("white")

		painter.setBrush(QBrush(QColor("transparent")))
		painter.setPen(QPen(QColor(pointColor), linewidth))
		# painter.setBackgroundMode(Qt.TransparentMode)

		center = QtCore.QPoint(int(self.width()/2), int(self.height()/2))
		self.center = center
		self.radius = size

		painter.drawEllipse(center, size, size)

		margin = .4 * size



		# painter.drawRect(text_rect)
		# self.text()

		fontsize = size * fontsizefactor
		# self.fontsize = fontsize

		f = painter.font()
		f.setPointSizeF(fontsize)
		painter.setFont(f)

		text_rect = QRectF(center.x() + size + margin, center.y() - fontsize, 100, 2 * fontsize)
		# painter.drawRect(text_rect)
		painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, self.text())

		self.textRect = text_rect

		if self.isChecked():
			painter.setBrush(QBrush(QColor(int(colors[self._ID], 0))))
			# painter.setPen(QPen(Qt.NoPen))
			painter.drawEllipse(center, size, size)

		# painter.drawLine(QtCore.QPointF(self.width()/2, 0), QtCore.QPointF(self.width()/2, self.height()))

		pass
