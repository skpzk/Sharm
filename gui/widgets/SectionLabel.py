import PySide6.QtWidgets as Qtw
from PySide6 import QtGui, QtCore


class SectionLabel(Qtw.QLabel):
	def __init__(self, text):
		# print(text)
		super(SectionLabel, self).__init__(text)
		self.padding = 0.2
		self._barsColor = QtGui.QColor("black")

	def _getBarsColor(self):
		# print("getfixedSize called")
		return self._barsColor

	def _setBarsColor(self, color: str):
		# print("setfixedSize called")
		self._barsColor = QtGui.QColor(color)

	barsColor = QtCore.Property(str, _getBarsColor, _setBarsColor)

	def paintEvent(self, arg__1: QtGui.QPaintEvent) -> None:
		p = QtGui.QPainter(self)
		font = p.font()
		fontsize = font.pointSizeF()

		p.setBackgroundMode(QtCore.Qt.TransparentMode)
		pointColor = QtGui.QColor(p.pen().color())
		bgColor = QtGui.QColor(p.background().color())

		# draw outer rect for dbg
		# p.drawRect(QtCore.QRectF(0, 0, self.width()-1, self.height()-1))

		# font.setPointSizeF()

		metrics = QtGui.QFontMetrics(font)

		rect = metrics.boundingRect(self.text())

		center = QtCore.QPoint(int(self.width()/2), int(self.height()/2)+1)

		padding = self.padding * fontsize

		text_rect = QtCore.QRectF(center.x() - rect.width()/2 - padding,
		                          center.y() - rect.height()/2,rect.width() + 2 * padding, rect.height())

		p.setBrush(QtGui.QBrush(pointColor))
		p.drawRect(text_rect)
		text_rect.setX(text_rect.x() + padding)
		p.setPen(QtGui.QColor(bgColor))
		# p.setPen(QtGui.QColor("red"))
		# print("label text = ", type(text))
		p.drawText(text_rect, self.text())


		p.setPen(self._barsColor)
		p.drawLine(QtCore.QPointF(center.x() + rect.width()/2 + padding*4, center.y()),
		           QtCore.QPointF(self.width(), center.y()))
		p.drawLine(QtCore.QPointF(center.x() - rect.width() / 2 - padding * 4, center.y()),
		           QtCore.QPointF(0, center.y()))
